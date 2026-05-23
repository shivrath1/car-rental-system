"""
CLI views - helpers for displaying data and getting input in the terminal.
"""

from datetime import datetime

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"


def header(title):
    """Print a section header with a divider."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def success(message):
    """Print a success message in green."""
    print(f"{GREEN}{message}{RESET}")


def error(message):
    """Print an error message in red."""
    print(f"{RED}{message}{RESET}")


def info(message):
    """Print an info message in cyan."""
    print(f"{CYAN}{message}{RESET}")


def show_car_list(cars):
    """Print a list of cars in a table."""
    if not cars:
        info("No cars available.")
        return

    print()
    print(f"{'ID':<5}{'Year':<6}{'Make':<12}{'Model':<15}{'Mileage':<12}{'Rate/day':<10}")
    print("-" * 60)
    for car in cars:
        print(
            f"{car.car_id:<5}"
            f"{car.year:<6}"
            f"{car.make:<12}"
            f"{car.model:<15}"
            f"{car.mileage:<12,.0f}"
            f"${car.base_rate:<9.2f}"
        )
    print()


def show_booking_list(bookings, show_customer=False):
    """Print a list of bookings. If show_customer is True, includes the customer name."""
    if not bookings:
        info("No bookings to show.")
        return

    print()
    if show_customer:
        print(f"{'ID':<5}{'Customer':<20}{'Car':<22}{'Dates':<25}{'Status':<12}{'Total':<10}")
        print("-" * 95)
    else:
        print(f"{'ID':<5}{'Car':<25}{'Dates':<25}{'Status':<12}{'Total':<10}")
        print("-" * 80)

    for b in bookings:
        dates = f"{b.start_date} to {b.end_date}"
        status = b.status

        # Color the status based on what it is
        if status == "confirmed":
            status_colored = f"{GREEN}{status:<12}{RESET}"
        elif status in ("cancelled", "overridden"):
            status_colored = f"{RED}{status:<12}{RESET}"
        else:
            status_colored = f"{status:<12}"

        if show_customer:
            print(
                f"{b.booking_id:<5}"
                f"{b.user.full_name:<20}"
                f"{b.car.get_display_name():<22}"
                f"{dates:<25}"
                f"{status_colored}"
                f"${b.total_amount:<9.2f}"
            )
        else:
            print(
                f"{b.booking_id:<5}"
                f"{b.car.get_display_name():<25}"
                f"{dates:<25}"
                f"{status_colored}"
                f"${b.total_amount:<9.2f}"
            )
    print()


def show_price_breakdown(breakdown):
    """Print the smart pricing breakdown."""
    print()
    print(breakdown.get_breakdown_text())
    print()


def prompt(message):
    """Ask the user for input."""
    return input(f"{message}: ").strip()


def prompt_int(message, min_value=None, max_value=None):
    """Ask for a whole number. Keeps asking until they enter a valid one."""
    while True:
        raw = prompt(message)
        try:
            value = int(raw)
        except ValueError:
            error("Please enter a whole number.")
            continue
        if min_value is not None and value < min_value:
            error(f"Must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            error(f"Must be at most {max_value}.")
            continue
        return value


def prompt_float(message, min_value=None):
    """Ask for a decimal number."""
    while True:
        raw = prompt(message)
        try:
            value = float(raw)
        except ValueError:
            error("Please enter a valid number.")
            continue
        if min_value is not None and value < min_value:
            error(f"Must be at least {min_value}.")
            continue
        return value


def prompt_date(message):
    """Ask for a date in YYYY-MM-DD format."""
    while True:
        raw = prompt(f"{message} (YYYY-MM-DD)")
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            error("Please use the format YYYY-MM-DD (e.g., 2026-12-25).")


def prompt_yes_no(message):
    """Ask a yes/no question. Returns True for yes, False for no."""
    while True:
        raw = prompt(f"{message} (y/n)").lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        error("Please answer 'y' or 'n'.")