"""
Subsystem Intel Regex Engine & Heuristic Parser.
Provides high-speed matching for system names, ship classes, cyno/bubble indicators, and threat levels.
"""

import re
from typing import Dict, List, Any, Optional
from core.eve_data import _FAST_SHIP_LOOKUP, SHIP_DATABASE
from subsystems.map import get_eve_map
from core.input_safety import clamp_text, strip_control_chars, safe_display_text
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
        line = clamp_text(strip_control_chars(line or ""), 1024)
        clean_line = line.strip(_STRIP_CHARS)
        if not clean_line or clean_line.startswith("---") or "Channel Name:" in clean_line or "Listener:" in clean_line:
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

        words = [w.strip(_STRIP_CHARS) for w in msg.split() if w.strip(_STRIP_CHARS)]
        if not words:
            return None

        # System lookup via EVE map graph
        found_system: Optional[str] = None
        for word in words:
            record = self.eve_map.resolve_system_name(word)
            if record:
                found_system = record["name"].upper()
                break

        if not found_system:
            return None

        # Check clear / NV status
        is_clear = bool(_RE_CLEAR.search(msg))
        has_cyno = bool(_RE_CYNO.search(msg))
        has_bubble = bool(_RE_BUBBLE.search(msg))

        # Ship class extraction
        ship_classes: List[str] = []
        msg_lower = msg.lower()

        for kw in _CAPITAL_KEYWORDS:
            if kw in msg_lower and "Capital" not in ship_classes:
                ship_classes.append("Capital")
        for kw in _BATTLESHIP_KEYWORDS:
            if kw in msg_lower and "Battleship" not in ship_classes:
                ship_classes.append("Battleship")

        for word in words:
            w_lower = word.lower()
            if w_lower in _FAST_SHIP_LOOKUP:
                cls_name = _FAST_SHIP_LOOKUP[w_lower].get("class", "")
                if cls_name and cls_name not in ship_classes:
                    ship_classes.append(cls_name)

        pilot_count = self.extract_pilot_count(msg)

        # Threat Level Calculation
        if is_clear:
            threat_level = "CLEAR"
        elif has_cyno or "Capital" in ship_classes or pilot_count >= 10:
            threat_level = "CRITICAL"
        elif has_bubble or "Battleship" in ship_classes or pilot_count >= 3:
            threat_level = "HOSTILE"
        else:
            threat_level = "SUSPICIOUS"

        return IntelReport(
            system_name=found_system,
            reporter=speaker,
            channel=channel_name,
            timestamp_str=timestamp_str,
            threat_level=threat_level,
            pilots=[],
            ship_classes=ship_classes,
            raw_message=msg,
            pilot_count=pilot_count,
            has_cyno=has_cyno,
            has_bubble=has_bubble,
            is_clear=is_clear
        )
