from microweb import MicroWeb

app = MicroWeb(ap={'ssid': 'MyWiFi', 'password': 'MyPassword'}, debug=True)



@app.route('/')
def index(req):
       return app.render_template('index.html', message="Welcome to MicroWeb API!")

    # Route with parameter
@app.route('/greet/<name>')
def greet(req, match):
        name = match.group(1) if match else "Anonymous"
        return {"message": f"Hello, {name}!", "status": "success"}

    # JSON API route
@app.route('/api/hello')
def api_hello(req):
        return {"message": "Hello from API!", "status": "success"}
    
# POST route
@app.route('/submit', methods=['GET', 'POST'])
def submit_form(req):
        if req.method == 'POST':
            return app.render_template('result.html', 
                                     data=str(req.form), 
                                     method="POST")
        else:
            return app.render_template('form.html')

# app.add_static('/', 'index.html')
    # Add static file
#app.add_static('/submit', 'form.html')
app.add_static('/style.css', 'style.css')
    
    # Start the server
app.run()