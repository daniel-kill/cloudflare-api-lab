"""
Cloudflare API Lab — Interactive Terminal Laboratory & Developer Tool for Cloudflare Workers AI & Edge Cloud Platform.
Author: Daniel Kill <daniel@danielkill.online>
License: MIT
"""

import sys

# Ensure UTF-8 output encoding across Windows and POSIX
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

__version__ = "1.0.0"
__author__ = "Daniel Kill"
