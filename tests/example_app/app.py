import wifi
from microweb import MicroWeb

# Initialize MicroWeb application with debug mode and Wi-Fi access point configuration
app = MicroWeb(debug=True, ap={"ssid": "MyESP32", "password": "mypassword"})

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

# Register static files
app.add_static('/style.css', 'style.css')
app.add_static('/script.js', 'script.js')


app.run()
