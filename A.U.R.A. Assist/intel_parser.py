"""
EVE Online Chat & Intel Channel Parser and Threat Radar.
Extracts hostile movement vectors, solar systems, ship classes, counts, and status indicators in real time.
Supports live file tailing and batch parsing.
"""
import re
from typing import Dict, List, Any, Optional
from eve_data import lookup_ship, THREAT_BUBBLE, THREAT_CYNO, THREAT_MARAUDER, THREAT_CAPITAL, THREAT_SUPER, THREAT_ECM


class IntelParser:
    """Parses in-game chat logs and intel channel streams in real-time."""

    SYS_PATTERN = re.compile(r"\b([A-Za-z0-9]{1,6}-[A-Za-z0-9]{1,6}|[A-Z][a-z]{2,14}(?:\s[A-Z][a-z]{2,14})?)\b")
    COUNT_PATTERN = re.compile(r"(?:\+|\b)(\d+)\s*(?:x|hostiles?|reds?|pilots?|gang)?\b", re.IGNORECASE)
    TIMESTAMP_PATTERN = re.compile(r"^\[\s*([\d\.\s:]+)\s*\]\s*([^>]+)>\s*(.*)$")

    NON_SHIP_WORDS = {
        "cyno", "cynos", "cynou", "bubble", "bubbled", "gate", "outgate", "ingate",
        "station", "undock", "dock", "pos", "anom", "site", "beacon", "belt", "sun",
        "local", "hostile", "hostiles", "red", "reds", "spike", "clear", "clr", "clean",
        "jump", "jumped", "warp", "warped", "lit", "on", "in", "off", "grid", "help", "intel"
    }

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

        # Find solar system
        sys_matches = IntelParser.SYS_PATTERN.findall(msg)
        found_system = "Unknown System"
        if sys_matches:
            filtered = [
                s for s in sys_matches if s.lower() not in IntelParser.NON_SHIP_WORDS and not lookup_ship(s)
            ]
            if filtered:
                # Prefer system with hyphen/digit (e.g. 1DQ1-A, V-3YG7, Hed-GP) or first valid non-ship term
                special_sys = [s for s in filtered if "-" in s or any(char.isdigit() for char in s)]
                found_system = special_sys[0] if special_sys else filtered[0]

        # Find count
        c_match = IntelParser.COUNT_PATTERN.search(msg)
        est_count = int(c_match.group(1)) if c_match else 1
        if est_count > 50:
            est_count = 1

        # Identify ship hulls
        words = re.findall(r"\b[A-Za-z0-9\-]+\b", msg)
        detected_ships = []
        threat_tags = []

        for w in words:
            if w.lower() in IntelParser.NON_SHIP_WORDS:
                continue
            s_info = lookup_ship(w)
            if s_info:
                cname = s_info.get("canonical_name", w.capitalize())
                if cname not in detected_ships:
                    detected_ships.append(cname)
                    threat = s_info.get("threat", "")
                    if threat and threat not in ["Standard", "None", "COMBATANT"]:
                        threat_tags.append(threat)


        # Status flags
        status_flags = []
        msg_l = msg.lower()
        if any(k in msg_l for k in ["cyno", "cyno lit", "cynou"]):
            status_flags.append("CYNO ACTIVE")
        if any(k in msg_l for k in ["bubble", "bubbled", "dictor", "hictor"]):
            status_flags.append("WARP BUBBLE ON GRID")
        if any(k in msg_l for k in ["gate", "on gate", "jump", "jumped", "outgate", "ingate"]):
            status_flags.append("GATE ACTIVITY")
        if any(k in msg_l for k in ["station", "undock", "citadel"]):
            status_flags.append("STATION/CITADEL")
        if any(k in msg_l for k in ["cloak", "cloaked", "stealth"]):
            status_flags.append("CLOAKED")
        if any(k in msg_l for k in ["spike", "huge", "fleet"]):
            status_flags.append("FLEET SPIKE")
        if any(k in msg_l for k in ["clr", "clear", "clean", "nv"]):
            status_flags.append("REPORTED CLEAR")

        # Threat evaluation
        threat_level = "GREEN"
        threat_color = "#34d399"
        is_critical = False

        if any(t in [THREAT_SUPER, THREAT_CAPITAL] for t in threat_tags) or "CYNO ACTIVE" in status_flags:
            threat_level = "CRITICAL"
            threat_color = "#ff4d6d"
            is_critical = True
        elif any(t in [THREAT_BUBBLE, THREAT_MARAUDER] for t in threat_tags) or "WARP BUBBLE ON GRID" in status_flags:
            threat_level = "HIGH"
            threat_color = "#f87171"
            is_critical = True
        elif any(t in [THREAT_CYNO, THREAT_ECM] for t in threat_tags) or "FLEET SPIKE" in status_flags or est_count >= 3:
            threat_level = "MEDIUM"
            threat_color = "#facc15"
        elif detected_ships:
            threat_level = "LOW"
            threat_color = "#38bdf8"


        return {
            "timestamp": timestamp,
            "speaker": speaker,
            "system": found_system,
            "est_count": est_count,
            "ships": list(set(detected_ships)),
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

            if parsed["is_critical"]:
                if any(t in [THREAT_SUPER, THREAT_CAPITAL, THREAT_MARAUDER] for t in parsed["threat_tags"]):
                    high_threats.append(f"{', '.join(parsed['ships']) or 'Hostiles'} in {sys_name}")
                if "CYNO ACTIVE" in parsed["status_flags"] or "WARP BUBBLE ON GRID" in parsed["status_flags"] or any(t in [THREAT_BUBBLE, THREAT_CYNO] for t in parsed["threat_tags"]):
                    cynos_or_bubbles.append(f"{', '.join(parsed['ships']) or 'Hazard'} in {sys_name}")

        summary_md = IntelParser._build_markdown_summary(
            parsed_reports, systems_detected, ships_spotted, high_threats, cynos_or_bubbles
        )

        return {
            "total_reports": len(parsed_reports),
            "systems_detected": systems_detected,
            "ships_spotted": ships_spotted,
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

        lines.append("#### 📝 Decoded Intel Stream:")
        for r in reports[:6]:
            flags = f" `[{' | '.join(r['status_flags'])}]`" if r['status_flags'] else ""
            ships_str = f" (Hulls: {', '.join(r['ships'])})" if r['ships'] else ""
            lines.append(f"- **{r['system']}** | *{r['clean_msg']}*{flags}{ships_str}")

        return "\n".join(lines)

