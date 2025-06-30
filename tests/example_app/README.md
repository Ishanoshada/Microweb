# MicroWeb Example Application

This is a simple MicroWeb application for MicroPython devices (e.g., ESP32). It demonstrates dynamic routing, template rendering with for loops, static file serving, and JSON responses.

## Files
- `app.py`: The main MicroWeb application script with routes for a project list and API endpoints.
- `static/index.html`: A template displaying a list of projects using a for loop and conditional rendering.
- `static/style.css`: CSS styles for the project list.
- `static/script.js`: Basic JavaScript for interactivity.
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
