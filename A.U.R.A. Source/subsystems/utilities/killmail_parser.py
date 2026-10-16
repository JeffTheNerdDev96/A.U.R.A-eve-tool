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
Killmail Clipboard Parser & EFT Fit Exporter for A.U.R.A. v0.7.1-alpha.4.
Parses in-game kill report copy text and zKillboard exports, extracts destroyed
and dropped modules, and reconstructs EFT-compliant ship fittings.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from core.eve_data import lookup_module
from core.eve_modules_data import CANONICAL_MODULES
from core.input_safety import parse_float_safe


@dataclass(slots=True)
class ParsedKillmail:
    victim_name: str = "Unknown Pilot"
    ship_type: str = "Unknown Ship"
    solar_system: str = "Unknown System"
    total_value_isk: float = 0.0
    high_slots: List[str] = field(default_factory=list)
    med_slots: List[str] = field(default_factory=list)
    low_slots: List[str] = field(default_factory=list)
    rig_slots: List[str] = field(default_factory=list)
    subsystems: List[str] = field(default_factory=list)
    cargo: List[str] = field(default_factory=list)
    eft_format: str = ""

    @property
    def ship_name(self) -> str:
        return self.ship_type

    @property
    def eft_fit(self) -> str:
        return self.eft_format


class KillmailParser:
    """Parses raw text of EVE kill reports and reconstructs EFT fitting blocks."""

    @classmethod
    def parse_clipboard(cls, text: str) -> Optional[ParsedKillmail]:
        if not text or not text.strip():
            return None

        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

        victim_name = "Unknown Pilot"
        ship_type = "Unknown Ship"
        solar_system = "Unknown System"
        total_value = 0.0

        highs: List[str] = []
        mids: List[str] = []
        lows: List[str] = []
        rigs: List[str] = []
        subsystems: List[str] = []
        cargo: List[str] = []

        current_section = "unknown"

        for line in lines:
            line_lower = line.lower()

            # Metadata matches
            if line_lower.startswith("victim:") or line_lower.startswith("character:"):
                victim_name = line.split(":", 1)[1].strip()
                continue
            if line_lower.startswith("ship:") or line_lower.startswith("destroyed:"):
                ship_type = line.split(":", 1)[1].strip()
                continue
            if line_lower.startswith("system:"):
                solar_system = line.split(":", 1)[1].strip()
                continue
            if "total value:" in line_lower or "value:" in line_lower:
                m_val = re.search(r"([\d,.\s\u00a0\u202f]+?)(?:\s*isk|\s*$)", line, re.IGNORECASE)
                if m_val:
                    total_value = parse_float_safe(m_val.group(1))
                continue

            # Section headers
            if "high power slots" in line_lower or line_lower.startswith("[high"):
                current_section = "high"
                continue
            elif "medium power slots" in line_lower or line_lower.startswith("[med"):
                current_section = "med"
                continue
            elif "low power slots" in line_lower or line_lower.startswith("[low"):
                current_section = "low"
                continue
            elif "rig slots" in line_lower or line_lower.startswith("[rig"):
                current_section = "rig"
                continue
            elif "subsystem slots" in line_lower or line_lower.startswith("[subsystem"):
                current_section = "subsystem"
                continue
            elif "cargo" in line_lower or "drone bay" in line_lower or line_lower.startswith("[cargo"):
                current_section = "cargo"
                continue

            # Strip item quantities / dropped status: e.g. "Scourge Heavy Missile (500)" or "Damage Control II, Dropped"
            clean_item = re.sub(r"\s*\([^)]*\)", "", line)
            clean_item = re.sub(r",\s*(?:Dropped|Destroyed|Fitted|Cargo)", "", clean_item, flags=re.IGNORECASE).strip()

            if not clean_item or clean_item.startswith("---") or clean_item.startswith("==="):
                continue

            # If inside an explicit section, add to that section
            if current_section == "high":
                highs.append(clean_item)
            elif current_section == "med":
                mids.append(clean_item)
            elif current_section == "low":
                lows.append(clean_item)
            elif current_section == "rig":
                rigs.append(clean_item)
            elif current_section == "subsystem":
                subsystems.append(clean_item)
            elif current_section == "cargo":
                cargo.append(clean_item)
            else:
                # If section unknown, deduce rack from CANONICAL_MODULES
                rack = cls._deduce_slot(clean_item)
                if rack == "high":
                    highs.append(clean_item)
                elif rack == "med":
                    mids.append(clean_item)
                elif rack == "low":
                    lows.append(clean_item)
                elif rack == "rig":
                    rigs.append(clean_item)
                elif rack == "subsystem":
                    subsystems.append(clean_item)
                else:
                    cargo.append(clean_item)

        eft = cls._build_eft(ship_type, victim_name, lows, mids, highs, rigs, subsystems)

        return ParsedKillmail(
            victim_name=victim_name,
            ship_type=ship_type,
            solar_system=solar_system,
            total_value_isk=total_value,
            high_slots=highs,
            med_slots=mids,
            low_slots=lows,
            rig_slots=rigs,
            subsystems=subsystems,
            cargo=cargo,
            eft_format=eft,
        )

    @staticmethod
    def _deduce_slot(item_name: str) -> str:
        if not item_name or not item_name.strip():
            return "cargo"
        clean = item_name.strip()
        mod = CANONICAL_MODULES.get(clean)
        if not mod:
            mod = lookup_module(clean)
        if mod and "slot" in mod:
            s = str(mod["slot"]).lower()
            return "med" if s == "mid" else s

        return "cargo"

    @staticmethod
    def _build_eft(
        ship: str,
        pilot: str,
        lows: List[str],
        mids: List[str],
        highs: List[str],
        rigs: List[str],
        subsystems: List[str],
    ) -> str:
        lines: List[str] = [f"[{ship}, {pilot}'s Reconstructed Fit]"]

        for l in lows:
            lines.append(l)
        lines.append("")

        for m in mids:
            lines.append(m)
        lines.append("")

        for h in highs:
            lines.append(h)
        lines.append("")

        for r in rigs:
            lines.append(r)

        if subsystems:
            lines.append("")
            for s in subsystems:
                lines.append(s)

        return "\n".join(lines).strip()
