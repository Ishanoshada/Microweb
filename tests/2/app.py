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