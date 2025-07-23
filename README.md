# MicroWeb

MicroWeb is a lightweight web server framework for MicroPython on the ESP32, designed for efficient development of web-based applications. It supports dynamic routing, Wi-Fi configuration (access point or station mode), query parameter and POST request handling, JSON responses, static file serving, and a powerful template engine with for loops and if conditionals. The package includes a robust CLI for flashing MicroPython, uploading files, and running custom applications on the ESP32.



**Example: Minimal MicroWeb Server**

```python
from microweb import MicroWeb

app = MicroWeb(ap={'ssid': 'MyWiFi', 'password': 'MyPassword'}, debug=True)

@app.route('/')
def index(req):
    return {"message": "Welcome to MicroWeb API!"}

@app.route('/status')
def status(req):
    return {"status": "running", "message": "Server is up and running!"}

@app.route('/greet/<name>')
def greet(req, match):
    name = match.group(1) if match else "Anonymous"
    return {"message": f"Hello, {name}!", "status": "success"}

app.run()
```

**Comparison: Raw MicroPython Web Server Example for ESP32**

For reference, here's how a basic web server looks using only MicroPython's built-in libraries on ESP32:

```python
import network
import socket
import ure  # micro regex

# Setup Wi-Fi Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-AP', password='12345678')
print("Access Point created with IP:", ap.ifconfig()[0])

# Start socket server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
.......................
        .......................
       

print('Listening on', addr)

# Define route logic
def handle_request(path):
    if path == "/":
        return {"message": "Welcome to MicroWeb API!"}

    elif path == "/status":
        return {"status": "running", "message": "Server is up and running!"}

    elif path.startswith("/greet/"):
        match = ure.match(r"/greet/(.+)", path)
        .......................
        .......................
       

    elif path == "/greet":
        return {"message": "Hello, Anonymous!", "status": "success"}

    else:
        return {"error": "Not found", "status": 404}

# Simple JSON response builder
def json_response(data, status_code=200):
   .......................
        .......................
        ......................
    response += ujson.dumps(data)
    return response

# Main loop
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        .......................
        .......................
        ......................
        cl.send(response)
    except Exception as e:
        print("Error:", e)
    finally:
        cl.close()

```

With MicroWeb, you get routing, templates, JSON, static files, and more—making web development on ESP32 much easier compared to the raw socket approach above.



## 📊 Code Size Comparison (Line Count)

| Component                 | Raw MicroPython Server   | MicroWeb Server                 |
| ------------------------- | ------------------------ | ------------------------------- |
| 📡 Wi-Fi Setup            | 5 lines                  | 1 line                          |
| 🔌 Socket Setup           | 5 lines                  | 0 lines (abstracted)            |
| 🔁 Server Loop            | 15+ lines                | 0 lines (abstracted)            |
| 📍 Route Definitions      | 20+ lines (manual logic) | 10 lines (with decorators)      |
| 🧠 Path Parsing / Routing | 5+ lines (manual regex)  | 0 lines (handled by MicroWeb)   |
| 🧾 JSON Response Builder  | 5 lines                  | 0 lines (handled automatically) |
| 🔍 Logging / Debug Info   | 5 lines (print-based)    | 0 lines (with `debug=True`)     |
| 🧱 Total Lines            | \~55–60 lines            | \~15 lines                      |

---

## Give us a ⭐️ if you find this project helpful!  

If you like this project, please consider giving it a star ⭐️ on GitHub. Your support motivates me to keep improving it!  

