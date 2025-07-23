import click
import serial.tools.list_ports
import esptool
import subprocess
import time
import os
import re
import pkg_resources
from microweb.uploader import upload_file, create_directory, verify_files
from microweb.dotenv import load_dotenv, get_env

# ANSI color codes for enhanced terminal output
COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m'
}

STYLES = {
    'underline': '\033[4m',
    'blink': '\033[5m',
}

def print_colored(message, color=None, style=None):
    """Print a message with optional color and style."""
    prefix = ''
    if color in COLORS:
        prefix += COLORS[color]
    if style in STYLES:
        prefix += STYLES[style]
    click.echo(f"{prefix}{message}{COLORS['reset']}")

def check_micropython(port):
    """Check if MicroPython is responding via mpremote on the given port."""
    try:
        cmd = ['mpremote', 'connect', port, 'eval', 'print("MicroPython detected")']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "MicroPython detected" in result.stdout:
            print_colored(f"MicroPython detected on {port}", color='green')
            return True
        else:
            print_colored(f"mpremote output:\n{result.stdout.strip()}\n{result.stderr.strip()}", color='yellow')
            return False
    except Exception as e:
        print_colored(f"Error checking MicroPython via mpremote: {e}. The app may be running boot.py.", color='blue')
        return False

def get_remote_file_info(port):
    """Get remote file information from ESP32 including sizes."""
    try:
        cmd = ['mpremote', 'connect', port, 'ls']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print_colored(f"Error getting remote file list: {result.stderr}", color='red')
            return {}
        file_info = {}
        lines = result.stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('ls :') or line == '':
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    size = int(parts[0])
                    filename = ' '.join(parts[1:])
                    file_info[filename] = size
                except ValueError:
                    continue
        return file_info
    except Exception as e:
        print_colored(f"Error getting remote file info: {e}", color='red')
        return {}

def should_upload_file(local_path, remote_filename, remote_files):
    """Determine if a file should be uploaded based on size comparison."""
    if not os.path.exists(local_path):
        return False, f"Local file {local_path} not found"
    local_size = os.path.getsize(local_path)
    if remote_filename not in remote_files:
        return True, f"New file (local: {local_size} bytes)"
    remote_size = remote_files[remote_filename]
    if local_size != remote_size:
        return True, f"Size changed (local: {local_size} bytes, remote: {remote_size} bytes)"
    return False, f"No change (both: {local_size} bytes)"

def analyze_app_static_files(app_file):
    """Analyze the app.py file to find static file and template references."""
    static_files = set()
    template_files = set()
    try:
        app_dir = os.path.dirname(app_file) or '.'
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        filtered_lines = []
        in_multiline_string = False
        string_delimiter = None
        for line in lines:
            if line.strip().startswith('#'):
                continue
            if '"""' in line or "'''" in line:
                if not in_multiline_string:
                    in_multiline_string = True
                    string_delimiter = '"""' if '"""' in line else "'''"
                elif string_delimiter in line:
                    in_multiline_string = False
                    string_delimiter = None
                continue
            if not in_multiline_string:
                if '#' in line:
                    line = line.split('#')[0]
                filtered_lines.append(line)
        filtered_content = '\n'.join(filtered_lines)
        static_pattern = r'app\.add_static\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)'
        static_matches = re.findall(static_pattern, filtered_content)
        for url_path, file_path in static_matches:
            if url_path in ['/url', '/path', '/example'] or file_path in ['path', 'file', 'example']:
                print_colored(f"⚠️  Skipping placeholder: app.add_static('{url_path}', '{file_path}')", color='yellow')
                continue
            if len(file_path) > 2 and not file_path.startswith('/'):
                static_files.add((url_path, file_path))
        template_pattern = r'app\.render_template\s*\(\s*[\'"]([^\'"]+)[\'"][^\)]*\)'
        template_matches = re.findall(template_pattern, filtered_content)
        for template in template_matches:
            if template not in ['template', 'example', 'placeholder']:
                template_path = os.path.join(app_dir, template)
                template_files.add(template_path)
        html_static_pattern = r'(?:href|src)\s*=\s*[\'"]([^\'"]+\.(css|js|png|jpg|jpeg|gif|ico|svg|webp))[\'"]'
        html_matches = re.findall(html_static_pattern, filtered_content, re.IGNORECASE)
        for url_path, ext in html_matches:
            if url_path.startswith('/') and not url_path.startswith('//') and 'http' not in url_path:
                guessed_path = url_path.lstrip('/')
                if '.' in guessed_path and len(guessed_path) > 3:
                    static_files.add((url_path, guessed_path))
        if template_files:
            print_colored(f"Resolved template file paths:", color='cyan')
            for template in template_files:
                print_colored(f"  {template} {'(exists)' if os.path.exists(template) else '(missing)'}", color='cyan')
        return static_files, template_files
    except Exception as e:
        print_colored(f"Error analyzing {app_file}: {e}", color='red')
        return set(), set()

