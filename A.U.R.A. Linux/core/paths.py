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
Canonical Path Resolver for Adaptive Underworld Recon Array (A.U.R.A.) - Linux Native.
Provides single-source-of-truth path resolution adhering to FreeDesktop XDG Base Directory
specifications and native Linux directory hierarchies (/usr/share, /opt, ~/.local/share).
"""
from __future__ import annotations

import os
import sys
from typing import Optional


def get_xdg_data_home() -> str:
    """Returns the XDG data home directory (~/.local/share/aura)."""
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "aura")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


def get_xdg_config_home() -> str:
    """Returns the XDG configuration directory (~/.config/aura)."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    path = os.path.join(base, "aura")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


def get_xdg_cache_home() -> str:
    """Returns the XDG cache directory (~/.cache/aura)."""
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    path = os.path.join(base, "aura")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


def get_app_root() -> str:
    """
    Returns the absolute path to the root directory of the application.
    - If running under PyInstaller bundle: returns sys._MEIPASS or executable directory.
    - If running from source: returns the 'A.U.R.A. Linux' root directory.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass and os.path.isdir(meipass):
        return os.path.abspath(meipass)

    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    # Resolves up to 'A.U.R.A. Linux' directory
    this_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(this_file)
    return os.path.dirname(core_dir)


def get_models_dir(model_folder: str = "phi-4-mini") -> str:
    """Returns the primary models directory path."""
    local_models = os.path.join(get_app_root(), "models", model_folder)
    if os.path.isdir(local_models):
        return local_models
    xdg_models = os.path.join(get_xdg_data_home(), "models", model_folder)
    try:
        os.makedirs(xdg_models, exist_ok=True)
    except OSError:
        pass
    return xdg_models


def get_data_dir() -> str:
    """Returns the bundled data directory path."""
    return os.path.join(get_app_root(), "data")


def get_logs_dir() -> str:
    """Returns the logs directory path (XDG data home / logs) and ensures it exists."""
    log_dir = os.path.join(get_xdg_data_home(), "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError:
        log_dir = os.path.join(get_app_root(), "logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            pass
    return log_dir


def get_assets_dir() -> str:
    """Returns the assets directory path."""
    return os.path.join(get_app_root(), "assets")


def get_bootstrap_dir() -> str:
    """Returns the bootstrap directory path."""
    return os.path.join(get_app_root(), "bootstrap")


def find_model_path(model_folder: str = "phi-4-mini", model_file: str = "model_q4.gguf") -> Optional[str]:
    """
    Scans candidate directories on Linux to locate the GGUF model weights file with caching.
    Supports source tree, XDG data home, /opt/aura, and /usr/share/aura.
    """
    app_root = get_app_root()
    home = os.path.expanduser("~")
    xdg_data = get_xdg_data_home()

    candidates = [
        os.path.join(app_root, "models", model_folder, model_file),
        os.path.join(xdg_data, "models", model_folder, model_file),
        os.path.join(home, ".local", "share", "aura", "models", model_folder, model_file),
        os.path.join(app_root, "..", "models", model_folder, model_file),
        os.path.join("/opt", "aura", "models", model_folder, model_file),
        os.path.join("/usr", "share", "aura", "models", model_folder, model_file),
        os.path.join("/usr", "local", "share", "aura", "models", model_folder, model_file),
    ]

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.insert(0, os.path.join(meipass, "models", model_folder, model_file))

    for path in candidates:
        if path and os.path.isfile(path) and os.path.getsize(path) > 1_000_000:
            return os.path.abspath(path)

    return None
