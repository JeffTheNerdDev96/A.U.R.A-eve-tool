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
A.U.R.A. Core Infrastructure Package.
Provides the async EventBus, typed event definitions, subsystem base contracts, configuration, lifecycle, and safety utilities.
"""

from .events import BaseEvent
from .base_subsystem import BaseSubsystem
from .config import config, AppConfig
from .error_handler import AURAErrorCode, AURAException, log_diagnostic_error, format_error_html
from .input_safety import (
    escape_html, strip_control_chars, clamp_text, safe_display_text,
    is_path_under, is_safe_log_file, wrap_untrusted
)
from .lifecycle import cleanup_temp_files, shutdown_application, install_thread_excepthook
from .eve_data import lookup_ship, get_tactical_grounding, SHIP_DATABASE
from .paths import (
    get_app_root, get_models_dir, get_data_dir, get_logs_dir,
    get_assets_dir, get_bootstrap_dir, find_model_path
)

__all__ = [
    "BaseEvent", "get_event_bus", "EventBus", "BaseSubsystem",
    "config", "AppConfig",
    "AURAErrorCode", "AURAException", "log_diagnostic_error", "format_error_html",
    "escape_html", "strip_control_chars", "clamp_text", "safe_display_text",
    "is_path_under", "is_safe_log_file", "wrap_untrusted",
    "cleanup_temp_files", "shutdown_application", "install_thread_excepthook",
    "lookup_ship", "get_tactical_grounding", "SHIP_DATABASE",
    "get_app_root", "get_models_dir", "get_data_dir", "get_logs_dir",
    "get_assets_dir", "get_bootstrap_dir", "find_model_path",
]


def __getattr__(name: str):
    if name in ("get_event_bus", "EventBus"):
        from .event_bus import get_event_bus, EventBus
        globals()["get_event_bus"] = get_event_bus
        globals()["EventBus"] = EventBus
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

