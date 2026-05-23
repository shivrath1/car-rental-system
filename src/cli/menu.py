"""
Main CLI menu - handles user interaction for main, customer, and admin screens.
"""

from src.controllers.booking_controller import BookingController
from src.cli import views


class MainMenu:
    """Top-level CLI menu."""

    def __init__(self):
        self.controller = BookingController()
        self.current_user = None

    def run(self):
        """Main loop. Keeps showing menus until the user exits."""
        views.header("Welcome to the Car Rental System")
        views.info("Type a menu number to choose an option.")

        while True:
            if self.current_user is None:
                self._show_main_menu()
            elif self.current_user.role == "admin":
                self._show_admin_menu()
            else:
                self._show_customer_menu()

    # Main menu (not logged in)

    def _show_main_menu(self):
        print()
        print("MAIN MENU")
        print("  1. Login")
        print("  2. Register as new customer")
        print("  3. Browse cars (as guest)")
        print("  4. Exit")
        choice = views.prompt_int("Your choice", min_value=1, max_value=4)

        if choice == 1:
            self._handle_login()
        elif choice == 2:
            self._handle_register()
        elif choice == 3:
            self._handle_guest_flow()
        elif choice == 4:
            views.info("\nThanks for using the Car Rental System. Goodbye!")
            exit(0)

    def _handle_login(self):
        views.header("Login")
        username = views.prompt("Username")
        password = views.prompt("Password")
        user = self.controller.login(username, password)
        if user:
            views.success(f"\nWelcome back, {user.full_name}!")
            self.current_user = user
        else:
            views.error("\nInvalid username or password. Please try again.")

    def _handle_register(self):
        views.header("Register New Customer")
        try:
            username = views.prompt("Choose a username")
            password = views.prompt("Choose a password")
            full_name = views.prompt("Full name")
            email = views.prompt("Email")
            phone = views.prompt("Phone (optional, press Enter to skip)") or None

            customer = self.controller.register_customer(
                username, password, full_name, email, phone
            )
            views.success(f"\nAccount created! Welcome, {customer.full_name}.")
            self.current_user = customer
        except ValueError as e:
            views.error(f"\nRegistration failed: {e}")

    def _handle_guest_flow(self):
        views.header("Browse Cars as Guest")
        self._browse_and_book(user=None)

    # Customer menu

    def _show_customer_menu(self):
        print()
        print(f"CUSTOMER MENU - {self.current_user.full_name}")
        print(f"Loyalty points: {self.current_user.loyalty_points}")
        print("  1. Browse and book a car")
        print("  2. View my bookings")
        print("  3. Cancel a booking")
        print("  4. Logout")
        choice = views.prompt_int("Your choice", min_value=1, max_value=4)

        if choice == 1:
            self._browse_and_book(user=self.current_user)
        elif choice == 2:
            self._view_my_bookings()
        elif choice == 3:
            self._cancel_booking()
        elif choice == 4:
            views.info(f"\nGoodbye, {self.current_user.full_name}!")
            self.current_user = None

    def _view_my_bookings(self):
        views.header("My Bookings")
        bookings = self.controller.get_user_bookings(self.current_user.user_id)
        views.show_booking_list(bookings)

    def _cancel_booking(self):
        views.header("Cancel a Booking")
        bookings = self.controller.get_user_bookings(self.current_user.user_id)
        active = [b for b in bookings if b.status == "confirmed"]
        if not active:
            views.info("You have no active bookings to cancel.")
            return

        views.show_booking_list(active)
        booking_id = views.prompt_int("Enter the booking ID to cancel")

        if not views.prompt_yes_no(f"Confirm cancellation of booking #{booking_id}?"):
            views.info("Cancellation aborted.")
            return

        result = self.controller.cancel_booking(booking_id, self.current_user)
        if result["success"]:
            views.success(f"\nBooking cancelled. Refund: ${result['refund']:.2f}")
        else:
            views.error(f"\nCancellation failed: {result['error']}")

    # Shared browse + book flow (used by customers and guests)

    def _browse_and_book(self, user):
        """Browse cars and book one. user=None for guests."""
        # Show available cars
        cars = self.controller.get_available_cars()
        if not cars:
            views.info("\nSorry, no cars are available right now.")
            return
        views.show_car_list(cars)

        if not views.prompt_yes_no("Would you like to book one of these cars?"):
            return

        car_id = views.prompt_int("Enter the car ID")
        start_date = views.prompt_date("Start date")
        end_date = views.prompt_date("End date")

        # Get the price quote
        quote = self.controller.calculate_quote(car_id, start_date, end_date, user=user)
        if not quote["success"]:
            views.error(f"\n{quote['error']}")
            return

        views.show_price_breakdown(quote["breakdown"])

        if not views.prompt_yes_no("Proceed with this booking?"):
            views.info("Booking cancelled.")
            return

        # If guest, collect contact info before payment
        if user is None:
            views.header("Guest Details")
            full_name = views.prompt("Full name")
            email = views.prompt("Email")
            phone = views.prompt("Phone")
            user = self.controller.create_guest_user(full_name, email, phone)

        # Collect payment info
        views.header("Payment")
        card_number = views.prompt("Card number")
        expiry = views.prompt("Expiry (MM/YY)")
        cvv = views.prompt("CVV")
        card_info = {"card_number": card_number, "expiry": expiry, "cvv": cvv}

        result = self.controller.confirm_booking(
            user=user,
            car=quote["car"],
            start_date=start_date,
            end_date=end_date,
            breakdown=quote["breakdown"],
            card_info=card_info,
        )
        if result["success"]:
            views.success(f"\nBooking confirmed! ID: {result['booking'].booking_id}")
            views.info("Confirmation email sent.")
        else:
            views.error(f"\nBooking failed: {result['error']}")

    # Admin menu

    def _show_admin_menu(self):
        print()
        print(f"ADMIN MENU - {self.current_user.full_name}")
        print("  1. Add a new car")
        print("  2. Update a car")
        print("  3. Delete a car")
        print("  4. View all bookings")
        print("  5. Override a booking")
        print("  6. Logout")
        choice = views.prompt_int("Your choice", min_value=1, max_value=6)

        if choice == 1:
            self._admin_add_car()
        elif choice == 2:
            self._admin_update_car()
        elif choice == 3:
            self._admin_delete_car()
        elif choice == 4:
            self._admin_view_bookings()
        elif choice == 5:
            self._admin_override_booking()
        elif choice == 6:
            views.info(f"\nGoodbye, {self.current_user.full_name}!")
            self.current_user = None

    def _admin_add_car(self):
        views.header("Add New Car")
        try:
            make = views.prompt("Make")
            model = views.prompt("Model")
            year = views.prompt_int("Year", min_value=1900, max_value=2100)
            mileage = views.prompt_float("Mileage", min_value=0)
            base_rate = views.prompt_float("Daily base rate ($)", min_value=0)

            car = self.controller.admin_add_car(make, model, year, mileage, base_rate)
            views.success(f"\nCar added: {car.get_display_name()} (ID {car.car_id})")
        except ValueError as e:
            views.error(f"\nFailed to add car: {e}")

    def _admin_update_car(self):
        views.header("Update Car")
        cars = self.controller.get_available_cars()
        views.show_car_list(cars)

        car_id = views.prompt_int("Enter car ID to update")
        car = self.controller.get_car_by_id(car_id)
        if car is None:
            views.error("Car not found.")
            return

        views.info(f"Current: {car.get_display_name()} - ${car.base_rate}/day")
        new_rate = views.prompt_float("New base rate (or 0 to keep current)", min_value=0)

        if new_rate > 0:
            result = self.controller.admin_update_car(car_id, base_rate=new_rate)
            if result["success"]:
                views.success(f"\nUpdated. New rate: ${result['car'].base_rate}/day")
            else:
                views.error(f"\nUpdate failed: {result['error']}")
        else:
            views.info("No changes made.")

    def _admin_delete_car(self):
        views.header("Delete Car")
        cars = self.controller.get_available_cars()
        views.show_car_list(cars)

        car_id = views.prompt_int("Enter car ID to delete")

        if not views.prompt_yes_no(f"Confirm deletion of car #{car_id}?"):
            views.info("Deletion aborted.")
            return

        result = self.controller.admin_delete_car(car_id)
        if result["success"]:
            views.success("\nCar deleted.")
        else:
            views.error(f"\nCannot delete: {result['error']}")

    def _admin_view_bookings(self):
        views.header("All Bookings")
        bookings = self.controller.admin_get_all_bookings()
        views.show_booking_list(bookings, show_customer=True)

    def _admin_override_booking(self):
        views.header("Override Booking")
        bookings = self.controller.admin_get_all_bookings()
        active = [b for b in bookings if b.status == "confirmed"]
        if not active:
            views.info("No active bookings to override.")
            return

        views.show_booking_list(active, show_customer=True)
        booking_id = views.prompt_int("Enter booking ID to override")
        reason = views.prompt("Reason for override")

        if not views.prompt_yes_no(f"Confirm override of booking #{booking_id}?"):
            views.info("Override aborted.")
            return

        result = self.controller.admin_override_booking(booking_id, reason)
        if result["success"]:
            views.success(f"\nBooking overridden. Refund: ${result['refund']:.2f}")
            views.info("Customer has been notified by email.")
        else:
            views.error(f"\nOverride failed: {result['error']}")