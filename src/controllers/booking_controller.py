"""
Booking controller - coordinate services and repositories for the booking flow.
"""

from datetime import date

from src.repositories.user_repository import UserRepository
from src.repositories.car_repository import CarRepository
from src.repositories.booking_repository import BookingRepository

from src.services.auth_service import AuthService
from src.services.pricing_engine import PricingEngine
from src.services.payment_service import PaymentService
from src.services.email_service import EmailService

from src.models.user import GuestUser
from src.models.car import Car
from src.models.booking import Booking


# Booking rules
MIN_RENTAL_DAYS = 1
MAX_RENTAL_DAYS = 30


class BookingController:
    """Controller for the booking flow."""

    def __init__(self):
        self._user_repo = UserRepository()
        self._car_repo = CarRepository()
        self._booking_repo = BookingRepository()

        self._auth = AuthService()
        self._pricing = PricingEngine()
        self._payment = PaymentService()
        self._email = EmailService()

    # Authentication

    def login(self, username, password):
        """Try to log in. Returns User or None."""
        return self._auth.login(username, password)

    def register_customer(self, username, password, full_name, email, phone=None):
        """Register a new customer."""
        return self._auth.register_customer(username, password, full_name, email, phone)

    # Browsing

    def get_available_cars(self):
        """Return all cars currently available for rental."""
        return self._car_repo.find_available()

    def get_car_by_id(self, car_id):
        """Find a car by ID. Returns Car or None."""
        return self._car_repo.find_by_id(car_id)

    # Quote

    def calculate_quote(self, car_id, start_date, end_date, user=None):
        """Calculate a price quote. Returns a dict with success status."""
        car = self._car_repo.find_by_id(car_id)
        if car is None or not car.is_active:
            return {"success": False, "error": "Car not found", "breakdown": None}
        if not car.is_available:
            return {"success": False, "error": "Car is not available", "breakdown": None}

        date_error = self._validate_dates(start_date, end_date)
        if date_error:
            return {"success": False, "error": date_error, "breakdown": None}

        # Look up loyalty count for registered customers
        rental_count = 0
        if user is not None and user.role == "customer":
            rental_count = self._booking_repo.get_customer_rental_count(user.user_id)

        breakdown = self._pricing.calculate_price(
            base_rate=car.base_rate,
            start_date=start_date,
            end_date=end_date,
            rental_count=rental_count,
        )

        return {"success": True, "error": None, "car": car, "breakdown": breakdown}

    # Guest 

    def create_guest_user(self, full_name, email, phone):
        """Save a guest user before they book."""
        guest = GuestUser(user_id=None, full_name=full_name, email=email, phone=phone)
        self._user_repo.save_guest(guest)
        return guest

    # Booking confirmation

    def confirm_booking(self, user, car, start_date, end_date, breakdown, card_info):
        """Process payment and save the booking. Returns a result dict."""
        # Process payment
        payment_result = self._payment.charge(breakdown.total_amount, card_info)
        if not payment_result["success"]:
            return {
                "success": False,
                "error": f"Payment failed: {payment_result['reason']}",
                "booking": None,
            }

        # Save the booking
        booking = Booking(
            booking_id=None,
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            price_breakdown=breakdown,
            status="confirmed",
            payment_status="paid",
            notes=f"Payment ref: {payment_result['transaction_ref']}",
        )
        self._booking_repo.save(booking)

        # Mark car unavailable and send email
        self._car_repo.update_availability(car.car_id, False)
        self._email.send_booking_confirmation(user.email, user.full_name, booking)

        return {"success": True, "error": None, "booking": booking}

    # Bookings

    def get_user_bookings(self, user_id):
        """Get all bookings for a specific user."""
        return self._booking_repo.find_by_user(user_id)

    def cancel_booking(self, booking_id, requesting_user):
        """Cancel a booking. Full refund if not yet started."""
        booking = self._booking_repo.find_by_id(booking_id)
        if booking is None:
            return {"success": False, "error": "Booking not found", "refund": 0}

        if booking.user.user_id != requesting_user.user_id:
            return {"success": False, "error": "Not your booking", "refund": 0}

        if booking.status != "confirmed":
            return {
                "success": False,
                "error": f"Cannot cancel a {booking.status} booking",
                "refund": 0,
            }

        # Full refund if cancelling before the rental starts
        refund_amount = 0.0
        if booking.start_date > date.today():
            refund_amount = booking.total_amount
            self._payment.refund(refund_amount, "original_transaction")

        self._booking_repo.update_status(
            booking_id, "cancelled",
            notes=f"Cancelled by user. Refund: ${refund_amount:.2f}"
        )
        self._car_repo.update_availability(booking.car.car_id, True)

        self._email.send_cancellation_notice(
            booking.user.email, booking.user.full_name, booking, refund_amount
        )

        return {"success": True, "error": None, "refund": refund_amount}

    # Admin: cars 

    def admin_add_car(self, make, model, year, mileage, base_rate):
        """Admin: add a new car."""
        car = Car(car_id=None, make=make, model=model, year=year,
                  mileage=mileage, base_rate=base_rate)
        self._car_repo.save(car)
        return car

    def admin_update_car(self, car_id, **updates):
        """Admin: update a car's rate or mileage."""
        car = self._car_repo.find_by_id(car_id)
        if car is None:
            return {"success": False, "error": "Car not found"}

        if "base_rate" in updates:
            car.update_rate(updates["base_rate"])
        if "mileage" in updates:
            car.update_mileage(updates["mileage"])

        self._car_repo.update(car)
        return {"success": True, "car": car}

    def admin_delete_car(self, car_id):
        """Admin: soft-delete a car. Blocked if it has active bookings."""
        if self._booking_repo.has_active_bookings_for_car(car_id):
            return {"success": False, "error": "Cannot delete - car has active bookings"}

        car = self._car_repo.find_by_id(car_id)
        if car is None:
            return {"success": False, "error": "Car not found"}

        self._car_repo.soft_delete(car_id)
        return {"success": True}

    # Admin: bookings 

    def admin_get_all_bookings(self):
        """Admin: view all bookings in the system."""
        return self._booking_repo.find_all()

    def admin_override_booking(self, booking_id, admin_note):
        """Admin: override a confirmed booking with full refund."""
        booking = self._booking_repo.find_by_id(booking_id)
        if booking is None:
            return {"success": False, "error": "Booking not found"}

        if booking.status != "confirmed":
            return {"success": False, "error": f"Cannot override a {booking.status} booking"}

        refund_amount = booking.total_amount
        self._payment.refund(refund_amount, "original_transaction")

        self._booking_repo.update_status(
            booking_id, "overridden",
            notes=f"Admin override: {admin_note}. Refund: ${refund_amount:.2f}"
        )
        self._car_repo.update_availability(booking.car.car_id, True)

        self._email.send_override_notice(
            booking.user.email, booking.user.full_name, booking, admin_note
        )

        return {"success": True, "refund": refund_amount}

    # Helpers 

    def _validate_dates(self, start_date, end_date):
        """Check that the dates make sense. Returns error message or None."""
        if start_date < date.today():
            return "Start date cannot be in the past"
        if end_date < start_date:
            return "End date must be after start date"

        duration = (end_date - start_date).days + 1
        if duration < MIN_RENTAL_DAYS:
            return f"Minimum rental is {MIN_RENTAL_DAYS} day(s)"
        if duration > MAX_RENTAL_DAYS:
            return f"Maximum rental is {MAX_RENTAL_DAYS} days"
        return None


