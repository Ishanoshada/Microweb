import usocket as socket
import ujson
import ure
import gc
import wifi
import os

class Request:
    def __init__(self, method, path, query_params, post_data):
        self.method = method
        self.path = path
        self.query_params = query_params
        self.form = post_data

class Response:
    def __init__(self, content, status=200, content_type='text/html', headers=None):
        self.content = content
        self.status = status
        self.content_type = content_type
        self.headers = headers or {}
        self.headers['Access-Control-Allow-Origin'] = '*'
    
    def to_http_response(self):
        status_text = {
            200: 'OK', 
            404: 'Not Found', 
            405: 'Method Not Allowed', 
            500: 'Internal Server Error',
            302: 'Found'
        }
        
        response = f'HTTP/1.1 {self.status} {status_text.get(self.status, "OK")}\r\n'
        response += f'Content-Type: {self.content_type}\r\n'
        
        for key, value in self.headers.items():
            response += f'{key}: {value}\r\n'
        
        response += '\r\n'
        response += str(self.content)
        
        return response

class FileResponse:
    def __init__(self, file_path, content_type):
        self.file_path = file_path
        self.content_type = content_type

def parse_template(template):
    """Parse HTML template into a node structure optimized for MicroPython."""
    nodes = []
    stack = [nodes]  # Stack for nested structures
    pos = 0
    line = 1  # Track line number for error reporting
    buffer = ''  # Buffer for text content to reduce list appends
    
    while pos < len(template):
        if template[pos] == '\n':
            line += 1
        
        # Find next tag
        next_double = template.find('{{', pos)
        next_percent = template.find('{%', pos)
        
        if next_double == -1 and next_percent == -1:
            # No more tags, append remaining text
            buffer += template[pos:]
            if buffer:
                stack[-1].append({'type': 'text', 'content': buffer})
                buffer = ''
            break
        
        # Determine the next tag to process
        if next_double == -1:
            tag_start = next_percent
            tag_type = 'percent'
        elif next_percent == -1:
            tag_start = next_double
            tag_type = 'double'
        else:
            tag_start = min(next_double, next_percent)
            tag_type = 'double' if tag_start == next_double else 'percent'
        
        # Append text before the tag
        if pos < tag_start:
            buffer += template[pos:tag_start]
            if len(buffer) > 100:  # Flush buffer to avoid excessive memory use
                stack[-1].append({'type': 'text', 'content': buffer})
                buffer = ''
        
        if tag_type == 'double':
            close_pos = template.find('}}', tag_start + 2)
            if close_pos == -1:
                raise ValueError(f"Unclosed {{ at line {line}, position {tag_start}")
            tag = template[tag_start + 2:close_pos].strip()
            
            # Flush buffer before adding a new node
            if buffer:
                stack[-1].append({'type': 'text', 'content': buffer})
                buffer = ''
            
            if tag == 'endfor':
                if len(stack) == 1:
                    raise ValueError(f"Mismatched endfor at line {line}, position {tag_start}")
                stack.pop()
            elif tag == 'endif':
                if len(stack) == 1:
                    raise ValueError(f"Mismatched endif at line {line}, position {tag_start}")
                stack.pop()
            elif tag == 'else':
                if len(stack) == 1:
                    raise ValueError(f"Mismatched else at line {line}, position {tag_start}")
                found_if = False
                for i in range(len(stack) - 1, 0, -1):
                    parent_nodes = stack[i - 1]
                    if parent_nodes and parent_nodes[-1].get('type') == 'if':
                        if parent_nodes[-1].get('else_branch') is not None:
                            raise ValueError(f"Multiple else clauses at line {line}, position {tag_start}")
                        parent_nodes[-1]['else_branch'] = []
                        stack.pop()
                        stack.append(parent_nodes[-1]['else_branch'])
                        found_if = True
                        break
                if not found_if:
                    raise ValueError(f"Mismatched else at line {line}, position {tag_start}")
            elif tag.startswith('for '):
                parts = tag[4:].split(' in ')
                if len(parts) != 2:
                    raise ValueError(f"Invalid for syntax at line {line}, position {tag_start}")
                var, iterable = parts
                for_node = {'type': 'for', 'var': var.strip(), 'iterable': iterable.strip(), 'body': []}
                stack[-1].append(for_node)
                stack.append(for_node['body'])
            elif tag.startswith('if '):
                condition = tag[3:].strip()
                if_node = {'type': 'if', 'condition': condition, 'then_branch': [], 'else_branch': None}
                stack[-1].append(if_node)
                stack.append(if_node['then_branch'])
            else:
                stack[-1].append({'type': 'var', 'name': tag})
            pos = close_pos + 2
        else:
            close_pos = template.find('%}', tag_start + 2)
            if close_pos == -1:
                raise ValueError(f"Unclosed {{% at line {line}, position {tag_start}")
            tag = template[tag_start + 2:close_pos].strip()
            
            # Flush buffer before adding a new node
            if buffer:
                stack[-1].append({'type': 'text', 'content': buffer})
                buffer = ''
            
            stack[-1].append({'type': 'var', 'name': tag})
            pos = close_pos + 2
    
    if len(stack) > 1:
        raise ValueError(f"Unclosed control structure at line {line}")
    
    # Final buffer flush
    if buffer:
        stack[-1].append({'type': 'text', 'content': buffer})
    
    return nodes

