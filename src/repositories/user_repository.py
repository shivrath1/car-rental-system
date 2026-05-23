"""
User repository - handles database queries for users.
"""

from src.repositories.base_repository import BaseRepository
from src.models.user import Customer, Admin, GuestUser


class UserRepository(BaseRepository):
    """Database operations for users."""

    def find_by_username(self, username):
        """Find a user by username. Returns User or None."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_user(row)

    def find_by_id(self, user_id):
        """Find a user by ID. Returns User or None."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_user(row)

    def username_exists(self, username):
        """Check if a username is already taken."""
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def save_customer(self, customer):
        """Insert a new customer. Returns the new user_id."""
        cursor = self._get_cursor()
        cursor.execute(
            """INSERT INTO users
               (username, password_hash, full_name, email, phone, role, loyalty_points)
               VALUES (?, ?, ?, ?, ?, 'customer', ?)""",
            (
                customer.username,
                customer.password_hash,
                customer.full_name,
                customer.email,
                customer.phone,
                customer.loyalty_points,
            ),
        )
        self._commit()
        new_id = cursor.lastrowid
        customer.set_user_id(new_id)
        return new_id

    def save_guest(self, guest):
        """Insert a new guest user. Returns the new user_id."""
        cursor = self._get_cursor()
        cursor.execute(
            """INSERT INTO users (full_name, email, phone, role)
               VALUES (?, ?, ?, 'guest')""",
            (guest.full_name, guest.email, guest.phone),
        )
        self._commit()
        new_id = cursor.lastrowid
        guest.set_user_id(new_id)
        return new_id

    def _row_to_user(self, row):
        """Convert a database row into the right User subclass based on role."""
        role = row["role"]

        if role == "customer":
            return Customer(
                user_id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                full_name=row["full_name"],
                email=row["email"],
                phone=row["phone"],
                loyalty_points=row["loyalty_points"] or 0,
                is_active=bool(row["is_active"]),
            )

        if role == "admin":
            return Admin(
                user_id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                full_name=row["full_name"],
                email=row["email"],
                phone=row["phone"],
                admin_level=row["admin_level"] or "regular",
                is_active=bool(row["is_active"]),
            )

        # Guest user
        return GuestUser(
            user_id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            is_active=bool(row["is_active"]),
        )


# test
if __name__ == "__main__":
    print("Testing UserRepository\n")

    repo = UserRepository()

    # Find the seeded admin
    admin = repo.find_by_username("admin")
    if admin:
        print(f"Found admin: {admin.full_name}")
        print(f"Type: {type(admin).__name__}")

    # Look up someone who doesn't exist
    missing = repo.find_by_username("nobody")
    print(f"Missing user returns: {missing}")

    # Check if a username is taken
    print(f"Is 'admin' taken? {repo.username_exists('admin')}")