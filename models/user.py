class User:
    def __init__(self, username, password_hash, role):
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def check_password(self, plain_password):
        """
        In a real app, you would hash 'plain_password' and compare.
        For this prototype, we might compare directly if not using hashing yet.
        """
        return self.password_hash == plain_password

    def is_admin(self):
        return self.role.lower() == "admin"

    def __str__(self):
        return f"User(username='{self.username}', role='{self.role}')"