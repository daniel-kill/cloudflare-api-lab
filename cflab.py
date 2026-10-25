#!/usr/bin/env python3
"""
Cloudflare API Lab (cflab) — Interactive Terminal Laboratory & Developer Tool
for Cloudflare Workers AI & Edge Cloud Platform.

Usage:
  python cflab.py               Launch interactive menu
  python cflab.py --help        Display CLI command-line options
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cflab.cli import main

if __name__ == "__main__":
    main()
