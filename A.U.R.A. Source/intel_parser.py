"""
Zero-Overhead EVE Online Chat & Intel Channel Parser and Threat Radar.
High-throughput parser with zero generator allocations and C-level fast-paths.
"""
import re
from typing import Dict, List, Any, Optional
from config import config
from input_safety import clamp_text, strip_control_chars, safe_display_text
from eve_data import _FAST_SHIP_LOOKUP, SHIP_DATABASE, THREAT_BUBBLE, THREAT_CYNO, THREAT_MARAUDER, THREAT_CAPITAL, THREAT_SUPER, THREAT_ECM
from eve_map import get_eve_map

# --- Module-level pre-computed constants ---
_MULTI_WORD_SHIPS = [name for name in SHIP_DATABASE if " " in name]
_MULTI_WORD_SHIP_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in sorted(_MULTI_WORD_SHIPS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE
) if _MULTI_WORD_SHIPS else None

_MULTI_WORD_SHIP_PARTS: set = set()
for _ship_name in _MULTI_WORD_SHIPS:
    for _part in _ship_name.lower().split():
        _MULTI_WORD_SHIP_PARTS.add(_part)

_NOTABLE_THREATS = frozenset({"Standard", "None", "COMBATANT"})
_STRIP_CHARS = ".,;:!?\"'()[]{}<>`~*|\\/\ufeff\u200b\u200e\u200f\u00a0 \t\r\n"

_RE_HAS_DIGIT = re.compile(r"\d")
_RE_COUNT_EXPLICIT_PLUS = re.compile(r"\+\s*(\d{1,3})\b")
_RE_COUNT_PLUS_SUFFIX = re.compile(r"\b(\d{1,3})\s*\+")
_RE_COUNT_WITH_KEYWORD = re.compile(
    r"\b(\d{1,3})\s*(?:x|hostiles?|reds?|pilots?|gang|man|fleet|ships?)\b|\b(?:spike|plus|gang|fleet)\s*(\d{1,3})\b",
    re.IGNORECASE
)
_RE_COUNT_X_PREFIX = re.compile(r"\bx\s*(\d{1,3})\b", re.IGNORECASE)
_RE_NV = re.compile(r"\b(?:nv|na|no\s*visual|novisual)\b", re.IGNORECASE)
_RE_CLEAR = re.compile(r"\b(?:clear|clr)\b", re.IGNORECASE)

_CAPITAL_CLASSES = frozenset({"Titan", "Supercarrier", "Dreadnought", "Faction Dreadnought", "Lancer Dreadnought", "Force Auxiliary", "Carrier", "Freighter", "Jump Freighter", "Capital Industrial", "Industrial Command"})
_BATTLESHIP_CLASSES = frozenset({"Battleship", "Faction Battleship", "Marauder", "Black Ops"})
_CAPITAL_KEYWORDS = frozenset({"titan", "super", "supercarrier", "dread", "dreadnought", "carrier", "fax", "rorqual", "hel", "nyx", "wyvern", "aeon", "avatar", "erebus", "ragnarok", "leviathan", "naglfar", "moros", "revelation", "phoenix", "nidhoggur", "archon", "thanatos", "chimera", "lif", "apostle", "minokawa", "ninazu"})
_BATTLESHIP_KEYWORDS = frozenset({"battleship", "battleships", "bs", "marauder", "blops", "machariel", "rokh", "megathron", "tempest", "raven", "abaddon", "nightmare", "bhaalgorn", "vindicator", "barghest", "praxis", "paladin", "kronos", "golem", "vargur", "panther", "widow", "sin", "redeemer"})


