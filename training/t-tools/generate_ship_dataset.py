import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
# -*- coding: utf-8 -*-
"""
EVE Online Complete Ship Dataset Generator
Generates:
- training/t-data/eve_ships.json
- training/t-data/eve_ships.csv
"""
import os
import sys
import json
import csv
from typing import Dict, List, Any

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "t-data"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "A.U.R.A. Source"))
sys.path.insert(0, SRC_DIR)

from tools.build_all_eve_data import (
    get_ship_data,
    get_amarr_ships,
    get_caldari_ships,
    get_gallente_ships,
    get_minmatar_and_ore_ships
)

SUBCLASS_DEFAULTS = {
    "Corvette": {"high": 2, "mid": 1, "low": 1, "rig": 0, "turrets": 2, "launchers": 1, "pg": 15, "cpu": 110, "drone_bay": 0, "drone_bw": 0, "sig": 35, "speed": 340},
    "Shuttle": {"high": 0, "mid": 0, "low": 0, "rig": 0, "turrets": 0, "launchers": 0, "pg": 1, "cpu": 10, "drone_bay": 0, "drone_bw": 0, "sig": 25, "speed": 600},
    "Combat Frigate": {"high": 3, "mid": 3, "low": 3, "rig": 3, "turrets": 3, "launchers": 3, "pg": 45, "cpu": 150, "drone_bay": 0, "drone_bw": 0, "sig": 38, "speed": 360},
    "Assault Frigate": {"high": 4, "mid": 3, "low": 4, "rig": 2, "turrets": 3, "launchers": 3, "pg": 58, "cpu": 175, "drone_bay": 0, "drone_bw": 0, "sig": 35, "speed": 380},
    "Interceptor": {"high": 3, "mid": 3, "low": 3, "rig": 2, "turrets": 2, "launchers": 2, "pg": 38, "cpu": 140, "drone_bay": 0, "drone_bw": 0, "sig": 32, "speed": 470},
    "Covert Ops": {"high": 3, "mid": 4, "low": 2, "rig": 2, "turrets": 1, "launchers": 1, "pg": 28, "cpu": 210, "drone_bay": 0, "drone_bw": 0, "sig": 34, "speed": 330},
    "Stealth Bomber": {"high": 5, "mid": 4, "low": 2, "rig": 2, "turrets": 0, "launchers": 3, "pg": 45, "cpu": 240, "drone_bay": 0, "drone_bw": 0, "sig": 40, "speed": 280},
    "Electronic Attack Ship": {"high": 3, "mid": 5, "low": 3, "rig": 2, "turrets": 2, "launchers": 2, "pg": 42, "cpu": 220, "drone_bay": 15, "drone_bw": 15, "sig": 36, "speed": 390},
    "Faction Frigate": {"high": 3, "mid": 4, "low": 3, "rig": 3, "turrets": 3, "launchers": 3, "pg": 50, "cpu": 170, "drone_bay": 20, "drone_bw": 20, "sig": 35, "speed": 430},
    "Logistics Frigate": {"high": 3, "mid": 4, "low": 3, "rig": 2, "turrets": 0, "launchers": 0, "pg": 40, "cpu": 200, "drone_bay": 0, "drone_bw": 0, "sig": 33, "speed": 400},
    "Destroyer": {"high": 8, "mid": 2, "low": 3, "rig": 3, "turrets": 7, "launchers": 7, "pg": 72, "cpu": 200, "drone_bay": 0, "drone_bw": 0, "sig": 65, "speed": 310},
    "Interdictor": {"high": 8, "mid": 3, "low": 3, "rig": 2, "turrets": 6, "launchers": 6, "pg": 76, "cpu": 225, "drone_bay": 0, "drone_bw": 0, "sig": 68, "speed": 325},
    "Command Destroyer": {"high": 6, "mid": 4, "low": 4, "rig": 2, "turrets": 4, "launchers": 4, "pg": 88, "cpu": 245, "drone_bay": 0, "drone_bw": 0, "sig": 62, "speed": 330},
    "Tactical Destroyer": {"high": 6, "mid": 4, "low": 4, "rig": 1, "turrets": 4, "launchers": 4, "pg": 84, "cpu": 235, "drone_bay": 0, "drone_bw": 0, "sig": 60, "speed": 315},
    "Cruiser": {"high": 5, "mid": 4, "low": 5, "rig": 3, "turrets": 4, "launchers": 4, "pg": 950, "cpu": 360, "drone_bay": 50, "drone_bw": 50, "sig": 130, "speed": 220},
    "Heavy Assault Cruiser": {"high": 5, "mid": 4, "low": 6, "rig": 2, "turrets": 5, "launchers": 5, "pg": 1150, "cpu": 410, "drone_bay": 50, "drone_bw": 50, "sig": 125, "speed": 230},
    "Heavy Interdiction Cruiser": {"high": 6, "mid": 6, "low": 4, "rig": 2, "turrets": 4, "launchers": 4, "pg": 1300, "cpu": 430, "drone_bay": 25, "drone_bw": 25, "sig": 140, "speed": 210},
    "Combat Recon Ship": {"high": 5, "mid": 5, "low": 4, "rig": 2, "turrets": 4, "launchers": 4, "pg": 900, "cpu": 480, "drone_bay": 50, "drone_bw": 50, "sig": 120, "speed": 215},
    "Force Recon Ship": {"high": 5, "mid": 5, "low": 4, "rig": 2, "turrets": 3, "launchers": 3, "pg": 880, "cpu": 470, "drone_bay": 40, "drone_bw": 40, "sig": 115, "speed": 225},
    "Logistics Cruiser": {"high": 5, "mid": 5, "low": 4, "rig": 2, "turrets": 0, "launchers": 0, "pg": 1050, "cpu": 440, "drone_bay": 25, "drone_bw": 25, "sig": 110, "speed": 240},
    "Strategic Cruiser": {"high": 6, "mid": 6, "low": 6, "rig": 3, "turrets": 5, "launchers": 5, "pg": 1200, "cpu": 460, "drone_bay": 60, "drone_bw": 50, "sig": 115, "speed": 235, "subsystems": 4},
    "Faction Cruiser": {"high": 5, "mid": 5, "low": 5, "rig": 3, "turrets": 4, "launchers": 4, "pg": 1050, "cpu": 390, "drone_bay": 75, "drone_bw": 50, "sig": 120, "speed": 260},
    "Battlecruiser": {"high": 7, "mid": 5, "low": 6, "rig": 3, "turrets": 6, "launchers": 6, "pg": 1350, "cpu": 440, "drone_bay": 50, "drone_bw": 50, "sig": 260, "speed": 155},
    "Attack Battlecruiser": {"high": 8, "mid": 5, "low": 5, "rig": 3, "turrets": 8, "launchers": 8, "pg": 9500, "cpu": 410, "drone_bay": 0, "drone_bw": 0, "sig": 310, "speed": 200},
    "Command Ship": {"high": 7, "mid": 5, "low": 6, "rig": 2, "turrets": 5, "launchers": 5, "pg": 1600, "cpu": 510, "drone_bay": 75, "drone_bw": 50, "sig": 240, "speed": 165},
    "Faction Battlecruiser": {"high": 7, "mid": 5, "low": 6, "rig": 3, "turrets": 6, "launchers": 6, "pg": 1500, "cpu": 470, "drone_bay": 75, "drone_bw": 50, "sig": 250, "speed": 180},
    "Battleship": {"high": 8, "mid": 6, "low": 7, "rig": 3, "turrets": 7, "launchers": 7, "pg": 16500, "cpu": 650, "drone_bay": 125, "drone_bw": 100, "sig": 420, "speed": 115},
    "Marauder": {"high": 8, "mid": 6, "low": 7, "rig": 2, "turrets": 4, "launchers": 4, "pg": 19500, "cpu": 720, "drone_bay": 125, "drone_bw": 100, "sig": 440, "speed": 120},
    "Black Ops": {"high": 8, "mid": 6, "low": 7, "rig": 2, "turrets": 6, "launchers": 6, "pg": 17500, "cpu": 700, "drone_bay": 125, "drone_bw": 100, "sig": 380, "speed": 140},
    "Faction Battleship": {"high": 8, "mid": 7, "low": 7, "rig": 3, "turrets": 7, "launchers": 7, "pg": 18000, "cpu": 710, "drone_bay": 175, "drone_bw": 125, "sig": 400, "speed": 145},
    "Dreadnought": {"high": 6, "mid": 5, "low": 7, "rig": 3, "turrets": 3, "launchers": 3, "pg": 650000, "cpu": 950, "drone_bay": 0, "drone_bw": 0, "sig": 8500, "speed": 75},
    "Lancer Dreadnought": {"high": 6, "mid": 5, "low": 7, "rig": 3, "turrets": 3, "launchers": 3, "pg": 680000, "cpu": 980, "drone_bay": 0, "drone_bw": 0, "sig": 8700, "speed": 75},
    "Carrier": {"high": 5, "mid": 6, "low": 6, "rig": 3, "turrets": 0, "launchers": 0, "pg": 550000, "cpu": 1100, "drone_bay": 0, "drone_bw": 0, "sig": 9800, "speed": 70},
    "Force Auxiliary": {"high": 5, "mid": 6, "low": 6, "rig": 3, "turrets": 0, "launchers": 0, "pg": 580000, "cpu": 1050, "drone_bay": 0, "drone_bw": 0, "sig": 9500, "speed": 65},
    "Supercarrier": {"high": 6, "mid": 7, "low": 7, "rig": 3, "turrets": 0, "launchers": 0, "pg": 1200000, "cpu": 1800, "drone_bay": 0, "drone_bw": 0, "sig": 18000, "speed": 60},
    "Titan": {"high": 8, "mid": 7, "low": 8, "rig": 3, "turrets": 6, "launchers": 6, "pg": 4500000, "cpu": 2500, "drone_bay": 0, "drone_bw": 0, "sig": 35000, "speed": 50},
    "Mining Barge": {"high": 2, "mid": 4, "low": 2, "rig": 3, "turrets": 2, "launchers": 0, "pg": 45, "cpu": 260, "drone_bay": 50, "drone_bw": 25, "sig": 200, "speed": 100},
    "Exhumer": {"high": 2, "mid": 4, "low": 3, "rig": 2, "turrets": 2, "launchers": 0, "pg": 60, "cpu": 320, "drone_bay": 50, "drone_bw": 50, "sig": 180, "speed": 110},
    "Industrial": {"high": 2, "mid": 4, "low": 4, "rig": 3, "turrets": 0, "launchers": 0, "pg": 95, "cpu": 250, "drone_bay": 0, "drone_bw": 0, "sig": 240, "speed": 130},
    "Blockade Runner": {"high": 2, "mid": 4, "low": 4, "rig": 2, "turrets": 0, "launchers": 0, "pg": 110, "cpu": 280, "drone_bay": 0, "drone_bw": 0, "sig": 150, "speed": 210},
    "Deep Space Transport": {"high": 2, "mid": 4, "low": 5, "rig": 2, "turrets": 0, "launchers": 0, "pg": 180, "cpu": 310, "drone_bay": 0, "drone_bw": 0, "sig": 220, "speed": 105},
    "Freighter": {"high": 0, "mid": 0, "low": 3, "rig": 3, "turrets": 0, "launchers": 0, "pg": 0, "cpu": 0, "drone_bay": 0, "drone_bw": 0, "sig": 3500, "speed": 65},
    "Jump Freighter": {"high": 0, "mid": 0, "low": 3, "rig": 3, "turrets": 0, "launchers": 0, "pg": 0, "cpu": 0, "drone_bay": 0, "drone_bw": 0, "sig": 3800, "speed": 60}
}


