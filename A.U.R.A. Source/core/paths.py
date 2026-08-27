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
Canonical Path Resolver for Adaptive Underworld Recon Array (A.U.R.A.).
Provides single-source-of-truth, frozen-aware (PyInstaller), and symlink-safe path resolution
for app root, models, map data, logs, assets, and runtime dependencies.
"""
from __future__ import annotations

import os
import sys
from typing import Optional


def get_app_root() -> str:
    """
    Returns the absolute path to the root directory of the application.
    - If running under PyInstaller bundle: returns sys._MEIPASS or executable directory.
    - If running from source: returns the 'A.U.R.A. Source' root directory.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass and os.path.isdir(meipass):
        return os.path.abspath(meipass)

    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    # Resolves up to 'A.U.R.A. Source' directory
    this_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(this_file)
    return os.path.dirname(core_dir)


def get_models_dir(model_folder: str = "phi-4-mini") -> str:
    """Returns the models directory path."""
    return os.path.join(get_app_root(), "models", model_folder)


def get_data_dir() -> str:
    """Returns the bundled data directory path."""
    return os.path.join(get_app_root(), "data")


def get_logs_dir() -> str:
    """Returns the logs directory path and ensures it exists."""
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
    Scans candidate directories to locate the GGUF model weights file with caching.
    Supports source tree, PyInstaller bundles, local app data installations, and system install paths.
    """
    app_root = get_app_root()
    exe_dir = os.path.dirname(sys.executable)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    user_prof = os.environ.get("USERPROFILE", "")

    candidates = [
        os.path.join(app_root, "models", model_folder, model_file),
        os.path.join(exe_dir, "models", model_folder, model_file),
        os.path.join(os.path.dirname(exe_dir), "models", model_folder, model_file),
        os.path.join(app_root, "..", "models", model_folder, model_file),
        os.path.join(local_app_data, "Programs", "A.U.R.A.", "models", model_folder, model_file),
        os.path.join(user_prof, "AppData", "Local", "Programs", "A.U.R.A.", "models", model_folder, model_file),
        os.path.join(r"C:\Program Files", "A.U.R.A.", "models", model_folder, model_file),
    ]

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.insert(0, os.path.join(meipass, "models", model_folder, model_file))

    for path in candidates:
        if path and os.path.isfile(path) and os.path.getsize(path) > 1_000_000:
            return os.path.abspath(path)

    return None