def analyze_template_static_files(template_files):
    """Analyze template files to find additional static file references."""
    static_files = set()
    for template_file in template_files:
        if not os.path.exists(template_file):
            print_colored(f"Warning: Template file {template_file} not found", color='yellow')
            continue
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            html_static_pattern = r'(?:href|src)\s*=\s*[\'"]([^\'"]+\.(css|js|png|jpg|jpeg|gif|ico|svg|webp))[\'"]'
            html_matches = re.findall(html_static_pattern, content, re.IGNORECASE)
            for url_path, ext in html_matches:
                if url_path.startswith('/') and not url_path.startswith('//') and 'http' not in url_path:
                    guessed_path = url_path.lstrip('/')
                    if '.' in guessed_path and len(guessed_path) > 3:
                        static_files.add((url_path, guessed_path))
        except Exception as e:
            print_colored(f"Error analyzing template {template_file}: {e}", color='red')
    return static_files

def verify_static_files_exist(static_files, static_dir):
    """Verify that all required static files exist locally."""
    missing_files = []
    existing_files = []
    for url_path, file_rel_path in static_files:
        if os.path.isabs(file_rel_path):
            full_path = file_rel_path
        else:
            full_path = os.path.join(static_dir, file_rel_path)
        if os.path.exists(full_path):
            existing_files.append((url_path, full_path))
        else:
            missing_files.append((url_path, full_path))
    return existing_files, missing_files

def upload_boot_py(port, module_name):
    """Create and upload boot.py that imports the specified app module."""
    boot_content = f"import {module_name}\n"

    with open("boot.py", "w", encoding="utf-8") as f:
        f.write(boot_content)

    try:
        print_colored(f"⬆️  Uploading boot.py to import '{module_name}'...", color='cyan')
        upload_file("boot.py", port, destination='boot.py')
        print_colored("✅ boot.py uploaded successfully.", color='green')
    finally:
        os.remove("boot.py")


def remove_boot_py(port):
    """Replace boot.py on ESP32 with minimal content using ampy."""
    boot_content = "import gc\ngc.collect()\n"
    boot_filename = "boot.py"

    # Write minimal boot.py locally
    with open(boot_filename, "w", encoding="utf-8") as f:
        f.write(boot_content)

    try:
        print_colored(f"🗑️ Replacing boot.py on ESP32 (port {port}) using ampy...", color='cyan')
        cmd = ["ampy", "--port", port, "put", boot_filename]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode != 0:
            print_colored(f"⚠️ Failed to replace boot.py: {result.stderr.strip()}", color='yellow')
        else:
            print_colored("✅ boot.py replaced successfully.", color='green')

    except Exception as e:
        print_colored(f"❌ Error replacing boot.py: {e}", color='red')

    finally:
        if os.path.exists(boot_filename):
            os.remove(boot_filename)

            
@click.group()
def cli():
    pass
    
@cli.command()
@click.option('--port', default=None, help='Serial port, e.g., COM10')
@click.option('--baud', default=460800, help='Baud rate for flashing (default: 460800)')
@click.option('--erase', is_flag=True, help='Erase all flash before writing firmware')
@click.option('--esp8266', is_flag=True, help='Flash ESP8266 firmware instead of ESP32')
@click.option('--firmware', type=click.Path(exists=True), help='Custom firmware .bin file to flash')
@click.option('--full-flash', is_flag=True, help='Use full flash mode (offset 0) instead of 0x1000')
def flash(port, baud, erase, esp8266, firmware, full_flash):
    """Flash MicroPython and MicroWeb to the ESP32, ESP8266, or other ESP boards."""
    port = port
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        print_colored("No ESP device found. Specify --port or set PORT in .env file.", color='red')
        return

    chip_name = "ESP8266" if esp8266 else "ESP32"
    if firmware:
        firmware_path = os.path.abspath(firmware)
        print_colored(f"Using custom firmware: {firmware_path}", color='cyan')
    else:
        firmware_file = f"{chip_name}_GENERIC-20250415-v1.25.0.bin"
        firmware_path = pkg_resources.resource_filename('microweb', f'firmware/{firmware_file}')

    if erase:
        print_colored(f"You requested --erase. This will erase ALL data on the {chip_name}!", color='yellow')
        confirm = input("Type 'erase' to continue, or anything else to cancel: ")
        if "erase" not in confirm.lower():
            print_colored("Erase cancelled.", color='yellow')
            return
        print_colored(f"Erasing all flash on {port} ({chip_name})...", color='yellow')
        esptool.main(['--port', port, '--baud', str(baud), 'erase_flash'])

    try:
        print_colored(f"Checking for MicroPython on {port}...", color='blue')
        if check_micropython(port):
            print_colored(f"MicroPython detected on {port}. Skipping firmware flash.", color='green')
        else:
            if not os.path.exists(firmware_path):
                print_colored(f"Error: Firmware file not found at {firmware_path}.", color='red')
                return
            flash_offset = '0x0' if full_flash else '0x1000'
            print_colored(f"Flashing {chip_name} firmware at offset {flash_offset} on {port}...", color='blue')
            esptool.main(['--port', port, '--baud', str(baud), 'write_flash', '-z', flash_offset, firmware_path])

        print_colored("Uploading core files...", color='blue')
        core_files = [
            ('firmware/boot.py', 'boot.py'),
            ('microweb.py', 'microweb.py'),
            ('wifi.py', 'wifi.py'),
            ('dotenv.py', 'dotenv.py'),
        ]
        for src, dest in core_files:
            src_path = pkg_resources.resource_filename('microweb', src) if src.startswith('firmware/') else os.path.join(os.path.dirname(__file__), src)
            print_colored(f"Uploading {dest} from {src_path}...", color='cyan')
            if not os.path.exists(src_path):
                print_colored(f"Error: Source file {src_path} not found.", color='red')
                return
            upload_file(src_path, port, destination=dest)

        print_colored("Verifying uploaded files...", color='blue')
        verify_files(port, [dest for _, dest in core_files])
        print_colored(f"MicroWeb flashed successfully to {chip_name}", color='green')

    except Exception as e:
        print_colored(f"Error during flash: {e}", color='red')



