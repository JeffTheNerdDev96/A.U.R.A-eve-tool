# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
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
A.U.R.A. VOIP (Mumble) Native Runtime Helper.
Registers the provisioned Opus codec DLL directory before pymumble import.
Importing this module has no side effects beyond PATH / DLL registration.
"""

from __future__ import annotations

import os
import sys
# PyMumble 1.6.1 bundles proto stubs generated with legacy protoc.
# Modern protobuf (>=4.x, 5.x, 7.x) requires the Python implementation backend
# to allow legacy descriptor instantiation without TypeError.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

_DLL_DIR_HANDLES: list = []


def get_voip_runtime_dir() -> str:
    """Absolute path of the VOIP native runtime directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.dirname(os.path.dirname(here))
    return os.path.join(source_dir, "voip_runtime")


def ensure_opus_dll_path() -> str | None:
    """Register voip_runtime/ for DLL discovery. Returns dir or None."""
    if sys.platform != "win32":
        return None
    runtime_dir = get_voip_runtime_dir()
    if not os.path.isdir(runtime_dir):
        return None
    dll_path = os.path.join(runtime_dir, "opus.dll")
    if not os.path.isfile(dll_path):
        return None
    if hasattr(os, "add_dll_directory"):
        try:
            handle = os.add_dll_directory(runtime_dir)
            if handle is not None:
                _DLL_DIR_HANDLES.append(handle)
        except OSError:
            pass
    path_env = os.environ.get("PATH", "")
    if runtime_dir not in path_env:
        os.environ["PATH"] = runtime_dir + os.pathsep + path_env
    return runtime_dir


def is_opus_available() -> bool:
    """True when opus.dll exists and ctypes can resolve the 'opus' library."""
    if sys.platform != "win32":
        return False
    dll_path = os.path.join(get_voip_runtime_dir(), "opus.dll")
    if not (os.path.isfile(dll_path) and os.path.getsize(dll_path) > 1024):
        return False
    try:
        from ctypes.util import find_library
    except ImportError:
        return False
    ensure_opus_dll_path()
    try:
        return find_library("opus") is not None
    except OSError:
        return False
