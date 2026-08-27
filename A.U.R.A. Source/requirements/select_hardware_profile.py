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
"""Detect live hardware and optionally install composed Python stacks into the venv."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ_DIR = os.path.dirname(os.path.abspath(__file__))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from hardware.profile import compose_install_plan, save_install_profile  # noqa: E402
from bootstrap.bootstrap_llama import probe_llama_backend  # noqa: E402


def _pip(python_exe: str, args: list[str]) -> int:
    cmd = [python_exe, "-m", "pip", *args]
    print("[*] " + " ".join(cmd))
    return subprocess.call(cmd)


def _verify_llama_wheel(wheel: str) -> tuple[bool, str]:
    require_cuda = wheel == "cuda"
    require_vulkan = wheel == "vulkan"
    return probe_llama_backend(
        require_cuda=require_cuda,
        require_vulkan=require_vulkan,
    )


def _install_llama(python_exe: str, wheel: str) -> str:
    indexes = {
        "cuda": "https://abetlen.github.io/llama-cpp-python/whl/cu124",
        "vulkan": "https://abetlen.github.io/llama-cpp-python/whl/vulkan",
        "cpu": "https://abetlen.github.io/llama-cpp-python/whl/cpu",
    }
    extra = indexes.get(wheel, indexes["cpu"])
    pip_args = [
        "install",
        "llama-cpp-python",
        "--upgrade",
        "--force-reinstall",
        "--no-cache-dir",
        "--extra-index-url",
        extra,
    ]
    if wheel in ("cuda", "vulkan"):
        pip_args.insert(1, "--only-binary=:all:")
    code = _pip(python_exe, pip_args)
    if code != 0 and wheel != "cpu":
        print(f"[!] {wheel} llama-cpp wheel failed; falling back to CPU.")
        _pip(
            python_exe,
            [
                "install",
                "llama-cpp-python",
                "--upgrade",
                "--force-reinstall",
                "--no-cache-dir",
                "--extra-index-url",
                indexes["cpu"],
            ],
        )
        return "cpu"

    if wheel == "cpu":
        return "cpu"

    ok, detail = _verify_llama_wheel(wheel)
    if ok:
        return wheel

    print(f"[!] {wheel} wheel pip install ok but bootstrap probe failed:\n{detail[:800]}")

    if wheel == "cuda":
        print("[*] CUDA wheel probe failed; retrying binary-only cu124 install...")
        retry_code = _pip(
            python_exe,
            [
                "install",
                "llama-cpp-python",
                "--upgrade",
                "--force-reinstall",
                "--no-cache-dir",
                "--only-binary=:all:",
                "--extra-index-url",
                indexes["cuda"],
            ],
        )
        if retry_code == 0:
            ok, detail = _verify_llama_wheel("cuda")
            if ok:
                return "cuda"
            print(f"[!] CUDA retry probe failed:\n{detail[:800]}")

    if wheel == "vulkan":
        print("[*] Vulkan wheel probe failed; retrying binary-only vulkan install...")
        retry_code = _pip(
            python_exe,
            [
                "install",
                "llama-cpp-python",
                "--upgrade",
                "--force-reinstall",
                "--no-cache-dir",
                "--only-binary=:all:",
                "--extra-index-url",
                indexes["vulkan"],
            ],
        )
        if retry_code == 0:
            ok, detail = _verify_llama_wheel("vulkan")
            if ok:
                return "vulkan"
            print(f"[!] Vulkan retry probe failed:\n{detail[:800]}")

    print(f"[!] {wheel} llama wheel failed verification; falling back to CPU.")
    _pip(
        python_exe,
        [
            "install",
            "llama-cpp-python",
            "--upgrade",
            "--force-reinstall",
            "--no-cache-dir",
            "--extra-index-url",
            indexes["cpu"],
        ],
    )
    return "cpu"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install composed stacks into this Python")
    parser.add_argument("--json", action="store_true", help="Print composed plan JSON")
    args = parser.parse_args()

    python_exe = sys.executable
    req = lambda name: os.path.join(REQ_DIR, name)

    if args.install:
        _pip(python_exe, ["install", "--upgrade", "pip"])
        _pip(python_exe, ["install", "--prefer-binary", "psutil>=5.9.0"])
        _pip(
            python_exe,
            [
                "install",
                "--prefer-binary",
                "--extra-index-url",
                "https://abetlen.github.io/llama-cpp-python/whl/cpu",
                "-r",
                req("requirements.txt"),
            ],
        )

    from hardware.detector import HardwareDetector

    detector = HardwareDetector(force_rescan=True, apply_profile=False)
    plan = compose_install_plan(detector.devices)
    print("[*] Live topology: " + detector.get_live_summary_string())
    print(
        "[*] Compose plan: primary={primary} profiles={profiles} llama={llama_wheel} "
        "coprocessor={coprocessor}".format(**plan)
    )

    if args.json:
        import json
        print(json.dumps(plan, indent=2))

    if not args.install:
        return 0

    if "intel_npu" in plan["profiles"]:
        _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements-intel-npu.txt")])
    elif any(p in plan["profiles"] for p in ("intel_igpu", "intel_dgpu")):
        _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements-intel-gpu.txt")])

    if "amd_npu" in plan["profiles"]:
        _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements-amd-npu.txt")])
    if any(p in plan["profiles"] for p in ("amd_dgpu", "amd_igpu")):
        _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements-amd-gpu.txt")])
    if "nvidia_dgpu" in plan["profiles"]:
        _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements-nvidia-gpu.txt")])

    plan["llama_wheel"] = _install_llama(python_exe, plan["llama_wheel"])
    path = save_install_profile(plan)
    print(f"[OK] Wrote composed hardware profile -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
