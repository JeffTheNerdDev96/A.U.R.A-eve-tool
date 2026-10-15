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
Survey Scanner Clipboard Parser & Mining Yield Planner for A.U.R.A. v0.7.0-alpha.1.
Parses in-game survey scanner results, computes optimal laser cycles,
depletion timers, extraction rate (m3/hr), and tracks mining session ledgers.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class SurveyScannerRock:
    ore_name: str
    units: int
    volume_m3: float
    distance_km: float


@dataclass(slots=True)
class MiningCyclePlan:
    rock_name: str
    rock_volume_m3: float
    laser_m3_per_cycle: float
    cycle_time_sec: float
    num_lasers: int
    cycles_needed: int
    total_time_sec: float
    total_time_str: str
    m3_per_hour: float


class SurveyScannerParser:
    """Parses clipboard output from the EVE Online Survey Scanner window."""

    @classmethod
    def parse(cls, text: str) -> List[SurveyScannerRock]:
        if not text or not text.strip():
            return []

        results: List[SurveyScannerRock] = []
        for line in text.strip().splitlines():
            rock = cls._parse_line(line)
            if rock:
                results.append(rock)
        return results

    parse_clipboard = parse

    @classmethod
    def _parse_line(cls, line: str) -> Optional[SurveyScannerRock]:
        clean = line.strip()
        if not clean or clean.startswith("#"):
            return None

        # Tab format: Asteroid (Veldspar) \t 1,200,000 \t 120,000 m3 \t 18.5 km
        parts = [p.strip() for p in clean.split("\t") if p.strip()]
        if len(parts) >= 3:
            raw_name = parts[0]
            if raw_name.lower() in ("ore", "name", "type", "asteroid", "item"):
                return None
            m_ore = re.search(r"\(([^)]+)\)", raw_name)
            ore_name = m_ore.group(1).strip() if m_ore else raw_name.replace("Asteroid", "").strip()
            if not ore_name or ore_name.lower() in ("ore", "name", "type", "asteroid", "item"):
                return None

            units_str = parts[1].replace(",", "").replace(".", "").replace("units", "").strip()
            units = int(units_str) if units_str.isdigit() else 0

            vol_m = re.search(r"([\d,.]+)", parts[2])
            volume_m3 = float(vol_m.group(1).replace(",", "")) if vol_m else 0.0

            if units == 0 and volume_m3 == 0.0:
                return None

            dist_km = 0.0
            if len(parts) >= 4:
                dist_m = re.search(r"([\d,.]+)", parts[3])
                if dist_m:
                    dist_km = float(dist_m.group(1).replace(",", ""))
                    if "m" in parts[3].lower() and "km" not in parts[3].lower():
                        dist_km = dist_km / 1000.0

            return SurveyScannerRock(ore_name, units, volume_m3, dist_km)

        # Regex fallback for space/comma separated lines
        m_regex = re.search(r"([A-Za-z\s]+)\s+([\d,]+)\s*(?:units)?\s+([\d,.]+)\s*m3", clean, re.IGNORECASE)
        if m_regex:
            ore_name = m_regex.group(1).strip()
            units = int(m_regex.group(2).replace(",", ""))
            volume_m3 = float(m_regex.group(3).replace(",", ""))
            return SurveyScannerRock(ore_name, units, volume_m3, 0.0)

        return None


class MiningYieldPlanner:
    """Calculates laser cycle requirements and m3/hr throughput."""

    @staticmethod
    def plan_depletion(
        rock_name: str,
        rock_volume_m3: float,
        laser_m3_per_cycle: float = 1200.0,
        cycle_time_sec: float = 180.0,
        num_lasers: int = 2,
    ) -> MiningCyclePlan:
        combined_vol_per_cycle = max(1.0, laser_m3_per_cycle * max(1, num_lasers))
        cycles = math.ceil(rock_volume_m3 / combined_vol_per_cycle)
        total_time_sec = cycles * cycle_time_sec

        mins = int(total_time_sec // 60)
        secs = int(total_time_sec % 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        cycles_per_hr = 3600.0 / cycle_time_sec if cycle_time_sec > 0 else 0.0
        m3_per_hour = combined_vol_per_cycle * cycles_per_hr

        return MiningCyclePlan(
            rock_name=rock_name,
            rock_volume_m3=round(rock_volume_m3, 2),
            laser_m3_per_cycle=laser_m3_per_cycle,
            cycle_time_sec=cycle_time_sec,
            num_lasers=num_lasers,
            cycles_needed=cycles,
            total_time_sec=total_time_sec,
            total_time_str=time_str,
            m3_per_hour=round(m3_per_hour, 1),
        )


@dataclass
class MiningLedgerRecord:
    ore_name: str
    total_units: int = 0
    total_volume_m3: float = 0.0
    cycles_count: int = 0


class MiningLedger:
    """Aggregates real-time mining events from the gamelog."""

    def __init__(self):
        self._totals: Dict[str, MiningLedgerRecord] = {}

    def record_cycle(self, ore_name: str, units: int, volume_m3: float) -> None:
        clean = ore_name.strip()
        if clean not in self._totals:
            self._totals[clean] = MiningLedgerRecord(ore_name=clean)
        rec = self._totals[clean]
        rec.total_units += units
        rec.total_volume_m3 += volume_m3
        rec.cycles_count += 1

    def get_summary(self) -> Dict[str, Any]:
        records = [
            {
                "ore": rec.ore_name,
                "units": rec.total_units,
                "m3": round(rec.total_volume_m3, 2),
                "cycles": rec.cycles_count,
            }
            for rec in self._totals.values()
        ]
        total_m3 = sum(r["m3"] for r in records)
        total_units = sum(r["units"] for r in records)
        return {
            "records": records,
            "total_m3": round(total_m3, 2),
            "total_units": total_units,
        }

    def clear(self) -> None:
        self._totals.clear()
