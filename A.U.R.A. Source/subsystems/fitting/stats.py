"""
Approximate hull HP / CPU / powergrid and per-module load for the visual fitter.
Uses class baselines plus keyword matching for EFT names. Not a full dogma engine.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.eve_data import lookup_module, lookup_ship

# cpu, powergrid, shield, armor, hull, calibration
_CLASS_HULL: Dict[str, Tuple[float, float, float, float, float, float]] = {
    "Corvette": (125, 28, 200, 180, 160, 400),
    "Frigate": (180, 48, 500, 450, 350, 400),
    "Navy Frigate": (195, 52, 550, 500, 380, 400),
    "Faction Frigate": (200, 55, 580, 480, 360, 400),
    "Assault Frigate": (180, 50, 700, 800, 450, 400),
    "Interceptor": (160, 40, 380, 320, 280, 400),
    "Covert Ops": (200, 32, 320, 280, 250, 400),
    "Stealth Bomber": (265, 40, 350, 300, 280, 400),
    "Electronic Attack Ship": (220, 42, 400, 380, 300, 400),
    "Expedition Frigate": (200, 50, 600, 500, 400, 400),
    "Logistics Frigate": (220, 48, 500, 700, 400, 400),
    "Destroyer": (200, 68, 750, 700, 600, 400),
    "Tactical Destroyer": (240, 80, 900, 850, 700, 400),
    "Command Destroyer": (230, 75, 850, 800, 650, 400),
    "Interdictor": (210, 62, 700, 650, 550, 400),
    "Cruiser": (375, 820, 2200, 2100, 1800, 400),
    "Navy Cruiser": (400, 880, 2500, 2400, 1900, 400),
    "Faction Cruiser": (420, 900, 2600, 2300, 1900, 400),
    "Heavy Assault Cruiser": (400, 950, 2800, 3200, 2200, 400),
    "Heavy Interdiction Cruiser": (420, 1000, 3200, 3400, 2400, 400),
    "Recon": (420, 780, 1800, 2000, 1600, 400),
    "Combat Recon": (420, 800, 2000, 2200, 1700, 400),
    "Force Recon": (430, 760, 1700, 1900, 1500, 400),
    "Logistics": (430, 850, 1800, 2800, 2000, 400),
    "Strategic Cruiser": (450, 900, 2800, 3000, 2200, 400),
    "Flag Cruiser": (440, 920, 2600, 2800, 2100, 400),
    "Battlecruiser": (475, 1350, 4500, 4300, 3800, 400),
    "Attack Battlecruiser": (450, 1250, 2800, 2600, 2400, 400),
    "Command Ship": (520, 1450, 5500, 5200, 4200, 400),
    "Battleship": (780, 12500, 7500, 7200, 6800, 400),
    "Faction Battleship": (820, 13500, 8200, 7800, 7200, 400),
    "Marauder": (780, 14000, 9000, 9500, 8000, 400),
    "Black Ops": (750, 11000, 7000, 7500, 6500, 400),
    "Dreadnought": (900, 550000, 180000, 200000, 160000, 400),
    "Faction Dreadnought": (950, 580000, 200000, 220000, 170000, 400),
    "Lancer Dreadnought": (950, 560000, 190000, 210000, 165000, 400),
    "Carrier": (850, 450000, 160000, 180000, 150000, 400),
    "Force Auxiliary": (900, 500000, 200000, 240000, 180000, 400),
    "Supercarrier": (1100, 900000, 1400000, 1200000, 900000, 400),
    "Titan": (1400, 1500000, 2500000, 2200000, 1800000, 400),
    "Freighter": (500, 18000, 20000, 40000, 35000, 400),
    "Jump Freighter": (520, 20000, 22000, 45000, 38000, 400),
    "Industrial": (280, 250, 1200, 1400, 1100, 400),
    "Industrial Command": (400, 900, 4000, 4500, 3800, 400),
    "Capital Industrial": (700, 400000, 120000, 140000, 110000, 400),
    "Mining Barge": (310, 220, 2500, 1800, 1600, 400),
    "Exhumer": (340, 260, 3200, 2200, 1800, 400),
}

# Typical T2-ish CPU / PG by (category-or-keyword, size)
# size: S M L XL C U
_CAT_LOAD: Dict[str, Dict[str, Tuple[float, float]]] = {
    "Energy Turret": {"S": (16, 9), "M": (30, 155), "L": (44, 1650), "C": (80, 100000)},
    "Hybrid Turret": {"S": (18, 10), "M": (35, 165), "L": (50, 1800), "C": (85, 110000)},
    "Projectile Turret": {"S": (10, 5), "M": (22, 110), "L": (38, 1450), "C": (70, 90000)},
    "Missile": {"S": (22, 4), "M": (40, 90), "L": (55, 1100), "C": (90, 80000)},
    "Disintegrator": {"S": (24, 12), "M": (42, 180), "L": (60, 1900), "C": (90, 120000)},
    "Smartbomb": {"S": (16, 8), "M": (28, 140), "L": (40, 1400), "C": (70, 80000)},
    "Energy Nosferatu": {"S": (10, 6), "M": (18, 150), "L": (28, 1500), "C": (50, 80000)},
    "Energy Neutralizer": {"S": (12, 8), "M": (22, 175), "L": (32, 1750), "C": (55, 90000)},
    "Cloak": {"U": (24, 1)},
    "Probe": {"U": (20, 1)},
    "Propulsion": {"S": (22, 14), "M": (50, 165), "L": (75, 1375), "C": (100, 50000)},
    "Afterburner": {"S": (18, 10), "M": (30, 75), "L": (40, 625), "C": (60, 25000)},
    "Shield Extender": {"S": (18, 2), "M": (28, 2), "L": (38, 2), "C": (55, 50)},
    "Shield Booster": {"S": (22, 8), "M": (50, 150), "L": (80, 800), "C": (120, 40000)},
    "Shield Hardener": {"U": (30, 1)},
    "Shield Resistance": {"U": (25, 1)},
    "Cap Battery": {"S": (12, 6), "M": (20, 80), "L": (28, 250), "C": (40, 8000)},
    "Cap Booster": {"S": (8, 6), "M": (14, 120), "L": (20, 400), "C": (30, 12000)},
    "Warp Disruptor": {"U": (32, 1)},
    "Warp Scrambler": {"U": (30, 1)},
    "Stasis Webifier": {"U": (30, 1)},
    "Target Painter": {"U": (28, 1)},
    "Tracking Computer": {"U": (22, 1)},
    "Sensor Booster": {"U": (18, 1)},
    "ECCM": {"U": (22, 1)},
    "ECM": {"U": (40, 1)},
    "Dampener": {"U": (30, 1)},
    "Tracking Disruptor": {"U": (30, 1)},
    "Guidance Disruptor": {"U": (30, 1)},
    "Armor Repairer": {"S": (8, 6), "M": (18, 145), "L": (28, 1688), "C": (50, 90000)},
    "Armor Plate": {"S": (8, 1), "M": (14, 1), "L": (22, 1), "C": (40, 50)},
    "Armor Hardener": {"U": (22, 1)},
    "Energized": {"U": (24, 1)},
    "Damage Control": {"U": (28, 1)},
    "Gyrostabilizer": {"U": (18, 1)},
    "Magnetic Field": {"U": (18, 1)},
    "Heat Sink": {"U": (18, 1)},
    "Ballistic Control": {"U": (35, 1)},
    "Tracking Enhancer": {"U": (16, 1)},
    "Nanofiber": {"U": (18, 1)},
    "Overdrive": {"U": (16, 1)},
    "Inertia": {"U": (16, 1)},
    "Warp Core": {"U": (20, 1)},
    "Drone Amp": {"U": (28, 1)},
    "Drone Nav": {"U": (22, 1)},
    "Omnidirectional": {"U": (32, 1)},
    "Power Diagnostic": {"U": (14, 0)},
    "Reactor Control": {"U": (16, 0)},
    "CPU Upgrade": {"U": (0, 1)},
    "Co-Processor": {"U": (0, 1)},
    "Rig": {"S": (0, 0), "M": (0, 0), "L": (0, 0), "C": (0, 0)},
}

_SHIELD_HP = {
    "small shield extender": 400,
    "medium shield extender": 1500,
    "large shield extender": 2000,
    "capital shield extender": 20000,
}
_ARMOR_HP = {
    "200mm": 450,
    "400mm": 850,
    "800mm": 1600,
    "1600mm": 3200,
}


def _class_key(ship_class: str) -> str:
    c = (ship_class or "Frigate").strip()
    if c in _CLASS_HULL:
        return c
    cl = c.lower()
    for key in _CLASS_HULL:
        if key.lower() in cl or cl in key.lower():
            return key
    if "frigate" in cl:
        return "Frigate"
    if "destroyer" in cl:
        return "Destroyer"
    if "battlecruiser" in cl:
        return "Battlecruiser"
    if "battleship" in cl:
        return "Battleship"
    if "cruiser" in cl:
        return "Cruiser"
    if "dread" in cl:
        return "Dreadnought"
    if "carrier" in cl and "super" in cl:
        return "Supercarrier"
    if "carrier" in cl:
        return "Carrier"
    if "titan" in cl:
        return "Titan"
    return "Cruiser"


def hull_resources(ship_info: Optional[Dict[str, Any]]) -> Dict[str, float]:
    if not ship_info:
        cpu, pg, sh, ar, hu, cal = _CLASS_HULL["Frigate"]
        return {"cpu": cpu, "powergrid": pg, "shield": sh, "armor": ar, "hull": hu, "calibration": cal}
    key = _class_key(str(ship_info.get("class") or "Frigate"))
    cpu, pg, sh, ar, hu, cal = _CLASS_HULL[key]
    faction = str(ship_info.get("faction") or "").lower()
    mult = 1.0
    if any(p in faction for p in ("angel", "gurista", "serpentis", "blood", "sansha", "mordu", "soe", "triglav", "edencom", "ore")):
        mult = 1.08
    elif "navy" in faction or "fleet" in str(ship_info.get("class") or "").lower():
        mult = 1.05
    explicit_cpu = ship_info.get("cpu")
    explicit_pg = ship_info.get("powergrid")
    return {
        "cpu": float(explicit_cpu if explicit_cpu is not None else cpu * mult),
        "powergrid": float(explicit_pg if explicit_pg is not None else pg * mult),
        "shield": float(ship_info.get("shield_hp") or sh * mult),
        "armor": float(ship_info.get("armor_hp") or ar * mult),
        "hull": float(ship_info.get("hull_hp") or hu * mult),
        "calibration": float(ship_info.get("calibration") or cal),
    }


def _size_token(text: str, info: Optional[Dict[str, Any]]) -> str:
    blob = (text or "").lower()
    size = str((info or {}).get("size") or "").lower()
    if "capital" in blob or size.startswith("capital"):
        return "C"
    if any(k in blob for k in ("500mn", "100mn", "xl ", "x-large", "capital")) or size.startswith("large") and "xl" in blob:
        if "x-large" in blob or "xl " in blob:
            return "L"
    if any(k in blob for k in ("1400mm", "1200mm", "800mm ac", "425mm rail", "350mm", "mega ", "tachyon", "cruise", "torpedo", "large ")) or size == "large":
        return "L"
    if any(k in blob for k in ("50mn", "10mn", "720mm", "650mm", "425mm", "220mm", "heavy ", "medium ", "ham", "rapid heavy")) or size == "medium":
        return "M"
    if any(k in blob for k in ("1mn", "5mn", "small ", "light ", "rocket")) or size == "small":
        return "S"
    if size.startswith("small"):
        return "S"
    if size.startswith("medium"):
        return "M"
    if size.startswith("large"):
        return "L"
    return "U"


def _category_load(info: Optional[Dict[str, Any]], name: str) -> Tuple[float, float]:
    blob = name.lower()
    cat = str((info or {}).get("category") or "")
    size = _size_token(name, info)

    def pick(key: str) -> Optional[Tuple[float, float]]:
        row = _CAT_LOAD.get(key)
        if not row:
            return None
        if size in row:
            return row[size]
        if "U" in row:
            return row["U"]
        return next(iter(row.values()))

    if cat and cat in _CAT_LOAD:
        hit = pick(cat)
        if hit:
            return hit

    rules = [
        (("pulse laser", "beam laser", "energy turret"), "Energy Turret"),
        (("blaster", "railgun", "hybrid"), "Hybrid Turret"),
        (("autocannon", "artillery", "projectile"), "Projectile Turret"),
        (("missile", "rocket", "torpedo", "launcher", "bomb"), "Missile"),
        (("disintegrator", "entropic"), "Disintegrator"),
        (("smartbomb",), "Smartbomb"),
        (("nosferatu", "nos "), "Energy Nosferatu"),
        (("neutralizer", "neut"), "Energy Neutralizer"),
        (("cloak", "cloaking"), "Cloak"),
        (("probe launcher", "core probe", "expanded probe"), "Probe"),
        (("microwarpdrive", "mwd", "micro jump"), "Propulsion"),
        (("afterburner",), "Afterburner"),
        (("shield extender",), "Shield Extender"),
        (("shield booster", "ancillary shield"), "Shield Booster"),
        (("shield hardener", "invulnerability", "adaptive invul"), "Shield Hardener"),
        (("shield resistance", "em ward", "thermal dissip", "kinetic deflect", "explosive deflect"), "Shield Resistance"),
        (("cap battery", "capacitor battery"), "Cap Battery"),
        (("cap booster", "capacitor booster"), "Cap Booster"),
        (("warp disruptor", "disruptor"), "Warp Disruptor"),
        (("warp scrambler", "scrambler", "scram"), "Warp Scrambler"),
        (("webifier", "stasis web", "grappler"), "Stasis Webifier"),
        (("target painter",), "Target Painter"),
        (("tracking computer",), "Tracking Computer"),
        (("sensor booster",), "Sensor Booster"),
        (("ecm", "jammer"), "ECM"),
        (("dampener", "remote sensor damp"), "Dampener"),
        (("tracking disruptor",), "Tracking Disruptor"),
        (("armor repairer", "ancillary armor"), "Armor Repairer"),
        (("steel plate", "rolled tungsten", "1600mm", "800mm", "400mm", "200mm"), "Armor Plate"),
        (("armor hardener", "reactive armor"), "Armor Hardener"),
        (("energized", "coating", "membrane"), "Energized"),
        (("damage control", "assault damage"), "Damage Control"),
        (("gyro",), "Gyrostabilizer"),
        (("magnetic field", "mag stab"), "Magnetic Field"),
        (("heat sink",), "Heat Sink"),
        (("ballistic control", "bcs"), "Ballistic Control"),
        (("tracking enhancer",), "Tracking Enhancer"),
        (("nanofiber",), "Nanofiber"),
        (("overdrive",), "Overdrive"),
        (("inertial", "i-stab"), "Inertia"),
        (("warp core stab",), "Warp Core"),
        (("drone damage amplifier", "dda"), "Drone Amp"),
        (("drone navigation",), "Drone Nav"),
        (("omnidirectional", "omni tracking"), "Omnidirectional"),
        (("power diagnostic", "pdu"), "Power Diagnostic"),
        (("reactor control",), "Reactor Control"),
        (("co-processor", "cpu upgrade"), "CPU Upgrade"),
        (("rig", "cdfe", "trimark", "polycarbon", "hyperspatial", "burst aerator"), "Rig"),
    ]
    for keys, cat_name in rules:
        if any(k in blob for k in keys):
            hit = pick(cat_name)
            if hit:
                return hit
    slot = str((info or {}).get("slot") or "").lower()
    if slot.startswith("rig"):
        return (0.0, 0.0)
    if slot.startswith("high"):
        return (20.0, 12.0) if size == "S" else ((32.0, 140.0) if size != "L" else (45.0, 1500.0))
    if slot.startswith("mid"):
        return (25.0, 8.0)
    if slot.startswith("low"):
        return (18.0, 1.0)
    return (12.0, 5.0)


def module_load(name: str) -> Dict[str, float]:
    """CPU, PG, calibration, and extra shield/armor HP from a fitted module name."""
    info = lookup_module(name)
    cpu, pg = _category_load(info, name)
    blob = name.lower()
    cal = 0.0
    if "rig" in blob or str((info or {}).get("slot") or "").lower().startswith("rig"):
        cal = 150.0 if " ii" in blob or blob.endswith("ii") else 100.0
        if "compact" in blob or " i " in f" {blob} ":
            cal = 100.0
    shield_add = 0.0
    armor_add = 0.0
    for key, hp in _SHIELD_HP.items():
        if key in blob:
            shield_add = hp
            break
    if "shield extender" in blob and not shield_add:
        shield_add = 1500.0
    for key, hp in _ARMOR_HP.items():
        if key in blob:
            armor_add = hp
            break
    cpu_bonus = 0.0
    pg_bonus = 0.0
    if "co-processor" in blob or "cpu" in blob and "upgrade" in blob:
        cpu_bonus = 50.0
        cpu = 0.0
    if "reactor control" in blob:
        pg_bonus = 50.0
        cpu = 16.0
        pg = 0.0
    if "power diagnostic" in blob:
        pg_bonus = 20.0
        cpu_bonus = 15.0
    shield_pct = 0.0
    armor_pct = 0.0
    if "core defense field extender" in blob or "cdfe" in blob:
        shield_pct = 0.15
        cal = cal or 150.0
    if "trimark" in blob:
        armor_pct = 0.15
        cal = cal or 150.0
    return {
        "name": name,
        "cpu": cpu,
        "powergrid": pg,
        "calibration": cal,
        "cpu_bonus": cpu_bonus,
        "pg_bonus": pg_bonus,
        "shield_hp": shield_add,
        "armor_hp": armor_add,
        "shield_pct": shield_pct,
        "armor_pct": armor_pct,
        "slot": str((info or {}).get("slot") or ""),
        "category": str((info or {}).get("category") or ""),
    }


def compute_fit(hull_name: str, fitted: List[str]) -> Dict[str, Any]:
    ship = lookup_ship(hull_name)
    base = hull_resources(ship)
    modules = [module_load(n) for n in fitted if n]
    cpu_used = sum(m["cpu"] for m in modules)
    pg_used = sum(m["powergrid"] for m in modules)
    cal_used = sum(m["calibration"] for m in modules)
    cpu_out = base["cpu"] + sum(m["cpu_bonus"] for m in modules)
    pg_out = base["powergrid"] + sum(m["pg_bonus"] for m in modules)
    shield = (base["shield"] + sum(m["shield_hp"] for m in modules)) * (1.0 + sum(m["shield_pct"] for m in modules))
    armor = (base["armor"] + sum(m["armor_hp"] for m in modules)) * (1.0 + sum(m["armor_pct"] for m in modules))
    hull = base["hull"]
    ehp = shield + armor + hull
    return {
        "hull_name": ship.get("canonical_name", hull_name) if ship else hull_name,
        "ship_class": ship.get("class", "") if ship else "",
        "cpu_output": cpu_out,
        "cpu_used": cpu_used,
        "pg_output": pg_out,
        "pg_used": pg_used,
        "cal_output": base["calibration"],
        "cal_used": cal_used,
        "shield": shield,
        "armor": armor,
        "hull": hull,
        "ehp": ehp,
        "cpu_ok": cpu_used <= cpu_out + 0.05,
        "pg_ok": pg_used <= pg_out + 0.05,
        "cal_ok": cal_used <= base["calibration"] + 0.05,
        "modules": modules,
        "approximate": True,
    }


def calculate_fit_stats(fit_dict: Dict[str, Any]) -> Dict[str, Any]:
    ship_name = fit_dict.get("ship_name", "")
    all_modules = (
        fit_dict.get("high_slots", []) +
        fit_dict.get("mid_slots", []) +
        fit_dict.get("low_slots", []) +
        fit_dict.get("rig_slots", []) +
        fit_dict.get("subsystems", [])
    )
    res = compute_fit(ship_name, all_modules)
    ehp = res.get("ehp", 0.0)
    cpu_pct = (res["cpu_used"] / max(res["cpu_output"], 1.0)) * 100.0
    pg_pct = (res["pg_used"] / max(res["pg_output"], 1.0)) * 100.0
    return {
        "ehp": ehp,
        "total_dps": 0.0,
        "cap_stable": True,
        "cap_time_sec": 300.0,
        "cpu_pct": cpu_pct,
        "pg_pct": pg_pct,
        "compute_fit": res
    }

