"""
Car class - represents a vehicle in the rental fleet.
"""


class Car:
    """A single car available for rent."""

    def __init__(self, car_id, make, model, year, mileage, base_rate,
                 is_available=True, is_active=True):

        if base_rate < 0:
            raise ValueError("Base rate can't be negative")
        if mileage < 0:
            raise ValueError("Mileage can't be negative")

        self._car_id = car_id
        self._make = make
        self._model = model
        self._year = year
        self._mileage = mileage
        self._base_rate = base_rate
        self._is_available = is_available
        self._is_active = is_active

    # Getters
    @property
    def car_id(self):
        return self._car_id

    @property
    def make(self):
        return self._make

    @property
    def model(self):
        return self._model

    @property
    def year(self):
        return self._year

    @property
    def mileage(self):
        return self._mileage

    @property
    def base_rate(self):
        return self._base_rate

    @property
    def is_available(self):
        return self._is_available

    @property
    def is_active(self):
        return self._is_active

    def set_car_id(self, car_id):
        self._car_id = car_id

    def update_availability(self, is_available):
        """Mark the car as available or not available."""
        self._is_available = is_available

    def soft_delete(self):
        """Hide the car from customers but keep the record in the database."""
        self._is_active = False
        self._is_available = False

    def update_rate(self, new_rate):
        """Change the daily rental rate."""
        if new_rate < 0:
            raise ValueError("Rate can't be negative")
        self._base_rate = new_rate

    def update_mileage(self, new_mileage):
        """Update the mileage after a rental ends."""
        if new_mileage < self._mileage:
            raise ValueError("New mileage is less than current mileage")
        self._mileage = new_mileage

    def get_display_name(self):
        """Return a name like '2022 Toyota Camry'."""
        return f"{self._year} {self._make} {self._model}"

    def __repr__(self):
        return (f"<Car id={self._car_id} {self.get_display_name()} "
                f"${self._base_rate:.2f}/day>")


# test
if __name__ == "__main__":
    print("Testing Car\n")

    car = Car(car_id=1, make="Toyota", model="Camry", year=2022,
              mileage=15000.5, base_rate=85.0)

    print(car)
    print(f"Display name: {car.get_display_name()}")

    car.update_availability(False)
    print(f"After booking - available: {car.is_available}")

    car.update_mileage(15850.0)
    print(f"After return - mileage: {car.mileage}")

    car.soft_delete()
    print(f"After delete - active: {car.is_active}")

    # Quick validation checks
    try:
        Car(car_id=None, make="Ford", model="Focus", year=2020,
            mileage=0, base_rate=-50)
    except ValueError as e:
        print(f"Negative rate blocked: {e}")