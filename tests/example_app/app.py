import wifi
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