def get_var(context, var_name):
    """Resolve variable names with dot notation (e.g., project.title)."""
    parts = var_name.split('.')
    value = context
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part, '')
        elif hasattr(value, part):
            value = getattr(value, part)
        else:
            return ''
    return value

def render_nodes(nodes, context):
    output = []
    
    for node in nodes:
        if node['type'] == 'text':
            output.append(node['content'])
        elif node['type'] == 'var':
            value = get_var(context, node['name'])
            output.append(str(value))
        elif node['type'] == 'if':
            condition_value = get_var(context, node['condition'])
            if condition_value and condition_value != '' and condition_value != []:
                output.append(render_nodes(node['then_branch'], context))
            elif node['else_branch'] is not None:
                output.append(render_nodes(node['else_branch'], context))
        elif node['type'] == 'for':
            iterable = get_var(context, node['iterable'])
            if isinstance(iterable, list):
                for item in iterable:
                    loop_context = context.copy()
                    loop_context[node['var']] = item
                    output.append(render_nodes(node['body'], loop_context))
    
    return ''.join(output)

    
class MicroWeb:
    def __init__(self, ssid=None, password=None, port=80, debug=False, ap=None, mode="ap"):
        self.routes = {}
        self.static_files = {}
        self.lib_files = []  # Added to store library files
        self.config = {'port': port, 'debug': debug}
        self.session = {}
        self._template_cache = {}

        ip = None

        if ap and isinstance(ap, dict):
            ssid = ap.get('ssid', 'ESP32-MicroWeb')
            password = ap.get('password', '12345678')

        if mode == "wifi":
            ip = wifi.connect_wifi(ssid, password)
            if not ip:
                print("[Fallback] Failed to connect to WiFi. Starting Access Point instead.")
                ip = wifi.setup_ap(ssid, password)
        else:
            ip = wifi.setup_ap(ssid, password)

        self.config['ip'] = ip
        self.config['ssid'] = ssid
        self.config['password'] = password

    
    def stop_wifi(self):
        try:
            """Stop the Wi-Fi Access Point."""
            
            wifi.stop_ap()
            return {"success": True, "message": "Wi-Fi Access Point stopped."}
        except Exception as e:
            return {"success": False, "message": f"Failed to stop Wi-Fi Access Point: {str(e)}"}

    def start_wifi(self):
        try:
            """Start the Wi-Fi Access Point."""
            wifi.setup_ap(self.config.get('ssid', 'ESP32-MicroWeb'), 
                        self.config.get('password', '12345678'))
            return {"success": True, "message": "Wi-Fi Access Point started."}
        except Exception as e:
            return {"success": False, "message": f"Failed to start Wi-Fi Access Point: {str(e)}"}
    

    def route(self, path, methods=['GET']):
        def decorator(func):
            self.routes[path] = {'func': func, 'methods': methods}
            return func
        return decorator
    
    def url_encode(self, s):
        """Encode a string for safe use in URLs."""
        safe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~'
        result = ''
        for char in s:
            if char in safe:
                result += char
            else:
                hex_val = hex(ord(char))[2:].upper()
                # Ensure two-digit hex by adding leading zero if needed
                if len(hex_val) == 1:
                    hex_val = '0' + hex_val
                result += '%' + hex_val
        return result
    
    def add_static(self, path, file_path):
        self.static_files[path] = file_path
    
    def render_template(self, template_file, **kwargs):
        try:
            cache_key = template_file
            if cache_key not in self._template_cache:
                with open(template_file, 'r') as f:
                    template = f.read()
                self._template_cache[cache_key] = parse_template(template)
            
            nodes = self._template_cache[cache_key]
            content = render_nodes(nodes, kwargs)
            
            if self.config['debug']:
                print(f'Rendered template: {template_file} ({len(content)} chars)')
            
            return content
            
        except Exception as e:
            if self.config['debug']:
                print(f'Template error: {e}')
            return f'<h1>Template Error</h1><p>Error in {template_file}: {str(e)}</p>'
    
    def get_ip(self):
        return self.config.get('ip', '0.0.0.0')

    def lib_add(self, file_path):
        """Register a library file to be uploaded to the ESP32."""
        self.lib_files.append(file_path)
        if self.config['debug']:
            print(f"Registered library file: {file_path}")

    def json_response(self, data, status=200):
        return Response(ujson.dumps(data), status=200, content_type='application/json')
    
    def html_response(self, content, status=200):
        return Response(content, status=status, content_type='text/html')
    
    def redirect(self, location, status=302):
        return Response('', status=status, headers={'Location': location})

    def parse_request(self, request):
        try:
            lines = request.split('\r\n')
            if not lines or not lines[0]:
                return None
            
            request_parts = lines[0].split(' ', 2)
            if len(request_parts) < 2:
                return None
                
            method = request_parts[0]
            full_path = request_parts[1]
            
            if self.config['debug']:
                print(f'Parsed method: {method}, path: {full_path}')
            
            if '?' in full_path:
                path, query_string = full_path.split('?', 1)
            else:
                path = full_path
                query_string = ''
            
            query_params = {}
            if query_string:
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        value = value.replace('%20', ' ').replace('%21', '!').replace('%2B', '+')
                        query_params[key] = value
            
            post_data = {}
            if method == 'POST':
                body_index = request.find('\r\n\r\n')
                if body_index != -1:
                    body = request[body_index + 4:]
                    is_json = 'application/json' in request.lower()
                    is_form = 'application/x-www-form-urlencoded' in request.lower()
                    if is_json and body:
                        try:
                            post_data = ujson.loads(body)
                        except:
                            post_data = {}
                    elif is_form and body:
                        for param in body.split('&'):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                post_data[key] = value.replace('%20', ' ')
            
            if self.config['debug']:
                print(f'Parsed query_params: {query_params}')
                print(f'Parsed post_data: {post_data}')
            
            return Request(method, path, query_params, post_data)
            
        except Exception as e:
            if self.config['debug']:
                print(f'Parse request error: {e}')
            return None

    def get_content_type(self, file_path):
        ext = file_path.split('.')[-1].lower()
        content_types = {
            'html': 'text/html; charset=utf-8',
            'htm': 'text/html; charset=utf-8', 
            'css': 'text/css; charset=utf-8',
            'js': 'application/javascript; charset=utf-8',
            'json': 'application/json',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'ico': 'image/x-icon',
            'txt': 'text/plain; charset=utf-8'
        }
        return content_types.get(ext, 'text/plain')
    
    def match_route(self, path, route_pattern):
        if route_pattern == path:
            return True, None
        
        if '<' in route_pattern and '>' in route_pattern:
            regex_pattern = route_pattern
            param_pattern = ure.compile(r'<([^>]+)>')
            regex_pattern = param_pattern.sub(r'([^/]+)', regex_pattern)
            
            if not regex_pattern.startswith('^'):
                regex_pattern = '^' + regex_pattern
            if not regex_pattern.endswith('$'):
                regex_pattern = regex_pattern + '$'
            
            try:
                match = ure.match(regex_pattern, path)
                if match:
                    return True, match
            except Exception as e:
                if self.config['debug']:
                    print(f'Regex match error: {e}')
                return False, None
        
        try:
            pattern = route_pattern
            if not pattern.startswith('^'):
                pattern = '^' + pattern
            if not pattern.endswith('$'):
                pattern = pattern + '$'
            
            match = ure.match(pattern, path)
            if match:
                return True, match
        except Exception as e:
            if self.config['debug']:
                print(f'Direct regex error: {e}')
        
        return False, None
    
    def handle_request(self, request):
        req = self.parse_request(request)
        
        if not req:
            return Response('<h1>400 Bad Request</h1>', status=400).to_http_response()
        
        if self.config['debug']:
            print(f'Request: {req.method} {req.path}')
        
        # Handle static files with FileResponse
        if req.path in self.static_files:
            file_path = self.static_files[req.path]
            content_type = self.get_content_type(file_path)
            return FileResponse(file_path, content_type)
        
        for route_pattern, route_config in self.routes.items():
            is_match, match_obj = self.match_route(req.path, route_pattern)
            
            if is_match:
                if req.method not in route_config['methods']:
                    return Response('<h1>405 Method Not Allowed</h1>', 
                                  status=405).to_http_response()
                
                try:
                    if match_obj and hasattr(match_obj, 'group'):
                        result = route_config['func'](req, match_obj)
                    else:
                        result = route_config['func'](req)
                    
                    if isinstance(result, Response):
                        return result.to_http_response()
                    elif isinstance(result, str):
                        return Response(result).to_http_response()
                    elif isinstance(result, dict):
                        return self.json_response(result).to_http_response()
                    else:
                        return Response(str(result)).to_http_response()
                        
                except Exception as e:
                    if self.config['debug']:
                        print(f'Route handler error: {e}')
                    return Response(f'<h1>500 Internal Server Error</h1><p>{str(e)}</p>', 
                                  status=500).to_http_response()
        
        return Response('<h1>404 Not Found</h1><p>Page not found</p>', 
                      status=404).to_http_response()
    

    
    def run(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.config['port']))
        s.listen(5)
        
        if self.config['debug']:
            print(f"MicroWeb running on http://0.0.0.0:{self.config['port']}")
        
        while True:
            conn = None
            try:
                conn, addr = s.accept()
                conn.settimeout(5.0)
                
                if self.config['debug']:
                    print(f'Connection from {addr}')
                
                request_data = b''
                while True:
                    try:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        request_data += chunk
                        if b'\r\n\r\n' in request_data:
                            break
                    except:
                        break
                
                if request_data:
                    request = request_data.decode('utf-8')
                    response = self.handle_request(request)
                    
                    if isinstance(response, FileResponse):
                        # Handle static file response
                        try:
                            file_size = os.stat(response.file_path)[6]  # Get file size
                        except Exception as e:
                            if self.config['debug']:
                                print(f'File access error: {e}')
                            error_response = Response('<h1>404 Not Found</h1><p>File not found</p>', 
                                                    status=404).to_http_response()
                            conn.send(error_response.encode('utf-8'))
                            continue
                        
                        headers = {
                            'Content-Type': response.content_type,
                            'Content-Length': str(file_size),
                            'Access-Control-Allow-Origin': '*',
                            'Cache-Control': 'public, max-age=20'
                        }
                        header_response = 'HTTP/1.1 200 OK\r\n'
                        for key, value in headers.items():
                            header_response += f'{key}: {value}\r\n'
                        header_response += '\r\n'
                        conn.send(header_response.encode('utf-8'))
                        
                        # Send file in chunks
                        with open(response.file_path, 'rb') as f:
                            while True:
                                chunk = f.read(1024)
                                if not chunk:
                                    break
                                conn.send(chunk)
                        
                        if self.config['debug']:
                            print(f'Served static: {response.file_path} ({file_size} bytes)')
                    
                    else:
                        # Handle regular string response
                        if isinstance(response, str):
                            response = response.encode('utf-8')
                        sent = 0
                        while sent < len(response):
                            chunk = response[sent:sent + 1024]
                            conn.send(chunk)
                            sent += len(chunk)
                
            except Exception as e:
                if self.config['debug']:
                    print(f'Request handling error: {e}')
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                gc.collect()  # Clear memory