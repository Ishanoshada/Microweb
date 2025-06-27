# MicroWeb

MicroWeb is a lightweight web server framework for MicroPython on the ESP32. It enables rapid development of web-based applications with dynamic routing, Wi-Fi configuration, query parameter handling, POST request support, JSON responses, and static file serving. The package includes a robust CLI for flashing MicroPython and running custom applications.


**Example: Minimal MicroWeb Server**

```python
from microweb import MicroWeb

app = MicroWeb(ap={'ssid': 'MyWiFi', 'password': 'MyPassword'}, debug=True)

@app.route('/')
def index(req):
    return {"message": "Welcome to MicroWeb API!"}

app.run()
```

**Comparison: Raw MicroPython Web Server Example for ESP32**

For reference, here's how a basic web server looks using only MicroPython's built-in libraries on ESP32:

```python
import network
import socket

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-AP', password='12345678')

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    request = cl.recv(1024)
    response = """\
HTTP/1.1 200 OK

Hello from ESP32 MicroPython!
"""
    cl.send(response)
    cl.close()
```

With MicroWeb, you get routing, templates, JSON, static files, and more—making web development on ESP32 much easier compared to the raw socket approach above.

---
## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Flashing the ESP32](#flashing-the-esp32)
    - [Running a Custom Application](#running-a-custom-application)
- [Example Usage](#example-usage)
    - [Minimal Example (`tests/2/app.py`)](#minimal-example-tests2apppy)
    - [Static Files and Templates Example (`tests/1/app.py`)](#static-files-and-templates-example-tests1apppy)
    - [Portfolio Demo (`tests/portfolio/`)](#portfolio-demo-testsportfolio)
- [Wi-Fi Configuration](#wi-fi-configuration)
- [Accessing the Web Server](#accessing-the-web-server)
- [CLI Tool Usage Examples](#cli-tool-usage-examples)
- [ Feature Updates ](#feature-updates)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

![example](/src/img.jpg)

## Features

- **Dynamic Routing**: Define routes like `@app.route('/welcome/<name>')` for flexible URL handling.
- **Wi-Fi Configuration**: Configure Wi-Fi via constructor parameters, an `internet` dictionary, or a web interface, with settings saved to `config.json`.
- **Query Parameters and POST Handling**: Support for URL query strings and form/JSON POST requests.
- **JSON Responses**: Return JSON data with customizable HTTP status codes.
- **Static File Serving**: Serve HTML, CSS, and other files from `static/`.
- **CLI Tools**: Flash MicroPython, upload, and run scripts with validation and auto-detection.
- **MicroPython Detection**: Verifies MicroPython before running scripts.
- **Easy Cleanup**: Remove all files from the ESP32 home directory using `microweb remove --port COM10 --remove`—try this if you need to reset or clean up your device.

![uml](/src/uml.svg)

---
## Installation

You can install MicroWeb using pip (for the CLI and development tools):

```bash
pip install microweb
```

Or, to use the latest source code, clone the repository from GitHub:
```bash
git clone https://github.com/ishanoshada/Microweb.git
cd Microweb
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install .
```

> **Note:** The workspace does not contain a git repository. If you want to contribute or track changes, initialize one with `git init`.


---

## Usage

Flash MicroPython and MicroWeb:

```bash
microweb flash --port COM10
```

#### Options:

* `--erase`
  Erase the entire flash memory before flashing firmware.

* `--esp8266`
  Flash ESP8266 firmware instead of the default ESP32.

* `--firmware firmware.bin`
  Use a custom `.bin` firmware file. This overrides the default firmware for ESP32 or ESP8266 ( any ).




---

### Running a Custom Application

Upload and run a MicroPython script:

```bash
microweb run app.py --port COM10
```

- Validates your `.py` file and checks for MicroPython on the device.
- Uploads and executes the script.
- Checks and uploads only changed files by default.
- Prompts to run `microweb flash` if MicroPython is not detected.
- After running `app.run()`, the ESP32 will host a Wi-Fi access point (AP) if it cannot connect to a configured network. You can then connect your device to this AP and access the web server using the ESP32's IP address (typically `http://192.168.4.1` in AP mode).

---

### Boot Script Management

You can configure your ESP32 to automatically start your application after any power cycle or reset by managing the `boot.py` file:

- **Add boot script (auto-run on power-up):**
    ```bash
    microweb run app.py --add-boot --port COM10
    ```
    This uploads a `boot.py` that will auto-run your app every time the ESP32 is powered on or reset. After upload, you can disconnect the ESP32 from your computer and power it from any source; the server will start automatically.

- **Remove boot script:**
    ```bash
    microweb run app.py --remove-boot --port COM10
    ```
    This removes the `boot.py` file, so your app will not auto-run on power-up.

---




## Example Usage

### Minimal Example (`tests/2/app.py`)

```python
from microweb import MicroWeb, Response

app = MicroWeb(debug=True, ap={'ssid': 'MyWiFi', 'password': 'MyPassword'})

@app.route("/")
def home(request):
    return Response("Hello from MicroWeb!", content_type="text/plain")

@app.route("/json")
def json_example(request):
    return {"message": "This is JSON"}

@app.route("/greet/<name>")
def greet(req, match):
    name = match.group(1) if match else "Anonymous"
    return {"message": f"Hello, {name}!", "status": "success"}

@app.route("/status")
def status(request):
    return {"status": "OK"}

@app.route("/headers")
def headers_example(request):
    resp = Response("Custom header set!", content_type="text/plain")
    resp.headers["X-Custom-Header"] = "Value"
    return resp

if __name__ == "__main__":
    app.run()
```

---

### Static Files and Templates Example (`tests/1/app.py`)

```python
import wifi
from microweb import MicroWeb

app = MicroWeb(debug=True, ap={"ssid": "MyESP32", "password": "mypassword"})

@app.route('/')
def home(req):
    return app.render_template('index.html', message="Welcome to MicroWeb API!")

@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({"status": "running", "ip": wifi.get_ip()})

@app.route('/api/echo', methods=['POST'])
def echo(req):
    data = req.form
    return app.json_response({"received": data})


@app.route('/api/methods', methods=['GET', 'POST'])
def methods(req):
    if req.method == 'GET':
        return app.json_response({"method": "GET", "message": "This is a GET request"})
    elif req.method == 'POST':
        data = req.json()
        return app.json_response({"method": "POST", "received": data})


@app.route('/submit', methods=['GET', 'POST'])
def submit_form(req):
    if req.method == 'POST':
        return app.render_template('result.html', data=str(req.form), method="POST")
    else:
        return app.render_template('form.html')

app.add_static('/style.css', 'style.css')
app.run()
```

#### Example Static Files (`tests/1/static/`)

- `index.html`: Main page with API demo and buttons.
- `form.html`: Simple HTML form for POST testing.
- `result.html`: Displays submitted form data.
- `style.css`: Enhanced styling for the test app.

---

### Portfolio Demo (`tests/portfolio/`)

The `tests/portfolio/` directory contains a full-featured portfolio web app built with MicroWeb, demonstrating:

- Multi-page routing (`/`, `/about`, `/projects`, `/contact`)
- Dynamic template rendering with variables
- Static assets (CSS, JS, images)
- API endpoints (e.g., `/api/info` returns JSON)
- Responsive, animated UI using HTML/CSS/JS
- Example of serving a personal portfolio from an ESP32

See `tests/portfolio/app.py` and the `static/` folder for a complete, ready-to-deploy example.

---

## Wi-Fi Configuration

Configure Wi-Fi via:

- Parameters: `MicroWeb(ssid='MyWiFi', password='MyPassword')`

If no credentials are provided, loads `config.json`. If connection fails, starts an access point (default: SSID `ESP32-MicroWeb`, password `12345678`).

---

## Accessing the Web Server

- Connect to the ESP32’s Wi-Fi (default: `ESP32-MicroWeb`/`12345678` in AP mode or the configured network).
- Access `http://<ESP32-IP>/` (e.g., `http://192.168.4.1` in AP mode).
- Use the control panel to update Wi-Fi, test routes, or submit forms.

---
## CLI Tool Usage Examples

The following table summarizes common `microweb` CLI commands. See also: #changes.

| Command Example                              | Description                                               |
|----------------------------------------------|-----------------------------------------------------------|
| `microweb exmples `                               | Show example commands for using microweb CLI.**          |
| `microweb flash --port COM10`                | Flash MicroPython firmware and upload MicroWeb files.      |
| `microweb flash --port COM10 --erase`        | Erase ESP32 flash before installing MicroPython.           |
| `microweb run app.py --port COM10`           | Upload and run a custom MicroPython script.                |
| `microweb run app.py --check-only`           | Check static/template dependencies without uploading.      |
| `microweb run app.py --force`                | Force upload all files, even if unchanged.                 |
| `microweb run app.py --add-boot`             | Uploads a `boot.py` to auto-run your app on boot.          |
| `microweb run app.py --remove-boot`          | Removes `boot.py` from the ESP32.                          |
| `microweb run app.py --static static/`       | Specify a custom static files folder.                      |
| `microweb run app.py --no-stop`              | Do not reset ESP32 before running the app.                 |
| `microweb run app.py --timeout 600`          | Set a custom timeout (in seconds) for app execution.       |
| `microweb remove --port COM10`               | List files on ESP32 (requires `--remove` to actually delete). |
| `microweb remove --port COM10 --remove`      | Remove all files in ESP32 home directory.                  |

**Notes:**
- `microweb flash` auto-detects the ESP32 port if not specified.
- `microweb run` validates dependencies, uploads only changed files by default, and can manage static/template files.
- Use `--help` with any command for more options and details.

For more details, run `microweb --help`.


---

### Feature Updates

- Improved CLI usability and error messages.
- Added support for static file serving and template rendering.
- Enhanced Wi-Fi configuration with fallback AP mode.
- Added validation for MicroPython firmware before running scripts.
- CLI now supports file cleanup and dependency checking.
- Auto-detects ESP32 port for flashing and running.
- Added support for custom HTTP headers and JSON responses.
- Improved documentation and usage examples.
- Support for GET, POST, and custom HTTP methods in route handlers.
- Static and template file hot-reloading for faster development.
- Built-in JSON and form data parsing for request bodies.
- Customizable AP SSID/password and web-based Wi-Fi setup page.
- CLI options for forced upload, boot script management, and static directory selection.
- Enhanced error handling and troubleshooting guidance.
- Modular project structure for easier extension and maintenance.


## Project Structure


```
microweb/
├── microweb/
│   ├── __init__.py
│   ├── microweb.py
│   ├── wifi.py
│   ├── uploader.py
│   ├── cli.py
│   ├── firmware/
│   │   ├── ESP32_GENERIC-20250415-v1.25.0.bin
│   │   ├── boot.py         # Minimal boot script 
│   │   ├── main.py         # Imports and runs your app module
├── setup.py                # Packaging and install configuration
├── README.md               # Project documentation
```


---

## Troubleshooting

- **Port Issues**: Specify `--port COM10` if auto-detection fails.
- **MicroPython Missing**: Run `microweb flash`.
- **Wi-Fi Failure**: Verify credentials or connect to default AP.
- **File Errors**: Ensure `app.py` and static files exist.

---

## Contributing

Fork and submit pull requests at [https://github.com/ishanoshada/microweb](https://github.com/ishanoshada/microweb).

---

**Repository Views** ![Views](https://profile-counter.glitch.me/microweb/count.svg)
