"""
Application lifecycle: temp-file cleanup and ordered shutdown of threads and neural resources.
"""
from __future__ import annotations

import gc
import os
import shutil
import sys
import threading
import time
from typing import Any, Optional

WORKER_JOIN_MS = 2000
CHAT_MONITOR_JOIN_MS = 1500

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_THIS_DIR) if os.path.basename(_THIS_DIR) == "core" else _THIS_DIR


def cleanup_temp_files() -> None:
    """Purges orphaned __pycache__ and stale non-crash logs."""
    pc = os.path.join(_APP_DIR, "__pycache__")
    if os.path.exists(pc):
        try:
            shutil.rmtree(pc, ignore_errors=True)
        except OSError:
            pass

    log_dir = os.path.join(_APP_DIR, "logs")
    if not os.path.exists(log_dir):
        return
    now = time.time()
    for name in os.listdir(log_dir):
        if not name.endswith(".log") or name == "crash.log":
            continue
        path = os.path.join(log_dir, name)
        try:
            if os.stat(path).st_mtime < now - (3 * 86400):
                os.remove(path)
        except OSError:
            pass


def _log_shutdown_error(exc: Exception, context: str) -> None:
    try:
        from .error_handler import AURAErrorCode, log_diagnostic_error
        log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, context)
    except Exception:
        sys.stderr.write(f"[A.U.R.A.] Shutdown error ({context}): {exc}\n")


def shutdown_application(window: Optional[Any] = None) -> None:
    """Stop timers, background workers, neural core, and purge in-memory buffers."""
    if window is not None and getattr(window, "_shutdown_done", False):
        cleanup_temp_files()
        gc.collect()
        return

    if window is not None:
        try:
            if hasattr(window, "idle_timer") and window.idle_timer is not None:
                window.idle_timer.stop()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: idle_timer")

        try:
            if hasattr(window, "tray_icon") and window.tray_icon:
                window.tray_icon.hide()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: tray_icon")

        try:
            worker = getattr(window, "worker", None)
            if worker is not None and worker.isRunning():
                if hasattr(worker, "stop"):
                    worker.stop()
                worker.quit()
                worker.wait(WORKER_JOIN_MS)
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: worker_thread")

        try:
            monitor = getattr(window, "chat_monitor", None)
            if monitor is not None and monitor.isRunning():
                monitor.stop()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: chat_monitor")

        try:
            engine = getattr(window, "engine", None)
            if engine is not None:
                engine.unload_model()
                coprocessor = getattr(engine, "coprocessor", None)
                if coprocessor is not None:
                    coprocessor.stop_all_workers()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: engine")

        try:
            if hasattr(window, "chat_history"):
                window.chat_history.clear()
            if hasattr(window, "attachments"):
                window.attachments.clear()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: memory_buffers")

        window._shutdown_done = True

    cleanup_temp_files()
    gc.collect()


def install_thread_excepthook() -> None:
    """Route unhandled background-thread exceptions to crash.log."""

    def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
        try:
            from .error_handler import AURAErrorCode, log_diagnostic_error
            log_diagnostic_error(
                AURAErrorCode.ERR_5001_WORKER_CRASH,
                args.exc_value if isinstance(args.exc_value, BaseException) else None,
                f"thread:{getattr(args.thread, 'name', 'unknown')}",
            )
        except Exception:
            if args.exc_value is not None:
                sys.stderr.write(f"[A.U.R.A.] Unhandled thread error: {args.exc_value}\n")

    threading.excepthook = _thread_excepthook
