"""
EVE Online Directional Scanner (D-Scan) Parser & Fleet Composition Analyzer.
Parses in-game clipboard copy-pastes into structured tactical threat matrices for A.U.R.A.
Handles all client formats: tab-separated, multi-column with TypeID, space-separated,
missing distances (D-scan 14.3 AU sphere), quantities, and comma-separated lists.
"""
import re
from typing import Dict, List, Any, Optional
from eve_data import (
    lookup_ship, SHIP_DATABASE,
    THREAT_BUBBLE, THREAT_CYNO, THREAT_ECM, THREAT_MARAUDER,
    THREAT_CAPITAL, THREAT_SUPER, THREAT_LOGI, THREAT_PIRATE, THREAT_T2_COMBAT
)


class DScanParser:
    """Parses raw in-game D-Scan clipboard data into tactical breakdowns."""

    @staticmethod
    def _extract_quantity_and_clean(text: str) -> tuple[int, str]:
        """Extracts quantity like '5x', 'x5', '5 Sabre' and returns (count, clean_text)."""
        clean = text.strip()
        count = 1
        
        # Match '5x Sabre' or '5x'
        m1 = re.match(r"^(\d+)\s*[xX*]\s*(.+)$", clean)
        if m1:
            try:
                count = max(1, int(m1.group(1)))
                clean = m1.group(2).strip()
            except Exception:
                pass
            return count, clean
            
        # Match 'Sabre x5' or 'Sabre 5x'
        m2 = re.search(r"^(.*?)\s+[xX*]\s*(\d+)$", clean)
        if m2:
            try:
                count = max(1, int(m2.group(2)))
                clean = m2.group(1).strip()
            except Exception:
                pass
            return count, clean
            
        # Match leading number e.g. '5 Sabre'
        m3 = re.match(r"^(\d+)\s+([A-Za-z].+)$", clean)
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
        # 1. Direct exact lookup
        info = lookup_ship(text)
        if info:
            return info.get("canonical_name", text), info
            
        # 2. Check parts split by tab or multiple spaces
        parts = [p.strip() for p in re.split(r"\t+|\s{2,}", text) if p.strip()]
        for p in parts:
            if p.isdigit() or any(u in p.lower() for u in ["km", "au", "m", "-"]):
                continue
            info = lookup_ship(p)
            if info:
                return info.get("canonical_name", p), info

        # 3. Check individual tokens
        words = [w.strip() for w in re.split(r"[\t,;|]+", text) if w.strip()]
        for w in words:
            info = lookup_ship(w)
            if info:
                return info.get("canonical_name", w), info

        # 4. Search for known ship names inside the string (longest first)
        sorted_hulls = sorted(SHIP_DATABASE.keys(), key=len, reverse=True)
        text_lower = text.lower()
        for hull in sorted_hulls:
            pattern = r"\b" + re.escape(hull.lower()) + r"\b"
            if re.search(pattern, text_lower):
                return hull, SHIP_DATABASE[hull]

        return None

    @staticmethod
    def _parse_distance(text: str) -> tuple[str, str, Optional[float]]:
        """Parses distance string and returns (display_distance, category, km_val)."""
        clean = text.strip()
        
        # Check for AU
        m_au = re.search(r"([\d\.,]+)\s*au\b", clean, re.IGNORECASE)
        if m_au:
            try:
                au_val = float(m_au.group(1).replace(",", ""))
                return f"{au_val:.1f} AU", "Off-Grid / Warping (> 150 km / AU)", au_val * 149597870.7
            except Exception:
                return clean, "Off-Grid / Warping (> 150 km / AU)", None

        # Check for km
        m_km = re.search(r"([\d\.,]+)\s*km\b", clean, re.IGNORECASE)
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
        m_m = re.search(r"([\d\.,]+)\s*m\b", clean, re.IGNORECASE)
        if m_m and not re.search(r"[\d\.,]+\s*km\b", clean, re.IGNORECASE):
            try:
                m_val = float(m_m.group(1).replace(",", ""))
                km_val = m_val / 1000.0
                return f"{m_val:,.0f} m", "Point Range (<= 20 km)", km_val
            except Exception:
                return clean, "Point Range (<= 20 km)", None

        # Standard D-Scan unknown distance or dash (-)
        return "D-Scan Sphere (< 14.3 AU)", "D-Scan Sphere (< 14.3 AU)", None

    @staticmethod
    def parse(raw_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
        
        parsed_items: List[Dict[str, Any]] = []
        ship_counts: Dict[str, int] = {}
        class_counts: Dict[str, int] = {}
        threats_detected: List[Dict[str, Any]] = []
        
        range_brackets = {
            "Point Range (<= 20 km)": 0,
            "Grid Range (20 - 150 km)": 0,
            "Off-Grid / Warping (> 150 km / AU)": 0,
            "D-Scan Sphere (< 14.3 AU)": 0
        }

        for line in lines:
            # Handle comma-separated multiple entries in a single line
            if "," in line and not ("\t" in line):
                sub_entries = [e.strip() for e in line.split(",") if e.strip()]
            else:
                sub_entries = [line]

            for entry in sub_entries:
                qty, clean_entry = DScanParser._extract_quantity_and_clean(entry)
                
                # Check for ship in entry
                ship_match = DScanParser._find_ship_in_text(clean_entry)
                dist_str, dist_cat, dist_km = DScanParser._parse_distance(clean_entry)
                
                if ship_match:
                    ship_name, ship_info = ship_match
                    ship_class = ship_info.get("class", "Combat Vessel")
                    threat = ship_info.get("threat", "COMBATANT")
                    
                    ship_counts[ship_name] = ship_counts.get(ship_name, 0) + qty
                    class_counts[ship_class] = class_counts.get(ship_class, 0) + qty
                    range_brackets[dist_cat] = range_brackets.get(dist_cat, 0) + qty
                    
                    # Add to threats detected (all combat vessels on D-Scan are active threats!)
                    threats_detected.append({
                        "type": ship_name,
                        "name": ship_name,
                        "class": ship_class,
                        "threat": threat,
                        "distance": dist_str,
                        "range_cat": dist_cat,
                        "count": qty,
                        "role": ship_info.get("role", ""),
                        "tactics": ship_info.get("tactics", "")
                    })
                    
                    parsed_items.append({
                        "type": ship_name,
                        "name": ship_name,
                        "distance": dist_str,
                        "is_ship": True,
                        "count": qty,
                        "class": ship_class,
                        "threat": threat
                    })

        total_ships = sum(ship_counts.values())
        
        # Threat evaluation score
        threat_level = "GREEN (CLEAR GRID)"
        threat_color = "#34d399"
        
        if any(t["threat"] in [THREAT_SUPER, THREAT_CAPITAL] for t in threats_detected):
            threat_level = "CRITICAL (CAPITAL / TITAN OMNI-THREAT)"
            threat_color = "#ff4d6d"
        elif any(t["threat"] in [THREAT_BUBBLE, THREAT_CYNO, THREAT_MARAUDER] for t in threats_detected):
            threat_level = "RED (HIGH COMBAT / TACKLE THREAT)"
            threat_color = "#f87171"
        elif any(t["threat"] in [THREAT_ECM, THREAT_LOGI, THREAT_PIRATE] for t in threats_detected) or total_ships >= 4:
            threat_level = "AMBER (EWAR / FLEET THREAT)"
            threat_color = "#fbbf24"
        elif total_ships > 0:
            threat_level = "YELLOW (ACTIVE HOSTILES)"
            threat_color = "#facc15"

        summary_md = DScanParser._build_markdown_summary(
            total_ships, ship_counts, class_counts, threats_detected, range_brackets, threat_level
        )

        return {
            "total_ships": total_ships,
            "ship_counts": ship_counts,
            "class_counts": class_counts,
            "threats_detected": threats_detected,
            "range_brackets": range_brackets,
            "threat_level": threat_level,
            "threat_color": threat_color,
            "summary_md": summary_md,
            "raw_items": parsed_items
        }

    @staticmethod
    def _build_markdown_summary(
        total_ships: int,
        ship_counts: Dict[str, int],
        class_counts: Dict[str, int],
        threats: List[Dict[str, Any]],
        ranges: Dict[str, int],
        threat_level: str
    ) -> str:
        if total_ships == 0:
            return "📡 **D-Scan Readout**: *No recognized combat vessels detected on directional scan.*"

        lines = [
            f"### 📡 D-Scan Tactical Fleet Breakdown",
            f"**Total Hostile Vessels Detected:** `{total_ships}` | **Threat Assessment:** `{threat_level}`\n",
        ]

        if threats:
            lines.append("#### ⚠️ Priority Threats & Tactical Countermeasures:")
            seen_types = set()
            for t in threats:
                stype = t["type"]
                if stype in seen_types:
                    continue
                seen_types.add(stype)
                cnt = ship_counts.get(stype, 1)
                tactics = f" — *{t.get('tactics', '')}*" if t.get('tactics') else ""
                lines.append(f"- **{stype}** (`{cnt}x` {t['class']}) — `{t['threat']}` | Range: *{t['distance']}*{tactics}")
            lines.append("")

        lines.append("#### 🚀 Fleet Hull Breakdown & Ship Table Context:")
        for ship, count in sorted(ship_counts.items(), key=lambda x: x[1], reverse=True)[:12]:
            info = lookup_ship(ship)
            if info:
                s_class = info.get("class", "Vessel")
                s_faction = info.get("faction", "Empire/Standard")
                s_tank = info.get("tank", "Shield/Armor")
                s_opt = info.get("optimal_range", "Standard")
                lines.append(f"- **{ship}** (`{count}x` {s_class} - {s_faction}) | Tank: *{s_tank}* | Optimal: *{s_opt}*")
            else:
                lines.append(f"- **{ship}**: `{count}x`")
        lines.append("")

        lines.append("#### 📏 Distance Distribution (D-Scan Sphere):")
        for r_name, r_cnt in ranges.items():
            if r_cnt > 0:
                lines.append(f"- **{r_name}**: `{r_cnt}` vessel(s)")

        return "\n".join(lines)

    @staticmethod
    def parse_unified(raw_text: str) -> Dict[str, Any]:
        """
        Unified analyzer for both D-Scan table dumps and Chat/Intel logs.
        Detects whether input is D-Scan, Intel, or a mixture, and combines the intelligence.
        """
        from intel_parser import IntelParser
        
        raw_lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
        
        chat_lines = [l for l in raw_lines if (l.startswith("[") or ">" in l or re.match(r"^\d{1,2}:\d{2}", l))]
        dscan_lines = [l for l in raw_lines if not (l.startswith("[") or ">" in l or re.match(r"^\d{1,2}:\d{2}", l))]
        
        dscan_res = DScanParser.parse("\n".join(dscan_lines)) if dscan_lines else {"total_ships": 0, "summary_md": "", "threat_level": "LOW", "threat_color": "#38bdf8"}
        intel_res = IntelParser.parse("\n".join(chat_lines)) if chat_lines else {"total_reports": 0, "summary_md": ""}
        
        if chat_lines and not dscan_lines:
            return {
                "total_ships": intel_res.get("total_reports", 0),
                "threat_level": "INTEL LOGS",
                "threat_color": "#38bdf8",
                "summary_md": intel_res.get("summary_md", ""),
                "type": "intel",
                "intel_data": intel_res
            }
        elif chat_lines and dscan_lines and dscan_res.get("total_ships", 0) > 0 and intel_res.get("total_reports", 0) > 0:
            combined_md = f"{dscan_res['summary_md']}\n\n---\n\n{intel_res['summary_md']}"
            return {
                "total_ships": dscan_res["total_ships"] + intel_res["total_reports"],
                "threat_level": dscan_res["threat_level"],
                "threat_color": dscan_res["threat_color"],
                "summary_md": combined_md,
                "type": "combined",
                "dscan_data": dscan_res,
                "intel_data": intel_res
            }
        elif chat_lines and dscan_res.get("total_ships", 0) == 0:
            return {
                "total_ships": intel_res.get("total_reports", 0),
                "threat_level": "INTEL LOGS",
                "threat_color": "#38bdf8",
                "summary_md": intel_res.get("summary_md", ""),
                "type": "intel",
                "intel_data": intel_res
            }
        else:
            return {
                "total_ships": dscan_res["total_ships"],
                "threat_level": dscan_res["threat_level"],
                "threat_color": dscan_res["threat_color"],
                "summary_md": dscan_res["summary_md"],
                "type": "dscan",
                "dscan_data": dscan_res
            }




