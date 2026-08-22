"""
Fleet vs D-scan composition matchup: role buckets, comparison table, local assessment.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from dscan_parser import (
    DScanParser,
    _is_dist_or_id,
    _SHIP_SUBSTR_PATTERN,
    _RE_TAB_SPLIT,
)
from eve_data import (
    lookup_ship,
    SHIP_DATABASE,
    THREAT_ECM,
    THREAT_HAULER,
    THREAT_MINING,
    THREAT_LOGI,
)

_MULTI_WORD_SHIPS = [name for name in SHIP_DATABASE if " " in name]
_MULTI_WORD_SHIP_PATTERN = (
    re.compile(
        r"\b(" + "|".join(re.escape(s) for s in sorted(_MULTI_WORD_SHIPS, key=len, reverse=True)) + r")\b",
        re.IGNORECASE,
    )
    if _MULTI_WORD_SHIPS
    else None
)

_RE_OVERVIEW_VELOCITY = re.compile(r"\bm/s\b", re.IGNORECASE)

# Display order. Hide a row when both sides are empty.
CATEGORY_ORDER = [
    "logi",
    "hac",
    "hic",
    "ewar",
    "tackle",
    "command",
    "bs_bc",
    "capital",
    "other_combat",
    "noncombat",
]

CATEGORY_LABELS = {
    "logi": "Logistics (Main / Cap)",
    "hac": "Heavy Assault Cruisers",
    "hic": "Heavy Interdiction",
    "ewar": "Recons / EWAR",
    "tackle": "Interdictors / Tackle",
    "command": "Command / Links",
    "bs_bc": "Battlecruisers / Battleships",
    "capital": "Capitals",
    "other_combat": "Other combat",
    "noncombat": "Non-combat",
}

_LOGI_CLASSES = {
    "Logistics Cruiser",
    "Logistics Frigate",
    "Force Auxiliary",
}
_HAC_CLASSES = {"Heavy Assault Cruiser"}
_HIC_CLASSES = {"Heavy Interdiction Cruiser"}
_EWAR_CLASSES = {
    "Combat Recon",
    "Force Recon",
    "Recon Ship",
    "Electronic Attack Ship",
}
_TACKLE_CLASSES = {"Interdictor", "Interceptor", "Assault Frigate"}
_COMMAND_CLASSES = {"Command Ship", "Command Destroyer"}
_BS_CLASSES = {"Battlecruiser", "Battleship", "Marauder", "Black Ops"}
_CAPITAL_CLASSES = {"Dreadnought", "Carrier", "Supercarrier", "Titan"}
_NONCOMBAT_CLASSES = {
    "Industrial",
    "Freighter",
    "Jump Freighter",
    "Mining Barge",
    "Exhumer",
    "Hauler",
    "Transport Ship",
    "Blockade Runner",
    "Deep Space Transport",
    "Salvage Ship",
}

_MISSILE_HACS = {
    "Cerberus",
    "Eagle",
    "Sacrilege",
    "Caracal Navy Issue",
}
_GUN_HACS = {
    "Muninn",
    "Ishtar",
    "Zealot",
    "Deimos",
    "Vagabond",
}

_SENSITIVE_CATS = {"logi", "ewar"}


def strip_intel_line(line: str) -> str:
    """Strip EVE chat / intel log prefix; return message body."""
    clean_line = line.strip()
    if clean_line.startswith("["):
        r_bracket = clean_line.find("]")
        if r_bracket != -1:
            gt_idx = clean_line.find(">", r_bracket)
            if gt_idx != -1:
                return clean_line[gt_idx + 1:].strip()
            return clean_line[r_bracket + 1:].strip()
    if ">" in clean_line:
        gt_idx = clean_line.find(">")
        return clean_line[gt_idx + 1:].strip()
    return clean_line


def is_skippable_metadata(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("---") or "Channel Name:" in s or "Listener:" in s:
        return True
    sl = re.sub(r"\s+", " ", s.lower()).strip()
    if sl in ("clear", "clr", "nv", "na", "no visual", "novisual"):
        return True
    return False


def _looks_like_intel_line(line: str) -> bool:
    s = line.strip()
    if s.startswith("["):
        return True
    if ">" in s and "\t" not in s:
        gt_idx = s.find(">")
        prefix = s[:gt_idx].strip()
        if prefix and len(prefix) < 120:
            return True
    return False


def count_ships_in_text(text: str) -> Dict[str, int]:
    """Count hull mentions with repeats (Composition-only)."""
    counts: Dict[str, int] = {}
    if not text:
        return counts

    covered: set[int] = set()

    if _MULTI_WORD_SHIP_PATTERN is not None and " " in text:
        for match in _MULTI_WORD_SHIP_PATTERN.finditer(text):
            info = lookup_ship(match.group(1))
            if info:
                cname = info.get("canonical_name", match.group(1))
                counts[cname] = counts.get(cname, 0) + 1
                for i in range(match.start(), match.end()):
                    covered.add(i)

    text_lower = text.lower()
    for match in _SHIP_SUBSTR_PATTERN.finditer(text_lower):
        if any(i in covered for i in range(match.start(), match.end())):
            continue
        info = lookup_ship(match.group(1))
        if info:
            cname = info.get("canonical_name", match.group(1).capitalize())
            counts[cname] = counts.get(cname, 0) + 1

    if "\t" in text:
        for part in _RE_TAB_SPLIT.split(text):
            part = part.strip()
            if not part or _is_dist_or_id(part):
                continue
            if _RE_OVERVIEW_VELOCITY.search(part):
                continue
            info = lookup_ship(part)
            if info:
                cname = info.get("canonical_name", part)
                counts[cname] = counts.get(cname, 0) + 1

    return counts


def apply_line_quantity(entry: str, counts: Dict[str, int]) -> Dict[str, int]:
    if not counts:
        return {}
    qty, _ = DScanParser._extract_quantity_and_clean(entry.strip())
    if len(counts) == 1:
        hull = next(iter(counts))
        counts[hull] = max(counts[hull], qty)
    return counts


def parse_composition_subentry(entry: str) -> Dict[str, int]:
    entry = entry.strip()
    counts = count_ships_in_text(entry)
    if not counts:
        ship_match = DScanParser._find_ship_in_text(entry)
        if ship_match:
            counts = {ship_match[0]: 1}
    if not counts:
        return {}
    return apply_line_quantity(entry, counts)


def parse_overview_row(line: str) -> Dict[str, int]:
    cells = line.split("\t") if "\t" in line else _RE_TAB_SPLIT.split(line)
    hulls: List[str] = []
    seen: set[str] = set()
    for cell in cells:
        cell = cell.strip()
        if not cell or _is_dist_or_id(cell):
            continue
        if _RE_OVERVIEW_VELOCITY.search(cell):
            continue
        info = lookup_ship(cell)
        if info:
            cname = info.get("canonical_name", cell)
            if cname not in seen:
                seen.add(cname)
                hulls.append(cname)
    if not hulls:
        return {}
    return {h: 1 for h in hulls}


def parse_composition_line(line: str) -> Dict[str, int]:
    line = line.strip()
    if is_skippable_metadata(line):
        return {}

    if _looks_like_intel_line(line):
        body = strip_intel_line(line)
        counts = count_ships_in_text(body)
        if not counts:
            ship_match = DScanParser._find_ship_in_text(body)
            if ship_match:
                counts = {ship_match[0]: 1}
        if not counts:
            return {}
        return apply_line_quantity(body, counts)

    if "\t" in line or len(_RE_TAB_SPLIT.split(line)) >= 3:
        row_counts = parse_overview_row(line)
        if row_counts:
            return row_counts

    out: Dict[str, int] = {}
    if "," in line and "\t" not in line:
        sub_entries = [e.strip() for e in line.split(",") if e.strip()]
    else:
        sub_entries = [line]
    for entry in sub_entries:
        sub = parse_composition_subentry(entry)
        for hull, n in sub.items():
            out[hull] = out.get(hull, 0) + n
    return out


def parse_composition_paste(raw_text: str) -> Dict[str, int]:
    ship_counts: Dict[str, int] = {}
    for line in (raw_text or "").strip().split("\n"):
        line_counts = parse_composition_line(line)
        for hull, n in line_counts.items():
            ship_counts[hull] = ship_counts.get(hull, 0) + n
    return ship_counts


def count_unmatched_composition_lines(raw_text: str) -> int:
    unmatched = 0
    for line in (raw_text or "").strip().split("\n"):
        stripped = line.strip()
        if is_skippable_metadata(stripped):
            continue
        if not parse_composition_line(stripped):
            unmatched += 1
    return unmatched


def parse_fleet_paste(raw_text: str) -> Dict[str, Any]:
    ship_counts = parse_composition_paste(raw_text or "")
    return {
        "ship_counts": dict(ship_counts),
        "total_ships": sum(ship_counts.values()),
        "unmatched": count_unmatched_composition_lines(raw_text or ""),
    }


def bucket_for_hull(name: str, info: Optional[Dict[str, Any]]) -> str:
    if not info:
        return "other_combat"
    cls = str(info.get("class") or "")
    role = str(info.get("role") or "")
    threat = str(info.get("threat") or "")
    role_l = role.lower()

    if (
        cls in _LOGI_CLASSES
        or threat in (THREAT_LOGI, "THREAT_LOGI")
        or "logistics" in role_l
    ):
        return "logi"
    if cls in _HAC_CLASSES or "heavy assault" in role_l:
        return "hac"
    if cls in _HIC_CLASSES or "heavy interdiction" in role_l:
        return "hic"
    if cls in _EWAR_CLASSES or threat == THREAT_ECM or "ewar" in role_l or "recon" in role_l:
        return "ewar"
    if cls in _TACKLE_CLASSES or "tackler" in role_l or "tackle" in role_l:
        return "tackle"
    if cls in _COMMAND_CLASSES:
        return "command"
    if cls in _CAPITAL_CLASSES:
        return "capital"
    if cls in _BS_CLASSES:
        return "bs_bc"
    if cls in _NONCOMBAT_CLASSES or threat in (THREAT_HAULER, THREAT_MINING):
        return "noncombat"
    return "other_combat"


def _bucket_counts(ship_counts: Dict[str, int]) -> Dict[str, Dict[str, int]]:
    buckets: Dict[str, Dict[str, int]] = {k: {} for k in CATEGORY_ORDER}
    for hull, qty in ship_counts.items():
        info = lookup_ship(hull)
        cat = bucket_for_hull(hull, info)
        cname = (info.get("canonical_name") if info else hull) or hull
        buckets[cat][cname] = buckets[cat].get(cname, 0) + int(qty)
    return buckets


def _mix_label(hulls: Dict[str, int]) -> str:
    total = sum(hulls.values())
    if total <= 0:
        return "0"
    parts = [f"{name}: {n}" for name, n in sorted(hulls.items(), key=lambda x: (-x[1], x[0]))]
    return f"{total} ({', '.join(parts)})"


def _delta_cell(friendly_n: int, enemy_n: int, cat: str) -> Tuple[str, str]:
    """Returns (display text, semantic: adv|disadv|even)."""
    d = friendly_n - enemy_n
    if d == 0:
        return "0", "even"
    sign = f"+{d}" if d > 0 else str(d)
    sensitive = cat in _SENSITIVE_CATS
    if d > 0 and (sensitive or abs(d) >= 2):
        return f"{sign} (Adv)", "adv"
    if d < 0 and (sensitive or abs(d) >= 2):
        return f"{sign} (Disadv)", "disadv"
    return sign, "even"


def compare_fleets(friendly_counts: Dict[str, int], enemy_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    f_b = _bucket_counts(friendly_counts)
    e_b = _bucket_counts(enemy_counts)
    rows: List[Dict[str, Any]] = []
    for cat in CATEGORY_ORDER:
        f_hulls = f_b.get(cat) or {}
        e_hulls = e_b.get(cat) or {}
        f_n = sum(f_hulls.values())
        e_n = sum(e_hulls.values())
        if f_n == 0 and e_n == 0:
            continue
        delta_txt, delta_kind = _delta_cell(f_n, e_n, cat)
        rows.append({
            "id": cat,
            "label": CATEGORY_LABELS[cat],
            "friendly": _mix_label(f_hulls),
            "enemy": _mix_label(e_hulls),
            "friendly_n": f_n,
            "enemy_n": e_n,
            "delta": delta_txt,
            "delta_kind": delta_kind,
            "friendly_hulls": f_hulls,
            "enemy_hulls": e_hulls,
        })
    return rows


def _dps_count(rows: List[Dict[str, Any]], side: str) -> int:
    keys = {"hac", "hic", "bs_bc", "other_combat", "capital"}
    nkey = "friendly_n" if side == "friendly" else "enemy_n"
    return sum(r[nkey] for r in rows if r["id"] in keys)


def assess_matchup(
    rows: List[Dict[str, Any]],
    friendly_total: int,
    enemy_total: int,
) -> List[str]:
    by_id = {r["id"]: r for r in rows}
    bullets: List[str] = []

    bullets.append(
        f"Numbers: friendly {friendly_total} hull(s) vs enemy {enemy_total} hull(s)."
    )

    ewar_e = (by_id.get("ewar") or {}).get("enemy_n", 0)
    if ewar_e >= 2:
        ewar_lvl = "High"
    elif ewar_e == 1:
        ewar_lvl = "Medium"
    else:
        ewar_lvl = "Low"
    bullets.append(
        f"EWAR threat: {ewar_lvl} (enemy Recons / EWAR platforms: {ewar_e})."
    )

    logi_f = (by_id.get("logi") or {}).get("friendly_n", 0)
    logi_e = (by_id.get("logi") or {}).get("enemy_n", 0)
    dps_f = max(1, _dps_count(rows, "friendly"))
    dps_e = max(1, _dps_count(rows, "enemy"))
    if logi_f == 0 and logi_e == 0:
        bullets.append("Logi ratio: none detected on either side.")
    else:
        rf = (dps_f / logi_f) if logi_f else float("inf")
        re = (dps_e / logi_e) if logi_e else float("inf")
        if logi_f and (not logi_e or rf < re):
            verdict = "Favorable"
        elif logi_e and (not logi_f or re < rf):
            verdict = "Unfavorable"
        else:
            verdict = "Even"
        f_txt = f"1:{rf:.1f}" if logi_f else "no logi"
        e_txt = f"1:{re:.1f}" if logi_e else "no logi"
        bullets.append(
            f"Logi ratio: {verdict} (friendly logi-to-DPS {f_txt} vs enemy {e_txt})."
        )

    tack_f = (by_id.get("tackle") or {}).get("friendly_n", 0)
    tack_e = (by_id.get("tackle") or {}).get("enemy_n", 0)
    if tack_e - tack_f >= 2:
        bullets.append(
            f"Tackle: enemy dictors / tackle exceed friendly by {tack_e - tack_f}."
        )
    elif tack_f or tack_e:
        bullets.append(f"Tackle: friendly {tack_f} vs enemy {tack_e}.")

    hac = by_id.get("hac")
    if hac:
        f_hulls = hac.get("friendly_hulls") or {}
        e_hulls = hac.get("enemy_hulls") or {}
        combined = {}
        for src in (f_hulls, e_hulls):
            for k, v in src.items():
                combined[k] = combined.get(k, 0) + v
        missile_n = sum(n for h, n in combined.items() if h in _MISSILE_HACS)
        gun_n = sum(n for h, n in combined.items() if h in _GUN_HACS and h not in _MISSILE_HACS)
        if missile_n > gun_n and missile_n > 0:
            bullets.append("Speed / range envelope: projected engagement range 40-70 km (missile HAC mix).")
        elif gun_n > missile_n and gun_n > 0:
            bullets.append("Speed / range envelope: projected engagement range 10-30 km (gun / drone HAC mix).")

    return bullets
