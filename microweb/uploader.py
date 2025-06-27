import subprocess
import os
import serial.tools.list_ports

def upload_file(file_path, port=None,destination=None):
    """Upload a file to the ESP32 filesystem using mpremote."""
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        raise Exception("No ESP32 found. Specify --port.")
    
    file_name = file_path.split('/')[-1].split('\\')[-1]
    
    try:
        if not os.path.exists(file_path):
            raise Exception(f"File {file_path} does not exist.")
        
        # Use mpremote to copy the file
        cmd = ['mpremote', 'connect', port, 'cp', file_path, f':{file_name}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"mpremote failed: {result.stderr}")
        
        # Verify file was uploaded
        verify_cmd = ['mpremote', 'connect', port, 'ls']
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
        
        if verify_result.returncode == 0 and file_name in verify_result.stdout:
            print(f"Successfully uploaded {file_name}")
        else:
            raise Exception(f"File {file_name} not found after upload")
            
    except subprocess.TimeoutExpired:
        raise Exception(f"Upload timeout for {file_name} or that's uploaded that is effect to boot.py that is why timeout. ")
    except Exception as e:
        raise Exception(f"Upload error for {file_name}: {e}")

def create_directory(dir_name, port=None):
    """Create a directory on the ESP32 filesystem."""
    if not port:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        port = ports[0] if ports else None
    if not port:
        raise Exception("No ESP32 found. Specify --port.")
    
    try:
        cmd = ['mpremote', 'connect', port, 'mkdir', f':{dir_name}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # mkdir might fail if directory exists, that's ok
        if result.returncode == 0 or 'exists' in result.stderr.lower():
            print(f"Directory {dir_name} ready")
        else:
            raise Exception(f"Failed to create directory {dir_name}: {result.stderr}")
            
    except Exception as e:
        raise Exception(f"Directory creation error for {dir_name}: {e}")

def verify_files(port, expected_files):
    """Verify that expected files are present on the ESP32."""
    try:
        cmd = ['mpremote', 'connect', port, 'ls']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise Exception(f"Failed to list files: {result.stderr}")
        
        output = result.stdout
        missing = [f for f in expected_files if f not in output]
        
        if missing:
            print(f"Warning: Missing files on ESP32: {missing}")
        else:
            print("All expected files verified on ESP32")
            
    except Exception as e:
        print(f"Error verifying files: {e}")