"""
Email service - simulates sending emails for the assignment.
"""


class EmailService:
    """Mock email service"""

    def send_booking_confirmation(self, recipient_email, recipient_name, booking):
        """Send a booking confirmation email."""
        subject = f"Booking confirmed - #{booking.booking_id}"
        body = (
            f"Hi {recipient_name},\n\n"
            f"Your booking has been confirmed!\n\n"
            f"Car:        {booking.car.get_display_name()}\n"
            f"Dates:      {booking.start_date} to {booking.end_date}\n"
            f"Total:      ${booking.total_amount:.2f}\n\n"
            f"Thank you for choosing us!"
        )
        return self._send(recipient_email, subject, body)

    def send_cancellation_notice(self, recipient_email, recipient_name, booking, refund_amount=0):
        """Send a booking cancellation email."""
        subject = f"Booking cancelled - #{booking.booking_id}"
        refund_line = (
            f"A refund of ${refund_amount:.2f} will be processed.\n\n"
            if refund_amount > 0
            else "No refund applicable for this cancellation.\n\n"
        )
        body = (
            f"Hi {recipient_name},\n\n"
            f"Your booking for {booking.car.get_display_name()} has been cancelled.\n"
            f"{refund_line}"
            f"If this was a mistake, please contact us."
        )
        return self._send(recipient_email, subject, body)

    def send_override_notice(self, recipient_email, recipient_name, booking, reason):
        """Send an admin override notification."""
        subject = f"Important: Booking #{booking.booking_id} has been changed"
        body = (
            f"Hi {recipient_name},\n\n"
            f"Your booking for {booking.car.get_display_name()} has been "
            f"modified by our admin team.\n\n"
            f"Reason: {reason}\n\n"
            f"Please contact us for any questions."
        )
        return self._send(recipient_email, subject, body)

    def _send(self, recipient, subject, body):
        """Print the email to the console (mock version)."""
        print("\n  [EmailService] Sending email")
        print(f"  To:      {recipient}")
        print(f"  Subject: {subject}")
        print(f"  Body:")
        for line in body.split("\n"):
            print(f"    {line}")
        return True


# Test
if __name__ == "__main__":
    from datetime import date
    from src.models.user import Customer
    from src.models.car import Car
    from src.models.booking import Booking
    from src.models.price_breakdown import PriceBreakdown

    print("Testing EmailService\n")

    # Build a test booking
    user = Customer(user_id=1, username="alice", password_hash="hash",
                    full_name="Alice Smith", email="alice@example.com")
    car = Car(car_id=1, make="Toyota", model="Camry", year=2022,
              mileage=15000, base_rate=80)
    breakdown = PriceBreakdown(base_rate=80, duration_days=3)
    booking = Booking(
        booking_id=42, user=user, car=car,
        start_date=date(2026, 12, 1), end_date=date(2026, 12, 3),
        price_breakdown=breakdown,
    )

    email = EmailService()

    # Send each type of email
    email.send_booking_confirmation(user.email, user.full_name, booking)
    email.send_cancellation_notice(user.email, user.full_name, booking, refund_amount=240.0)
    email.send_override_notice(user.email, user.full_name, booking,
                                reason="Vehicle mechanical failure")