def build_complete_ship_dataset() -> List[Dict[str, Any]]:
    raw_ships = {}
    raw_ships.update(get_ship_data())
    raw_ships.update(get_amarr_ships())
    raw_ships.update(get_caldari_ships())
    raw_ships.update(get_gallente_ships())
    raw_ships.update(get_minmatar_and_ore_ships())

    ships_list = []

    for name, s_info in sorted(raw_ships.items()):
        s_class = s_info.get("class", "Frigate")
        role = s_info.get("role", "Combat Ship")
        faction = s_info.get("faction", "Generic")
        tank_type = s_info.get("tank", "Shield / Armor")
        optimal = s_info.get("optimal_range", "Standard")
        tactics = s_info.get("tactics", "Standard combat doctrine.")
        threat = s_info.get("threat", "THREAT_COMBAT")

        subclass_key = "Combat Frigate"
        if "Titan" in s_class: subclass_key = "Titan"
        elif "Supercarrier" in s_class: subclass_key = "Supercarrier"
        elif "Carrier" in s_class: subclass_key = "Carrier"
        elif "Force Auxiliary" in s_class or "FAX" in role: subclass_key = "Force Auxiliary"
        elif "Dreadnought" in s_class: subclass_key = "Dreadnought"
        elif "Marauder" in s_class or "Marauder" in role: subclass_key = "Marauder"
        elif "Black Ops" in s_class or "Black Ops" in role: subclass_key = "Black Ops"
        elif "Strategic Cruiser" in s_class or "T3C" in role: subclass_key = "Strategic Cruiser"
        elif "Tactical Destroyer" in s_class or "T3D" in role: subclass_key = "Tactical Destroyer"
        elif "Command Ship" in s_class or "Command Ship" in role: subclass_key = "Command Ship"
        elif "Command Destroyer" in s_class: subclass_key = "Command Destroyer"
        elif "Heavy Assault Cruiser" in s_class or "HAC" in role: subclass_key = "Heavy Assault Cruiser"
        elif "Heavy Interdiction" in s_class or "HIC" in role: subclass_key = "Heavy Interdiction Cruiser"
        elif "Interdictor" in s_class or "Dictor" in role: subclass_key = "Interdictor"
        elif "Assault Frigate" in s_class or "Assault" in role: subclass_key = "Assault Frigate"
        elif "Interceptor" in s_class or "Interceptor" in role: subclass_key = "Interceptor"
        elif "Stealth Bomber" in s_class or "Bomber" in role: subclass_key = "Stealth Bomber"
        elif "Covert Ops" in s_class: subclass_key = "Covert Ops"
        elif "Electronic Attack" in s_class: subclass_key = "Electronic Attack Ship"
        elif "Logistics Cruiser" in s_class or "Logistics" in role: subclass_key = "Logistics Cruiser"
        elif "Combat Recon" in s_class: subclass_key = "Combat Recon Ship"
        elif "Force Recon" in s_class: subclass_key = "Force Recon Ship"
        elif "Attack Battlecruiser" in s_class: subclass_key = "Attack Battlecruiser"
        elif "Battlecruiser" in s_class: subclass_key = "Battlecruiser"
        elif "Battleship" in s_class: subclass_key = "Battleship"
        elif "Cruiser" in s_class: subclass_key = "Cruiser"
        elif "Destroyer" in s_class: subclass_key = "Destroyer"
        elif "Mining Barge" in s_class: subclass_key = "Mining Barge"
        elif "Exhumer" in s_class: subclass_key = "Exhumer"
        elif "Industrial" in s_class: subclass_key = "Industrial"
        elif "Freighter" in s_class: subclass_key = "Freighter"
        elif "Shuttle" in s_class: subclass_key = "Shuttle"
        elif "Corvette" in s_class: subclass_key = "Corvette"

        profile = SUBCLASS_DEFAULTS.get(subclass_key, SUBCLASS_DEFAULTS["Combat Frigate"])

        bonuses = []
        if "Laser" in role or "Amarr" in faction:
            bonuses.append("Energy Turret Damage & Optimal Range bonus per level")
            bonuses.append("Capacitor usage reduction for Energy Weapons")
        if "Missile" in role or "Caldari" in faction:
            bonuses.append("Missile kinetic/thermal velocity, flight time and explosion radius bonus")
            bonuses.append("Shield resistance or shield capacity bonus")
        if "Hybrid" in role or "Blaster" in role or "Rail" in role or "Gallente" in faction:
            bonuses.append("Hybrid Turret damage and tracking speed bonus per level")
            bonuses.append("Armor repairer effectiveness or Armor HP bonus")
        if "Projectile" in role or "Autocannon" in role or "Artillery" in role or "Minmatar" in faction:
            bonuses.append("Projectile Turret rate of fire and falloff bonus per level")
            bonuses.append("Sub-warp velocity and signature radius mobility bonus")
        if "Drone" in role or "Guristas" in faction or "Gila" in name or "Worm" in name or "Rattlesnake" in name:
            bonuses.append("Role Bonus: Extreme Drone HP and Damage output multiplier (up to 500%)")
        if "Web" in role or "Serpentis" in faction or "Vindicator" in name or "Daredevil" in name:
            bonuses.append("Role Bonus: 90% Stasis Webifier velocity reduction strength")
        if "Neut" in role or "NOS" in role or "Blood Raiders" in faction or "Bhaalgorn" in name:
            bonuses.append("Role Bonus: 100% Energy Drain range and Nosferatu cap-neutral drain bonus")
        if "Marauder" in subclass_key:
            bonuses.append("Role Bonus: Bastion Module capability (100% weapon range, 100% local rep, EWAR immunity)")
        if "Covert" in role or "Stealth" in role or "Black Ops" in subclass_key:
            bonuses.append("Role Bonus: Covert Ops Cloaking Device fitting & zero cloak reactivation delay")

        ship_record = {
            "name": name,
            "ship_class": s_class,
            "sub_class": subclass_key,
            "faction": faction,
            "role": role,
            "threat_rating": threat,
            "tank_doctrine": tank_type,
            "optimal_engagement_range": optimal,
            "tactical_combat_notes": tactics,
            "slot_layout": {
                "high_slots": profile.get("high", 4),
                "mid_slots": profile.get("mid", 4),
                "low_slots": profile.get("low", 4),
                "rig_slots": profile.get("rig", 3),
                "subsystem_slots": profile.get("subsystems", 0)
            },
            "hardpoints": {
                "turret_hardpoints": profile.get("turrets", 3),
                "launcher_hardpoints": profile.get("launchers", 3)
            },
            "fitting_capacity": {
                "powergrid_mw": profile.get("pg", 50),
                "cpu_tf": profile.get("cpu", 180),
                "rig_calibration": 400 if profile.get("rig", 3) == 3 else 300
            },
            "mobility": {
                "base_speed_ms": profile.get("speed", 300),
                "signature_radius_m": profile.get("sig", 40)
            },
            "drone_bay": {
                "capacity_m3": profile.get("drone_bay", 0),
                "bandwidth_mbits": profile.get("drone_bw", 0)
            },
            "specific_hull_bonuses": bonuses
        }
        ships_list.append(ship_record)

    return ships_list


