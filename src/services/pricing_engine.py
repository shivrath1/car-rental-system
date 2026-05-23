"""
Pricing engine - calculates dynamic rental prices based on duration,
loyalty, season, and lead time.
"""

from datetime import date

from src.models.price_breakdown import PriceBreakdown


class PricingEngine:
    """Calculates the price for a car rental."""

    # Pricing rules - easy to change in one place
    LONG_RENTAL_THRESHOLD_DAYS = 7
    LONG_RENTAL_DISCOUNT = 10.0

    PEAK_MONTHS = [12, 1, 7]    # December, January, July
    PEAK_SURCHARGE = 15.0

    LAST_MINUTE_THRESHOLD_DAYS = 3
    LAST_MINUTE_SURCHARGE = 20.0

    # Loyalty tiers (past rentals, discount per day)
    LOYALTY_TIERS = [
        (10, 15.0),
        (5, 10.0),
        (3, 5.0),
        (0, 0.0),
    ]

    def calculate_price(self, base_rate, start_date, end_date, rental_count=0):
        """Work out the price for a rental and return a PriceBreakdown."""
        duration_days = (end_date - start_date).days + 1

        duration_discount = self._duration_discount(duration_days)
        loyalty_discount = self._loyalty_discount(rental_count)
        seasonal_charge = self._seasonal_charge(start_date)
        lead_time_charge = self._lead_time_charge(start_date)

        return PriceBreakdown(
            base_rate=base_rate,
            duration_days=duration_days,
            duration_discount=duration_discount,
            loyalty_discount=loyalty_discount,
            seasonal_charge=seasonal_charge,
            lead_time_charge=lead_time_charge,
        )

    def _duration_discount(self, duration_days):
        """Long rentals get a per-day discount."""
        if duration_days >= self.LONG_RENTAL_THRESHOLD_DAYS:
            return self.LONG_RENTAL_DISCOUNT
        return 0.0

    def _loyalty_discount(self, rental_count):
        """Loyal customers get a per-day discount."""
        for threshold, discount in self.LOYALTY_TIERS:
            if rental_count >= threshold:
                return discount
        return 0.0

    def _seasonal_charge(self, start_date):
        """Peak season months get a surcharge."""
        if start_date.month in self.PEAK_MONTHS:
            return self.PEAK_SURCHARGE
        return 0.0

    def _lead_time_charge(self, start_date):
        """Last-minute bookings get a surcharge."""
        days_ahead = (start_date - date.today()).days
        if 0 <= days_ahead < self.LAST_MINUTE_THRESHOLD_DAYS:
            return self.LAST_MINUTE_SURCHARGE
        return 0.0


# test
if __name__ == "__main__":
    print("Testing PricingEngine\n")

    engine = PricingEngine()

    print("Simple rental:")
    pb = engine.calculate_price(80.0, date(2026, 9, 15), date(2026, 9, 17))
    print(pb.get_breakdown_text())
    print()

    print("Long rental (7 days):")
    pb = engine.calculate_price(80.0, date(2026, 9, 15), date(2026, 9, 21))
    print(pb.get_breakdown_text())
    print()

    print("Loyal customer, peak season, long rental:")
    pb = engine.calculate_price(80.0, date(2026, 12, 20), date(2026, 12, 27),
                                 rental_count=10)
    print(pb.get_breakdown_text())
    print()
