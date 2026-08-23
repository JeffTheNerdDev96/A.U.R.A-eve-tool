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
_RE_CLEAR = re.compile(r"\b(?:clear|clr|clean|safe|nv|na|no\s*visual)\b", re.IGNORECASE)

_RE_CYNO = re.compile(r"\b(?:cyno|cynos|cynou|lit|beacon)\b", re.IGNORECASE)
_RE_BUBBLE = re.compile(r"\b(?:bubble|bubbled|bubbles|drag)\b", re.IGNORECASE)

_CAPITAL_KEYWORDS = frozenset({"titan", "super", "supercarrier", "dread", "dreadnought", "carrier", "fax", "rorqual"})
_BATTLESHIP_KEYWORDS = frozenset({"battleship", "battleships", "bs", "marauder", "blops"})


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
        has_cyno = bool(_RE_CYNO.search(msg))
        has_bubble = bool(_RE_BUBBLE.search(msg))

        ships: List[str] = []
        msg_lower = msg.lower()

        for kw in _CAPITAL_KEYWORDS:
            if kw in msg_lower and "Capital" not in ships:
                ships.append("Capital")
        for kw in _BATTLESHIP_KEYWORDS:
            if kw in msg_lower and "Battleship" not in ships:
                ships.append("Battleship")

        for word in words:
            w_lower = word.lower()
            if w_lower in _FAST_SHIP_LOOKUP:
                canonical = _FAST_SHIP_LOOKUP[w_lower].get("canonical_name", word)
                if canonical and canonical not in ships:
                    ships.append(canonical)

        pilot_count = engine.extract_pilot_count(msg)

        status_flags = []
        if is_clear:
            threat_level = "CLEAR"
            status_flags.append("SYSTEM CLEAR")
        elif has_cyno:
            threat_level = "CRITICAL"
            status_flags.append("CYNO LIT")
        elif "Capital" in ships:
            threat_level = "CRITICAL"
            status_flags.append("CAPITAL SPIKE")
        elif pilot_count >= 10:
            threat_level = "CRITICAL"
            status_flags.append("FLEET SPIKE")
        elif has_bubble:
            threat_level = "HIGH"
            status_flags.append("BUBBLE ON GATE")
        elif "Battleship" in ships or "Marauder" in ships:
            threat_level = "HIGH"
            status_flags.append("BATTLESHIP CONTACT")
        elif pilot_count >= 3:
            threat_level = "MEDIUM"
            status_flags.append("GANG IN LOCAL")
        elif ships:
            threat_level = "MEDIUM"
            status_flags.append("HOSTILE CONTACT")
        else:
            threat_level = "INFO"
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
