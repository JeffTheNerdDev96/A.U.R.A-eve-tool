"""Exit 0 if this interpreter is Python 3.12+, else 1. Used by _bootstrap_venv.bat."""
import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 12:
    raise SystemExit(0)
raise SystemExit(1)
