"""
Auth service - handles login, registration, and password hashing.
"""

import hashlib

from src.repositories.user_repository import UserRepository
from src.models.user import Customer


class AuthService:
    """Handles user login and registration."""

    def __init__(self):
        self._user_repo = UserRepository()

    def login(self, username, password):
        """Try to log in. Returns User if valid, None if not."""
        user = self._user_repo.find_by_username(username)
        if user is None:
            return None

        # Compare the hash of the entered password against the stored hash
        if self._hash_password(password) == user.password_hash:
            return user
        return None

    def register_customer(self, username, password, full_name, email, phone=None):
        """Register a new customer. Raises ValueError if username is taken."""
        if self._user_repo.username_exists(username):
            raise ValueError(f"Username '{username}' is already taken")

        customer = Customer(
            user_id=None,
            username=username,
            password_hash=self._hash_password(password),
            full_name=full_name,
            email=email,
            phone=phone,
            loyalty_points=0,
        )

        self._user_repo.save_customer(customer)
        return customer

    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()


# test
if __name__ == "__main__":
    print("Testing AuthService\n")

    auth = AuthService()

    # Login with seeded admin
    user = auth.login("admin", "admin123")
    print(f"Admin login: {user.full_name if user else 'FAILED'}")

    # Wrong password
    user = auth.login("admin", "wrongpass")
    print(f"Wrong password: {user}")

    # Unknown user
    user = auth.login("nobody", "anything")
    print(f"Unknown user: {user}")

    # Register or skip if exists
    try:
        new_customer = auth.register_customer(
            username="alice", password="alice123",
            full_name="Alice S", email="alice@gmail.com",
        )
        print(f"Registered: {new_customer.full_name}")
    except ValueError as e:
        print(f"Skipped registration: {e}")

    # Try duplicate
    try:
        auth.register_customer(username="alice", password="other",
                               full_name="Another", email="other@gmail.com")
    except ValueError as e:
        print(f"Duplicate blocked: {e}")

    # Login as alice
    alice = auth.login("alice", "alice123")
    print(f"Alice login: {alice.full_name if alice else 'FAILED'}")