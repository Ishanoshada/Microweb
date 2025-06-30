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
