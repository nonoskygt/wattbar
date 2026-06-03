"""Permite ejecutar `python -m wattbar`."""
import sys

from .app import main

if __name__ == "__main__":
    sys.exit(main())
