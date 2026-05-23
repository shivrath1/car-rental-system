"""
Booking class - represents a car rental booking.
Links a user, a car, dates, and the price breakdown.
"""

from datetime import date, datetime


class Booking:
    """A car rental booking."""

    def __init__(self, booking_id, user, car, start_date, end_date,
                 price_breakdown, status="confirmed", payment_status="pending",
                 notes=None, created_at=None, updated_at=None):

        if end_date < start_date:
            raise ValueError("End date can't be before start date")

        self._booking_id = booking_id
        self._user = user
        self._car = car
        self._start_date = start_date
        self._end_date = end_date
        self._price_breakdown = price_breakdown
        self._status = status
        self._payment_status = payment_status
        self._notes = notes

        now = datetime.now()
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    # Getters
    @property
    def booking_id(self):
        return self._booking_id

    @property
    def user(self):
        return self._user

    @property
    def car(self):
        return self._car

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def price_breakdown(self):
        return self._price_breakdown

    @property
    def status(self):
        return self._status

    @property
    def payment_status(self):
        return self._payment_status

    @property
    def notes(self):
        return self._notes

    @property
    def total_amount(self):
        return self._price_breakdown.total_amount

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    def set_booking_id(self, booking_id):
        """Set the booking ID after saving to the database."""
        self._booking_id = booking_id
        self._price_breakdown.set_booking_id(booking_id)

    def calculate_duration(self):
        """returns number of days for this booking."""
        return (self._end_date - self._start_date).days + 1

    def get_summary(self):
        """summary of the booking for display."""
        return (
            f"Booking #{self._booking_id or 'NEW'}\n"
            f"  Customer:   {self._user.full_name} ({self._user.role})\n"
            f"  Car:        {self._car.get_display_name()}\n"
            f"  Dates:      {self._start_date} to {self._end_date} "
            f"({self.calculate_duration()} days)\n"
            f"  Status:     {self._status}\n"
            f"  Payment:    {self._payment_status}\n"
            f"  Total:      ${self.total_amount:.2f}"
        )

    def __repr__(self):
        return (f"<Booking id={self._booking_id} "
                f"{self._start_date} to {self._end_date} status={self._status}>")


# test
if __name__ == "__main__":
    from src.models.user import Customer
    from src.models.car import Car
    from src.models.price_breakdown import PriceBreakdown

    print("Testing Booking\n")

    customer = Customer(
        user_id=10, username="alice", password_hash="hashed",
        full_name="Alice Smith", email="alice@example.com",
    )
    car = Car(car_id=5, make="Toyota", model="Camry", year=2022,
              mileage=15000.0, base_rate=80.0)
    breakdown = PriceBreakdown(base_rate=80.0, duration_days=3,
                               loyalty_discount=5.0)

    booking = Booking(
        booking_id=None, user=customer, car=car,
        start_date=date(2026, 12, 1), end_date=date(2026, 12, 3),
        price_breakdown=breakdown,
    )

    print(booking.get_summary())
    print(f"\nDuration: {booking.calculate_duration()} days")
    print(f"Total: ${booking.total_amount}")

    # Test ID propagation
    booking.set_booking_id(101)
    print(f"\nBooking ID set to: {booking.booking_id}")
    print(f"Breakdown booking_id linked: {booking.price_breakdown.booking_id}")

    # Test validation
    try:
        Booking(booking_id=None, user=customer, car=car,
                start_date=date(2026, 12, 10), end_date=date(2026, 12, 5),
                price_breakdown=breakdown)
    except ValueError as e:
        print(f"\nBad dates blocked: {e}")