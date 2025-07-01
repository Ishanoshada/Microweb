# models/products.py
class Product:
    def __init__(self):
        self.products = [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Phone", "price": 499.99}
        ]
    
    def get_all(self):
        return self.products
    
    def get_by_id(self, product_id):
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
    
    def add_product(self, name, price):
        new_id = max([product["id"] for product in self.products], default=0) + 1
        new_product = {"id": new_id, "name": name, "price": price}
        self.products.append(new_product)
        return new_product
