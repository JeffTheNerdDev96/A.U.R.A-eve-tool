"""
Main entry point for A.U.R.A. Assist (Adaptive Underworld Recon Array).
Angel Cartel EVE Online Tactical AI Assistant - v0.2.0.
"""
import sys
import os
import traceback
import time
import shutil
import atexit
import gc

# Enforce no stale bytecode caching across all executions
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 0. Strict Python 3.12+ Architecture Requirement
if sys.version_info < (3, 12):
    err_text = (
        f"{config.display_title} requires Python 3.12 or higher.\n\n"
        f"Detected: Python {sys.version.split()[0]}\n\n"
        f"Legacy versions (< 3.12) are not supported. Please run the v0.2.0 installer."
    )
    sys.stderr.write(f"[FATAL] {err_text}\n")
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, err_text, "A.U.R.A. Version Error", 0x10)
        except Exception:
            pass
    sys.exit(1)

# 1. Native Windows High-DPI Awareness (Per-Monitor V2)
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# 2. Automated Stale Cache & Temporary File Cleaner
def _cleanup_stale_caches():
    """Purges orphaned __pycache__ and temporary logs to keep filesystem pristine."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    pc = os.path.join(app_dir, "__pycache__")
    if os.path.exists(pc):
        try:
            shutil.rmtree(pc, ignore_errors=True)
        except Exception:
            pass

    log_dir = os.path.join(app_dir, "logs")
    if os.path.exists(log_dir):
        now = time.time()
        for f in os.listdir(log_dir):
            if f.endswith(".log") and f != "crash.log":
                f_path = os.path.join(log_dir, f)
                try:
                    # Remove non-crash logs older than 3 days
                    if os.stat(f_path).st_mtime < now - (3 * 86400):
                        os.remove(f_path)
                except Exception:
                    pass

_cleanup_stale_caches()
atexit.register(_cleanup_stale_caches)

# 3. Global Uncaught Exception Trap & Crash Logger
def _global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    crash_log = os.path.join(log_dir, "crash.log")

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    try:
        with open(crash_log, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n[CRASH TIMESTAMP: {timestamp}]\n{err_msg}\n{'='*70}\n")
    except Exception:
        pass

    sys.stderr.write(f"\n[!] A.U.R.A. Critical Error: {err_msg}\n")

sys.excepthook = _global_exception_handler

# Ensure local directory is at top of import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import run_app

if __name__ == "__main__":
    run_app()
