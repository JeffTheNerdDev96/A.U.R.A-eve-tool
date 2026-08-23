"""
A.U.R.A. Hardware Acceleration & Topology Package.
Provides multi-hardware detection, NPU/GPU co-processor telemetry, and driver installation guidance.
"""

from .detector import HardwareDetector, DynamicHardwareRouter
from .profile import (
    apply_install_mask, gpu_strategy_label, load_install_profile,
    standby_label, summarize_devices, install_hint_for_gpu
)

__all__ = [
    "HardwareDetector", "DynamicHardwareRouter",
    "apply_install_mask", "gpu_strategy_label", "load_install_profile",
    "standby_label", "summarize_devices", "install_hint_for_gpu"
]
