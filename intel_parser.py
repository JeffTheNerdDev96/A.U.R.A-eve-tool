"""
EVE Online Chat & Intel Channel Parser and Threat Radar.
Extracts hostile movement vectors, solar systems, ship classes, counts, pilot names, and status indicators in real time.
Supports live file tailing and batch parsing with high-performance O(1) matching.
"""
import re
from typing import Dict, List, Any, Optional
from eve_data import lookup_ship, SHIP_DATABASE, THREAT_BUBBLE, THREAT_CYNO, THREAT_MARAUDER, THREAT_CAPITAL, THREAT_SUPER, THREAT_ECM

# --- Module-level pre-computed constants (computed ONCE at import time) ---
# Pre-filter multi-word ship names and build a single combined regex
_MULTI_WORD_SHIPS = [name for name in SHIP_DATABASE if len(name.split()) > 1]
_MULTI_WORD_SHIP_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in sorted(_MULTI_WORD_SHIPS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE
) if _MULTI_WORD_SHIPS else None

# Pre-build set of lowercase multi-word ship parts for fast O(1) membership tests
_MULTI_WORD_SHIP_PARTS: set = set()
for _ship_name in _MULTI_WORD_SHIPS:
    for _part in _ship_name.lower().split():
        _MULTI_WORD_SHIP_PARTS.add(_part)

# Threat tags that indicate a real tactical threat (not standard combatants)
_NOTABLE_THREATS = frozenset({"Standard", "None", "COMBATANT"})


