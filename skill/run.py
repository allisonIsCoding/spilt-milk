#!/usr/bin/env python3
"""Entry point for the milk-carton-schematics skill. Usage: python scripts/run.py --help"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from milk_carton.__main__ import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
