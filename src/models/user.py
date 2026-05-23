"""
User classes for the Car Rental System.
Includes a base User class and three child classes: Customer, Admin, GuestUser.
"""


class User:
    """Base class for all user types. Holds shared user details."""

    def __init__(self, user_id, full_name, email, phone=None,
                 role="", username=None, password_hash=None, is_active=True):
        self._user_id = user_id
        self._full_name = full_name
        self._email = email
        self._phone = phone
        self._role = role
        self._username = username
        self._password_hash = password_hash
        self._is_active = is_active

    # Getters
    @property
    def user_id(self):
        return self._user_id

    @property
    def full_name(self):
        return self._full_name

    @property
    def email(self):
        return self._email

    @property
    def phone(self):
        return self._phone

    @property
    def role(self):
        return self._role

    @property
    def username(self):
        return self._username

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def is_active(self):
        return self._is_active

    def set_user_id(self, user_id):
        """Set the ID after the user is saved to the database."""
        self._user_id = user_id

    def get_dashboard(self):
        """Return a simple dashboard message. Child classes override this."""
        return f"Dashboard for {self._full_name}"

    def __repr__(self):
        return f"<{type(self).__name__} id={self._user_id} name='{self._full_name}'>"


class Customer(User):
    """A registered customer who can log in and book cars."""

    def __init__(self, user_id, username, password_hash, full_name, email,
                 phone=None, loyalty_points=0, is_active=True):
        super().__init__(
            user_id=user_id,
            full_name=full_name,
            email=email,
            phone=phone,
            role="customer",
            username=username,
            password_hash=password_hash,
            is_active=is_active,
        )
        self._loyalty_points = loyalty_points

    @property
    def loyalty_points(self):
        return self._loyalty_points

    def add_loyalty_points(self, points):
        """Add points to the customer's loyalty balance."""
        if points < 0:
            raise ValueError("Points must be positive")
        self._loyalty_points += points

    def get_dashboard(self):
        return (
            f"Customer Dashboard - {self._full_name}\n"
            f"  - Browse and book cars\n"
            f"  - View booking history\n"
            f"  - Modify or cancel bookings\n"
            f"  - Loyalty points: {self._loyalty_points}"
        )


class Admin(User):
    """An admin who can manage cars and bookings."""

    def __init__(self, user_id, username, password_hash, full_name, email,
                 phone=None, admin_level="regular", is_active=True):
        super().__init__(
            user_id=user_id,
            full_name=full_name,
            email=email,
            phone=phone,
            role="admin",
            username=username,
            password_hash=password_hash,
            is_active=is_active,
        )
        self._admin_level = admin_level

    @property
    def admin_level(self):
        return self._admin_level

    def get_dashboard(self):
        return (
            f"Admin Dashboard - {self._full_name} ({self._admin_level})\n"
            f"  - Add / update / delete cars\n"
            f"  - View all bookings\n"
            f"  - Override booking decisions"
        )


class GuestUser(User):
    """A guest who books without creating an account."""

    def __init__(self, user_id, full_name, email, phone=None, is_active=True):
        super().__init__(
            user_id=user_id,
            full_name=full_name,
            email=email,
            phone=phone,
            role="guest",
            username=None,
            password_hash=None,
            is_active=is_active,
        )

    def get_dashboard(self):
        return (
            f"Guest Checkout - {self._full_name}\n"
            f"  - One-time booking\n"
            f"  - Confirmation will be sent to: {self._email}"
        )


# test
if __name__ == "__main__":
    print("Testing User classes\n")

    customer = Customer(
        user_id=1, username="alice", password_hash="abc123",
        full_name="Alice Smith", email="alice@example.com",
        loyalty_points=250,
    )

    admin = Admin(
        user_id=2, username="bob", password_hash="xyz789",
        full_name="Bob Manager", email="bob@carrental.com",
        admin_level="super",
    )

    guest = GuestUser(
        user_id=3, full_name="Charlie Walker", email="charlie@example.com",
    )

    print(customer.get_dashboard())
    print()
    print(admin.get_dashboard())
    print()
    print(guest.get_dashboard())
    print()

    for user in [customer, admin, guest]:
        print(f"{type(user).__name__}: {user.role}")