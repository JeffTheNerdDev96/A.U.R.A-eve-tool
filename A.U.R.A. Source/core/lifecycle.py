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
from pathlib import Path
from typing import Any

from .paths import get_app_root, get_logs_dir

WORKER_JOIN_MS = 2000
CHAT_MONITOR_JOIN_MS = 1500


def cleanup_temp_files() -> None:
    """Purges orphaned __pycache__ and stale non-crash logs."""
    pc = Path(get_app_root()) / "__pycache__"
    if pc.exists():
        try:
            shutil.rmtree(pc, ignore_errors=True)
        except OSError:
            pass

    log_dir = Path(get_logs_dir())
    if not log_dir.exists():
        return
    now = time.time()
    try:
        for entry in log_dir.iterdir():
            if not entry.is_file() or not entry.name.endswith(".log") or entry.name == "crash.log":
                continue
            try:
                if entry.stat().st_mtime < now - (3 * 86400):
                    entry.unlink(missing_ok=True)
            except OSError:
                pass
    except OSError:
        pass


def _log_shutdown_error(exc: Exception, context: str) -> None:
    try:
        from .error_handler import AURAErrorCode, log_diagnostic_error
        log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, context)
    except Exception:
        sys.stderr.write(f"[A.U.R.A.] Shutdown error ({context}): {exc}\n")


def shutdown_application(window: Any | None = None) -> None:
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

        # 1. Immediately abort active inference and stop worker thread
        try:
            engine = getattr(window, "engine", None)
            if engine is not None:
                engine.request_abort()

            worker = getattr(window, "worker", None)
            if worker is not None and worker.isRunning():
                if hasattr(worker, "stop"):
                    worker.stop()
                worker.quit()
                worker.wait(WORKER_JOIN_MS)
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: worker_thread")

        # 2. Stop live chat monitor thread
        try:
            monitor = getattr(window, "chat_monitor", None)
            if monitor is not None and monitor.isRunning():
                monitor.stop()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: chat_monitor")

        # 3. Unload neural model and coprocessors
        try:
            if engine is not None:
                engine.unload_model()
                coprocessor = getattr(engine, "coprocessor", None)
                if coprocessor is not None:
                    coprocessor.stop_all_workers()
                    coprocessor.unload_coprocessor()
        except Exception as exc:
            _log_shutdown_error(exc, "shutdown: engine")

        # 4. Stop all attached subsystems
        for sub_attr in ("intel_subsystem", "map_subsystem", "fleet_comp_subsystem", "fitting_subsystem", "wormhole_subsystem", "ai_subsystem"):
            try:
                sub = getattr(window, sub_attr, None)
                if sub is not None and hasattr(sub, "stop"):
                    sub.stop()
            except Exception as exc:
                _log_shutdown_error(exc, f"shutdown: {sub_attr}")

        # 5. Clear chat history and memory buffers
        try:
            if hasattr(window, "chat_history"):
                window.chat_history.clear()
            if hasattr(window, "attachments"):
                window.attachments.clear()
            if hasattr(window, "current_assistant_tokens"):
                window.current_assistant_tokens.clear()
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
