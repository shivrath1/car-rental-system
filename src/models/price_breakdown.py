"""
PriceBreakdown class - holds the result of a Smart Pricing calculation.
Each booking has one breakdown showing how the final price was worked out.
"""


class PriceBreakdown:
    """Stores the itemised price details for a booking."""

    def __init__(self, base_rate, duration_days,
                 duration_discount=0.0, loyalty_discount=0.0,
                 seasonal_charge=0.0, lead_time_charge=0.0
                 , breakdown_id=None, booking_id=None):

        # Basic validation
        if base_rate < 0:
            raise ValueError("Base rate can't be negative")
        if duration_days < 1:
            raise ValueError("Duration must be at least 1 day")

        self._breakdown_id = breakdown_id
        self._booking_id = booking_id
        self._base_rate = base_rate
        self._duration_days = duration_days
        self._duration_discount = duration_discount
        self._loyalty_discount = loyalty_discount
        self._seasonal_charge = seasonal_charge
        self._lead_time_charge = lead_time_charge

        # Work out the final per-day rate
        self._final_rate = round(
            base_rate
            - duration_discount
            - loyalty_discount
            + seasonal_charge
            + lead_time_charge,
            2,
        )

        # Don't let the rate go below zero if discounts are huge
        if self._final_rate < 0:
            self._final_rate = 0.0

        self._total_amount = round(self._final_rate * duration_days, 2)

    # Getters
    @property
    def breakdown_id(self):
        return self._breakdown_id

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def base_rate(self):
        return self._base_rate

    @property
    def duration_days(self):
        return self._duration_days

    @property
    def duration_discount(self):
        return self._duration_discount

    @property
    def loyalty_discount(self):
        return self._loyalty_discount

    @property
    def seasonal_charge(self):
        return self._seasonal_charge

    @property
    def lead_time_charge(self):
        return self._lead_time_charge


    @property
    def final_rate(self):
        return self._final_rate

    @property
    def total_amount(self):
        return self._total_amount

    def set_breakdown_id(self, breakdown_id):
        self._breakdown_id = breakdown_id

    def set_booking_id(self, booking_id):
        self._booking_id = booking_id

    def get_breakdown_text(self):
        """Return the price breakdown as a readable receipt."""
        lines = [
            "Price Breakdown",
            "---------------",
            f"  Base rate              ${self._base_rate:>8.2f} / day",
        ]

        if self._duration_discount > 0:
            lines.append(f"  Duration discount      -${self._duration_discount:>7.2f} / day")
        if self._loyalty_discount > 0:
            lines.append(f"  Loyalty discount       -${self._loyalty_discount:>7.2f} / day")
        if self._seasonal_charge > 0:
            lines.append(f"  Seasonal surcharge     +${self._seasonal_charge:>7.2f} / day")
        if self._lead_time_charge > 0:
            lines.append(f"  Last-minute surcharge  +${self._lead_time_charge:>7.2f} / day")

        lines.append("  ---------------")
        lines.append(f"  Final rate             ${self._final_rate:>8.2f} / day")
        lines.append(f"  Duration               {self._duration_days} day(s)")
        lines.append(f"  ===============")
        lines.append(f"  TOTAL                  ${self._total_amount:>8.2f}")

        return "\n".join(lines)

    def __repr__(self):
        return (f"<PriceBreakdown id={self._breakdown_id} "
                f"final_rate=${self._final_rate:.2f} total=${self._total_amount:.2f}>")


# test
if __name__ == "__main__":
    print("Testing PriceBreakdown\n")

    # Simple rental
    pb1 = PriceBreakdown(base_rate=80.0, duration_days=3)
    print(f"Simple 3-day rental: ${pb1.total_amount}")

    # Full pricing scenario
    pb2 = PriceBreakdown(
        base_rate=80.0,
        duration_days=7,
        duration_discount=10.0,
        loyalty_discount=5.0,
        seasonal_charge=15.0
    )
    print()
    print(pb2.get_breakdown_text())
    print()

    # Check validation
    try:
        PriceBreakdown(base_rate=-10, duration_days=1)
    except ValueError as e:
        print(f"Negative rate blocked: {e}")

    try:
        PriceBreakdown(base_rate=50, duration_days=0)
    except ValueError as e:
        print(f"Zero days blocked: {e}")