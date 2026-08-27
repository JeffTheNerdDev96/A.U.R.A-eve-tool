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
A.U.R.A. Bootstrap Package.
Handles low-level Python runtime, Qt plugin path discovery, and C++ library DLL loading.
"""

from .bootstrap_runtime import configure_qt_paths, configure_frozen_qt_paths
from .bootstrap_llama import configure_llama_dll_paths, probe_llama_backend

__all__ = [
    "configure_qt_paths", "configure_frozen_qt_paths",
    "configure_llama_dll_paths", "probe_llama_backend"
]
