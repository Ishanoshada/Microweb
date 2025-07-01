from microweb import MicroWeb
import some_lib
from users import User
from products import Product

# Initialize MicroWeb with debug mode and Wi-Fi access point
app = MicroWeb(debug=True, ap={"ssid": "TestESP32", "password": "test1234"})

# Register library and model files
app.lib_add("some_lib.py")
app.lib_add("models/users.py")
app.lib_add("models/products.py")

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
        return app.json_response(user)
    return app.json_response({"error": "User not found"}, status=404)

@app.route('/product/<id>')
def get_product(req, match):
    product_id = int(match.group(1)) if match else 0
    product = products.get_by_id(product_id)
    if product:
        return app.json_response(product)
    return app.json_response({"error": "Product not found"}, status=404)

@app.route('/add_user', methods=['POST'])
def add_user(req):
    name = req.form.get('name', '')
    email = req.form.get('email', '')
    if name and email:
        new_user = users.add_user(name, email)
        return app.json_response({"message": "User added", "user": new_user})
    return app.json_response({"error": "Invalid input"}, status=400)

@app.route('/add_product', methods=['POST'])
def add_product(req):
    name = req.form.get('name', '')
    price = float(req.form.get('price', 0)) if req.form.get('price', '').replace('.', '', 1).isdigit() else 0
    if name and price > 0:
        new_product = products.add_product(name, price)
        return app.json_response({"message": "Product added", "product": new_product})
    return app.json_response({"error": "Invalid input"}, status=400)

# Register static files
app.add_static('/style.css', 'style.css')

app.run()