@cli.command()
@click.argument('file')
@click.option('--port', default=None, help='Serial port, e.g., COM10')
@click.option('--check-only', is_flag=True, help='Only check static files, don\'t upload')
@click.option('--static', default=None, help='Local static files folder path')
@click.option('--force', is_flag=True, help='Force upload all files regardless of changes')
@click.option('--no-stop', is_flag=True, help='Do not reset ESP32 before running app')
@click.option('--timeout', default=3600, show_default=True, help='Timeout seconds for running app')
@click.option('--add-boot', is_flag=True, help='Add boot.py that imports the app to run it on boot')
@click.option('--remove-boot', is_flag=True, help='Remove boot.py from the ESP32')
def run(file, port, check_only, static, force, no_stop, timeout, add_boot, remove_boot):
    """Upload and execute a file on the ESP32 (only uploads changed files)."""
    env_vars = load_dotenv()
    port = port or get_env('PORT', default=None, env_vars=env_vars)
    static = static or get_env('STATIC_DIR', default='static', env_vars=env_vars)
    if not file.endswith('.py'):
        print_colored("Error: File must have a .py extension.", color='red')
        return
    if not os.path.exists(file):
        print_colored(f"Error: File {file} does not exist.", color='red')
        return
    module_name = os.path.splitext(os.path.basename(file))[0]
    if add_boot and remove_boot:
        print_colored("Error: --add-boot and --remove-boot options cannot be used together.", color='red')
        return
    print_colored(f"Analyzing {file} for static file, template, and library/model dependencies...", color='blue')
    static_files, template_files = analyze_app_static_files(file)
    # --- Find templates in ./ and ./static ---
    found_templates = set()
    for folder in [os.path.dirname(file), static]:
        if os.path.isdir(folder):
            for entry in os.listdir(folder):
                if entry.endswith('.html') or entry.endswith('.htm'):
                    found_templates.add(os.path.join(folder, entry))
    for tfile in found_templates:
        if tfile not in template_files:
            template_files.add(tfile)
    if template_files:
        print_colored(f"Found template files: {', '.join(os.path.basename(t) for t in template_files)}", color='cyan')
        template_static_files = analyze_template_static_files(template_files)
        static_files.update(template_static_files)
    # --- Find static files in ./ and ./static ---
    found_static = set()
    for folder in [os.path.dirname(file), static]:
        if os.path.isdir(folder):
            for entry in os.listdir(folder):
                if entry.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp')):
                    found_static.add(('/' + entry, entry))
    for url_path, file_rel_path in found_static:
        if (url_path, file_rel_path) not in static_files:
            static_files.add((url_path, file_rel_path))
    existing_files = []
    missing_files = []
    if static_files:
        print_colored(f"Found {len(static_files)} static file references:", color='blue')
        for url_path, file_rel_path in static_files:
            print_colored(f"  {url_path} -> {file_rel_path}", color='cyan')
        existing_files, missing_files = verify_static_files_exist(static_files, static)
        if missing_files:
            print_colored(f"\nError: Missing {len(missing_files)} static files:", color='red')
            for url_path, file_full_path in missing_files:
                print_colored(f"  {url_path} -> {file_full_path} (NOT FOUND)", color='red')
            print_colored("\nPlease create these files or update your app.py file or --static folder.", color='yellow')
            return
        print_colored(f"\nAll {len(existing_files)} static files found locally:", color='green')
        for url_path, file_full_path in existing_files:
            file_size = os.path.getsize(file_full_path)
            print_colored(f"  ✓ {url_path} -> {file_full_path} ({file_size} bytes)", color='green')
    else:
        print_colored("No static files found in app.", color='yellow')
    # --- Analyze library and model files ---
    lib_files = set()
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        lib_pattern = r'app\.lib_add\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        lib_matches = re.findall(lib_pattern, content)
        for lib_file in lib_matches:
            if lib_file not in ['lib', 'example', 'placeholder']:
                lib_path = os.path.join(os.path.dirname(file), lib_file)
                lib_files.add(lib_path)
        if lib_files:
            print_colored(f"Found {len(lib_files)} library/model file references:", color='blue')
            for lib_file in lib_files:
                print_colored(f"  {lib_file} {'(exists)' if os.path.exists(lib_file) else '(missing)'}", color='cyan')
            missing_libs = [lib for lib in lib_files if not os.path.exists(lib)]
            if missing_libs:
                print_colored(f"\nError: Missing {len(missing_libs)} library/model files:", color='red')
                for lib in missing_libs:
                    print_colored(f"  {lib} (NOT FOUND)", color='red')
                print_colored("\nPlease create these library/model files or update your app.py file.", color='yellow')
                return
        # Check for load_dotenv import to determine if .env file should be uploaded
        dotenv_pattern = r'^\s*(?:import\s+dotenv|from\s+dotenv\s+import\s+.*)\s*$'
        uses_dotenv = False
        for line in content.split('\n'):
            if re.match(dotenv_pattern, line, re.MULTILINE):
                uses_dotenv = True
                print_colored("Detected dotenv import in app.py, checking for .env file...", color='cyan')
                break
    except Exception as e:
        print_colored(f"Error analyzing library/model files in {file}: {e}", color='red')
        return
    if check_only:
        print_colored("\nStatic file, template, and library/model check complete.", color='green')
        return
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        print_colored("No ESP32 found. Specify --port or set PORT in .env file.", color='red')
        return
    if remove_boot:
        remove_boot_py(port)
        return
    if not check_micropython(port):
        print_colored(f"MicroPython not detected on ESP32. Please run 'microweb flash --port {port}' first.", color='red')
        return
    try:
        print_colored(f"\nGetting remote file information from {port}...", color='blue')
        remote_files = get_remote_file_info(port)
        print_colored(f"Found {len(remote_files)} files on ESP32:", color='blue')
        for filename, size in remote_files.items():
            print_colored(f"  {filename}: {size} bytes", color='cyan')
        files_to_upload = []
        files_skipped = []
        main_filename = os.path.basename(file)
        should_upload, reason = should_upload_file(file, main_filename, remote_files)
        if force or should_upload:
            files_to_upload.append(('main', file, main_filename, reason))
        else:
            files_skipped.append((main_filename, reason))
        template_uploads = []
        for template_file in template_files:
            if os.path.exists(template_file):
                remote_name = os.path.basename(template_file)
                should_upload, reason = should_upload_file(template_file, remote_name, remote_files)
                if force or should_upload:
                    template_uploads.append((template_file, remote_name, reason))
                else:
                    files_skipped.append((remote_name, reason))
            else:
                print_colored(f"Warning: Template file {template_file} not found locally, skipping upload.", color='yellow')
        static_uploads = []
        if existing_files:
            for url_path, file_full_path in existing_files:
                filename = os.path.basename(file_full_path)
                should_upload, reason = should_upload_file(file_full_path, f"static/{filename}", remote_files)
                if force or should_upload:
                    static_uploads.append((file_full_path, filename, reason))
                else:
                    files_skipped.append((f"static/{filename}", reason))
        lib_uploads = []
        if lib_files:
            for lib_file in lib_files:
                if os.path.exists(lib_file):
                    filename = os.path.basename(lib_file)
                    relative_path = os.path.relpath(lib_file, os.path.dirname(file)).replace('\\', '/')
                    remote_name = relative_path if relative_path.startswith(('lib/', 'models/')) else f"lib/{filename}"
                    should_upload, reason = should_upload_file(lib_file, remote_name, remote_files)
                    if force or should_upload:
                        lib_uploads.append((lib_file, filename, relative_path, reason))
                    else:
                        files_skipped.append((remote_name, reason))
        env_upload = []
        if uses_dotenv:
            env_file = os.path.join(os.path.dirname(file), '.env')
            if os.path.exists(env_file):
                should_upload, reason = should_upload_file(env_file, '.env', remote_files)
                if force or should_upload:
                    env_upload.append((env_file, '.env', reason))
                else:
                    files_skipped.append(('.env', reason))
            else:
                print_colored("Warning: .env file not found in project directory, skipping upload.", color='yellow')

        total_uploads = len(files_to_upload) + len(template_uploads) + len(static_uploads) + len(lib_uploads)
        if files_skipped:
            print_colored(f"\n📋 Files skipped ({len(files_skipped)}):", color='yellow')
            for filename, reason in files_skipped:
                print_colored(f"  ⏭️  {filename}: {reason}", color='yellow')
        if total_uploads == 0:
            print_colored(f"\n✅ All files are up to date! No uploads needed.", color='green')
            if not force:
                print_colored("Use --force to upload all files anyway.", color='yellow')
        else:
            print_colored(f"\n📤 Files to upload ({total_uploads}):", color='blue')
            for file_type, local_path, remote_name, reason in files_to_upload:
                print_colored(f"  📁 {remote_name}: {reason}", color='cyan')
            for template_file, remote_name, reason in template_uploads:
                print_colored(f"  📄 {remote_name}: {reason}", color='cyan')
            for local_path, filename, reason in static_uploads:
                print_colored(f"  🎨 static/{filename}: {reason}", color='cyan')
            for lib_file, filename, relative_path, reason in lib_uploads:
                print_colored(f"  📚 {relative_path}: {reason}", color='cyan')
        upload_count = 0
        for file_type, local_path, remote_name, reason in files_to_upload:
            print_colored(f"\n⬆️  Uploading {remote_name}...", color='cyan')
            upload_file(local_path, port, destination=remote_name)
            upload_count += 1
        for template_file, remote_name, reason in template_uploads:
            print_colored(f"⬆️  Uploading template: {remote_name}...", color='cyan')
            upload_file(template_file, port, destination=remote_name)
            upload_count += 1
        if static_uploads:
            print_colored("📁 Creating static directory on ESP32...", color='blue')
            create_directory('static', port)
            for file_full_path, filename, reason in static_uploads:
                print_colored(f"⬆️  Uploading static file: static/{filename}...", color='cyan')
                upload_file(file_full_path, port, destination=f"static/{filename}")
                upload_count += 1
        if lib_uploads:
            lib_dirs = set(os.path.dirname(relative_path) for _, _, relative_path, _ in lib_uploads)
            for dir_name in lib_dirs:
                print_colored(f"📁 Creating {dir_name} directory on ESP32...", color='blue')
                create_directory(dir_name, port)
            for lib_file, filename, relative_path, reason in lib_uploads:
                print_colored(f"⬆️  Uploading library/model file: {relative_path}...", color='cyan')
                upload_file(lib_file, port, destination=relative_path)
                upload_count += 1
        for env_file_path, remote_name, reason in env_upload:
            print_colored(f"⬆️  Uploading environment file: {remote_name}...", color='cyan')
            upload_file(env_file_path, port, destination=remote_name)
            upload_count += 1
        if add_boot:
            upload_boot_py(port, module_name)
        if not no_stop:
            print_colored(f"\n🔄 Resetting ESP32 to ensure clean state...", color='blue')
            subprocess.run(['mpremote', 'connect', port, 'reset'], capture_output=True, text=True, timeout=10)
            time.sleep(2)
        if not add_boot:
            print_colored(f"🚀 Starting {module_name}.run() with timeout {timeout} seconds...", color='blue')
            cmd = ['mpremote', 'connect', port, 'exec', f'import {module_name}; {module_name}.app.run()']
            try:
                print_colored(f"\n✅ {file} is running on ESP32", color='green')
                ssid = get_env('SSID', default=None, env_vars=env_vars)
                password = get_env('PASSWORD', default=None, env_vars=env_vars)
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ap_match = re.search(
                        r'MicroWeb\s*\(\s*.*ap\s*=\s*{[^}]*["\']ssid["\']\s*:\s*["\']([^"\']+)["\']\s*,\s*["\']password["\']\s*:\s*["\']([^"\']+)["\']',
                        content
                    )
                    if ap_match:
                        ssid = ssid or ap_match.group(1)
                        password = password or ap_match.group(2)
                    else:
                        ap_match = re.search(
                            r'MicroWeb\s*\([^)]*ap\s*=\s*{\s*["\']ssid["\']\s*:\s*["\']([^"\']+)["\']\s*,\s*["\']password["\']\s*:\s*["\']([^"\']+)["\']',
                            content, re.DOTALL
                        )
                        if ap_match:
                            ssid = ssid or ap_match.group(1)
                            password = password or ap_match.group(2)
                except Exception:
                    pass
                if ssid and password:
                    print_colored(f"📶 Connect to SSID: {ssid}, Password: {password}", color='cyan')
                else:
                    print_colored(" ⚠️ No Wi-Fi access point configured in app.py or .env. Using default IP.", color='yellow')
                try:
                    ip_line = f"import {module_name}; print({module_name}.app.get_ip())"
                    result = subprocess.run(['mpremote', 'connect', port, 'exec', ip_line],
                                            capture_output=True, text=True, timeout=5)
                    ip = result.stdout.strip().splitlines()[-1] if result.returncode == 0 else "192.168.4.1"
                except:
                    ip = "192.168.4.1"
                print_colored(f"🌐 Visit: http://{ip} or http://192.168.8.102/, if you want app print logs use `mpremote connect {port} run {file}`", color='cyan')
                print_colored(" If you want remove this app, run 'microweb remove --port {port} --remove'", color='cyan')
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                if result.returncode != 0:
                    print_colored(f"❌ Error running {file}: return code {result.returncode}", color='red')
                    print_colored(f"stdout:\n{result.stdout.strip()}\nstderr:\n{result.stderr.strip()}", color='red')
                    print_colored(f"Try: microweb flash --port {port}", color='cyan')
                    print_colored(" If you want remove this app, run 'microweb remove --port {port} --remove'", color='cyan')
                    return
                if upload_count > 0:
                    print_colored(f"📊 Uploaded {upload_count} file(s), skipped {len(files_skipped)} file(s)", color='green')
                else:
                    print_colored(f"📊 No files uploaded, {len(files_skipped)} file(s) were already up to date", color='green')
            except subprocess.TimeoutExpired:
                print_colored(f"❌ Error: Running {file} timed out after {timeout} seconds.", color='red')
            except Exception as e:
                print_colored(f"❌ Unexpected error running {file}: {e}", color='red')
        else:
            print_colored(f"⚠️ boot.py uploaded, app will run automatically on boot. Not running app.run() now.", color='yellow')

    except Exception as e:
        print_colored(f"❌ Error: {e}", color='red')


