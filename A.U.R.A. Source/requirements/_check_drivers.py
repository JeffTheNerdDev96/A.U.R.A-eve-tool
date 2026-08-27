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
"""Print official vendor driver download links when OS drivers appear missing. Does not install drivers."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from hardware.profile import load_install_profile  # noqa: E402

NVIDIA_URL = "https://www.nvidia.com/Download/index.aspx"
INTEL_NPU_URL = "https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html"
INTEL_GPU_URL = "https://www.intel.com/content/www/us/en/products/docs/discrete-gpus/arc/software/drivers.html"
AMD_URL = "https://www.amd.com/en/support/download/drivers.html"


def _nvidia_ok() -> bool:
    smi = shutil.which("nvidia-smi")
    if not smi:
        return False
    try:
        proc = subprocess.run(
            [smi, "-L"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        return proc.returncode == 0 and bool((proc.stdout or "").strip())
    except Exception:
        return False


def _vulkan_ok() -> bool:
    if os.path.isfile(os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "vulkan-1.dll")):
        return True
    return shutil.which("vulkaninfo") is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check vendor GPU/NPU drivers; print links if missing.")
    parser.add_argument("--profiles", nargs="*", default=None, help="Profile ids to check (default: hardware_profile.json)")
    args = parser.parse_args()

    profiles = list(args.profiles or [])
    if not profiles:
        stored = load_install_profile()
        if stored:
            profiles = list(stored.get("profiles") or [])
            if stored.get("gpu_class") and stored["gpu_class"] != "none":
                profiles.append(stored["gpu_class"])
            if stored.get("npu") == "intel":
                profiles.append("intel_npu")
            if stored.get("npu") == "amd":
                profiles.append("amd_npu")

    profiles = list(dict.fromkeys(profiles))
    if not profiles:
        print("[!] No hardware profile specified; skipping OS driver checks.")
        return 0

    print("")
    print("[*] Checking vendor OS drivers (links only — nothing is installed)...")
    missing = False

    if any(p in profiles for p in ("nvidia_dgpu",)):
        if _nvidia_ok():
            print("[OK] NVIDIA driver detected (nvidia-smi).")
        else:
            missing = True
            print("[!] NVIDIA GPU driver not detected. Install Game Ready 550+ / CUDA 12.4+:")
            print(f"    {NVIDIA_URL}")

    if any(p in profiles for p in ("amd_dgpu", "amd_igpu", "amd_npu")):
        if _vulkan_ok() or any(p == "amd_npu" for p in profiles):
            if any(p in profiles for p in ("amd_dgpu", "amd_igpu")) and not _vulkan_ok():
                missing = True
                print("[!] Vulkan runtime not detected for AMD GPU. Install latest AMD Adrenalin (Vulkan 1.3):")
                print(f"    {AMD_URL}")
            elif "amd_npu" in profiles:
                print("[!] Confirm AMD Ryzen AI / XDNA NPU drivers via AMD Adrenalin or OEM support:")
                print(f"    {AMD_URL}")
            else:
                print("[OK] Vulkan runtime detected for AMD GPU.")
        else:
            missing = True
            print("[!] AMD GPU/NPU drivers not verified. Install latest Adrenalin / Ryzen AI package:")
            print(f"    {AMD_URL}")

    if any(p in profiles for p in ("intel_dgpu", "intel_igpu")):
        print("[*] Intel GPU: keep graphics drivers current via Intel Driver & Support Assistant:")
        print(f"    {INTEL_GPU_URL}")

    if "intel_npu" in profiles:
        print("[*] Intel NPU: Intel NPU Driver 32.0.100.3104+ is required for OpenVINO Level Zero:")
        print(f"    {INTEL_NPU_URL}")

    if not missing:
        print("[OK] Driver checks complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
