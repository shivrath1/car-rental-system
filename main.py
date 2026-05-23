"""
Car Rental System - main entry
"""

import os
import sys

# Make sure the Python can find the src/ modules
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.cli.menu import MainMenu


def main():
    """Start the CLI."""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()