"""`python -m rota`. The one entry point; everything else is a module it calls."""
from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
