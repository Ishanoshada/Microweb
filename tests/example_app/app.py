import wifi
from microweb import MicroWeb

# Define a simple User model to store and retrieve user data
class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email
        }

# Initialize MicroWeb application with debug mode and Wi-Fi access point configuration
app = MicroWeb(debug=True, ap={"ssid": "MyESP32", "password": "mypassword"})

# Define route for the root URL, rendering the index.html template with a welcome message
@app.route('/')
def home(req):
    return app.render_template('index.html', message="Welcome to MicroWeb API!")

# Define API route to return server status and IP address as JSON
@app.route('/api/status', methods=['GET'])
def status(req):
    return app.json_response({"status": "running", "ip": wifi.get_ip()})

# Define API route to get user data using the User model
@app.route('/api/user/<id>')
def get_user(req, match):
    # Extract ID from URL parameter, default to "Anonymous" if not provided
    id = match.group(1) if match else "Anonymous"
    # Create a sample user instance (in a real app, this could come from a database)
    user = User(user_id=id, name=f"User {id}", email=f"user{id}@example.com")
    return app.json_response(user.to_dict())

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
#         data = req.json()  # Get JSON data from POST body
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

# Register static file style.css to be served at /style.css
# app.add_static('/style.css', 'style.css')

# Start the MicroWeb server
app.run()
