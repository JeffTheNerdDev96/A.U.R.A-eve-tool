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

from hardware import HardwareDetector  # noqa: E402
from hardware_profile import compose_install_plan, save_install_profile  # noqa: E402


def _pip(python_exe: str, args: list[str]) -> int:
    cmd = [python_exe, "-m", "pip", *args]
    print("[*] " + " ".join(cmd))
    return subprocess.call(cmd)


def _install_llama(python_exe: str, wheel: str) -> str:
    indexes = {
        "cuda": "https://abetlen.github.io/llama-cpp-python/whl/cu124",
        "vulkan": "https://abetlen.github.io/llama-cpp-python/whl/vulkan",
        "cpu": "https://abetlen.github.io/llama-cpp-python/whl/cpu",
    }
    extra = indexes.get(wheel, indexes["cpu"])
    code = _pip(
        python_exe,
        [
            "install",
            "llama-cpp-python",
            "--upgrade",
            "--force-reinstall",
            "--no-cache-dir",
            "--extra-index-url",
            extra,
        ],
    )
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
    return wheel if code == 0 else "cpu"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install composed stacks into this Python")
    parser.add_argument("--json", action="store_true", help="Print composed plan JSON")
    args = parser.parse_args()

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

    python_exe = sys.executable
    req = lambda name: os.path.join(REQ_DIR, name)

    _pip(python_exe, ["install", "--prefer-binary", "-r", req("requirements.txt")])

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
