#!/usr/bin/env python3
"""Echoes of Asteria - A terminal RPG adventure."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from echoes_of_asteria.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
