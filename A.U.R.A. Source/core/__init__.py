"""
A.U.R.A. Core Infrastructure Package.
Provides the async EventBus, typed event definitions, subsystem base contracts, configuration, lifecycle, and safety utilities.
"""

from .events import BaseEvent
from .event_bus import get_event_bus, EventBus
from .base_subsystem import BaseSubsystem
from .config import config, AppConfig
from .error_handler import AURAErrorCode, AURAException, log_diagnostic_error, format_error_html
from .input_safety import (
    escape_html, strip_control_chars, clamp_text, safe_display_text,
    is_path_under, is_safe_log_file, wrap_untrusted
)
from .lifecycle import cleanup_temp_files, shutdown_application, install_thread_excepthook
from .eve_data import lookup_ship, get_tactical_grounding, SHIP_DATABASE

__all__ = [
    "BaseEvent", "get_event_bus", "EventBus", "BaseSubsystem",
    "config", "AppConfig",
    "AURAErrorCode", "AURAException", "log_diagnostic_error", "format_error_html",
    "escape_html", "strip_control_chars", "clamp_text", "safe_display_text",
    "is_path_under", "is_safe_log_file", "wrap_untrusted",
    "cleanup_temp_files", "shutdown_application", "install_thread_excepthook",
    "lookup_ship", "get_tactical_grounding", "SHIP_DATABASE",
]
