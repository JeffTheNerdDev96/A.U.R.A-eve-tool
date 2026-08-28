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
EVE Online Directional Scanner (D-Scan) Parser & Class Breakdown Engine.
Parses in-game clipboard copy-pastes into structured class-grouped tactical matrices.
"""

from __future__ import annotations

import re
from typing import Dict, List, Any, Optional

from core.eve_data import (
    lookup_ship, SHIP_DATABASE,
    THREAT_BUBBLE, THREAT_CYNO, THREAT_ECM, THREAT_MARAUDER,
    THREAT_CAPITAL, THREAT_SUPER, THREAT_LOGI, THREAT_PIRATE,
)
from .models import DScanEntry, DScanClassSummary, DScanAnalysis

_RE_QTY_PREFIX = re.compile(r"^(\d+)\s*[xX*]\s*(.+)$")
_RE_QTY_SUFFIX = re.compile(r"^(.*?)\s+[xX*]\s*(\d+)$")
_RE_QTY_LEADING = re.compile(r"^(\d+)\s+([A-Za-z].+)$")
_RE_TAB_SPLIT = re.compile(r"\t+|\s{2,}")
_RE_DELIM_SPLIT = re.compile(r"[\t,;|]+")
_RE_DIST_AU = re.compile(r"([\d\.,]+)\s*au\b", re.IGNORECASE)
_RE_DIST_KM = re.compile(r"([\d\.,]+)\s*km\b", re.IGNORECASE)
_RE_DIST_M = re.compile(r"([\d\.,]+)\s*m\b", re.IGNORECASE)
_RE_CHAT_TIME = re.compile(r"^\d{1,2}:\d{2}")

_SORTED_HULLS_BY_LENGTH = sorted(SHIP_DATABASE.keys(), key=len, reverse=True)
_SHIP_SUBSTR_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(h.lower()) for h in _SORTED_HULLS_BY_LENGTH) + r")\b"
)
_RE_DIST_TOKEN = re.compile(r"^[\d\.,\s]+(?:km|au|m)?$", re.IGNORECASE)


def _is_dist_or_id(token: str) -> bool:
    t = token.strip().lower()
    if not t or t == "-":
        return True
    if t.isdigit():
        return True
    if _RE_DIST_TOKEN.match(t):
        return True
    return False


class DScanParser:
    """Parses raw in-game D-Scan clipboard data into ship-class tactical breakdowns."""

    @staticmethod
    def _extract_quantity_and_clean(text: str) -> tuple[int, str]:
        """Extracts quantity like '5x', 'x5', '5 Sabre' and returns (count, clean_text)."""
        clean = text.strip()
        count = 1

        # Match '5x Sabre' or '5x'
        m1 = _RE_QTY_PREFIX.match(clean)
        if m1:
            try:
                count = max(1, int(m1.group(1)))
                clean = m1.group(2).strip()
            except Exception:
                pass
            return count, clean

        # Match 'Sabre x5' or 'Sabre 5x'
        m2 = _RE_QTY_SUFFIX.search(clean)
        if m2:
            try:
                count = max(1, int(m2.group(2)))
                clean = m2.group(1).strip()
            except Exception:
                pass
            return count, clean

        # Match leading number e.g. '5 Sabre'
        m3 = _RE_QTY_LEADING.match(clean)
        if m3:
            try:
                potential_count = int(m3.group(1))
                if potential_count < 200:  # Avoid matching item IDs like 11987
                    if lookup_ship(m3.group(2).strip()):
                        count = potential_count
                        clean = m3.group(2).strip()
            except Exception:
                pass

        return count, clean

    @staticmethod
    def _find_ship_in_text(text: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Finds the best matching ship hull from any arbitrary text line or token list."""
        if not text:
            return None

        # 1. Direct exact lookup
        info = lookup_ship(text)
        if info:
            return info.get("canonical_name", text), info

        # 2. Fast split if tab present
        if "\t" in text:
            for p in text.split("\t"):
                p_clean = p.strip()
                if not p_clean or _is_dist_or_id(p_clean):
                    continue
                info = lookup_ship(p_clean)
                if info:
                    return info.get("canonical_name", p_clean), info

        # 3. Check parts split by tab or multiple spaces
        parts = [p.strip() for p in _RE_TAB_SPLIT.split(text) if p.strip()]
        for p in parts:
            if not p or _is_dist_or_id(p):
                continue
            info = lookup_ship(p)
            if info:
                return info.get("canonical_name", p), info

        # 4. Check individual tokens
        words = [w.strip() for w in _RE_DELIM_SPLIT.split(text) if w.strip()]
        for w in words:
            if not w or _is_dist_or_id(w):
                continue
            info = lookup_ship(w)
            if info:
                return info.get("canonical_name", w), info

        # 5. Search for known ship names inside the string
        text_lower = text.lower()
        match = _SHIP_SUBSTR_PATTERN.search(text_lower)
        if match:
            matched_lower = match.group(1)
            info = lookup_ship(matched_lower)
            if info:
                return info.get("canonical_name", matched_lower.capitalize()), info

        return None

    @staticmethod
    def _parse_distance(text: str) -> tuple[str, str, Optional[float]]:
        """Parses distance string and returns (display_distance, category, km_val)."""
        clean = text.strip()

        # Check for AU
        m_au = _RE_DIST_AU.search(clean)
        if m_au:
            try:
                au_val = float(m_au.group(1).replace(",", ""))
                return f"{au_val:.1f} AU", "Off-Grid / Warping (> 150 km / AU)", au_val * 149597870.7
            except Exception:
                return clean, "Off-Grid / Warping (> 150 km / AU)", None

        # Check for km
        m_km = _RE_DIST_KM.search(clean)
        if m_km:
            try:
                km_val = float(m_km.group(1).replace(",", ""))
                if km_val <= 20:
                    return f"{km_val:,.0f} km", "Point Range (<= 20 km)", km_val
                elif km_val <= 150:
                    return f"{km_val:,.0f} km", "Grid Range (20 - 150 km)", km_val
                else:
                    return f"{km_val:,.0f} km", "Off-Grid / Warping (> 150 km / AU)", km_val
            except Exception:
                return clean, "Grid Range (20 - 150 km)", None

        # Check for meters
        m_m = _RE_DIST_M.search(clean)
        if m_m and not m_km and not m_au:
            try:
                m_val = float(m_m.group(1).replace(",", ""))
                km_val = m_val / 1000.0
                return f"{m_val:,.0f} m", "Point Range (<= 20 km)", km_val
            except Exception:
                return clean, "Point Range (<= 20 km)", None

        return "D-Scan Sphere (< 14.3 AU)", "D-Scan Sphere (< 14.3 AU)", None

    @classmethod
    def parse_dscan(cls, raw_text: str) -> DScanAnalysis:
        """
        Parses raw D-Scan text and groups vessels into class summaries:
        e.g. Heavy Assault Cruiser : 3 : Muninn, Cerberus x2
        """
        lines = [line.strip() for line in (raw_text or "").split("\n") if line.strip()]

        raw_entries: List[DScanEntry] = []
        ship_counts: Dict[str, int] = {}
        class_to_ships: Dict[str, Dict[str, int]] = {}
        class_distances: Dict[str, List[str]] = {}
        class_threats: Dict[str, str] = {}

        range_brackets = {
            "Point Range (<= 20 km)": 0,
            "Grid Range (20 - 150 km)": 0,
            "Off-Grid / Warping (> 150 km / AU)": 0,
            "D-Scan Sphere (< 14.3 AU)": 0,
        }

        for line in lines:
            if "," in line and not ("\t" in line):
                sub_entries = [e.strip() for e in line.split(",") if e.strip()]
            else:
                sub_entries = [line]

            for entry in sub_entries:
                qty, clean_entry = cls._extract_quantity_and_clean(entry)
                ship_match = cls._find_ship_in_text(clean_entry)
                dist_str, dist_cat, dist_km = cls._parse_distance(clean_entry)

                if ship_match:
                    ship_name, ship_info = ship_match
                    ship_class = ship_info.get("class", "Combat Vessel")
                    threat = ship_info.get("threat", "COMBATANT")
                    role = ship_info.get("role", "")
                    tactics = ship_info.get("tactics", "")

                    ship_counts[ship_name] = ship_counts.get(ship_name, 0) + qty
                    range_brackets[dist_cat] = range_brackets.get(dist_cat, 0) + qty

                    if ship_class not in class_to_ships:
                        class_to_ships[ship_class] = {}
                        class_distances[ship_class] = []
                        class_threats[ship_class] = threat

                    class_to_ships[ship_class][ship_name] = (
                        class_to_ships[ship_class].get(ship_name, 0) + qty
                    )
                    if dist_str not in class_distances[ship_class]:
                        class_distances[ship_class].append(dist_str)

                    raw_entries.append(
                        DScanEntry(
                            name=ship_name,
                            item_type=ship_name,
                            ship_class=ship_class,
                            distance_str=dist_str,
                            distance_km=dist_km,
                            count=qty,
                            threat_level=threat,
                            is_ship=True,
                            role=role,
                            tactics=tactics,
                        )
                    )

        total_ships = sum(ship_counts.values())

        # Build class summaries: Example "Heavy Assault Cruiser : 3 : Muninn, Cerberus x2"
        class_summaries: List[DScanClassSummary] = []
        class_counts: Dict[str, int] = {}

        for ship_class, ships_in_class in sorted(class_to_ships.items()):
            cls_total = sum(ships_in_class.values())
            class_counts[ship_class] = cls_total

            # Format items: e.g. "Muninn, Cerberus x2"
            formatted_types: List[str] = []
            for s_name, s_qty in sorted(ships_in_class.items(), key=lambda x: (-x[1], x[0])):
                if s_qty > 1:
                    formatted_types.append(f"{s_name} x{s_qty}")
                else:
                    formatted_types.append(s_name)

            types_str = ", ".join(formatted_types)
            breakdown_line = f"{ship_class} : {cls_total} : {types_str}"

            class_summaries.append(
                DScanClassSummary(
                    ship_class=ship_class,
                    total_count=cls_total,
                    ship_counts=ships_in_class,
                    breakdown_str=breakdown_line,
                    primary_threat=class_threats.get(ship_class, "COMBATANT"),
                    sample_distances=class_distances.get(ship_class, []),
                )
            )

        # Threat evaluation score
        threat_level = "CLEAR"
        threat_color = "#34d399"

        if any(e.threat_level in [THREAT_SUPER, THREAT_CAPITAL] for e in raw_entries):
            threat_level = "CRITICAL (CAPITAL / TITAN OMNI-THREAT)"
            threat_color = "#ff4d6d"
        elif any(e.threat_level in [THREAT_BUBBLE, THREAT_CYNO, THREAT_MARAUDER] for e in raw_entries):
            threat_level = "RED (HIGH COMBAT / TACKLE THREAT)"
            threat_color = "#f87171"
        elif any(e.threat_level in [THREAT_ECM, THREAT_LOGI, THREAT_PIRATE] for e in raw_entries) or total_ships >= 4:
            threat_level = "AMBER (EWAR / FLEET THREAT)"
            threat_color = "#fbbf24"
        elif total_ships > 0:
            threat_level = "YELLOW (ACTIVE HOSTILES)"
            threat_color = "#facc15"

        # Build human-readable formatted summary text
        summary_lines = [
            f"📡 **D-Scan Readout: {total_ships} Hostile Vessels Detected** (`{threat_level}`)",
            "",
        ]
        for cs in class_summaries:
            summary_lines.append(f"• **{cs.breakdown_str}**")

        return DScanAnalysis(
            total_ships=total_ships,
            class_summaries=class_summaries,
            ship_counts=ship_counts,
            class_counts=class_counts,
            threat_level=threat_level,
            threat_color=threat_color,
            range_brackets=range_brackets,
            raw_entries=raw_entries,
            summary_text="\n".join(summary_lines),
        )