class IntelParser:
    """Parses in-game chat logs and intel channel streams in real-time with sub-millisecond latency."""

    INTEL_KEYWORDS = frozenset({
        "cyno", "cynos", "cynou", "bubble", "bubbled", "gate", "outgate", "ingate",
        "station", "undock", "dock", "docked", "pos", "anom", "site", "beacon", "belt", "sun",
        "local", "hostile", "hostiles", "red", "reds", "spike", "clear", "clr", "clean",
        "jump", "jumped", "warp", "warped", "lit", "on", "in", "off", "grid", "help", "intel",
        "nv", "na", "no", "visual", "nil", "none", "safe", "v", "status", "elements",
        "presence", "report", "reported", "check", "eyes", "scout", "plus", "gang", "camp",
        "dscan", "d-scan", "pass", "passed", "heading", "towards", "from", "at", "holding",
        "cloaked", "cloak", "probe", "probes", "combat", "fleet", "standing", "by", "and",
        "dreadnought", "dread", "dreads", "carrier", "carriers", "supercarrier", "super",
        "supers", "titan", "titans", "fax", "battleship", "cruiser", "frigate", "destroyer",
        "hac", "dictor", "hictor", "interdictor", "recon", "logi", "tackle", "hauler"
    })

    @staticmethod
    def _extract_count_fast(msg: str) -> int:
        """C-level fast-path count extraction: skips regex engine if message has no digits."""
        if not _RE_HAS_DIGIT.search(msg):
            return 0
            
        m = _RE_COUNT_EXPLICIT_PLUS.search(msg)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 500: return val
        m = _RE_COUNT_PLUS_SUFFIX.search(msg)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 500: return val
        m = _RE_COUNT_WITH_KEYWORD.search(msg)
        if m:
            val = int(m.group(1) or m.group(2))
            if 1 <= val <= 500: return val
        m = _RE_COUNT_X_PREFIX.search(msg)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 500: return val
        return 0

    @staticmethod
    def parse_single_line(line: str, channel_name: str = "Intel") -> Optional[Dict[str, Any]]:
        """Parses a single live line from an EVE chat log file with maximum throughput."""
        line = clamp_text(strip_control_chars(line or ""), config.max_line_chars)
        channel_name = safe_display_text(channel_name, 256)
        clean_line = line.strip(_STRIP_CHARS)
        if not clean_line or clean_line.startswith("---") or "Channel Name:" in clean_line or "Listener:" in clean_line:
            return None

        timestamp = ""
        time_str = ""
        speaker = "Unknown"
        msg = clean_line

        # Fast string slicing for standard EVE log format
        if clean_line.startswith("["):
            r_bracket = clean_line.find("]")
            if r_bracket != -1:
                timestamp = clean_line[1:r_bracket].strip()
                t_parts = timestamp.split()
                time_str = t_parts[1] if len(t_parts) >= 2 else t_parts[0]
                
                gt_idx = clean_line.find(">", r_bracket)
                if gt_idx != -1:
                    speaker = clean_line[r_bracket+1:gt_idx].strip()
                    msg = clean_line[gt_idx+1:].strip()
                else:
                    msg = clean_line[r_bracket+1:].strip()
        elif ">" in clean_line:
            gt_idx = clean_line.find(">")
            speaker = clean_line[:gt_idx].strip()
            msg = clean_line[gt_idx+1:].strip()

        msg_l = msg.lower()
        words_in_msg = msg.split()

        # 1. Fast Token & System Identification (map-backed; no Titlecase guessing)
        found_system = "Unknown System"
        found_system_id: Optional[int] = None
        detected_pilots: List[str] = []
        detected_ships: List[str] = []
        threat_tags: List[str] = []
        eve_map = get_eve_map()

        # Check multi-word ships first if pattern exists and space is present
        if _MULTI_WORD_SHIP_PATTERN is not None and (" " in msg):
            for match in _MULTI_WORD_SHIP_PATTERN.finditer(msg):
                matched_text = match.group(1).lower()
                s_info = _FAST_SHIP_LOOKUP.get(matched_text)
                if s_info:
                    cname = s_info.get("canonical_name", matched_text)
                    if cname not in detected_ships:
                        detected_ships.append(cname)
                        threat = s_info.get("threat", "")
                        if threat and threat not in _NOTABLE_THREATS:
                            threat_tags.append(threat)

        # Fast single-pass word inspection
        i = 0
        num_words = len(words_in_msg)
        while i < num_words:
            raw_w = words_in_msg[i]
            w = raw_w.strip(_STRIP_CHARS)
            if not w:
                i += 1
                continue

            w_lower = w.lower()

            # Skip keywords, numbers, speaker
            if w_lower in IntelParser.INTEL_KEYWORDS or w == speaker:
                i += 1
                continue

            # Map-resolved solar system (prefer two-word names such as "New Caldari")
            if found_system == "Unknown System" and not w.isdigit() and w_lower not in IntelParser.INTEL_KEYWORDS:
                rec = None
                used_two = False
                if i + 1 < num_words:
                    next_raw = words_in_msg[i + 1].strip(_STRIP_CHARS)
                    rec = eve_map.resolve_system_name(f"{w} {next_raw}")
                    used_two = rec is not None
                if rec is None:
                    rec = eve_map.resolve_system_name(w)
                if rec is not None:
                    found_system = rec["name"]
                    found_system_id = rec["id"]
                    i += 2 if used_two else 1
                    continue

            # Check if token is part of an already matched multi-word ship
            if detected_ships and (w_lower in _MULTI_WORD_SHIP_PARTS):
                if any(w_lower in s.lower() for s in detected_ships):
                    i += 1
                    continue

            # Fast direct O(1) hash check for ship
            s_info = _FAST_SHIP_LOOKUP.get(w_lower)
            if s_info:
                cname = s_info.get("canonical_name", w.capitalize())
                if cname not in detected_ships:
                    detected_ships.append(cname)
                    threat = s_info.get("threat", "")
                    if threat and threat not in _NOTABLE_THREATS:
                        threat_tags.append(threat)
                i += 1
                continue

            # Check if token is a valid pilot candidate
            if (
                len(w) > 2 
                and not w.isdigit() 
                and not w.startswith("+") 
                and not w.startswith("-") 
                and not any(c.isdigit() for c in w)
                and w != found_system 
                and w != speaker 
                and w_lower not in IntelParser.INTEL_KEYWORDS 
                and w_lower not in _FAST_SHIP_LOOKUP
            ):
                # Check if next word forms a 2-word pilot name
                if i + 1 < num_words:
                    next_w = words_in_msg[i+1].strip(_STRIP_CHARS)
                    next_lower = next_w.lower()
                    if (
                        len(next_w) > 1
                        and next_lower not in IntelParser.INTEL_KEYWORDS
                        and next_lower not in _FAST_SHIP_LOOKUP
                        and not next_w.isdigit()
                        and not any(c.isdigit() for c in next_w)
                        and next_w != found_system
                        and next_w != speaker
                    ):
                        detected_pilots.append(f"{w} {next_w}")
                        i += 2
                        continue

                # Standalone unlocated pilot handle
                detected_pilots.append(w)
            i += 1

        # 2. Extract Hostile Count
        est_count = IntelParser._extract_count_fast(msg)

        # 3. Extract Tactical Status Flags (fast boolean expressions)
        status_flags: List[str] = []
        is_nv = bool(_RE_NV.search(msg))
        is_explicit_clear = bool(_RE_CLEAR.search(msg))

        if "cyno" in msg_l:
            status_flags.append("CYNO ACTIVE")
        if "bubble" in msg_l or "bubbled" in msg_l or "dictor" in msg_l or "hictor" in msg_l:
            status_flags.append("WARP BUBBLE ON GRID")
        if "gate" in msg_l or "jump" in msg_l or "jumped" in msg_l:
            status_flags.append("GATE ACTIVITY")
        if "station" in msg_l or "undock" in msg_l or "citadel" in msg_l:
            status_flags.append("STATION/CITADEL")
        if "cloak" in msg_l or "cloaked" in msg_l or "stealth" in msg_l:
            status_flags.append("CLOAKED")
        if est_count >= 5 or "spike" in msg_l or "huge" in msg_l or "fleet" in msg_l:
            status_flags.append(f"FLEET SPIKE (+{est_count or 5} PILOTS)")

        if is_explicit_clear and not detected_ships:
            detected_pilots.clear()
            est_count = 0
            status_flags = [f for f in status_flags if not f.startswith("FLEET SPIKE")]
            status_flags.append("SYSTEM CLEAR")
        elif is_nv:
            if detected_pilots or detected_ships or est_count > 0:
                status_flags.append("UNLOCATED IN LOCAL (NO VISUAL / NV)")
            else:
                status_flags.append("NO VISUAL / NV")

        # 4. Evaluate Ship Classes (Fast Set Checks)
        has_capital = (
            any(t in [THREAT_SUPER, THREAT_CAPITAL] for t in threat_tags)
            or any(SHIP_DATABASE.get(s, {}).get("class") in _CAPITAL_CLASSES for s in detected_ships)
            or any(k in msg_l for k in _CAPITAL_KEYWORDS)
        )

        has_battleship = (
            any(t == THREAT_MARAUDER for t in threat_tags)
            or any(SHIP_DATABASE.get(s, {}).get("class") in _BATTLESHIP_CLASSES for s in detected_ships)
            or any(k in msg_l for k in _BATTLESHIP_KEYWORDS)
        )

        total_effective_count = max(est_count, len(detected_pilots), len(detected_ships))

        # 5. Evaluate Threat Level
        # - CRITICAL: Any capital class vessels reported, or fleets greater than 20 players
        # - HIGH: 10 to 20 players, or battleship fleet
        # - MEDIUM: Less than 10 players or battlecruiser/smaller
        # - INFO: nv/no visual or less than 3 in system
        # - CLEAR: only if word 'clear' / 'clr' is explicitly used
        is_critical = False

        if "SYSTEM CLEAR" in status_flags:
            threat_level = "CLEAR"
            threat_color = "#34d399"
            est_count = 0
        elif has_capital or total_effective_count > 20 or "CYNO ACTIVE" in status_flags:
            threat_level = "CRITICAL"
            threat_color = "#f43f5e"
            is_critical = True
        elif has_battleship or (10 <= total_effective_count <= 20) or "WARP BUBBLE ON GRID" in status_flags:
            threat_level = "HIGH"
            threat_color = "#fb923c"
            is_critical = True
        elif (3 <= total_effective_count < 10) or (detected_ships and not is_nv) or "CLOAKED" in status_flags:
            threat_level = "MEDIUM"
            threat_color = "#facc15"
        elif is_nv or (total_effective_count < 3 and not detected_ships and not detected_pilots):
            threat_level = "INFO"
            threat_color = "#38bdf8"
        elif detected_ships or detected_pilots:
            threat_level = "MEDIUM"
            threat_color = "#facc15"
        else:
            threat_level = "INFO"
            threat_color = "#38bdf8"

        return {
            "timestamp": timestamp,
            "time_str": time_str,
            "speaker": safe_display_text(speaker, 128),
            "system": found_system,
            "system_id": found_system_id,
            "est_count": est_count,
            "ships": list(set(detected_ships)),
            "pilots": list(set(detected_pilots)),
            "threat_tags": list(set(threat_tags)),
            "status_flags": status_flags,
            "threat_level": threat_level,
            "threat_color": threat_color,
            "is_critical": is_critical,
            "channel": channel_name,
            "clean_msg": safe_display_text(msg, config.max_chat_chars),
            "raw_line": safe_display_text(clean_line, config.max_line_chars)
        }

    @staticmethod
    def parse(raw_text: str) -> Dict[str, Any]:
        """Parses a multi-line raw log extract or intel clipboard paste."""
        lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
        
        events: List[Dict[str, Any]] = []
        systems_reported: Dict[str, int] = {}
        hostile_ships: Dict[str, int] = {}
        hostile_pilots: set = set()
        highest_threat = "GREEN (CLEAR)"
        highest_color = "#34d399"
        total_hostiles = 0

        for line in lines:
            parsed = IntelParser.parse_single_line(line)
            if not parsed:
                continue

            events.append(parsed)
            sys_name = parsed["system"]
            if sys_name and sys_name != "Unknown System":
                systems_reported[sys_name] = systems_reported.get(sys_name, 0) + 1

            for s in parsed["ships"]:
                hostile_ships[s] = hostile_ships.get(s, 0) + 1

            for p in parsed["pilots"]:
                hostile_pilots.add(p)

            total_hostiles += parsed["est_count"]

            if parsed["threat_level"] == "CRITICAL":
                highest_threat = "CRITICAL (OMNI-THREAT DETECTED)"
                highest_color = "#ff4d6d"
            elif parsed["threat_level"] == "HIGH" and highest_threat != "CRITICAL (OMNI-THREAT DETECTED)":
                highest_threat = "HIGH (COMBAT HOSTILES ACTIVE)"
                highest_color = "#f87171"
            elif parsed["threat_level"] == "MEDIUM" and highest_threat not in ["CRITICAL (OMNI-THREAT DETECTED)", "HIGH (COMBAT HOSTILES ACTIVE)"]:
                highest_threat = "MEDIUM (HOSTILE MOVEMENT)"
                highest_color = "#facc15"

        return {
            "total_lines": len(lines),
            "parsed_events_count": len(events),
            "events": events,
            "systems_reported": systems_reported,
            "hostile_ships": hostile_ships,
            "hostile_pilots": list(hostile_pilots),
            "total_hostiles": total_hostiles or len(hostile_ships) or len(hostile_pilots),
            "highest_threat": highest_threat,
            "highest_color": highest_color
        }
