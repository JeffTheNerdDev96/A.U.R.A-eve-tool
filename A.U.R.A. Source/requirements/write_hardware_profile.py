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
"""Write requirements/hardware_profile.json after a named hardware setup bat."""
from __future__ import annotations

import argparse
import os
import sys

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from hardware.profile import PROFILE_IDS, build_named_profile, save_install_profile  # noqa: E402


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
