import usocket as socket
import ujson
import ure
import gc
import wifi

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
        # Add CORS header by default
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

class MicroWeb:
    def __init__(self, ssid=None, password=None, port=80, debug=False, ap=None):
        self.routes = {}
        self.static_files = {}
        self.config = {'port': port, 'debug': debug}
        self.session = {}
        
        if ap and isinstance(ap, dict) and 'ssid' in ap:
            ap_ssid = ap.get('ssid', 'ESP32-MicroWeb')
            ap_password = ap.get('password', '12345678')
        elif ssid and password:
            ap_ssid = ssid
            ap_password = password
        else:
            ap_ssid = 'ESP32-MicroWeb'
            ap_password = '12345678'
            
        wifi.setup_ap(ap_ssid, ap_password)
    
    def route(self, path, methods=['GET']):
        def decorator(func):
            self.routes[path] = {'func': func, 'methods': methods}
            return func
        return decorator
    
    def add_static(self, path, file_path):
        self.static_files[path] = file_path
    
    def render_template(self, template_file, **kwargs):
        try:
            with open(template_file, 'r') as f:
                content = f.read()
            
            if self.config['debug']:
                print(f'Template content before replacement: {content[:100]}...')
                print(f'Template variables: {kwargs}')
            
            for key, value in kwargs.items():
                patterns = [
                    '{%' + key + '%}',
                    '{% ' + key + ' %}',
                    '{%  ' + key + '  %}',
                ]
                for pattern in patterns:
                    content = content.replace(pattern, str(value))
            
            if self.config['debug']:
                print(f'Template content after replacement: {content[:100]}...')
            
            return content
        except Exception as e:
            if self.config['debug']:
                print(f'Template error: {e}')
            return f'<h1>Template Error</h1><p>Template not found: {template_file}</p><p>Error: {str(e)}</p>'
       
    def json_response(self, data, status=200):
        return Response(ujson.dumps(data), status=status, content_type='application/json')
    
    def html_response(self, content, status=200):
        return Response(content, status=status, content_type='text/html')
    
    def redirect(self, location, status=302):
        return Response('', status=status, headers={'Location': location})


    def parse_request(self, request):
        try:
            lines = request.split('\r\n')
            if not lines or not lines[0]:
                if self.config['debug']:
                    print('Invalid request: empty or no request line')
                return None
            
            request_parts = lines[0].split(' ')
            if len(request_parts) < 2:
                if self.config['debug']:
                    print('Invalid request: malformed request line')
                return None
                
            method = request_parts[0]
            full_path = request_parts[1]
            
            if self.config['debug']:
                print(f'Raw request: {request[:100]}...')
                print(f'Parsed method: {method}, path: {full_path}')
            
            path = full_path.split('?')[0]
            query_params = {}
            
            if '?' in full_path:
                query_string = full_path.split('?')[1]
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        value = value.replace('%20', ' ').replace('%21', '!')
                        query_params[key] = value
            
            post_data = {}
            if method == 'POST':
                body_start = -1
                for i, line in enumerate(lines):
                    if line == '':
                        body_start = i + 1
                        break
                
                if body_start > 0 and body_start < len(lines):
                    body = '\r\n'.join(lines[body_start:])
                    if self.config['debug']:
                        print(f'Request body: {body}')
                    
                    # Check for Content-Type header case-insensitively
                    content_type_header = None
                    for line in lines:
                        if line.lower().startswith('content-type:'):
                            content_type_header = line.split(':', 1)[1].strip()
                            break
                    
                    if content_type_header and 'application/x-www-form-urlencoded' in content_type_header.lower():
                        for param in body.split('&'):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                post_data[key] = value.replace('%20', ' ')
                    elif content_type_header and 'application/json' in content_type_header.lower():
                        try:
                            post_data = ujson.loads(body)
                        except Exception as e:
                            if self.config['debug']:
                                print(f'JSON parse error: {e}')
                            post_data = {}
            
            if self.config['debug']:
                print(f'Parsed query_params: {query_params}')
                print(f'Parsed post_data: {post_data}')
            
            return Request(method, path, query_params, post_data)
        except Exception as e:
            if self.config['debug']:
                print(f'Parse request error: {e}')
            return None


    def get_content_type(self, file_path):
        if file_path.endswith('.html') or file_path.endswith('.htm'):
            return 'text/html'
        elif file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.json'):
            return 'application/json'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        elif file_path.endswith('.gif'):
            return 'image/gif'
        elif file_path.endswith('.ico'):
            return 'image/x-icon'
        elif file_path.endswith('.txt'):
            return 'text/plain'
        else:
            return 'text/plain'
    
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
        
        if req.path in self.static_files:
            try:
                file_path = self.static_files[req.path]
                with open(file_path, 'r') as f:
                    content = f.read()
                content_type = self.get_content_type(file_path)
                if self.config['debug']:
                    print(f'Serving static file: {file_path} as {content_type}')
                return Response(content, content_type=content_type).to_http_response()
            except Exception as e:
                if self.config['debug']:
                    print(f'Static file error: {e}')
                return Response('<h1>404 Not Found</h1><p>File not found</p>', 
                              status=404).to_http_response()
        
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
                if self.config['debug']:
                    print(f'Connection from {addr}')
                
                request = conn.recv(1024).decode('utf-8')
                if request:
                    response = self.handle_request(request)
                    conn.send(response.encode('utf-8'))
                
            except Exception as e:
                if self.config['debug']:
                    print(f'Request handling error: {e}')
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                gc.collect()

