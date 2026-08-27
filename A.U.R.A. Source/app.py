# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
"""
Main entry point for Adaptive Underworld Recon Array (A.U.R.A.).
Angel Cartel EVE Online Tactical AI Assistant - v0.4.1-alpha.1.
"""
import sys
import os
import traceback
import time
import atexit

from version import INSTALLER_EXE_NAME

# Enforce no stale bytecode caching across all executions
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 0. Strict Python 3.12+ Architecture Requirement
if sys.version_info < (3, 12):
    _display_title = "A.U.R.A. Assist"
    err_text = (
        f"{_display_title} requires Python 3.12 or higher.\n\n"
        f"Detected: Python {sys.version.split()[0]}\n\n"
        f"Legacy versions (< 3.12) are not supported. Please run the {INSTALLER_EXE_NAME} installer."
    )
    try:
        _log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(_log_dir, exist_ok=True)
        with open(os.path.join(_log_dir, "crash.log"), "a", encoding="utf-8") as _f:
            _f.write(
                f"\n[AURA-ERR-1003] Python incompatible: {sys.version.split()[0]}\n"
            )
    except OSError:
        pass
    if sys.stderr is not None:
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootstrap import configure_qt_paths
configure_qt_paths()

from core import cleanup_temp_files, install_thread_excepthook

cleanup_temp_files()
atexit.register(cleanup_temp_files)
install_thread_excepthook()

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

    if sys.stderr is not None:
        sys.stderr.write(f"\n[!] A.U.R.A. Critical Error: {err_msg}\n")

sys.excepthook = _global_exception_handler


def _show_startup_error(exc: BaseException) -> None:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    crash_log = os.path.join(log_dir, "crash.log")
    err_msg = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(crash_log, "a", encoding="utf-8") as f:
            f.write(f"\n[STARTUP FAILURE {time.strftime('%Y-%m-%d %H:%M:%S')}]\n{err_msg}\n")
    except OSError:
        pass
    if sys.stderr is not None:
        sys.stderr.write(f"\n[!] A.U.R.A. startup failed: {err_msg}\n")
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                (
                    "A.U.R.A. failed to start.\n\n"
                    f"{type(exc).__name__}: {exc}\n\n"
                    f"Details were written to:\n{crash_log}\n\n"
                    "Try Launch_A.U.R.A_Debug.bat in the install folder."
                ),
                "A.U.R.A. Startup Error",
                0x10,
            )
        except Exception:
            pass


if __name__ == "__main__":
    try:
        from ui import run_app
        run_app()
    except Exception as startup_exc:
        _show_startup_error(startup_exc)
        sys.exit(1)
else:
    try:
        from ui import run_app
    except Exception as startup_exc:
        _show_startup_error(startup_exc)
        raise
