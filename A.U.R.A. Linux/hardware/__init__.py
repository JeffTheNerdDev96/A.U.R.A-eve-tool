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
A.U.R.A. Hardware Acceleration & Topology Package.
Provides multi-hardware detection, NPU/GPU co-processor telemetry, and driver installation guidance.
"""

from .profile import (
    apply_install_mask, gpu_strategy_label, load_install_profile,
    standby_label, summarize_devices, install_hint_for_gpu
)

__all__ = [
    "HardwareDetector", "DynamicHardwareRouter",
    "apply_install_mask", "gpu_strategy_label", "load_install_profile",
    "standby_label", "summarize_devices", "install_hint_for_gpu"
]


def __getattr__(name: str):
    if name in ("HardwareDetector", "DynamicHardwareRouter"):
        from .detector import HardwareDetector, DynamicHardwareRouter
        globals()["HardwareDetector"] = HardwareDetector
        globals()["DynamicHardwareRouter"] = DynamicHardwareRouter
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

