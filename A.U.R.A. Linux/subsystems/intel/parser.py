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
Subsystem Intel Regex Engine & Heuristic Parser.
Provides high-speed matching for system names, ship classes, cyno/bubble indicators, and threat levels.
"""

import re
from typing import Dict, List, Any, Optional
from core.eve_data import _FAST_SHIP_LOOKUP
from subsystems.map import get_eve_map
from core.input_safety import clamp_text, strip_control_chars
from .models import IntelReport

_STRIP_CHARS = ".,;:!?\"'()[]{}<>`~*|\\/\ufeff\u200b\u200e\u200f\u00a0 \t\r\n"

# RegEx patterns for counts and keywords
_RE_HAS_DIGIT = re.compile(r"\d")
_RE_COUNT_EXPLICIT_PLUS = re.compile(r"\+\s*(\d{1,3})\b")
_RE_COUNT_PLUS_SUFFIX = re.compile(r"\b(\d{1,3})\s*\+")
_RE_COUNT_WITH_KEYWORD = re.compile(
    r"\b(\d{1,3})\s*(?:x|hostiles?|reds?|pilots?|gang|man|fleet|ships?)\b|\b(?:spike|plus|gang|fleet)\s*(\d{1,3})\b",
    re.IGNORECASE
)
_RE_COUNT_X_PREFIX = re.compile(r"\bx\s*(\d{1,3})\b", re.IGNORECASE)
_RE_CLEAR = re.compile(r"\b(?:clear|clr|clean|safe)\b", re.IGNORECASE)
_RE_NV = re.compile(r"\b(?:nv|na|no\s*visual|unlocated)\b", re.IGNORECASE)

_RE_CYNO = re.compile(r"\b(?:cyno|cynos|cynou|lit|beacon|dropper|hotdrop|hot-drop)\b", re.IGNORECASE)
_RE_BUBBLE = re.compile(r"\b(?:bubble|bubbled|bubbles|drag)\b", re.IGNORECASE)

_CAPITAL_KEYWORDS = frozenset({"titan", "super", "supercarrier", "dread", "dreadnought", "carrier", "fax", "rorqual", "capital"})
_BATTLESHIP_KEYWORDS = frozenset({"battleship", "battleships", "bs", "marauder", "blops", "black ops"})
_MEDIUM_KEYWORDS = frozenset({"battlecruiser", "battlecruisers", "bc", "cruiser", "cruisers", "hac", "t3c", "recon", "command ship", "destroyer", "destroyers", "dictor", "hic"})
_FRIGATE_KEYWORDS = frozenset({"frigate", "frigates", "frig", "interceptor", "interceptors", "ceptor", "af", "covops", "bomber", "eas", "shuttle", "corvette", "rookie"})

_CAPITAL_CLASSES = frozenset({"Titan", "Supercarrier", "Dreadnought", "Carrier", "Force Auxiliary", "Lancer Dreadnought", "Faction Dreadnought", "Capital Industrial"})
_BATTLESHIP_CLASSES = frozenset({"Battleship", "Faction Battleship", "Marauder", "Black Ops"})
_MEDIUM_CLASSES = frozenset({
    "Battlecruiser", "Faction Battlecruiser", "Attack Battlecruiser", "Command Ship",
    "Cruiser", "Faction Cruiser", "Heavy Assault Cruiser", "Heavy Interdiction Cruiser",
    "Strategic Cruiser", "Combat Recon", "Force Recon", "Logistics Cruiser",
    "Destroyer", "Faction Destroyer", "Command Destroyer", "Tactical Destroyer", "Interdictor"
})
_FRIGATE_CLASSES = frozenset({
    "Frigate", "Faction Frigate", "Assault Frigate", "Interceptor", "Covert Ops",
    "Stealth Bomber", "Electronic Attack Ship", "Logistics Frigate", "Mining Frigate", "Expedition Frigate"
})


class IntelRegexParser:
    """Enhanced Intel Regex Parser with system lookup and threat calculation heuristics."""

    def __init__(self):
        self.eve_map = get_eve_map()

    def extract_pilot_count(self, text: str) -> int:
        """Extracts pilot count from line using heuristics."""
        if not _RE_HAS_DIGIT.search(text):
            return 1

        m = _RE_COUNT_EXPLICIT_PLUS.search(text)
        if m:
            return min(int(m.group(1)), 500)
        m = _RE_COUNT_PLUS_SUFFIX.search(text)
        if m:
            return min(int(m.group(1)), 500)
        m = _RE_COUNT_WITH_KEYWORD.search(text)
        if m:
            return min(int(m.group(1) or m.group(2)), 500)
        m = _RE_COUNT_X_PREFIX.search(text)
        if m:
            return min(int(m.group(1)), 500)
        return 1

    def parse_line(self, line: str, channel_name: str = "Intel") -> Optional[IntelReport]:
        """Parses a single line into an IntelReport DTO."""
        d = IntelParser.parse_single_line(line, channel_name=channel_name)
        if not d:
            return None
        return IntelReport(
            system_name=d.get("system", ""),
            reporter=d.get("speaker", "Unknown"),
            channel=d.get("channel", channel_name),
            timestamp_str=d.get("time_str", ""),
            threat_level=d.get("threat_level", "CLEAR"),
            pilots=d.get("pilots", []),
            ship_classes=d.get("ships", []),
            raw_message=d.get("clean_msg", ""),
            pilot_count=d.get("est_count", 1),
            has_cyno=d.get("has_cyno", False),
            has_bubble=d.get("has_bubble", False),
            is_clear=d.get("is_clear", False)
        )


class IntelParser:
    """Static helper and batch parser for Live Chat Monitor and UI Dialogs."""
    _instance: Optional[IntelRegexParser] = None

    @classmethod
    def _get_engine(cls) -> IntelRegexParser:
        if cls._instance is None:
            cls._instance = IntelRegexParser()
        return cls._instance

    @classmethod
    def parse_single_line(cls, line: str, channel_name: str = "Intel") -> Optional[Dict[str, Any]]:
        line = clamp_text(strip_control_chars(line or ""), 1024)
        clean_line = line.strip(" \t\r\n\ufeff\u200b\u200e\u200f\u00a0")
        if not clean_line or clean_line.startswith("---") or "Channel Name:" in clean_line or "Listener:" in clean_line or "Session Started:" in clean_line:
            return None

        speaker = "Unknown"
        timestamp_str = ""
        msg = clean_line

        if clean_line.startswith("["):
            r_bracket = clean_line.find("]")
            if r_bracket > 1:
                timestamp_str = clean_line[1:r_bracket].strip()
                rest = clean_line[r_bracket + 1:].strip()
                gt_pos = rest.find(">")
                if gt_pos > 0:
                    speaker = rest[:gt_pos].strip()
                    msg = rest[gt_pos + 1:].strip()
                else:
                    msg = rest

        words = [w.strip(_STRIP_CHARS) for w in msg.split() if w.strip(_STRIP_CHARS)]
        if not words:
            return None

        engine = cls._get_engine()
        found_system: Optional[str] = None
        for word in words:
            record = engine.eve_map.resolve_system_name(word)
            if record:
                found_system = record["name"].upper()
                break

        if not found_system:
            return None

        is_clear = bool(_RE_CLEAR.search(msg))
        has_nv = bool(_RE_NV.search(msg))
        has_cyno = bool(_RE_CYNO.search(msg))
        has_bubble = bool(_RE_BUBBLE.search(msg))

        ships: List[str] = []
        msg_lower = msg.lower()

        has_capital = any(kw in msg_lower for kw in _CAPITAL_KEYWORDS)
        has_battleship = any(kw in msg_lower for kw in _BATTLESHIP_KEYWORDS)
        has_medium_hull = any(kw in msg_lower for kw in _MEDIUM_KEYWORDS)
        has_frigate = any(kw in msg_lower for kw in _FRIGATE_KEYWORDS)

        for word in words:
            w_lower = word.lower()
            if w_lower in _FAST_SHIP_LOOKUP:
                ship_data = _FAST_SHIP_LOOKUP[w_lower]
                canonical = ship_data.get("canonical_name", word)
                if canonical and canonical not in ships:
                    ships.append(canonical)
                s_class = ship_data.get("class", "")
                if s_class in _CAPITAL_CLASSES:
                    has_capital = True
                elif s_class in _BATTLESHIP_CLASSES:
                    has_battleship = True
                elif s_class in _MEDIUM_CLASSES:
                    has_medium_hull = True
                elif s_class in _FRIGATE_CLASSES:
                    has_frigate = True

        if has_capital and "Capital" not in ships:
            ships.append("Capital")
        elif has_battleship and not any(s in ships for s in ["Battleship", "Marauder", "Black Ops"]):
            ships.append("Battleship")

        pilot_count = engine.extract_pilot_count(msg)

        status_flags = []
        if is_clear:
            threat_level = "CLEAR"
            status_flags.append("SYSTEM CLEAR")
        elif pilot_count >= 25 or has_capital:
            threat_level = "CRITICAL"
            if has_capital:
                status_flags.append("CAPITAL SPIKE")
            if pilot_count >= 25:
                status_flags.append("FLEET SPIKE (25+)")
            if has_cyno:
                status_flags.append("CYNO LIT")
            if has_bubble:
                status_flags.append("BUBBLE ON GATE")
        elif pilot_count > 10 or has_cyno or has_battleship:
            threat_level = "HIGH"
            if has_cyno:
                status_flags.append("CYNO LIT")
            if has_battleship:
                status_flags.append("BATTLESHIP CONTACT")
            if pilot_count > 10:
                status_flags.append("FLEET SPIKE (10+)")
            if has_bubble:
                status_flags.append("BUBBLE ON GATE")
        elif (pilot_count >= 2 and pilot_count <= 10) or has_medium_hull:
            threat_level = "MEDIUM"
            if pilot_count >= 2:
                status_flags.append("GANG IN LOCAL")
            elif has_medium_hull:
                status_flags.append("HOSTILE CONTACT")
            if has_bubble:
                status_flags.append("BUBBLE ON GATE")
            if has_nv:
                status_flags.append("NO VISUAL / NV")
        elif has_frigate or has_nv:
            threat_level = "LOW"
            if has_frigate:
                status_flags.append("FRIGATE CONTACT")
            if has_nv:
                status_flags.append("NO VISUAL / NV")
            if has_bubble:
                status_flags.append("BUBBLE ON GATE")
        else:
            threat_level = "LOW"
            status_flags.append("LOCAL ACTIVITY")
            if has_bubble:
                status_flags.append("BUBBLE ON GATE")

        if not status_flags:
            status_flags.append("LOCAL ACTIVITY")

        is_critical = threat_level in ("CRITICAL", "HIGH")

        return {
            "system": found_system,
            "system_name": found_system,
            "speaker": speaker,
            "reporter": speaker,
            "channel": channel_name,
            "time_str": timestamp_str,
            "timestamp": timestamp_str,
            "threat_level": threat_level,
            "pilots": [],
            "ships": ships,
            "ship_classes": ships,
            "clean_msg": msg,
            "raw_message": msg,
            "est_count": pilot_count,
            "pilot_count": pilot_count,
            "status_flags": status_flags,
            "has_cyno": has_cyno,
            "has_bubble": has_bubble,
            "is_clear": is_clear,
            "is_critical": is_critical
        }

    @classmethod
    def parse(cls, text: str, channel_name: str = "Batch.Intel") -> Dict[str, Any]:
        lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
        reports = []
        systems_seen = set()
        highest_threat = "INFO"
        threat_order = {"CLEAR": 0, "INFO": 1, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        for line in lines:
            parsed = cls.parse_single_line(line, channel_name)
            if parsed:
                reports.append(parsed)
                systems_seen.add(parsed["system"])
                lvl = parsed["threat_level"]
                if threat_order.get(lvl, 0) > threat_order.get(highest_threat, 0):
                    highest_threat = lvl

        summary_lines = [f"• **Decoded Intel Reports ({len(reports)} entries across {len(systems_seen)} solar systems):**"]
        for rep in reports[:15]:
            flags = " ".join(f"[{f}]" for f in rep.get("status_flags", []))
            ships = ", ".join(rep.get("ships", [])) or "Hostiles"
            summary_lines.append(f"  - `[{rep['time_str'] or 'LOG'}]` **{rep['system']}** ({rep['threat_level']}): {ships} (+{rep['est_count']}) {flags} — \"{rep['clean_msg']}\"")
        if len(reports) > 15:
            summary_lines.append(f"  - *(+{len(reports) - 15} additional lines decoded)*")

        return {
            "type": "intel",
            "reports": reports,
            "total_ships": len(reports),
            "threat_level": highest_threat,
            "systems": list(systems_seen),
            "summary_md": "\n".join(summary_lines)
        }
