# Note: This code is a simplified example and may not include all features of the original app.
# Make sure to adapt the routes and functionality as needed for your specific use case.
# To run this code, ensure you have the `microweb` package installed and run it on a compatible MicroPython device.
"""
first run the command:
```bash
microweb flash --port COM10
```
Then run the app with:
```bash
microweb run app.py --port COM10
```

"""

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
    data = req.form  # Get JSON data from POST body
    return app.json_response({"received": data})

# Example of a route that allows both GET and POST
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
            return app.render_template('result.html', 
                                     data=str(req.form), 
                                     method="POST")
        else:
            return app.render_template('form.html')
        
# Add static files
app.add_static('/style.css', 'style.css')
app.run()