@cli.command()
@click.option('--port', default=None, help='Serial port, e.g., COM10')
@click.option('--remove', 'remove_everything', is_flag=True, help='Actually remove all files in the ESP32 home directory')
def remove(port, remove_everything):
    """Remove all files in the ESP32 home directory (requires --remove flag to actually delete files)."""
    boot_files = ["boot.py","microweb.py","wifi.py","dotenv.py"]
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        print_colored("No ESP32 found. Specify --port, e.g., --port COM10.", color='red')
        return
    if not check_micropython(port):
        print_colored(f"MicroPython not detected on ESP32. Please run 'microweb flash --port {port}' first.", color='red')
        return
    try:
        if remove_everything:
            print_colored("Removing all files in ESP32 home directory...", color='yellow')
            remote_files = get_remote_file_info(port)
            
            if not remote_files:
                print_colored("No files found or error accessing filesystem.", color='yellow')
                return
            for filename in remote_files.keys():
                if filename in ('.', '..'):
                    continue
                if not filename in boot_files:
                        print_colored(f"Removing {filename}...", color='cyan')
                        cmd_rm = ['mpremote', 'connect', port, 'rm', filename]
                        result = subprocess.run(cmd_rm, capture_output=True, text=True, timeout=10)
                        if result.returncode != 0:
                            print_colored(f"Error removing {filename}: {result.stderr}", color='red')
            print_colored("All files in ESP32 home directory removed.", color='green')
        else:
            print_colored("Dry run: No files were removed. Use --remove to actually delete all files in the ESP32 home directory.", color='yellow')
    except Exception as e:
        print_colored(f"Error removing files: {e}", color='red')


