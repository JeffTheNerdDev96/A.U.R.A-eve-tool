"""Write requirements/hardware_profile.json after a named hardware setup bat."""
from __future__ import annotations

import argparse
import os
import sys

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from hardware_profile import PROFILE_IDS, build_named_profile, save_install_profile  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile_id", choices=PROFILE_IDS)
    parser.add_argument("--llama-wheel", default=None, choices=["cpu", "cuda", "vulkan"])
    args = parser.parse_args()
    payload = build_named_profile(args.profile_id, llama_wheel=args.llama_wheel)
    path = save_install_profile(payload)
    print(f"[OK] Wrote install profile {payload['primary']} (llama={payload['llama_wheel']}) -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