---
## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Creating an Example Application](#creating-an-example-application)
    - [Flashing the ESP32](#flashing-the-esp32)
    - [Running a Custom Application](#running-a-custom-application)
- [Example Usage](#example-usage)
    - [Example Projects](#example-projects)
    - [Minimal Example (`tests/2/app.py`)](#minimal-example-tests2apppy)
    - [Static Files and Templates Example (`tests/1/app.py`)](#static-files-and-templates-example-tests1apppy)
    - [Portfolio Demo (`tests/portfolio/`)](#portfolio-demo-testsportfolio)
    - [For Loop Example (`tests/for_loop`)](#for-loop-example-testsfor_loops)
    - [External API and Template Example (`tests/request_send`)](#external-api-and-template-example-testsrequest_send)
    - [Library and Model Upload Example (`tests/upload_lib/`)](#library-and-model-upload-example-testsupload_lib)
- [Wi-Fi Configuration](#wi-fi-configuration)
- [Accessing the Web Server](#accessing-the-web-server)
- [CLI Tool Usage Examples](#cli-tool-usage-examples)
- [How to Code with MicroWeb](#how-to-code-with-microweb)
- [ Feature Updates ](#feature-updates)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)


![example](/src/img.jpg)

## Features

- **Dynamic Routing**: Define routes like `@app.route('/welcome/<name>')` for flexible URL handling.
- **Wi-Fi Configuration**: Configure Wi-Fi via constructor parameters, an `ap` dictionary, or a web interface, with settings saved to `config.json`.
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




---


## Usage

### Creating an Example Application
Generate a sample MicroWeb application with a web server, template with `for` loops and conditionals, static CSS/JavaScript, and documentation:

```bash
microweb create --path example_app
```

- Creates a directory (default: `example_app`) containing `app.py`, `static/index.html`, `static/style.css`, `static/script.js`, and a `README.md` with usage instructions.
- Option: `--path <directory>` to specify a custom directory name.

### Flashing MicroPython and MicroWeb
Flash MicroPython firmware and MicroWeb to your device:

```bash
microweb flash --port COM10
```

#### ⚙️ Options:

* `--port COMx`
  Specify the serial port to which your ESP device is connected.
  Example: `--port COM5` (Windows), `--port /dev/ttyUSB0` (Linux/macOS)

* `--erase`
  Erase the entire flash memory before writing firmware. **Warning:** This will remove all existing data.

* `--esp8266`
  Flash ESP8266 firmware instead of the default ESP32 firmware.

* `--firmware firmware.bin`
  Use a custom `.bin` firmware file. Overrides the default firmware path.

* `--baud 460800`
  Set a custom baud rate for flashing. Defaults to `460800`, but can be changed to `115200`, `921600`, etc.

* `--full-flash`
  Flash the firmware to address `0x0` (useful for full `.bin` images with bootloader). Default flashing address is `0x1000`.

---

### 📝 Examples:

```bash
# Flash default ESP32 firmware and MicroWeb files
microweb flash --port COM10

# Flash custom firmware with erase
microweb flash --port COM10 --erase --firmware ./firmware/ESP32-C3-20250722-v1.25.1.bin

# Flash at 921600 baud and use full-flash mode (offset 0x0)
microweb flash --port COM10 --baud 921600 --full-flash --firmware ./firmware/full_image.bin

# Flash ESP8266 device with default firmware
microweb flash --port COM10 --esp8266
```


### Running a Custom Application
Upload and run a MicroPython script:

```bash
microweb run app.py --port COM10
```

- Validates your `.py` file and checks for MicroPython on the device.
- Uploads and executes the script.
- Checks and uploads only changed files by default.
- Prompts to run `microweb flash` if MicroPython is not detected.
- After running `app.run()`, the ESP32 will host a Wi-Fi access point (AP) if it cannot connect to a configured network. Connect to this AP and access the web server at `http://192.168.4.1` (typical IP in AP mode).

### Listing Files on the Device
List files on the MicroPython device's filesystem:

```bash
microweb ls --port COM10
```

- Displays all files and their sizes in the device's home directory.
- Requires MicroPython to be installed on the device.

---

### View real-time logs:
   ```bash
   mpremote connect COM10 run tests/request_send/app.py
   ```


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


**Checking the IP Address**:
- When running `microweb run app.py --port COM10`, the CLI displays the ESP32’s IP address (e.g., `🌐 🌐 Visit: http://192.168.4.1 or http://192.168.8.102/`).
- Alternatively, run `mpremote connect COM10 exec "import app; print(app.app.get_ip())"` to retrieve the IP.
- Check your router’s admin panel (e.g., `http://192.168.8.1`) for connected devices to find the ESP32’s IP.
- To view real-time logs, run:
  ```bash
  mpremote connect COM10 run app.py
  ```
  This prints logs like `Connecting to WiFi SSID: Dialog 4G 0F8`, `Connected. IP: 192.168.8.102`.

## Example Usage

Ah, got it! You want to **mention the `Microweb-Examples` repository in the `README.md` of your main [`Microweb`](https://github.com/Ishanoshada/Microweb) repository**.

Here’s what you can add to the bottom (or a "See Also" section) of your `Microweb/README.md`:

---

###  Example Projects

Looking for real-world examples using MicroWeb on ESP32?

👉 Check out the companion repository:
**[MicroWeb-Examples](https://github.com/Ishanoshada/Microweb-Examples)** – A collection of MicroPython-based IoT projects using the MicroWeb framework, featuring:

* 🔦 Laser Diode Control
* 📡 Microwave Radar Motion Detection
* 📏 Ultrasonic Distance Measuring

Explore how MicroWeb is used in practical applications with minimal setup!

---


### Minimal Example (`tests/2/app.py`)

```python
from microweb import MicroWeb, Response

#from dotenv import load_dotenv , get_env

# env_vars = load_dotenv()
# ssid = get_env('SSID', 'MyESP32', env_vars)
# password = get_env('PASSWORD', 'mypassword', env_vars)
# db_uri = get_env('DB_URI', None, env_vars)

app = MicroWeb(debug=True, ap={'ssid': 'MyWiFi', 'password': 'MyPassword'})

# app = MicroWeb(
#     ap={"ssid": "Dialog 4G 0F8", "password": "youpassword"},  # Change to your router
#     debug=True,
#     mode="wifi"  # Connect as client to your router
# )

# Uncomment to stop Wi-Fi access point
# app.stop_wifi()  # Uncomment to stop Wi-Fi access point
## app.start_wifi()  # Uncomment to start Wi-Fi access point after stop

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


app.run()
```


**Example Template (`tests/for_loops/static/index.html`)**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Projects</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Projects</h1>
    {% greeting %}
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
</body>
</html>
```
---

### Static Files and Templates Example (`tests/1/app.py`)

```python
import wifi
from microweb import MicroWeb

app = MicroWeb(debug=True, ap={"ssid": "MyESP32", "password": "mypassword"})
# app = MicroWeb(
#     ap={"ssid": "Dialog 4G 0F8", "password": "youpassword"},  # Change to your router
#     debug=True,
#     mode="wifi"  # Connect as client to your router
# )

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
        data = req.form
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

### **For Loop Example (`tests/for_loops`)**

This example demonstrates the use of MicroWeb’s template engine with a `for` loop to display a list of projects dynamically. It includes two routes: one with a populated project list and one with an empty list to showcase conditional rendering using `if`, `else`, and `for` constructs in the template.

**Example Code (`tests/for_loops/app.py`)**:

```python
import wifi
from microweb import MicroWeb

# Initialize MicroWeb with debug mode and access point
app = MicroWeb(debug=True, ap={'ssid': 'MyESP32', 'password': 'mypassword'})
# app = MicroWeb(
#     ap={"ssid": "Dialog 4G 0F8", "password": "youpassword"},  # Change to your router
#     debug=True,
#     mode="wifi"  # Connect as client to your router
# )

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

app.add_static('/style.css', 'style.css')


app.run()
```


**Explanation**:
- **Application Code (`app.py`)**:
  - The `/` route passes a list of projects with `title` and `description` fields, along with a `greeting` variable.
  - The `/empty` route passes an empty `projects` list to test the `else` branch of the template.
  - `app.add_static('/style.css', 'style.css')` serves the CSS file for styling the template.
- **Template (`index.html`)**:
  - `{% greeting %}` renders the greeting message (e.g., "Welcome to MicroWeb!").
  - `{{ if projects }}` checks if the `projects` list is non-empty.
  - `{{ for project in projects }}` iterates over the `projects` list, rendering each project’s `title` and `description` in an `<li>` element.
  - `{{ else }}` displays "No projects found" if the `projects` list is empty.
  - The `<link rel="stylesheet" href="/style.css">` tag applies styles from `style.css`.
- **Static File (`style.css`)**:
  - Provides a clean, modern look with a light background, styled list items, and shadowed boxes for each project.
- **Testing**:
  - Upload files: `microweb run app.py --static static/ --port COM10`.
  - Access `http://192.168.4.1/` to see the project list Zornlist with descriptions.
  - Access `http://192.168.4.1/empty` to see the "No projects found" message.
  - Use `curl http://192.168.4.1/` or a browser to verify the output.


---

### *External API and Template Example (`tests/request_send/`)*

This example, located in the `tests/request_send/` folder, demonstrates a MicroWeb application that:
- Connects to a Wi-Fi network (`mode='wifi'`) using the `Dialog 4G 0F8` network.
- Fetches data from an external API using `urequests` (with a fallback for HTTPS limitations).
- Renders a dynamic template (`index.html`) with a project list.
- Serves static files (`style.css`, `script.js`) for styling and client-side scripting.
- Includes routes for status checks, POST requests, and an offline fallback.

**Application Code (`tests/request_send/app.py`)**:

```python
from microweb import MicroWeb
import urequests

# This example demonstrates how to create a simple web server using MicroWeb on ESP32
# It includes routes for home, status check, POST handling, and live site mirroring.
# Make sure you have the MicroWeb library installed on your ESP32
# To run this, save it as app.py on your ESP32 and ensure you have the necessary files in the same directory:
# - index.html (for home page)
# - mirror.html (for offline fallback)
# - style.css (for styling)
# - script.js (for client-side scripting)

app = MicroWeb(
    ap={"ssid": "Dialog 4G 0F8", "password": "youpassword"},  # Change to your router
    debug=True,
    mode="wifi"  # Connect as client to your router
)

# Home route
@app.route('/')
def home(req):
    return app.render_template('index.html', greeting='Welcome to ESP32 MicroWeb!', projects=[
        {'title': 'Request Example', 'description': 'Live fetch from JSONPlaceholder /request'},
        {'title': 'Status Check', 'description': 'Check server status'},
        {'title': 'POST Example', 'description': 'Send POST to /post-test'}
    ])

# /status route
@app.route('/status', methods=['GET'])
def status(req):
    return app.json_response({
        "status": "running",
        "ip": app.get_ip(),
        "mode": "wifi"
    })

# POST test
@app.route('/post-test', methods=['POST'])
def post_test(req):
    return app.json_response({
        "received": req.form,
        "note": "You sent this via POST"
    })

# Live mirror of your site
@app.route('/request')
def mirror(req):
    try:
        res = urequests.get("https://jsonplaceholder.typicode.com/posts/1")  # Only works if HTTPS supported
        html = res.text
        res.close()
        return app.html_response(html)
    except Exception as e:
        return app.html_response(f"""
            <h1>Failed to fetch live site</h1>
            <p>{str(e)}</p>
            <p>ESP32 doesn't support HTTPS by default. Use a proxy or offline HTML instead.</p>
        """)

# Optional fallback if you save HTML locally
@app.route('/offline')
def offline(req):
    return app.render_template("mirror.html")

# Static files
app.add_static('/style.css', 'style.css')
app.add_static('/script.js', 'script.js')

app.run()
```

**Template (`tests/request_send/static/index.html`)**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>MicroWeb</title>
    <link rel="stylesheet" href="/style.css">
    <script src="/script.js"></script>
</head>
<body>
    <h1>{% greeting %}</h1>
    {{ if projects }}
        <ul>
        {{ for project in projects }}
            <li>{{ project.title }}: {{ project.description }}</li>
        {{ endfor }}
        </ul>
    {{ else }}
        <p>No projects found.</p>
    {{ endif }}
</body>
</html>
```

**Static CSS (`tests/request_send/static/style.css`)**:

```css
body {
    font-family: Arial, sans-serif;
    padding: 20px;
    background: #f7f7f7;
}
h1 {
    color: #007BFF;
}
.....
```

**Static JavaScript (`tests/request_send/static/script.js`)**:

```javascript
document.addEventListener("DOMContentLoaded", function () {
    console.log("📡 MicroWeb loaded from ESP32!");
});
```

**Explanation**:
- **Wi-Fi Configuration**: Uses `mode='wifi'` to connect to the `Dialog 4G 0F8` network (IP: `192.168.8.102`). If the connection fails, it falls back to an access point (IP: `192.168.4.1`).
- **Routes**:
  - `/`: Renders `index.html` with a greeting and a list of projects using a `for` loop and `if` conditional.
  - `/status`: Returns a JSON response with the server’s IP and status.
  - `/post-test`: Handles POST requests, returning the submitted form data as JSON.
  - `/request`: Attempts to fetch data from `https://jsonplaceholder.typicode.com/posts/1` using `urequests.get()`. If HTTPS fails (common on ESP32), it returns an error message.
  - `/offline`: Renders a local `mirror.html` file as a fallback (ensure `mirror.html` exists in `static/`).
- **Static Files**: Serves `style.css` for styling and `script.js` for client-side scripting (logs a message to the browser console).
- **Template**: `index.html` displays a greeting and a styled list of projects, with a fallback message if no projects are provided.
- **HTTPS Limitation**: The `/request` route may fail due to MicroPython’s limited HTTPS support on ESP32. The error message suggests using a proxy or offline HTML (`/offline`).

**Running**:
1. Place `app.py`, `index.html`, `style.css`, `script.js`, and `mirror.html` (if used) in `tests/request_send/` (with `index.html`, `style.css`, `script.js` in `tests/request_send/static/`).
2. Upload and run:
   ```bash
   microweb run tests/request_send/app.py --port COM10 --static tests/request_send/static/
   ```
3. Access the server at `http://192.168.8.102` (or `http://192.168.4.1` if Wi-Fi connection fails).
4. View real-time logs:
   ```bash
   mpremote connect COM10 run tests/request_send/app.py
   ```
   Expected logs:
   ```
   Connecting to WiFi SSID: Dialog 4G 0F8
   Connected. IP: 192.168.8.102
   MicroWeb running on http://0.0.0.0:80
   ```

**Testing**:
- **Home Page**: `http://192.168.8.102/` displays a styled project list:
  ```html
  <h1>Welcome to ESP32 MicroWeb!</h1>
  <ul>
    <li>Request Example: Live fetch from JSONPlaceholder /request</li>
    <li>Status Check: Check server status</li>
    <li>POST Example: Send POST to /post-test</li>
  </ul>
  ```
- **Status**: Test with `curl`:
  ```bash
  curl http://192.168.8.102/status
  ```
  Expected:
  ```json
  {"status": "running", "ip": "192.168.8.102", "mode": "wifi"}
  ```
- **POST**: Test with `curl`:
  ```bash
  curl -X POST -d "key=value" http://192.168.8.102/post-test
  ```
  Expected:
  ```json
  {"received": {"key": "value"}, "note": "You sent this via POST"}
  ```
- **Fetch**: Test `/request`:
  ```bash
  curl http://192.168.8.102/request
  ```
  - If HTTPS works: Returns JSON data from `jsonplaceholder.typicode.com`.
  - If HTTPS fails: Returns an HTML error message.
- **Offline**: Test `/offline` (requires `mirror.html`):
  ```bash
  curl http://192.168.8.102/offline
  ```

**Notes**:
- Ensure `urequests` is available on the ESP32 (bundled with MicroWeb or uploaded separately).
- If HTTPS fails on `/request`, create a `mirror.html` file in `static/` for the `/offline` route.
- Verify files with:
  ```bash
  microweb ls --port COM10
  ```
- Force re-upload if needed:
  ```bash
  microweb run tests/request_send/app.py --port COM10 --static tests/request_send/static/ --force
  ```

---


### Library and Model Upload Example (`tests/upload_lib/`)

This example, located in the `tests/upload_lib/` folder, demonstrates how to use MicroWeb’s `lib_add` method to include external libraries and model files, and how to handle both GET and POST requests with a dynamic template. It includes models for managing users and products, a utility library, and a form-based interface for adding data.

**Application Code (`tests/upload_lib/app.py`)**:

```python
from microweb import MicroWeb
import some_lib
from users import User
from products import Product

# Initialize MicroWeb with debug mode and Wi-Fi access point
app = MicroWeb(debug=True, ap={"ssid": "TestESP32", "password": "test1234"})

# Register library and model files
app.lib_add("some_lib.py")
app.lib_add("/models/users.py")
app.lib_add("/models/products.py")

# Initialize models
users = User()
products = Product()

@app.route('/')
def home(req):
    return app.render_template(
        'index.html',
        greeting=some_lib.say_hello(),
        timestamp=some_lib.get_timestamp(),
        users=users.get_all(),
        products=products.get_all()
    )

@app.route('/user/<id>')
def get_user(req, match):
    user_id = int(match.group(1)) if match else 0
    user = users.get_by_id(user_id)
    if user:
        .................................
        ....................
app.run()
```

**Library File (`tests/upload_lib/some_lib.py`)**:

```python
def say_hello():
    return "Hello from some_lib!"

def get_timestamp():
    import time
    return time.time()
```

**Model File (`tests/upload_lib/models/users.py`)**:

```python
class User:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    
    def get_all(self):
        return self.users
   ......................
```

**Model File (`tests/upload_lib/models/products.py`)**:

```python
class Product:
    def __init__(self):
        self.products = [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Phone", "price": 499.99}
        ]
    
    def get_all(self):
        return self.products
  .............................
  ...........................
```

**Template (`tests/upload_lib/static/index.html`)**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test App</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>{{ greeting }}</h1>
    <p>Timestamp: {{ timestamp }}</p>
    
    <h2>Add User</h2>
   ................
   ................
   ..........
    
    <h2>Users</h2>
    {{ if users }}
        <ul>
        {{ for user in users }}
            <li>{{ user.name }} ({{ user.email }}) - ID: {{ user.id }}</li>
        {{ endfor }}
        </ul>
    {{ else }}
        <p>No users found</p>
    {{ endif }}
    
    <h2>Products</h2>
    {{ if products }}
        <ul>
        {{ for product in products }}
            <li>{{ product.name }} - ${{ product.price }} - ID: {{ product.id }}</li>
        {{ endfor }}
        </ul>
    {{ else }}
        <p>No products found</p>
    {{ endif }}
</body>
</html>
```

**Static CSS (`tests/upload_lib/static/style.css`)**:

```css
body {
    font-family: Arial, sans-serif;
    margin: 20px;
    .............
```

**Explanation**:
- **Application Code (`app.py`)**:
  - Imports `User` and `Product` directly from `users` and `products` modules, reflecting their placement in the root directory (`tests/upload_lib/`).
  - Uses `app.lib_add()` to register `some_lib.py`, `users.py`, and `products.py` for upload to the ESP32.
  - The `/` route renders `index.html` with data from `some_lib` (greeting, timestamp) and the `User` and `Product` models.
  - Routes `/user/<id>` and `/product/<id>` handle GET requests, returning JSON for specific users or products.
  - Routes `/add_user` and `/add_product` handle POST requests from forms, adding new users or products and returning JSON responses.
  - `app.add_static('/style.css', 'style.css')` serves the CSS file for styling.
- **Library File (`some_lib.py`)**:
  - Provides utility functions `say_hello()` and `get_timestamp()` used in the `home` route.
  - Uploaded to `lib/some_lib.py` on the ESP32 for organized imports.
- **Model Files (`users.py`, `products.py`)**:
  - Define `User` and `Product` classes with in-memory data storage and methods for retrieving and adding data.
  - Uploaded to the ESP32 root directory to match the direct imports (`from users import User`, `from products import Product`).
- **Template (`index.html`)**:
  - Displays the greeting and timestamp from `some_lib`.
  - Includes forms for adding users (POST to `/add_user`) and products (POST to `/add_product`).
  - Lists users and products using `for` loops and `if` conditionals, with a fallback message if lists are empty.
  - Links to `style.css` for styling.
- **Static File (`style.css`)**:
  - Provides a clean, modern look with styled forms, lists, and buttons.
- **Directory Structure**:
  - Files are organized as:
    ```
    tests/upload_lib/
    ├── app.py
    ├── some_lib.py
    ├── /models/users.py
    ├── /models/products.py
    ├── static/
    │   ├── index.html
    │   ├── style.css
    ```

**Running**:
1. Place `app.py`, `some_lib.py`, `users.py`, `products.py`, and the `static/` folder with `index.html` and `style.css` in `tests/upload_lib/`.
2. Flash MicroPython (if not already done):
   ```bash
   microweb flash --port COM10
   ```
3. Upload and run the application:
   ```bash
   microweb run tests/upload_lib/app.py --port COM10 --static tests/upload_lib/static/
   ```
4. Connect to the Wi-Fi access point:
   - SSID: `TestESP32`
   - Password: `test1234`
   - Access the server at `http://192.168.4.1/`.
5. View real-time logs:
   ```bash
   mpremote connect COM10 run tests/upload_lib/app.py
   ```
   Expected logs:
   ```
   MicroWeb running on http://0.0.0.0:80
   ```


### Wi-Fi Configuration

Configure Wi-Fi via:

- **Station Mode (Connect to Existing Network)**:
  ```python
  MicroWeb(mode='wifi', ap={'ssid': 'MyWiFi', 'password': 'MyPassword'})
  ```
  - Connects the ESP32 to an existing Wi-Fi network (e.g., your router) using the provided SSID and password.
  - The ESP32 will be assigned an IP address by the network (e.g., `192.168.8.102`). Access the web server at `http://<ESP32-IP>/` (check the IP in the CLI output or your router’s admin panel).
  - If the connection fails, the ESP32 falls back to creating an access point (default: SSID `ESP32-MicroWeb`, password `12345678`, IP `192.168.4.1`).

- **Access Point Mode**:
  ```python
  MicroWeb(mode='ap', ap={'ssid': 'MyESP32', 'password': 'mypassword'})
  ```
  - Creates a Wi-Fi access point hosted by the ESP32. Connect to this network and access the server at `http://192.168.4.1`.

- **Configuration File**:
  If no credentials are provided, MicroWeb loads settings from `config.json` on the ESP32. Use the web interface (at `http://<ESP32-IP>/`) to update Wi-Fi settings if supported.



---


### Troubleshooting
- **Wrong IP (`192.168.4.1`)**: If the CLI shows `192.168.4.1` instead of `192.168.8.102`, the ESP32 failed to connect to `Dialog 4G ANY`. Verify the SSID/password or check the router’s connected devices.
- **No Logs**: Ensure `mpremote` is installed (`pip install mpremote`) and `COM10` is correct (`mpremote` to list ports).
- **File Issues**: Verify `app.py` and `wifi.py` are uploaded:
  ```bash
  microweb ls --port COM10
  ```


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
| `microweb create --path example_app`         | Create an example MicroWeb app with `app.py`, `static/index.html`, and `README.md`. |
| `microweb examples`                          | Show example commands for using the MicroWeb CLI.          |
| `microweb flash --port COM10`                | Flash MicroPython firmware and upload MicroWeb files.      |
| `microweb flash --port COM10 --erase`        | Erase ESP32 flash before installing MicroPython.           |
| `microweb run app.py --port COM10`           | Upload and run a custom MicroPython script.                |
| `microweb run app.py --check-only`           | Check static/template dependencies without uploading.      |
| `microweb run app.py --force`                | Force upload all files, even if unchanged.                 |
| `microweb run app.py --add-boot`             | Upload a `boot.py` to auto-run your app on boot.           |
| `microweb run app.py --remove-boot`          | Remove `boot.py` from the ESP32.                           |
| `microweb run app.py --static static/`       | Specify a custom static files folder.                      |
| `microweb run app.py --no-stop`              | Do not reset ESP32 before running the app.                 |
| `microweb run app.py --timeout 600`          | Set a custom timeout (in seconds) for app execution.       |
| `microweb ls --port COM10`                   | List files and their sizes on the ESP32 filesystem.        |
| `microweb remove --port COM10`               | List files on ESP32 (requires `--remove` to actually delete). |
| `microweb remove --port COM10 --remove`      | Remove all files in ESP32 home directory.                  |

**Notes:**
- `microweb flash` auto-detects the ESP32 port if not specified.
- `microweb run` validates dependencies, uploads only changed files by default, and can manage static/template files.
- Use `--help` with any command for more options and details.

For more details, run `microweb --help`.



---

## How to Code with MicroWeb

This section guides you through writing MicroWeb applications for MicroPython on ESP32. MicroWeb simplifies web development with features like dynamic routing, template rendering, static file serving, JSON responses, and Wi-Fi configuration. Below, we explain the key components of coding with MicroWeb, with examples to help you get started.

### **1. Setting Up the MicroWeb Application**
To start, import the `MicroWeb` class and initialize the app. You can configure debugging and Wi-Fi settings (access point or station mode) in the constructor.

```python
from microweb import MicroWeb

# Initialize MicroWeb with debug mode and access point (AP) settings
app = MicroWeb(debug=True, ap={'ssid': 'MyESP32', 'password': 'mypassword'})


# Uncomment to stop Wi-Fi access point
# app.stop_wifi()  # Uncomment to stop Wi-Fi access point
## app.start_wifi()  # Uncomment to start Wi-Fi access point after stop

```

**Explanation**:
- `debug=True`: Enables detailed logging for troubleshooting, useful during development.
- `ap={'ssid': ..., 'password': ...}`: Configures the ESP32 to create a Wi-Fi access point if it cannot connect to a network. Alternatively, use `internet={'ssid': ..., 'password': ...}` for station mode to connect to an existing Wi-Fi network.
- If no Wi-Fi credentials are provided, MicroWeb loads settings from `config.json` or starts a default AP (SSID: `ESP32-MicroWeb`, password: `12345678`).

### **2. Defining Routes**
Routes map URLs to handler functions. Use the `@app.route()` decorator to define endpoints and specify HTTP methods (e.g., GET, POST).

```python
@app.route('/')
def home(req):
    return app.render_template('index.html', message='Welcome to MicroWeb!')
```

**Explanation**:
- The `@app.route('/')` decorator maps the root URL (`/`) to the `home` function.
- The `req` parameter provides access to request data (e.g., `req.method`, `req.form`, `req.form`).
- `app.render_template` renders an HTML template (`index.html`) with dynamic variables (e.g., `message`).

For dynamic routing with URL parameters:
```python
@app.route('/greet/<name>')
def greet(req, match):
    name = match.group(1) if match else 'Anonymous'
    return {'message': f'Hello, {name}!', 'status': 'success'}
```

**Explanation**:
- `/greet/<name>` captures a URL parameter (e.g., `/greet/Alice` sets `name` to `Alice`).
- The `match` parameter contains the parsed URL parameters, accessed via `match.group(1)`.

### **3. Handling HTTP Methods**
MicroWeb supports multiple HTTP methods (GET, POST, etc.) for a single route using the `methods` parameter.

```python
@app.route('/api/methods', methods=['GET', 'POST'])
def methods(req):
    if req.method == 'GET':
        return app.json_response({'method': 'GET', 'message': 'This is a GET request'})
    elif req.method == 'POST':
        data = req.form
        return app.json_response({'method': 'POST', 'received': data})
```

**Explanation**:
- The `methods=['GET', 'POST']` parameter allows the route to handle both GET and POST requests.
- `req.method` checks the HTTP method to determine the response.
- `req.form` parses JSON data from the POST request body.
- `app.json_response` returns a JSON response with the specified data.


### **4. Rendering Templates (Updated with Advanced Template Engine Usage)**

MicroWeb supports rendering HTML templates with dynamic data, ideal for creating dynamic web interfaces. The template engine uses a simple syntax with `{% %}` for variables and control structures (e.g., loops, conditionals) and `{{ }}` for control blocks like `if`, `for`, `else`, and `endif`. This allows you to create flexible, reusable templates for your ESP32-based web applications.

#### **Basic Template Rendering**
Templates are stored in the `static/` directory (or a specified folder) and rendered using `app.render_template`. Variables passed to the template are inserted into placeholders.

```python
@app.route('/')
def home(req):
    return app.render_template('index.html', message='Welcome to MicroWeb!')
```

**Explanation**:
- `app.render_template('index.html', message='Welcome to MicroWeb!')` renders the `index.html` template, replacing `{% message %}` with the string `"Welcome to MicroWeb!"`.
- Templates must be uploaded to the ESP32’s filesystem (e.g., using `microweb run app.py --static static/ --port COM10`).

#### **Advanced Template Engine Usage**
MicroWeb’s template engine supports control structures like conditionals (`if`, `else`, `endif`) and loops (`for`, `endfor`), enabling dynamic content generation. Below is an example of a template (`projects.html`) that uses these features to display a list of projects or a fallback message.

**Example Template (`static/projects.html`)**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Projects</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Projects</h1>
    {% greeting %}
    {{ if projects }}
        <ul>
        {{ for project in projects }}
            <p>{{ project.title }}</p>
        {{ endfor }}
        </ul>
    {{ else }}
        <p>Projects not found</p>
    {{ endif }}
</body>
</html>
```

**Corresponding Route**:
```python
@app.route('/projects')
def projects(req):
    projects = [
        {'title': 'Project A', 'description': 'First project'},
        {'title': 'Project B', 'description': 'Second project'}
    ]
    return app.render_template('projects.html', greeting='Welcome to the Projects Page!', projects=projects)
```

**Explanation**:
- **Variable Substitution**: `{% greeting %}` is replaced with `"Welcome to the Projects Page!"`.
- **Conditional (`if`, `else`, `endif`)**: The `{{ if projects }}` block checks if the `projects` variable is non-empty. If `projects` exists and is not empty, the `ul` list is rendered; otherwise, the `Projects not found` message is shown.
- **Loop (`for`, `endfor`)**: The `{{ for project in projects }}` loop iterates over the `projects` list, rendering a `<p>` tag for each project’s `title` (accessed via `{{ project.title }}`).
- **Dot Notation**: The template engine supports dot notation for accessing dictionary keys or object attributes (e.g., `project.title` retrieves the `title` key from each project dictionary).
- **Static Files**: The `<link rel="stylesheet" href="/style.css">` tag references a static CSS file, served via `app.add_static('/style.css', 'style.css')`.

**Alternative Scenario (Empty Projects List)**:
```python
@app.route('/projects-empty')
def projects_empty(req):
    return app.render_template('projects.html', greeting='No Projects Available', projects=[])
```

**Explanation**:
- If `projects=[]` (empty list), the `{{ if projects }}` condition evaluates to false, and the template renders the fallback message: `<p>Projects not found</p>`.

#### **Template Syntax Rules**
- **Variables**: Use `{% variable %}` for simple variable substitution (e.g., `{% greeting %}`).
- **Control Structures**:
  - `{{ if condition }} ... {{ else }} ... {{ endif }}`: Evaluates `condition` (truthy/falsy) to render the appropriate branch.
  - `{{ for var in iterable }} ... {{ endfor }}`: Iterates over `iterable`, assigning each item to `var`.
- **Dot Notation**: Access nested data with `variable.subkey` (e.g., `project.title`).
- **Error Handling**: If a variable or key is undefined, the engine returns an empty string to avoid crashes, ensuring robust rendering on resource-constrained ESP32 devices.

#### **Best Practices for Templates**
- **File Placement**: Store templates in the `static/` directory and upload them to the ESP32 using the `microweb` CLI.
- **Caching**: MicroWeb caches parsed templates to optimize memory usage on the ESP32. Avoid frequent template changes in production to leverage caching.
- **Debugging**: Enable `debug=True` in `MicroWeb` initialization to log template rendering errors (e.g., missing files or syntax errors).
- **Validation**: Test templates with both valid and empty data (e.g., `projects=[]`) to ensure the `if` and `else` branches work as expected.
- **Static Assets**: Link CSS, JavaScript, or images in templates using `app.add_static` to serve them efficiently.

#### **Testing the Template**
- **Upload Files**: Ensure `projects.html` and `style.css` are in the `static/` directory and uploaded:
  ```bash
  microweb run app.py --static static/ --port COM10
  ```
- **Access**: Open `http://192.168.4.1/projects` (or the ESP32’s IP) in a browser to see the rendered project list.
- **Verify Output**:
  - With projects: Displays `<h1>Projects</h1><p>Welcome to the Projects Page!</p><ul><p>Project A</p><p>Project B</p></ul>`.
  - Without projects: Displays `<h1>Projects</h1><p>No Projects Available</p><p>Projects not found</p>`.
- **curl Test**:
  ```bash
  curl http://192.168.4.1/projects
  ```

#### **Complete Example with Template**
Here’s a full example combining the `projects.html` template with routes and static file serving:

```python
import wifi
from microweb import MicroWeb

app = MicroWeb(debug=True, ap={'ssid': 'MyESP32', 'password': 'mypassword'})

@app.route('/')
def home(req):
    return app.render_template('index.html', message='Welcome to MicroWeb!')

@app.route('/projects')
def projects(req):
    projects = [
        {'title': 'Project A', 'description': 'First project'},
        {'title': 'Project B', 'description': 'Second project'}
    ]
    return app.render_template('projects.html', greeting='Welcome to the Projects Page!', projects=projects)

@app.route('/projects-empty')
def projects_empty(req):
    return app.render_template('projects.html', greeting='No Projects Available', projects=[])

app.add_static('/style.css', 'style.css')
<<<<<<< HEAD


=======
>>>>>>> 90c3b61ce53aea3d7566bfbb301164c8360e34ba
app.run()
```

**Explanation**:
- The `/projects` route renders the `projects.html` template with a list of projects, triggering the `for` loop to display each project’s title.
- The `/projects-empty` route tests the `else` branch by passing an empty `projects` list.
- The `style.css` file is served as a static file for consistent styling.
- Run the app and access `http://192.168.4.1/projects` or `http://192.168.4.1/projects-empty` to test both scenarios.

### **5. Serving Static Files**
MicroWeb allows serving static files like CSS, JavaScript, or images to enhance web interfaces.

```python
app.add_static('/style.css', 'style.css')
```

**Explanation**:
- `app.add_static` maps a URL path (`/style.css`) to a file in the `static/` directory (`style.css`).
- Static files must be uploaded to the ESP32’s filesystem using:
  ```bash
  microweb run app.py --static static/ --port COM10
  ```
- In the `result.html` example, `<link rel="stylesheet" href="/style.css">` loads the CSS file for styling.

### **6. JSON Responses**
MicroWeb simplifies JSON responses for API endpoints.

```python
@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({'status': 'running', 'ip': wifi.get_ip()})
```

**Explanation**:
- `app.json_response` formats the dictionary as JSON and sets the `Content-Type` to `application/json`.
- The `wifi` module (if available) retrieves the ESP32’s IP address.

### **7. Custom HTTP Headers**
You can set custom headers using the `Response` class.

```python
from microweb import Response

@app.route('/headers')
def headers_example(req):
    resp = Response('Custom header set!', content_type='text/plain')
    resp.headers['X-Custom-Header'] = 'Value'
    return resp
```

**Explanation**:
- The `Response` class allows custom content types and headers.
- `resp.headers` sets additional HTTP headers for the response.

### **8. Wi-Fi Integration**
MicroWeb handles Wi-Fi configuration, allowing the ESP32 to act as an access point or connect to a network.

```python
import wifi
from microweb import MicroWeb

app = MicroWeb(debug=True, ap={'ssid': 'MyESP32', 'password': 'mypassword'})


# Uncomment to stop Wi-Fi access point
# app.stop_wifi()  # Uncomment to stop Wi-Fi access point
## app.start_wifi()  # Uncomment to start Wi-Fi access point after stop

@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({'status': 'running', 'ip': wifi.get_ip()})
```

**Explanation**:
- The `wifi` module (part of MicroWeb or MicroPython) provides functions like `wifi.get_ip()` to retrieve the device’s IP address.
- If Wi-Fi connection fails, the ESP32 starts an access point with the specified `ssid` and `password`.

### **9. Running the Application**
Start the web server with `app.run()`.

```python

app.run()
```

**Explanation**:
- `app.run()` starts the MicroWeb server, listening for HTTP requests.
- Use the CLI to upload and run the script:
  ```bash
  microweb run app.py --port COM10
  ```

### **10. Best Practices**
- **Error Handling**: Add try-except blocks for `wifi.get_ip()` or `req.form` to handle network or input errors.
  ```python
  try:
        ip = wifi.get_ip()
      
        # Uncomment to stop Wi-Fi access point
        # app.stop_wifi()  # Uncomment to stop Wi-Fi access point
        ## app.start_wifi()  # Uncomment to start Wi-Fi access point after stop
  except Exception as e:
      ip = 'N/A'
  return app.json_response({'status': 'running', 'ip': ip})
  ```
- **File Management**: Ensure templates (`index.html`, `form.html`, `result.html`) and static files (`style.css`) exist in the `static/` directory before running.
- **Security**: Avoid hardcoding Wi-Fi credentials; use `config.json` or the web interface for configuration.
- **Debugging**: Enable `debug=True` during development to log errors and requests.
- **Testing**: Test routes with tools like `curl` or a browser (e.g., `http://192.168.4.1/` in AP mode).

### **11. Example: Putting It All Together**
Below is a complete MicroWeb application combining routes, templates, static files, and JSON responses, including the `result.html` template.

```python
import wifi
from microweb import MicroWeb

app = MicroWeb(debug=True, ap={'ssid': 'MyESP32', 'password': 'mypassword'})

@app.route('/')
def home(req):
    return app.render_template('index.html', message='Welcome to MicroWeb!')

@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({'status': 'running', 'ip': wifi.get_ip()})

@app.route('/api/echo', methods=['POST'])
def echo(req):
    data = req.form
    return app.json_response({'received': data})

@app.route('/submit', methods=['GET', 'POST'])
def submit_form(req):
    if req.method == 'POST':
        return app.render_template('result.html', data=str(req.form), method='POST')
    else:
        return app.render_template('form.html')

app.add_static('/style.css', 'style.css')


app.run()
```

**Explanation**:
- Combines template rendering (`/`, `/submit`), JSON responses (`/api/status`, `/api/echo`), and static file serving (`/style.css`).
- The `/submit` route uses `result.html` (as shown above) to display form data and the HTTP method.
- Upload and run with:
  ```bash
  microweb run app.py --port COM10 --static static/
  ```
- Access at `http://192.168.4.1` (or the ESP32’s IP address).

### **12. Testing Your Application**
- **Browser**: Open `http://<ESP32-IP>/` (e.g., `http://192.168.4.1`) to access the web server.
- **curl**:
  ```bash
  curl http://192.168.4.1/api/status
  curl -X POST -d 'username=Alice' http://192.168.4.1/api/echo
  curl -X POST -d 'username=Alice' http://192.168.4.1/submit
  ```
- **CLI Logs**: Monitor logs with `debug=True` to debug issues.
- **Template Testing**: Submit a form via `http://192.168.4.1/submit` to see the `result.html` output, styled with `style.css`.

### **13. Next Steps**
- Explore the portfolio demo (`tests/portfolio/`) for a full-featured web app example.
- Use `microweb create --path my_app` to generate a template project.
- Add boot script support with `microweb run app.py --add-boot --port COM10` for auto-running on power-up.
- Check the [CLI Tool Usage Examples](#cli-tool-usage-examples) for advanced commands.

---

### Feature Updates

- Improvsed CLI usability and error messages.
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

![img2](/src/uml2.svg)

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

## Contributing

Fork and submit pull requests at [https://github.com/ishanoshada/microweb](https://github.com/ishanoshada/microweb).

---

**Repository Views** ![Views](https://profile-counter.glitch.me/microweb/count.svg)