@cli.command()
@click.option('--path', default='example_app', show_default=True, help='Directory to create the example app')
def create(path):
    """Create an example MicroWeb app with app.py, static/index.html, static/style.css, static/script.js, and README.md."""
    try:
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, 'static'), exist_ok=True)
        os.makedirs(os.path.join(path, 'models'), exist_ok=True)

        app_content = """import wifi
from microweb import MicroWeb

#import some_lib 
#import users
#import products

# Initialize MicroWeb application with debug mode and Wi-Fi access point configuration
app = MicroWeb(debug=True, ap={"ssid": "MyESP32", "password": "mypassword"})

# app = MicroWeb(
#     ap={"ssid": "Dialog 4G 0F8", "password": "youpassword"},  # Change to your router
#     debug=True,
#     mode="wifi"  # Connect as client to your router
# )

# Register library and model files
# app...lib_add("some_lib.py")
# app...lib_add("models/users.py")
# app...lib_add("models/products.py")


#############################################################

# this is example app.py file for MicroWeb
# It demonstrates dynamic routing, template rendering with for loops,
# if you want fresh start remove this all

#############################################################

@app.route('/')
def home(req):
    # Test case 1: Populated projects list
    projects = [
        {'title': 'Smart Home Dashboard', 'description': 'A dashboard for home automation'},
        {'title': 'Weather Station', 'description': 'Real-time weather monitoring'},
        {'title': 'IoT Sensor Network', 'description': 'Network for IoT sensors'}
    ]
    return app.render_template('index.html', greeting='Welcome to MicroWeb!', projects=projects)

@app.route('/empty')
def empty(req):
    # Test case 2: Empty projects list
    projects = []
    return app.render_template('index.html', greeting='No Projects Available', projects=projects)

# Define API route to return server status and IP address as JSON
@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({"status": "running", "ip": wifi.get_ip()})

# Define API route to greet a user by ID
@app.route('/greet/<name>')
def greet(req, match):
    name = match.group(1) if match else "Anonymous"
    return {"message": f"Hello, {name}!", "status": "success"}

# Define API route to echo back POST data as JSON
# @app.route('/api/echo', methods=['POST'])
# def echo(req):
#     data = req.form  # Get form data from POST body
#     return app.json_response({"received": data})

# Define a route that handles both GET and POST requests, returning method-specific JSON responses
# @app.route('/api/methods', methods=['GET', 'POST'])
# def methods(req):
#     if req.method == 'GET':
#         return app.json_response({"method": "GET", "message": "This is a GET request"})
#     elif req.method == 'POST':
#         data = req.form  # Get JSON data from POST body
#         return app.json_response({"method": "POST", "received": data})

# Define route for form submission, rendering form.html for GET and result.html for POST
# @app.route('/submit', methods=['GET', 'POST'])
# def submit_form(req):
#     if req.method == 'POST':
#         return app.render_template('result.html', 
#                                  data=str(req.form),  # Convert form data to string
#                                  method="POST")
#     else:
#         return app.render_template('form.html')


# @app.route('/add_user', methods=['POST'])
# def add_user(req):
#     name = req.form.get('name', '')
#     email = req.form.get('email', '')
#     if name and email:
#         new_user = users.add_user(name, email)
#         return app.json_response({"message": "User added", "user": new_user})
#     return app.json_response({"error": "Invalid input"}, status=400)

# @app.route('/add_product', methods=['POST'])
# def add_product(req):
#     name = req.form.get('name', '')
#     price = float(req.form.get('price', 0)) if req.form.get('price', '').replace('.', '', 1).isdigit() else 0
#     if name and price > 0:
#         new_product = products.add_product(name, price)
#         return app.json_response({"message": "Product added", "product": new_product})
#     return app.json_response({"error": "Invalid input"}, status=400)



# Register static files
app.add_static('/style.css', 'style.css')
app.add_static('/script.js', 'script.js')


## app.start_wifi()  # Uncomment to start Wi-Fi access point
# Uncomment to stop Wi-Fi access point
# app.stop_wifi()  # Uncomment to stop Wi-Fi access point

# Start the MicroWeb server
app.run()


"""

        index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Projects</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Projects</h1>
    <p>{% greeting %}</p>
    {{ if projects }}
        <ul>
        {{ for project in projects }}
            <li>
                <h2>{{ project.title }}</h2>
                <p>{{ project.description }}</p>
            </li>
        {{ endfor }}
        </ul>
    {{ else }}
        <p>No projects found</p>
    {{ endif }}
    <script src="/script.js"></script>
