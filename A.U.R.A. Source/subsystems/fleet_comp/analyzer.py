"""
Fleet Composition & Doctrine Counter Heuristics Engine.
Classifies hulls from SHIP_DATABASE class, role, and threat fields.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from core.eve_data import SHIP_DATABASE, lookup_ship, _COMMON_SHIP_ALIASES
from .dscan_parser import DScanParser, _is_dist_or_id
from .models import FleetCompAnalysis

_LOGI_CLASSES = {"Logistics Cruiser", "Logistics Frigate", "Force Auxiliary"}
_TACKLE_CLASSES = {
    "Interdictor",
    "Heavy Interdiction Cruiser",
    "Interceptor",
    "Assault Frigate",
}
_RECON_CLASSES = {
    "Combat Recon",
    "Force Recon",
    "Recon Ship",
    "Electronic Attack Ship",
}
_COVERT_CLASSES = {"Stealth Bomber", "Covert Ops", "Blockade Runner"}
_T3C_CLASS = "Strategic Cruiser"

ROLE_LOGI = "Logistics"
ROLE_TACKLE = "Tacklers"
ROLE_T3C = "Strategic Cruisers"
ROLE_MAINLINE = "Mainline DPS"
ROLE_RECON = "T2 Recons / EAS"
ROLE_COVERT = "Covert Ops"

CATEGORY_ORDER = ["logi", "tackle", "t3c", "mainline", "recon", "covert"]

CATEGORY_LABELS = {
    "logi": "Logistics",
    "tackle": "Interdictors / Tackle",
    "t3c": "Strategic Cruisers",
    "mainline": "Mainline DPS",
    "recon": "T2 Recons / EAS",
    "covert": "Covert Ops / Stealth",
}

_ROLE_TO_KEY = {
    ROLE_LOGI: "logi",
    ROLE_TACKLE: "tackle",
    ROLE_T3C: "t3c",
    ROLE_MAINLINE: "mainline",
    ROLE_RECON: "recon",
    ROLE_COVERT: "covert",
}

_EMPTY_ROLES = {
    ROLE_LOGI: 0,
    ROLE_TACKLE: 0,
    ROLE_T3C: 0,
    ROLE_MAINLINE: 0,
    ROLE_RECON: 0,
    ROLE_COVERT: 0,
}

_ROLE_SEQUENCE = (
    ROLE_LOGI,
    ROLE_TACKLE,
    ROLE_T3C,
    ROLE_MAINLINE,
    ROLE_RECON,
    ROLE_COVERT,
)

_QTY_AT = re.compile(r"(\d+)\s*[xX*]?\s+")
_SEG_SPLIT = re.compile(r"[,;|]+")
_COL_SPLIT = re.compile(r"\t+|\s{2,}")
_DIST_CELL = re.compile(
    r"^[\d,.\s]+(?:km|au|m|m3)?$|^-$",
    re.IGNORECASE,
)

_LOOKUP_KEYS = sorted(
    list(SHIP_DATABASE.keys()) + list(_COMMON_SHIP_ALIASES.keys()),
    key=len,
    reverse=True,
)


def _boundary_ok(text: str, start: int, end: int) -> bool:
    if start > 0 and text[start - 1].isalnum():
        return False
    if end < len(text) and text[end].isalnum():
        return False
    return True


def _hull_at(lower: str, idx: int) -> Optional[Tuple[str, int]]:
    for key in _LOOKUP_KEYS:
        kl = key.lower()
        end = idx + len(kl)
        if end > len(lower):
            continue
        if lower.startswith(kl, idx) and _boundary_ok(lower, idx, end):
            info = lookup_ship(key)
            if not info:
                continue
            return str(info.get("canonical_name", key)), end
    return None


def _consume_ships(text: str) -> List[Tuple[str, int]]:
    """Walk text left-to-right: optional quantity, then longest hull/alias match."""
    if not text:
        return []
    lower = text.lower()
    found: List[Tuple[str, int]] = []
    idx = 0
    length = len(lower)
    while idx < length:
        while idx < length and not lower[idx].isalnum():
            idx += 1
        if idx >= length:
            break
        nxt = idx
        qty = 1
        qty_ok = idx == 0 or not text[idx - 1].isalnum()
        qm = _QTY_AT.match(text, idx) if qty_ok else None
        if qm:
            n = int(qm.group(1))
            if 1 <= n < 200:
                hull = _hull_at(lower, qm.end())
                if hull:
                    qty = n
                    nxt = qm.end()
        hull = _hull_at(lower, nxt)
        if hull:
            name, end = hull
            found.append((name, qty))
            idx = end
            continue
        idx += 1
    return found


def _overview_cells(line: str) -> List[str]:
    if "\t" in line:
        return [c.strip() for c in line.split("\t") if c.strip()]
    return [c.strip() for c in _COL_SPLIT.split(line) if c.strip()]


def _is_distance_cell(cell: str) -> bool:
    return bool(_DIST_CELL.match(cell.strip()))


def _type_from_overview_row(line: str) -> Optional[str]:
    """
    Fleet window / D-scan row: TypeID, Name, Type, Distance (or Name, Type, Distance).
    Return the Type cell only so IDs and ship names are not counted as hulls.
    """
    cells = _overview_cells(line)
    if len(cells) < 2:
        return None
    body = [c for c in cells if not _is_dist_or_id(c) and not _is_distance_cell(c)]
    if not body:
        return None
    for cell in reversed(body):
        if lookup_ship(cell):
            return cell
    return body[-1]


def _is_columnar_overview(line: str) -> bool:
    cells = _overview_cells(line)
    if len(cells) < 3:
        return False
    if _is_dist_or_id(cells[0]) or _is_distance_cell(cells[-1]):
        return True
    return bool(_type_from_overview_row(line))


class FleetCompAnalyzer:
    """Classifies fleet pasted text or ship dictionary into role buckets and calculates counter advice."""

    def categorize_ship(self, ship_name: str) -> str:
        """Maps a hull to a tactical role using class, role, and threat from SHIP_DATABASE."""
        info = lookup_ship(ship_name)
        cls = info.get("class", "") if info else ""
        role = str(info.get("role", "") if info else "").lower()
        threat = str(info.get("threat", "") if info else "")
        name_l = ship_name.lower()

        if cls == _T3C_CLASS:
            return ROLE_T3C
        if cls in _RECON_CLASSES:
            return ROLE_RECON
        if (
            cls in _LOGI_CLASSES
            or "THREAT_LOGI" in threat
            or "logistics" in role
            or "remote repair" in role
            or "remote rep" in role
            or "fax" in role
        ):
            return ROLE_LOGI
        if cls in _TACKLE_CLASSES or "dictor" in name_l or "sabre" in name_l:
            return ROLE_TACKLE
        if cls in _COVERT_CLASSES or "bomber" in name_l:
            return ROLE_COVERT
        return ROLE_MAINLINE

    def analyze_fleet(self, ship_counts: Dict[str, int]) -> FleetCompAnalysis:
        """Performs full role distribution, threat identification, and counter recommendations."""
        roles = dict(_EMPTY_ROLES)
        total_ships = sum(ship_counts.values())
        threats: List[str] = []
        counters: List[str] = []

        for ship_name, count in ship_counts.items():
            role = self.categorize_ship(ship_name)
            roles[role] += count
            s_lower = ship_name.lower()
            if "dictor" in s_lower or "sabre" in s_lower or "flycatcher" in s_lower:
                threats.append(f"Interdiction Threat: {count}x {ship_name}")
            if s_lower in {
                "curse", "pilgrim", "huginn", "lachesis", "arazu", "rapier", "falcon", "rook",
            }:
                threats.append(f"T2 Recon EWAR: {count}x {ship_name}")
            if s_lower in {"hyena", "kitsune", "sentinel", "keres"}:
                threats.append(f"Electronic Attack Ship: {count}x {ship_name}")
            if role == ROLE_T3C:
                threats.append(f"Strategic Cruiser: {count}x {ship_name}")
            if "guardian" in s_lower or "basilisk" in s_lower or "fax" in s_lower or "nestor" in s_lower:
                threats.append(f"Logistics Backbone: {count}x {ship_name}")

        if roles[ROLE_LOGI] > 0 and (roles[ROLE_MAINLINE] > 0 or roles[ROLE_T3C] > 0):
            counters.append("Primary enemy Logistics before engaging mainline / T3C DPS.")
        if roles[ROLE_RECON] > 0:
            counters.append("Bring damps, ECM, or range to neutralize T2 Recons / EAS.")
        if roles[ROLE_T3C] > 0:
            counters.append("Respect Strategic Cruiser doctrine (webs, covert, nullification, HAMs).")
        if roles[ROLE_TACKLE] > 0:
            counters.append("Screen with Anti-Tackle destroyers/frigates before heavy escalation.")
        if roles[ROLE_COVERT] > 0:
            counters.append("Maintain mobile bubbles and align to safes; stealth bomber / covert threat present.")
        if not counters:
            counters.append("Standard engagement profile. Focus fire target caller targets.")

        if roles[ROLE_LOGI] >= 3 or roles[ROLE_RECON] >= 3 or roles[ROLE_T3C] >= 3 or total_ships >= 15:
            safety = "DISENGAGE"
        elif roles[ROLE_TACKLE] >= 2 or total_ships >= 6:
            safety = "CAUTION"
        else:
            safety = "FAVORABLE"

        return FleetCompAnalysis(
            total_ships=total_ships,
            role_counts=roles,
            ship_counts=ship_counts,
            primary_threats=threats[:5],
            counter_recommendations=counters,
            engagement_safety_score=safety,
        )

    def analyze_dscan_text(self, dscan_text: str) -> FleetCompAnalysis:
        parsed = parse_fleet_paste(dscan_text)
        return self.analyze_fleet(parsed["ship_counts"])

    def assess_fleet_matchup(self, friendly_dscan: str, enemy_dscan: str) -> Dict[str, Any]:
        f_parsed = parse_fleet_paste(friendly_dscan)
        e_parsed = parse_fleet_paste(enemy_dscan)
        rows = compare_fleets(f_parsed["ship_counts"], e_parsed["ship_counts"])
        bullets = assess_matchup(rows, f_parsed["total_ships"], e_parsed["total_ships"])
        ft = f_parsed["total_ships"]
        et = e_parsed["total_ships"]
        return {
            "rows": rows,
            "bullets": bullets,
            "friendly_total": ft,
            "enemy_total": et,
            "assessment": "Advantage" if ft > et else "Even" if ft == et else "Disadvantage",
        }


_GLOBAL_ANALYZER = FleetCompAnalyzer()


def parse_fleet_paste(text: str) -> Dict[str, Any]:
    """Extract ship names and counts from fleet-window, chat, or D-scan paste."""
    counts: Dict[str, int] = {}
    if not text or not text.strip():
        return {"total_ships": 0, "unmatched": 0, "ship_counts": {}}

    unmatched = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        hits: List[Tuple[str, int]] = []
        type_cell = _type_from_overview_row(line) if _is_columnar_overview(line) else None
        if type_cell is not None:
            qty, clean = DScanParser._extract_quantity_and_clean(type_cell)
            info = lookup_ship(clean)
            if info:
                hits.append((str(info.get("canonical_name", clean)), 1))
            else:
                walked = _consume_ships(clean)
                if walked:
                    hits.append((walked[0][0], 1))
        else:
            for segment in _SEG_SPLIT.split(line) or [line]:
                segment = segment.strip()
                if not segment:
                    continue
                qty, clean = DScanParser._extract_quantity_and_clean(segment)
                info = lookup_ship(clean)
                if info:
                    hits.append((str(info.get("canonical_name", clean)), qty))
                else:
                    hits.extend(_consume_ships(segment))

        if not hits:
            unmatched += 1
            continue
        for name, qty in hits:
            counts[name] = counts.get(name, 0) + max(1, int(qty))

    total = sum(counts.values())
    return {
        "total_ships": total,
        "unmatched": unmatched,
        "ship_counts": counts,
    }


def _role_mix(ship_counts: Dict[str, int]) -> Tuple[Dict[str, int], Dict[str, Dict[str, int]]]:
    totals = dict(_EMPTY_ROLES)
    mix: Dict[str, Dict[str, int]] = {role: {} for role in _EMPTY_ROLES}
    for ship_name, count in ship_counts.items():
        role = _GLOBAL_ANALYZER.categorize_ship(ship_name)
        totals[role] += count
        mix[role][ship_name] = mix[role].get(ship_name, 0) + count
    return totals, mix


def _format_cell(total: int, hulls: Dict[str, int]) -> str:
    if total <= 0:
        return "0"
    ranked = sorted(hulls.items(), key=lambda kv: (-kv[1], kv[0]))
    shown = ranked[:2]
    extra = len(ranked) - len(shown)
    parts = ", ".join(f"{name}: {n}" for name, n in shown)
    if extra:
        parts = f"{parts}, +{extra} more"
    return f"{total} ({parts})"


def compare_fleets(friendly_counts: Dict[str, int], enemy_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    """Compares friendly vs enemy fleets using FleetCompAnalyzer roles."""
    f_totals, f_mix = _role_mix(friendly_counts)
    e_totals, e_mix = _role_mix(enemy_counts)

    rows: List[Dict[str, Any]] = []
    for role_name in _ROLE_SEQUENCE:
        key = _ROLE_TO_KEY[role_name]
        f_count = f_totals.get(role_name, 0)
        e_count = e_totals.get(role_name, 0)
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
            "friendly": _format_cell(f_count, f_mix.get(role_name, {})),
            "enemy": _format_cell(e_count, e_mix.get(role_name, {})),
            "friendly_n": f_count,
            "enemy_n": e_count,
            "delta": delta_str,
            "delta_kind": kind,
        })
    return rows


def _recon_level(n: int) -> str:
    if n <= 0:
        return "None"
    if n == 1:
        return "Low"
    if n <= 3:
        return "Medium"
    return "High"


def assess_matchup(rows: List[Dict[str, Any]], friendly_total: int, enemy_total: int) -> List[str]:
    """Generates local (non-neural) tactical assessment bullets."""
    if not friendly_total and not enemy_total:
        return ["No recognized hulls on either side."]

    by_key = {row["key"]: row for row in rows}
    bullets: List[str] = []
    if friendly_total > enemy_total:
        bullets.append(f"Friendly fleet numbers advantage: {friendly_total} vs {enemy_total} enemy hulls.")
    elif enemy_total > friendly_total:
        bullets.append(f"Enemy numbers advantage: {enemy_total} vs {friendly_total} friendly hulls.")
    else:
        bullets.append(f"Fleets are evenly matched in total numbers ({friendly_total} hulls).")

    f_logi = by_key.get("logi", {}).get("friendly_n", 0)
    e_logi = by_key.get("logi", {}).get("enemy_n", 0)
    f_dps = by_key.get("mainline", {}).get("friendly_n", 0) + by_key.get("t3c", {}).get("friendly_n", 0)
    e_dps = by_key.get("mainline", {}).get("enemy_n", 0) + by_key.get("t3c", {}).get("enemy_n", 0)
    if f_dps or e_dps or f_logi or e_logi:
        f_ratio = f"{f_logi}:{max(f_dps, 1)}" if (f_dps or f_logi) else "0"
        e_ratio = f"{e_logi}:{max(e_dps, 1)}" if (e_dps or e_logi) else "0"
        bullets.append(f"Logi-to-DPS (incl. T3C): friendly {f_ratio}, enemy {e_ratio}.")

    f_tackle = by_key.get("tackle", {}).get("friendly_n", 0)
    e_tackle = by_key.get("tackle", {}).get("enemy_n", 0)
    if f_tackle != e_tackle:
        if f_tackle > e_tackle:
            bullets.append(f"Friendly tackle advantage ({f_tackle} vs {e_tackle}).")
        else:
            bullets.append(f"Enemy tackle advantage ({e_tackle} vs {f_tackle}).")

    f_t3c = by_key.get("t3c", {}).get("friendly_n", 0)
    e_t3c = by_key.get("t3c", {}).get("enemy_n", 0)
    if f_t3c or e_t3c:
        bullets.append(f"Strategic Cruisers on grid: friendly {f_t3c}, enemy {e_t3c}.")

    f_recon = by_key.get("recon", {}).get("friendly_n", 0)
    e_recon = by_key.get("recon", {}).get("enemy_n", 0)
    bullets.append(
        f"T2 Recon / EAS threat: friendly {_recon_level(f_recon)} ({f_recon}), "
        f"enemy {_recon_level(e_recon)} ({e_recon})."
    )
    return bullets
