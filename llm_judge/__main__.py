"""Enables `python -m llm_judge ...`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
