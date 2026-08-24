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

