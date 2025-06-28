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

app.run()


