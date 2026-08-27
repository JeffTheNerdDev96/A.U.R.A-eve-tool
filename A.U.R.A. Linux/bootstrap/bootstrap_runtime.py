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
Bootstrap Qt6 platform plugins, display server bindings, and shared libraries for Linux.
Handles Wayland / XCB display server selection, FreeDesktop font rendering, and plugin paths.
"""
from __future__ import annotations

import os
import sys
import site
from typing import List, Optional


def configure_linux_display_server() -> str:
    """
    Configures Qt6 display server integration based on desktop session environment.
    Supports native Wayland with automatic XCB / X11 fallback.
    """
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

    # If Wayland session is detected, set dual platform fallback
    if session_type == "wayland" or wayland_display:
        if "QT_QPA_PLATFORM" not in os.environ:
            os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
        return "wayland;xcb"
    else:
        if "QT_QPA_PLATFORM" not in os.environ:
            os.environ["QT_QPA_PLATFORM"] = "xcb"
        return "xcb"


def _find_pyqt6_plugin_dirs() -> List[str]:
    """Finds candidate plugin directories for PyQt6 on Linux."""
    candidates = []
    roots = []

    # 1. Virtual environment site-packages
    for prefix in (sys.prefix, sys.base_prefix):
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        candidates.append(os.path.join(prefix, "lib", py_ver, "site-packages", "PyQt6", "Qt6", "plugins"))
        candidates.append(os.path.join(prefix, "lib", "site-packages", "PyQt6", "Qt6", "plugins"))

    # 2. User site-packages
    try:
        user_site = site.getusersitepackages()
        if isinstance(user_site, str):
            candidates.append(os.path.join(user_site, "PyQt6", "Qt6", "plugins"))
    except Exception:
        pass

    # 3. System Qt6 plugin locations
    candidates.extend([
        "/usr/lib/x86_64-linux-gnu/qt6/plugins",
        "/usr/lib64/qt6/plugins",
        "/usr/lib/qt6/plugins",
    ])

    return [c for c in candidates if os.path.isdir(c)]


def configure_qt_plugin_paths() -> Optional[str]:
    """
    Discovers and configures Qt6 platform and plugin directories for Linux.
    Sets QT_PLUGIN_PATH and QT_QPA_PLATFORM_PLUGIN_PATH.
    """
    configure_linux_display_server()

    # Enable High DPI scaling
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    plugin_dirs = _find_pyqt6_plugin_dirs()
    if not plugin_dirs:
        return None

    primary = plugin_dirs[0]
    existing = os.environ.get("QT_PLUGIN_PATH", "")
    if existing:
        if primary not in existing.split(os.pathsep):
            os.environ["QT_PLUGIN_PATH"] = f"{primary}{os.pathsep}{existing}"
    else:
        os.environ["QT_PLUGIN_PATH"] = primary

    platforms_dir = os.path.join(primary, "platforms")
    if os.path.isdir(platforms_dir):
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", platforms_dir)

    return primary


def bootstrap_qt_runtime() -> None:
    """Canonical entrypoint to bootstrap Qt6 environment before importing PyQt6."""
    configure_qt_plugin_paths()
