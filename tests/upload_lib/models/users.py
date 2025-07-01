# models/users.py
class User:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    
    def get_all(self):
        return self.users
    
    def get_by_id(self, user_id):
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def add_user(self, name, email):
        new_id = max([user["id"] for user in self.users], default=0) + 1
        new_user = {"id": new_id, "name": name, "email": email}
        self.users.append(new_user)
        return new_user
