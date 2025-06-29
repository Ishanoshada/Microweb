# MicroWeb

MicroWeb is a lightweight web server framework for MicroPython on the ESP32, designed for efficient development of web-based applications. It supports dynamic routing, Wi-Fi configuration (access point or station mode), query parameter and POST request handling, JSON responses, static file serving, and a powerful template engine with for loops and if conditionals. The package includes a robust CLI for flashing MicroPython, uploading files, and running custom applications on the ESP32.



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
    - [Creating an Example Application](#creating-an-example-application)
    - [Flashing the ESP32](#flashing-the-esp32)
    - [Running a Custom Application](#running-a-custom-application)
- [Example Usage](#example-usage)
    - [Minimal Example (`tests/2/app.py`)](#minimal-example-tests2apppy)
    - [Static Files and Templates Example (`tests/1/app.py`)](#static-files-and-templates-example-tests1apppy)
    - [Portfolio Demo (`tests/portfolio/`)](#portfolio-demo-testsportfolio)
    - [For Loop Example](#for-loop-example-testsfor_loops)
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

#### Options:
- `--erase`: Erase the entire flash memory before flashing firmware.
- `--esp8266`: Flash ESP8266 firmware instead of the default ESP32.
- `--firmware firmware.bin`: Use a custom `.bin` firmware file, overriding the default firmware for ESP32 or ESP8266.

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

**Example Static File (`tests/for_loops/static/style.css`)**:

```css
body {
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
- **Output**:
  - For `/`: Displays a styled list of projects with titles and descriptions.
  - For `/empty`: Displays "No projects found" with the greeting.
- **Best Practices**:
  - Ensure `index.html` and `style.css` are in the `static/` directory.
  - Test both routes to verify conditional rendering.
  - Use `debug=True` to log any template or file-serving errors.


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
