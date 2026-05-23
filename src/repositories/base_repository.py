"""
Base Repository class.

Provides shared database connection logic for all repositories, 
allowing child repositories to focus only on queries related to their specific entities
"""

from src.database.connection import DBConnection


class BaseRepository:
    """Parent class for all repositories. Gives them a shared DB connection."""

    def __init__(self):
        # Singleton — always returns the same DB connection
        self._db = DBConnection.get_instance()

    def _get_cursor(self):
        """Get a cursor to run SQL queries."""
        return self._db.get_connection().cursor()

    def _commit(self):
        """Save changes to the database."""
        self._db.get_connection().commit()

    def _rollback(self):
        """Undo changes if something went wrong."""
        self._db.get_connection().rollback()