# test
if __name__ == "__main__":
    from datetime import timedelta

    print("Testing BookingController\n")

    controller = BookingController()

    # Setup - admin and a car
    admin = controller.login("admin", "admin123")
    new_car = controller.admin_add_car(make="Mazda", model="3", year=2024,
                                        mileage=5000.0, base_rate=75.0)
    print(f"Added car: {new_car.get_display_name()} (ID {new_car.car_id})")

    # Make sure alice exists for the test
    alice = controller.login("alice", "alice123")
    if alice is None:
        alice = controller.register_customer(
            username="alice", password="alice123",
            full_name="Alice Smith", email="alice@example.com",
        )
        print("(Created alice for testing)")

    # Customer books the car
    start = date.today() + timedelta(days=10)
    end = start + timedelta(days=2)

    quote = controller.calculate_quote(new_car.car_id, start, end, user=alice)
    result = controller.confirm_booking(
        user=alice, car=quote["car"], start_date=start, end_date=end,
        breakdown=quote["breakdown"],
        card_info={"card_number": "4111111111111111", "expiry": "12/27", "cvv": "123"},
    )

    if result["success"]:
        booking = result["booking"]
        print(f"Booked: ID {booking.booking_id}, total ${booking.total_amount}")

        # Cancel it
        cancel = controller.cancel_booking(booking.booking_id, alice)
        print(f"Cancelled: refund ${cancel['refund']:.2f}")

        # Try cancelling again - should fail
        again = controller.cancel_booking(booking.booking_id, alice)
        print(f"Second cancel blocked: {again['error']}")

    # Admin updates the car rate
    update = controller.admin_update_car(new_car.car_id, base_rate=85.0)
    if update["success"]:
        print(f"Rate updated to ${update['car'].base_rate}/day")

    # Show admin's view of all bookings
    all_bookings = controller.admin_get_all_bookings()
    print(f"\nTotal bookings: {len(all_bookings)}")
    for b in all_bookings[:5]:
        print(f"  #{b.booking_id}: {b.user.full_name} -> "
              f"{b.car.get_display_name()} [{b.status}]")