</body>
</html>
"""

        style_content = """body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f0f0f0;
}
h1 {
    color: #333;
}
ul {
    list-style-type: none;
    padding: 0;
}
li {
    background: #fff;
    margin: 10px 0;
    padding: 15px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
h2 {
    margin: 0 0 10px;
    color: #007BFF;
}
p {
    margin: 0;
    color: #555;
}
"""

        script_content = """document.addEventListener('DOMContentLoaded', function() {
    console.log('MicroWeb example app loaded!');
    // Add interactivity if needed
});
"""

        readme_content = """# MicroWeb Example Application

This is a simple MicroWeb application for MicroPython devices (e.g., ESP32). It demonstrates dynamic routing, template rendering with for loops, static file serving, and JSON responses.

## Files
- `app.py`: The main MicroWeb application script with routes for a project list and API endpoints.
- `static/index.html`: A template displaying a list of projects using a for loop and conditional rendering.
- `static/style.css`: CSS styles for the project list.
- `static/script.js`: Basic JavaScript for interactivity.
- `models/users.py`: A model for user data (not used in this example, but can be extended).
- `models/products.py`: A model for product data (not used in this example, but can be extended).
- `README.md`: This file.


## Setup and Usage

### Prerequisites
- A MicroPython-compatible device (e.g., ESP32).
- The `microweb` package installed (`pip install microweb`).
- A serial port connection (e.g., COM10).

### Flash MicroPython and MicroWeb
1. Connect your device to your computer.
2. Flash MicroPython and MicroWeb to your device:
   ```bash
   microweb flash --port COM10
   ```
   Replace `COM10` with your device's serial port.

### Run the Application
1. Upload and run the application:
   ```bash
   microweb run app.py --port COM10 --static static/
   ```
2. Connect to the Wi-Fi access point:
   - **SSID**: MyESP32
   - **Password**: MyPassword
3. Open a browser and visit:
   - `http://192.168.4.1/` to see the project list.
   - `http://192.168.4.1/empty` to see the "No projects found" message.
   - `http://192.168.4.1/api/status` for the server status.
   - `http://192.168.4.1/greet/Alice` to test dynamic routing.

### Additional Commands
- Set the app to run on boot:
  ```bash
  microweb run app.py --port COM10 --add-boot --static static/
  ```
- Remove all files from the device:
  ```bash
  microweb remove --port COM10 --remove
  ```

## Testing
- Use a browser to access `http://192.168.4.1/` and `http://192.168.4.1/empty` to verify the template's for loop and conditional rendering.
- Test API endpoints with curl:
  ```bash
  curl http://192.168.4.1/api/status
  curl http://192.168.4.1/greet/Alice
  ```
- Check the browser's developer console for JavaScript logs from `script.js`.

For more details, run:
```bash
microweb examples
```
"""

        models_users_content = """# models/products.py
class Product:
    def __init__(self):
        self.products = [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Phone", "price": 499.99}
        ]
    
    def get_all(self):
        return self.products
    
    def get_by_id(self, product_id):
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
    
    def add_product(self, name, price):
        new_id = max([product["id"] for product in self.products], default=0) + 1
        new_product = {"id": new_id, "name": name, "price": price}
        self.products.append(new_product)
        return new_product


        """

        models_products_content = """# models/products.py
class Product:
    def __init__(self):
        self.products = [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Phone", "price": 499.99}
        ]
    
    def get_all(self):
        return self.products
    
    def get_by_id(self, product_id):
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
    
    def add_product(self, name, price):
        new_id = max([product["id"] for product in self.products], default=0) + 1
        new_product = {"id": new_id, "name": name, "price": price}
        self.products.append(new_product)
        return new_product

        """

        app_path = os.path.join(path, 'app.py')
        index_path = os.path.join(path, 'static', 'index.html')
        style_path = os.path.join(path, 'static', 'style.css')
        script_path = os.path.join(path, 'static', 'script.js')
        readme_path = os.path.join(path, 'README.md')
        model_users = os.path.join(path,'models', 'users.py')
        models_products = os.path.join(path, 'models', 'products.py')
        
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        with open(style_path, 'w', encoding='utf-8') as f:
            f.write(style_content)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        with open(model_users, 'w', encoding='utf-8') as f:
            f.write(models_users_content)
        with open(models_products, 'w', encoding='utf-8') as f:
            f.write(models_products_content)
        
        print_colored(f"Example app created at {path}/", color='green')
        print_colored(f"  - {app_path}", color='cyan')
        print_colored(f"  - {index_path}", color='cyan')
        print_colored(f"  - {style_path}", color='cyan')
        print_colored(f"  - {script_path}", color='cyan')
        print_colored(f"  - {readme_path}", color='cyan')
        print_colored(f"  - {model_users}", color='cyan')
        print_colored(f"  - {models_products}", color='cyan')
        print_colored(f"Run with: microweb run {app_path} --port COM10 --static static/", color='yellow')
        
    except Exception as e:
        print_colored(f"Error creating example app: {e}", color='red')


@cli.command()
@click.option('--port', default=None, help='Serial port, e.g., COM10')
def ls(port):
    """List files on the MicroPython device's filesystem."""
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        print_colored("No device found. Specify --port, e.g., --port COM10.", color='red')
        return
    try:
        print_colored(f"Listing files on device at {port}...", color='blue')
        remote_files = get_remote_file_info(port)
        if not remote_files:
            print_colored("No files found or error accessing filesystem.", color='yellow')
            return
        print_colored(f"Found {len(remote_files)} files on device:", color='green')
        for filename, size in sorted(remote_files.items()):
            print_colored(f"  📄 {filename}: {size} bytes", color='cyan')
    except Exception as e:
        print_colored(f"Error listing files: {e}", color='red')



@cli.command()
def examples():
    """Show example commands for using microweb CLI."""
    print_colored("Example commands for microweb CLI:", color='blue', style='bold')
    print_colored("\n1. Create an example MicroWeb app:", color='cyan')
    print_colored("   microweb create --path example_app", color='green')
    print_colored("\n2. Flash MicroPython and MicroWeb to ESP32:", color='cyan')
    print_colored("   microweb flash --port COM10", color='green')
    print_colored("\n3. Upload and run your app.py on ESP32:", color='cyan')
    print_colored("   microweb run app.py --port COM10", color='green')
    print_colored("\n4. Check static/template files without uploading:", color='cyan')
    print_colored("   microweb run app.py --check-only", color='green')
    print_colored("\n5. List files on the ESP32 filesystem:", color='cyan')
    print_colored("   microweb ls --port COM10", color='green')
    print_colored("\n6. Remove all files from ESP32 (DANGEROUS):", color='cyan')
    print_colored("   microweb remove --port COM10 --remove", color='green')
    print_colored("\n7. Upload and set app to run on boot:", color='cyan')
    print_colored("   microweb run app.py --port COM10 --add-boot", color='green')
    print_colored("\n8. Remove boot.py from ESP32:", color='cyan')
    print_colored("   microweb run app.py --port COM10 --remove-boot", color='green')
    print_colored("\nReplace COM10 with your actual ESP32 serial port.", color='yellow')



if __name__ == '__main__':
    cli()