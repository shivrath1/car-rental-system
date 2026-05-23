"""
Database connection - uses the Singleton pattern so there's only one
SQLite connection shared across the whole app.
"""

import os
import sqlite3


class DBConnection:
    """Manages a single SQLite database connection (Singleton pattern)."""

    _instance = None

    # Build paths relative to this file so the app runs from anywhere
    _SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
    _DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    _DB_PATH = os.path.join(_DB_DIR, "car_rental.db")

    def __init__(self):
        # direct creation not allowed - must go through get_instance()
        if DBConnection._instance is not None:
            raise RuntimeError("Use the DBConnection.get_instance()")

        # Make sure the data folder exists
        os.makedirs(self._DB_DIR, exist_ok=True)

        # Check if this is a fresh database (before connecting)
        is_new_database = not os.path.exists(self._DB_PATH)

        # Open the SQLite connection
        self._connection = sqlite3.connect(self._DB_PATH, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

        # Run the schema script if the database is new
        if is_new_database:
            self._initialise_schema()

    @classmethod
    def get_instance(cls):
        """Return the shared DBConnection instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_connection(self):
        """Return the underlying sqlite3 connection."""
        return self._connection

    def close(self):
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            DBConnection._instance = None

    def _initialise_schema(self):
        """Run the schema.sql file to set up tables on first run."""
        if not os.path.exists(self._SCHEMA_PATH):
            raise FileNotFoundError(f"Schema file not found: {self._SCHEMA_PATH}")

        with open(self._SCHEMA_PATH, "r") as f:
            schema_sql = f.read()

        try:
            self._connection.executescript(schema_sql)
            self._connection.commit()
            print("Database initialised.")
        except sqlite3.Error as error:
            self._connection.rollback()
            raise


# test
if __name__ == "__main__":
    db = DBConnection.get_instance()
    conn = db.get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in cursor.fetchall()]

    print(f"Tables: {tables}")
    db.close()