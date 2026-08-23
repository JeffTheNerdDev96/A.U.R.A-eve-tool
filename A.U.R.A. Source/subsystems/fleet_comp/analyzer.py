"""
Fleet Composition & Doctrine Counter Heuristics Engine.
Classifies ships into Logistics, Tacklers, Mainline DPS, EWAR, and Covert Ops.
"""

from typing import Dict, List, Tuple, Any
from core.eve_data import lookup_ship, SHIP_DATABASE
from .models import FleetCompAnalysis

_LOGI_CLASSES = {"Logistics Cruiser", "Logistics Frigate", "Force Auxiliary"}
_TACKLE_CLASSES = {"Interdictor", "Heavy Interdiction Cruiser", "Interceptor", "Assault Frigate"}
_MAINLINE_CLASSES = {"Heavy Assault Cruiser", "Battlecruiser", "Battleship", "Marauder", "Black Ops", "Command Ship", "Dreadnought", "Carrier", "Supercarrier", "Titan", "Destroyer", "Cruiser"}
_EWAR_CLASSES = {"Combat Recon", "Force Recon", "Recon Ship", "Electronic Attack Ship"}
_COVERT_CLASSES = {"Stealth Bomber", "Covert Ops", "Blockade Runner"}

CATEGORY_ORDER = ["logi", "tackle", "mainline", "ewar", "covert"]

CATEGORY_LABELS = {
    "logi": "Logistics",
    "tackle": "Interdictors / Tackle",
    "mainline": "Mainline DPS",
    "ewar": "Recons / EWAR",
    "covert": "Covert Ops / Stealth",
}


class FleetCompAnalyzer:
    """Classifies fleet pasted text or ship dictionary into role buckets and calculates counter advice."""

    def categorize_ship(self, ship_name: str) -> str:
        """Maps ship name to one of 5 primary roles."""
        info = lookup_ship(ship_name)
        cls = info.get("class", "") if info else ""

        if cls in _LOGI_CLASSES:
            return "Logistics"
        if cls in _TACKLE_CLASSES or "dictor" in ship_name.lower() or "sabre" in ship_name.lower():
            return "Tacklers"
        if cls in _EWAR_CLASSES:
            return "EWAR"
        if cls in _COVERT_CLASSES or "bomber" in ship_name.lower():
            return "Covert Ops"
        if cls in _MAINLINE_CLASSES:
            return "Mainline DPS"
        return "Mainline DPS"

    def analyze_fleet(self, ship_counts: Dict[str, int]) -> FleetCompAnalysis:
        """Performs full role distribution, threat identification, and counter recommendations."""
        roles = {
            "Logistics": 0,
            "Tacklers": 0,
            "Mainline DPS": 0,
            "EWAR": 0,
            "Covert Ops": 0
        }

        total_ships = sum(ship_counts.values())
        threats: List[str] = []
        counters: List[str] = []

        for ship_name, count in ship_counts.items():
            role = self.categorize_ship(ship_name)
            roles[role] += count

            s_lower = ship_name.lower()
            if "dictor" in s_lower or "sabre" in s_lower or "flycatcher" in s_lower:
                threats.append(f"Interdiction Threat: {count}x {ship_name}")
            if "bhaalgorn" in s_lower or "lachesis" in s_lower or "huginn" in s_lower or "curse" in s_lower:
                threats.append(f"Heavy EWAR / Neuts: {count}x {ship_name}")
            if "guardian" in s_lower or "basilisk" in s_lower or "fax" in s_lower or "nestor" in s_lower:
                threats.append(f"Logistics Backbone: {count}x {ship_name}")

        # Counter recommendations
        if roles["Logistics"] > 0 and roles["Mainline DPS"] > 0:
            counters.append("Primary enemy Logistics before engaging Mainline DPS.")
        if roles["EWAR"] > 0:
            counters.append("Bring long-range Dampeners or ECM to neutralize enemy Recons.")
        if roles["Tacklers"] > 0:
            counters.append("Screen with Anti-Tackle destroyers/frigates before heavy escalation.")
        if roles["Covert Ops"] > 0:
            counters.append("Maintain mobile bubbles and align to safes; stealth bomber threat present.")
        if not counters:
            counters.append("Standard engagement profile. Focus fire target caller targets.")

        # Safety rating
        if roles["Logistics"] >= 3 or roles["EWAR"] >= 3 or total_ships >= 15:
            safety = "DISENGAGE"
        elif roles["Tacklers"] >= 2 or total_ships >= 6:
            safety = "CAUTION"
        else:
            safety = "FAVORABLE"

        return FleetCompAnalysis(
            total_ships=total_ships,
            role_counts=roles,
            ship_counts=ship_counts,
            primary_threats=threats[:5],
            counter_recommendations=counters,
            engagement_safety_score=safety
        )

    def analyze_dscan_text(self, dscan_text: str) -> FleetCompAnalysis:
        parsed = parse_fleet_paste(dscan_text)
        return self.analyze_fleet(parsed["ship_counts"])

    def assess_fleet_matchup(self, friendly_dscan: str, enemy_dscan: str) -> Dict[str, Any]:
        f_parsed = parse_fleet_paste(friendly_dscan)
        e_parsed = parse_fleet_paste(enemy_dscan)
        rows = compare_fleets(f_parsed["ship_counts"], e_parsed["ship_counts"])
        bullets = assess_matchup(rows, f_parsed["total_ships"], e_parsed["total_ships"])
        return {
            "rows": rows,
            "bullets": bullets,
            "friendly_total": f_parsed["total_ships"],
            "enemy_total": e_parsed["total_ships"],
            "assessment": "Advantage" if f_parsed["total_ships"] > e_parsed["total_ships"] else "Even" if f_parsed["total_ships"] == e_parsed["total_ships"] else "Disadvantage"
        }


