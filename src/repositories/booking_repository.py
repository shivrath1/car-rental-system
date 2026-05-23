"""
Booking repository - handles database queries for bookings and price breakdowns.
"""

from datetime import date, datetime

from src.repositories.base_repository import BaseRepository
from src.repositories.user_repository import UserRepository
from src.repositories.car_repository import CarRepository
from src.models.booking import Booking
from src.models.price_breakdown import PriceBreakdown


class BookingRepository(BaseRepository):
    """db operations for bookings."""

    def __init__(self):
        super().__init__()
        self._user_repo = UserRepository()
        self._car_repo = CarRepository()

    def save(self, booking):
        """Save a new booking and its price breakdown. Returns the new booking_id."""
        cursor = self._get_cursor()

        # Insert booking
        cursor.execute(
            """INSERT INTO bookings
               (user_id, car_id, start_date, end_date, duration_days,
                status, total_amount, payment_status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                booking.user.user_id,
                booking.car.car_id,
                booking.start_date.isoformat(),
                booking.end_date.isoformat(),
                booking.calculate_duration(),
                booking.status,
                booking.total_amount,
                booking.payment_status,
                booking.notes,
            ),
        )
        booking_id = cursor.lastrowid
        booking.set_booking_id(booking_id)

        # Insert the linked price breakdown
        breakdown = booking.price_breakdown
        cursor.execute(
            """INSERT INTO price_breakdowns
               (booking_id, base_rate, duration_days,
                duration_discount, loyalty_discount, seasonal_charge,
                lead_time_charge, final_rate, total_amount)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                booking_id,
                breakdown.base_rate,
                breakdown.duration_days,
                breakdown.duration_discount,
                breakdown.loyalty_discount,
                breakdown.seasonal_charge,
                breakdown.lead_time_charge,
                breakdown.final_rate,
                breakdown.total_amount,
            ),
        )
        self._commit()
        return booking_id

    def find_by_id(self, booking_id):
        """Find a booking by ID. Returns Booking or None."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_booking(row)

    def find_by_user(self, user_id):
        """Get all bookings for a specific user."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM bookings WHERE user_id = ? ORDER BY start_date DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        return [self._row_to_booking(row) for row in rows]

    def find_all(self):
        """Get all bookings for admin view."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM bookings ORDER BY start_date DESC")
        rows = cursor.fetchall()
        return [self._row_to_booking(row) for row in rows]

    def get_customer_rental_count(self, user_id):
        """Count how many confirmed/completed bookings a customer has."""
        cursor = self._get_cursor()
        cursor.execute(
            """SELECT COUNT(*) as count FROM bookings
               WHERE user_id = ? AND status IN ('confirmed', 'completed')""",
            (user_id,),
        )
        row = cursor.fetchone()
        return row["count"] if row else 0

    def update_status(self, booking_id, new_status, notes=None):
        """Update a booking's status."""
        cursor = self._get_cursor()
        cursor.execute(
            """UPDATE bookings
               SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (new_status, notes, booking_id),
        )
        self._commit()

    def has_active_bookings_for_car(self, car_id):
        """Check if a car has any future confirmed bookings."""
        cursor = self._get_cursor()
        cursor.execute(
            """SELECT COUNT(*) as count FROM bookings
               WHERE car_id = ? AND status = 'confirmed'
               AND end_date >= date('now')""",
            (car_id,),
        )
        row = cursor.fetchone()
        return row["count"] > 0

    def _row_to_booking(self, row):
        """Convert a booking row into a Booking object with user, car, and breakdown."""
        user = self._user_repo.find_by_id(row["user_id"])
        car = self._car_repo.find_by_id(row["car_id"])
        breakdown = self._load_breakdown(row["id"])

        start_date = date.fromisoformat(row["start_date"])
        end_date = date.fromisoformat(row["end_date"])

        created_at = datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        updated_at = datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None

        return Booking(
            booking_id=row["id"],
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            price_breakdown=breakdown,
            status=row["status"],
            payment_status=row["payment_status"] or "pending",
            notes=row["notes"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def _load_breakdown(self, booking_id):
        """Load the price breakdown for a booking."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM price_breakdowns WHERE booking_id = ?",
            (booking_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return PriceBreakdown(
            breakdown_id=row["id"],
            booking_id=row["booking_id"],
            base_rate=row["base_rate"],
            duration_days=row["duration_days"],
            duration_discount=row["duration_discount"],
            loyalty_discount=row["loyalty_discount"],
            seasonal_charge=row["seasonal_charge"],
            lead_time_charge=row["lead_time_charge"],
        )


# test
if __name__ == "__main__":
    print("Testing BookingRepository\n")

    repo = BookingRepository()

    # Find an existing user and car for the test
    user = repo._user_repo.find_by_username("admin")
    car = repo._car_repo.find_by_id(1)
    print(f"Using user: {user.full_name}")
    print(f"Using car:  {car.get_display_name()}\n")

    # Create a booking
    breakdown = PriceBreakdown(base_rate=80.0, duration_days=3,
                               loyalty_discount=5.0)
    booking = Booking(
        booking_id=None, user=user, car=car,
        start_date=date(2026, 12, 1), end_date=date(2026, 12, 3),
        price_breakdown=breakdown,
    )
    new_id = repo.save(booking)
    print(f"Saved booking ID: {new_id}")

    # Load it back
    loaded = repo.find_by_id(new_id)
    print(f"Loaded back: ${loaded.total_amount} total")

    # Get user's bookings
    user_bookings = repo.find_by_user(user.user_id)
    print(f"User has {len(user_bookings)} bookings")

    # Customer rental count
    count = repo.get_customer_rental_count(user.user_id)
    print(f"Rental count: {count}")

    # Update status
    repo.update_status(new_id, "cancelled", notes="Test cancellation")
    print(f"Status after update: {repo.find_by_id(new_id).status}")