def export_datasets():
    print("[A.U.R.A. Data Generator] Building full EVE Online Ships dataset...")
    ships = build_complete_ship_dataset()

    json_path = os.path.join(OUTPUT_DIR, "eve_ships.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ships, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported JSON dataset: {json_path} ({len(ships)} ships)")

    csv_path = os.path.join(OUTPUT_DIR, "eve_ships.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Class", "SubClass", "Faction", "Role", "ThreatRating", "TankDoctrine",
            "OptimalRange", "HighSlots", "MidSlots", "LowSlots", "RigSlots", "Turrets", "Launchers",
            "Powergrid_MW", "CPU_tf", "BaseSpeed_ms", "SigRadius_m", "DroneBay_m3", "DroneBandwidth_Mbit", "HullBonuses"
        ])
        for s in ships:
            writer.writerow([
                s["name"],
                s["ship_class"],
                s["sub_class"],
                s["faction"],
                s["role"],
                s["threat_rating"],
                s["tank_doctrine"],
                s["optimal_engagement_range"],
                s["slot_layout"]["high_slots"],
                s["slot_layout"]["mid_slots"],
                s["slot_layout"]["low_slots"],
                s["slot_layout"]["rig_slots"],
                s["hardpoints"]["turret_hardpoints"],
                s["hardpoints"]["launcher_hardpoints"],
                s["fitting_capacity"]["powergrid_mw"],
                s["fitting_capacity"]["cpu_tf"],
                s["mobility"]["base_speed_ms"],
                s["mobility"]["signature_radius_m"],
                s["drone_bay"]["capacity_m3"],
                s["drone_bay"]["bandwidth_mbits"],
                " | ".join(s["specific_hull_bonuses"])
            ])
    print(f"  [OK] Exported CSV dataset:  {csv_path} ({len(ships)} rows)")


if __name__ == "__main__":
    export_datasets()