class IntelParser:
    """Parses in-game chat logs and intel channel streams in real-time."""

    # Pre-compiled regex patterns (compiled ONCE, reused on every call)
    SYS_PATTERN = re.compile(r"\b([A-Za-z0-9]{1,6}-[A-Za-z0-9]{1,6}|[A-Z][a-z]{2,14}(?:\s[A-Z][a-z]{2,14})?)\b")
    COUNT_PATTERN = re.compile(r"(?:\+|\b)(\d+)\s*(?:x|hostiles?|reds?|pilots?|gang|man|fleet)?\b", re.IGNORECASE)
    TIMESTAMP_PATTERN = re.compile(r"^\[\s*([\d\.\s:]+)\s*\]\s*([^>]+)>\s*(.*)$")
    _RE_NV = re.compile(r"\b(nv|na|no\s*visual)\b")
    _RE_CLEAR = re.compile(r"\b(clr|clear|clean|safe|nil|none)\b")
    _RE_WORD_CLEAN = re.compile(r"[^\w\-]")

    INTEL_KEYWORDS = frozenset({
        "cyno", "cynos", "cynou", "bubble", "bubbled", "gate", "outgate", "ingate",
        "station", "undock", "dock", "docked", "pos", "anom", "site", "beacon", "belt", "sun",
        "local", "hostile", "hostiles", "red", "reds", "spike", "clear", "clr", "clean",
        "jump", "jumped", "warp", "warped", "lit", "on", "in", "off", "grid", "help", "intel",
        "nv", "na", "no", "visual", "nil", "none", "safe", "v", "status", "elements",
        "presence", "report", "reported", "check", "eyes", "scout", "plus", "gang", "camp",
        "dscan", "d-scan", "pass", "passed", "heading", "towards", "from", "at", "holding",
        "cloaked", "cloak", "probe", "probes", "combat", "fleet", "standing", "by"
    })


    @staticmethod
    def parse_single_line(line: str, channel_name: str = "Intel") -> Optional[Dict[str, Any]]:
        """Parses a single live line from an EVE chat log file."""
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("---") or "Channel Name:" in clean_line or "Listener:" in clean_line:
            return None

        timestamp = ""
        speaker = "Unknown"
        msg = clean_line

        m = IntelParser.TIMESTAMP_PATTERN.match(clean_line)
        if m:
            timestamp = m.group(1).strip()
            speaker = m.group(2).strip()
            msg = m.group(3).strip()

        msg_l = msg.lower()

        # 1. Identify Solar System
        sys_matches = IntelParser.SYS_PATTERN.findall(msg)
        found_system = "Unknown System"
        if sys_matches:
            filtered_sys = [
                s for s in sys_matches if s.lower() not in IntelParser.INTEL_KEYWORDS and not lookup_ship(s)
            ]
            if filtered_sys:
                # Prefer system with hyphen/digit (e.g. 1DQ1-A, V-3YG7, Hed-GP, MWA-5Q, UM-SCG)
                special_sys = [s for s in filtered_sys if "-" in s or any(char.isdigit() for char in s)]
                found_system = special_sys[0] if special_sys else filtered_sys[0]

        # 2. Extract Hostile Count (+20, 20 hostiles, +5)
        c_match = IntelParser.COUNT_PATTERN.search(msg)
        est_count = int(c_match.group(1)) if c_match else 0

        # 3. Identify Multi-Word Ship Hulls using single pre-compiled combined regex (O(1))
        detected_ships: List[str] = []
        threat_tags: List[str] = []

        if _MULTI_WORD_SHIP_PATTERN is not None:
            for match in _MULTI_WORD_SHIP_PATTERN.finditer(msg):
                matched_text = match.group(1)
                # Resolve to canonical name from database
                for s_name in _MULTI_WORD_SHIPS:
                    if s_name.lower() == matched_text.lower() and s_name not in detected_ships:
                        detected_ships.append(s_name)
                        threat = SHIP_DATABASE[s_name].get("threat", "")
                        if threat and threat not in _NOTABLE_THREATS:
                            threat_tags.append(threat)
                        break

        # 4. Extract 2-Word and 1-Word Pilot / Character Names
        # (e.g. "Fenrir Hammer", "John Doe", "LordMalor")
        detected_pilots: List[str] = []
        words_in_msg = msg.split()
        
        i = 0
        while i < len(words_in_msg):
            w = IntelParser._RE_WORD_CLEAN.sub("", words_in_msg[i]).strip()
            if not w or w.lower() in IntelParser.INTEL_KEYWORDS or w.isdigit() or w == found_system or w == speaker:
                i += 1
                continue

            # Check if this token is part of an already matched multi-word ship (O(1) set lookup)
            if w.lower() in _MULTI_WORD_SHIP_PARTS and any(w.lower() in s.lower().split() for s in detected_ships):
                i += 1
                continue

            # Check if next word forms a 2-word pilot name (e.g. "Fenrir Hammer")
            if i + 1 < len(words_in_msg):
                next_w = IntelParser._RE_WORD_CLEAN.sub("", words_in_msg[i+1]).strip()
                if (next_w and next_w.lower() not in IntelParser.INTEL_KEYWORDS and 
                    not next_w.isdigit() and next_w != found_system and next_w != speaker):
                    # Next word is not a ship or keyword -> Word1 Word2 is a character name!
                    if not lookup_ship(next_w):
                        full_pilot = f"{w} {next_w}"
                        detected_pilots.append(full_pilot)
                        i += 2
                        continue

            # If it's a standalone word that is a valid ship, add to ships
            s_info = lookup_ship(w)
            if s_info:
                cname = s_info.get("canonical_name", w.capitalize())
                if cname not in detected_ships:
                    detected_ships.append(cname)
                    threat = s_info.get("threat", "")
                    if threat and threat not in _NOTABLE_THREATS:
                        threat_tags.append(threat)
            else:
                # Standalone unlocated pilot handle (if not a system/keyword)
                if len(w) > 2 and w != found_system and w != speaker:
                    detected_pilots.append(w)
            i += 1

        # 5. Extract Tactical Status Flags (using pre-compiled regex for NV/clear)
        status_flags: List[str] = []
        is_nv = bool(IntelParser._RE_NV.search(msg_l))
        is_explicit_clear = bool(IntelParser._RE_CLEAR.search(msg_l))

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

        if is_nv:
            if detected_pilots or detected_ships or est_count > 0:
                status_flags.append("UNLOCATED IN LOCAL (NO VISUAL / NV)")
            else:
                status_flags.append("NO VISUAL / SYSTEM CLEAR")
        elif is_explicit_clear and not detected_ships and not detected_pilots:
            status_flags.append("NO VISUAL / SYSTEM CLEAR")


        # 6. Evaluate Threat Level
        threat_level = "LOW"
        threat_color = "#38bdf8"
        is_critical = False

        if any(t in [THREAT_SUPER, THREAT_CAPITAL] for t in threat_tags) or "CYNO ACTIVE" in status_flags or est_count >= 10:
            threat_level = "CRITICAL"
            threat_color = "#ff4d6d"
            is_critical = True
        elif any(t in [THREAT_BUBBLE, THREAT_MARAUDER] for t in threat_tags) or "WARP BUBBLE ON GRID" in status_flags or est_count >= 5:
            threat_level = "HIGH"
            threat_color = "#f87171"
            is_critical = True
        elif any(t in [THREAT_CYNO, THREAT_ECM] for t in threat_tags) or "FLEET SPIKE" in status_flags or detected_pilots or est_count >= 2:
            threat_level = "MEDIUM"
            threat_color = "#facc15"
        elif "NO VISUAL / SYSTEM CLEAR" in status_flags:
            threat_level = "GREEN (CLEAR)"
            threat_color = "#34d399"
            est_count = 0
        elif detected_ships:
            threat_level = "LOW"
            threat_color = "#38bdf8"
            if est_count == 0:
                est_count = len(detected_ships)

        return {
            "timestamp": timestamp,
            "speaker": speaker,
            "system": found_system,
            "est_count": est_count,
            "ships": list(set(detected_ships)),
            "pilots": list(set(detected_pilots)),
            "threat_tags": list(set(threat_tags)),
            "status_flags": status_flags,
            "threat_level": threat_level,
            "threat_color": threat_color,
            "is_critical": is_critical,
            "channel": channel_name,
            "clean_msg": msg,
            "raw_line": clean_line
        }

    @staticmethod
    def parse(raw_text: str) -> Dict[str, Any]:
        """Parses multiple lines of intel text."""
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
        if not lines:
            return {"error": "Empty intel text"}

        parsed_reports: List[Dict[str, Any]] = []
        systems_detected: Dict[str, int] = {}
        ships_spotted: Dict[str, int] = {}
        pilots_logged: Dict[str, int] = {}
        high_threats: List[str] = []
        cynos_or_bubbles: List[str] = []

        for line in lines:
            parsed = IntelParser.parse_single_line(line)
            if not parsed:
                continue
            parsed_reports.append(parsed)
            
            sys_name = parsed["system"]
            if sys_name != "Unknown System":
                systems_detected[sys_name] = systems_detected.get(sys_name, 0) + 1

            for s in parsed["ships"]:
                ships_spotted[s] = ships_spotted.get(s, 0) + 1

            for p in parsed.get("pilots", []):
                pilots_logged[p] = pilots_logged.get(p, 0) + 1

            if parsed["is_critical"]:
                if any(t in [THREAT_SUPER, THREAT_CAPITAL, THREAT_MARAUDER] for t in parsed["threat_tags"]):
                    high_threats.append(f"{', '.join(parsed['ships']) or 'Hostiles'} in {sys_name}")
                if "CYNO ACTIVE" in parsed["status_flags"] or "WARP BUBBLE ON GRID" in parsed["status_flags"] or any(t in [THREAT_BUBBLE, THREAT_CYNO] for t in parsed["threat_tags"]):
                    cynos_or_bubbles.append(f"{', '.join(parsed['ships']) or 'Hazard'} in {sys_name}")

        summary_md = IntelParser._build_markdown_summary(
            parsed_reports, systems_detected, ships_spotted, pilots_logged, high_threats, cynos_or_bubbles
        )

        return {
            "total_reports": len(parsed_reports),
            "systems_detected": systems_detected,
            "ships_spotted": ships_spotted,
            "pilots_logged": pilots_logged,
            "high_threats": high_threats,
            "cynos_or_bubbles": cynos_or_bubbles,
            "summary_md": summary_md,
            "parsed_reports": parsed_reports
        }

    @staticmethod
    def _build_markdown_summary(
        reports: List[Dict[str, Any]],
        systems: Dict[str, int],
        ships: Dict[str, int],
        pilots: Dict[str, int],
        high_threats: List[str],
        cynos_bubbles: List[str]
    ) -> str:
        lines = [
            "### 🛰️ Live Intel Threat Radar",
            f"**Active Intel Reports Ingested:** `{len(reports)}`",
            ""
        ]

        if high_threats or cynos_bubbles:
            lines.append("#### 🚨 Critical Combat Threats & Hotspots:")
            for ht in high_threats[:6]:
                lines.append(f"- 🔴 **Heavy Asset / Siege Risk:** `{ht}`")
            for cb in cynos_bubbles[:6]:
                lines.append(f"- ⚠️ **Bubble / Cyno Hazard:** `{cb}`")
            lines.append("")

        if systems:
            lines.append("#### 🗺️ Hot Solar Systems Identified:")
            for sys_name, cnt in sorted(systems.items(), key=lambda x: x[1], reverse=True)[:8]:
                lines.append(f"- **{sys_name}**: `{cnt}` activity report(s)")
            lines.append("")

        if ships:
            lines.append("#### 🛸 Hostile Hulls Logged in Area:")
            for s_name, s_cnt in sorted(ships.items(), key=lambda x: x[1], reverse=True)[:10]:
                info = lookup_ship(s_name)
                s_class = info.get("class", "Vessel") if info else "Vessel"
                lines.append(f"- **{s_name}** ({s_class}): `{s_cnt}x`")
            lines.append("")

        if pilots:
            lines.append("#### 👤 Target Pilots Logged in Local:")
            for p_name, p_cnt in sorted(pilots.items(), key=lambda x: x[1], reverse=True)[:8]:
                lines.append(f"- **{p_name}**: `{p_cnt}` sighting(s)")
            lines.append("")

        lines.append("#### 📝 Decoded Intel Stream:")
        for r in reports[:6]:
            flags = f" `[{' | '.join(r['status_flags'])}]`" if r['status_flags'] else ""
            ships_str = f" (Hulls: {', '.join(r['ships'])})" if r['ships'] else ""
            pilots_str = f" (Pilot: {', '.join(r['pilots'])})" if r.get('pilots') else ""
            lines.append(f"- **{r['system']}** | *{r['clean_msg']}*{flags}{ships_str}{pilots_str}")

        return "\n".join(lines)