_GLOBAL_ANALYZER = FleetCompAnalyzer()


def parse_fleet_paste(text: str) -> Dict[str, Any]:
    """Extracts ship names and counts from raw text."""
    counts: Dict[str, int] = {}
    if not text:
        return {"total_ships": 0, "unmatched": 0, "ship_counts": {}}

    lines = text.splitlines()
    unmatched = 0
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        # Check tab-delimited D-Scan columns first
        parts = cleaned.split("\t")
        found = False
        for part in parts:
            p_strip = part.strip()
            if not p_strip:
                continue
            info = lookup_ship(p_strip)
            if info:
                name = info.get("canonical_name", p_strip)
                counts[name] = counts.get(name, 0) + 1
                found = True
                break
        if not found:
            words = cleaned.split()
            for word in words:
                info = lookup_ship(word)
                if info:
                    name = info.get("canonical_name", word)
                    counts[name] = counts.get(name, 0) + 1
                    found = True
                    break
        if not found:
            unmatched += 1

    total = sum(counts.values())
    return {
        "total_ships": total,
        "unmatched": unmatched,
        "ship_counts": counts
    }


def compare_fleets(friendly_counts: Dict[str, int], enemy_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    """Compares friendly vs enemy fleets using FleetCompAnalyzer."""
    f_analysis = _GLOBAL_ANALYZER.analyze_fleet(friendly_counts)
    e_analysis = _GLOBAL_ANALYZER.analyze_fleet(enemy_counts)

    role_key_map = {
        "Logistics": "logi",
        "Tacklers": "tackle",
        "Mainline DPS": "mainline",
        "EWAR": "ewar",
        "Covert Ops": "covert"
    }

    rows: List[Dict[str, Any]] = []
    for role_name, key in role_key_map.items():
        f_count = f_analysis.role_counts.get(role_name, 0)
        e_count = e_analysis.role_counts.get(role_name, 0)
        delta_val = f_count - e_count
        delta_str = f"+{delta_val}" if delta_val > 0 else str(delta_val)

        kind = "even"
        if delta_val > 0:
            kind = "adv"
        elif delta_val < 0:
            kind = "disadv"

        rows.append({
            "key": key,
            "label": CATEGORY_LABELS[key],
            "friendly": str(f_count),
            "enemy": str(e_count),
            "delta": delta_str,
            "delta_kind": kind
        })

    return rows


def assess_matchup(rows: List[Dict[str, Any]], friendly_total: int, enemy_total: int) -> List[str]:
    """Generates tactical assessment bullets."""
    if not friendly_total and not enemy_total:
        return ["No recognized hulls on either side."]

    bullets: List[str] = []
    if friendly_total > enemy_total:
        bullets.append(f"Friendly fleet numbers advantage: {friendly_total} vs {enemy_total} enemy hulls.")
    elif enemy_total > friendly_total:
        bullets.append(f"Enemy numbers advantage: {enemy_total} vs {friendly_total} friendly hulls.")
    else:
        bullets.append(f"Fleets are evenly matched in total numbers ({friendly_total} hulls).")

    return bullets
