# MicroWeb Example Application

This is a simple MicroWeb application for MicroPython devices (e.g., ESP32). It includes a basic web server with a homepage and a status API endpoint.

## Files
- `app.py`: The main MicroWeb application script.
- `static/index.html`: The homepage template.

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
   microweb run app.py --port COM10
   ```
2. Connect to the Wi-Fi access point:
   - **SSID**: MyESP32
   - **Password**: MyPassword
3. Open a browser and visit `http://192.168.4.1` to see the homepage.

### Additional Commands
- Set the app to run on boot:
  ```bash
  microweb run app.py --port COM10 --add-boot
  ```
- Remove all files from the device:
  ```bash
  microweb remove --port COM10 --remove
  ```

For more details, run:
```bash
microweb examples
```
