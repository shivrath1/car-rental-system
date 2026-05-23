"""
Car repository - handles database queries for cars.
"""

from src.repositories.base_repository import BaseRepository
from src.models.car import Car


class CarRepository(BaseRepository):
    """Database operations for cars."""

    def find_all_active(self):
        """Get all cars that haven't been soft-deleted."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM cars WHERE is_active = 1 ORDER BY make, model")
        rows = cursor.fetchall()
        return [self._row_to_car(row) for row in rows]

    def find_available(self):
        """Get all cars currently available for rental."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM cars WHERE is_active = 1 AND is_available = 1 "
            "ORDER BY make, model"
        )
        rows = cursor.fetchall()
        return [self._row_to_car(row) for row in rows]

    def find_by_id(self, car_id):
        """Find a car by ID. Returns Car or None."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_car(row)

    def save(self, car):
        """Insert a new car. Returns the new car_id."""
        cursor = self._get_cursor()
        cursor.execute(
            """INSERT INTO cars
               (make, model, year, mileage, base_rate, is_available, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                car.make, car.model, car.year, car.mileage, car.base_rate,
                int(car.is_available), int(car.is_active),
            ),
        )
        self._commit()
        new_id = cursor.lastrowid
        car.set_car_id(new_id)
        return new_id

    def update(self, car):
        """Update a car's details."""
        cursor = self._get_cursor()
        cursor.execute(
            """UPDATE cars
               SET make = ?, model = ?, year = ?, mileage = ?, base_rate = ?,
                   is_available = ?, is_active = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                car.make, car.model, car.year, car.mileage, car.base_rate,
                int(car.is_available), int(car.is_active), car.car_id,
            ),
        )
        self._commit()

    def soft_delete(self, car_id):
        """Mark a car as deleted - won't show to customers anymore."""
        cursor = self._get_cursor()
        cursor.execute(
            """UPDATE cars
               SET is_active = 0, is_available = 0, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (car_id,),
        )
        self._commit()

    def update_availability(self, car_id, is_available):
        """Mark a car as available or unavailable."""
        cursor = self._get_cursor()
        cursor.execute(
            "UPDATE cars SET is_available = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (int(is_available), car_id),
        )
        self._commit()

    def _row_to_car(self, row):
        """Convert a database row into a Car object."""
        return Car(
            car_id=row["id"],
            make=row["make"],
            model=row["model"],
            year=row["year"],
            mileage=row["mileage"],
            base_rate=row["base_rate"],
            is_available=bool(row["is_available"]),
            is_active=bool(row["is_active"]),
        )


# Test
if __name__ == "__main__":
    print("Testing CarRepository\n")

    repo = CarRepository()

    # See what's already in the database
    cars = repo.find_all_active()
    print(f"Existing active cars: {len(cars)}")

    # Add a new car
    new_car = Car(car_id=None, make="Mazda", model="CX-5", year=2024,
                  mileage=5000.0, base_rate=90.0)
    new_id = repo.save(new_car)
    print(f"Saved new car with ID: {new_id}")

    # Find it back
    found = repo.find_by_id(new_id)
    print(f"Found: {found.get_display_name()} at ${found.base_rate}/day")

    # Mark it unavailable
    repo.update_availability(new_id, False)
    available = repo.find_available()
    print(f"Available cars after marking unavailable: {len(available)}")

    # Soft delete it
    repo.soft_delete(new_id)
    active = repo.find_all_active()
    print(f"Active cars after soft delete: {len(active)}")
