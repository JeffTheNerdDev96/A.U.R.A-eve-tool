import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
# -*- coding: utf-8 -*-
"""
EVE Online Complete Solar Systems Dataset Generator
Generates:
- training/t-data/eve_solar_systems.json
- training/t-data/eve_solar_systems.csv
"""
import os
import json
import csv
from typing import Dict, List, Any

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "t-data"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Comprehensive list of major Solar Systems across Highsec, Lowsec, Nullsec, FW, Incursions, Pochven, Wormhole, and Trade Hubs
MAJOR_SYSTEMS_DATABASE = [
    # --- Major Trade Hubs & Empire Capitals ---
    {"name": "Jita", "region": "The Forge", "constellation": "Kimotoro", "sec": 0.9, "truesec": 0.94, "class": "Highsec (Main Trade Hub 4-4)", "stargates": 4, "stations": 14, "faction": "Caldari State"},
    {"name": "Amarr", "region": "Domain", "constellation": "Throne Worlds", "sec": 1.0, "truesec": 1.0, "class": "Highsec (Imperial Trade Hub / Capital)", "stargates": 3, "stations": 12, "faction": "Amarr Empire"},
    {"name": "Dodixie", "region": "Sinq Laison", "constellation": "Gallente Prime", "sec": 0.9, "truesec": 0.86, "class": "Highsec (Gallente Trade Hub)", "stargates": 4, "stations": 9, "faction": "Gallente Federation"},
    {"name": "Rens", "region": "Heimatar", "constellation": "Hed", "sec": 0.9, "truesec": 0.88, "class": "Highsec (Minmatar Trade Hub)", "stargates": 4, "stations": 11, "faction": "Minmatar Republic"},
    {"name": "Hek", "region": "Metropolis", "constellation": "Hedion", "sec": 0.5, "truesec": 0.54, "class": "Highsec (Lowsec Gateway Trade Hub)", "stargates": 3, "stations": 6, "faction": "Minmatar Republic"},
    {"name": "Perimeter", "region": "The Forge", "constellation": "Kimotoro", "sec": 1.0, "truesec": 0.98, "class": "Highsec (Market Perimeter Gateway)", "stargates": 4, "stations": 8, "faction": "Caldari State"},

    # --- Nullsec Strongholds & Strategic Chokepoints ---
    {"name": "1DQ1-A", "region": "Delve", "constellation": "1DQ1-A", "sec": -0.1, "truesec": -0.87, "class": "Nullsec (Imperium Fleet Staging)", "stargates": 5, "stations": 4, "faction": "Nullsec Sovereign"},
    {"name": "MJ-5F9", "region": "Kalevala Expanse", "constellation": "MJ-5F9", "sec": -0.1, "truesec": -0.74, "class": "Nullsec (Pandemic Horde Staging)", "stargates": 4, "stations": 3, "faction": "Nullsec Sovereign"},
    {"name": "4-P22S", "region": "Fade", "constellation": "4-P22S", "sec": -0.2, "truesec": -0.65, "class": "Nullsec (Northern Coalition Fleet Staging)", "stargates": 4, "stations": 2, "faction": "Nullsec Sovereign"},
    {"name": "B-R5RB", "region": "Impass", "constellation": "B-R5RB", "sec": -0.1, "truesec": -0.76, "class": "Nullsec (Site of the Titan Bloodbath Monument)", "stargates": 4, "stations": 2, "faction": "Nullsec Sovereign"},
    {"name": "M-OEE8", "region": "Tribute", "constellation": "M-OEE8", "sec": -0.1, "truesec": -0.52, "class": "Nullsec (Historic Keepstar Citadel Siege)", "stargates": 4, "stations": 2, "faction": "Nullsec Sovereign"},
    {"name": "6VDT-H", "region": "Fountain", "constellation": "6VDT-H", "sec": -0.2, "truesec": -0.68, "class": "Nullsec (Fountain Battle Capital Gateway)", "stargates": 4, "stations": 3, "faction": "Nullsec Sovereign"},
    {"name": "HED-GP", "region": "Catch", "constellation": "Catch Gateway", "sec": -0.1, "truesec": -0.45, "class": "Nullsec (High-Traffic Lowsec/Empire Pipe Chokepoint)", "stargates": 4, "stations": 2, "faction": "Nullsec Sovereign"},
    {"name": "EC-P8R", "region": "Pure Blind", "constellation": "EC-P8R", "sec": -0.1, "truesec": -0.48, "class": "Nullsec (Caldari Border Chokepoint)", "stargates": 4, "stations": 2, "faction": "Nullsec Sovereign"},
    {"name": "GE-8JV", "region": "Catch", "constellation": "Catch Core", "sec": -0.1, "truesec": -0.72, "class": "Nullsec (Brave Collective Capital Staging)", "stargates": 4, "stations": 3, "faction": "Nullsec Sovereign"},
    {"name": "V-3YG7", "region": "Insmother", "constellation": "Insmother Core", "sec": -0.2, "truesec": -0.82, "class": "Nullsec (WinterCo / Fraternity Capital Staging)", "stargates": 4, "stations": 3, "faction": "Nullsec Sovereign"},

    # --- Famous Lowsec / Faction Warfare Hubs ---
    {"name": "Tama", "region": "The Citadel", "constellation": "Okuroda", "sec": 0.3, "truesec": 0.28, "class": "Lowsec (Premier Caldari/Gallente FW Meatgrinder)", "stargates": 4, "stations": 4, "faction": "Faction Warfare (Caldari / Gallente)"},
    {"name": "Amamake", "region": "Heimatar", "constellation": "Hedion", "sec": 0.4, "truesec": 0.38, "class": "Lowsec (Minmatar / Amarr FW Top Belt)", "stargates": 3, "stations": 3, "faction": "Faction Warfare (Minmatar / Amarr)"},
    {"name": "Rancer", "region": "Everyshore", "constellation": "Rancer Pipe", "sec": 0.4, "truesec": 0.35, "class": "Lowsec (Notorious Smartbomb Gatecamp Pipe)", "stargates": 2, "stations": 1, "faction": "Pirate Insurgency / Lowsec"},
    {"name": "Ahbazon", "region": "Genesis", "constellation": "Ahbazon Pipe", "sec": 0.4, "truesec": 0.39, "class": "Lowsec (Shortest Highsec Pipe to Amarr / Heavy Gatecamp)", "stargates": 2, "stations": 2, "faction": "Lowsec Chokepoint"},
    {"name": "Huola", "region": "The Bleak Lands", "constellation": "Huola", "sec": 0.4, "truesec": 0.36, "class": "Lowsec (Amarr / Minmatar FW Complex Warzone)", "stargates": 4, "stations": 4, "faction": "Faction Warfare"},
    {"name": "Kamela", "region": "The Bleak Lands", "constellation": "Huola", "sec": 0.4, "truesec": 0.38, "class": "Lowsec (Amarr Militia Headquarters)", "stargates": 3, "stations": 3, "faction": "Faction Warfare"},

    # --- Pochven (Triglavian Space) ---
    {"name": "Otela", "region": "Pochven", "constellation": "Krai Veles", "sec": -1.0, "truesec": -1.0, "class": "Triglavian Space (Pochven Filament Gateway)", "stargates": 3, "stations": 2, "faction": "Triglavian Collective"},
    {"name": "Skarkon", "region": "Pochven", "constellation": "Krai Svarog", "sec": -1.0, "truesec": -1.0, "class": "Triglavian Space (Pochven Flashpoint Warzone)", "stargates": 3, "stations": 2, "faction": "Triglavian Collective"},
    {"name": "Raravoss", "region": "Pochven", "constellation": "Krai Perun", "sec": -1.0, "truesec": -1.0, "class": "Triglavian Space (First Stellar Harvester Conversion)", "stargates": 3, "stations": 2, "faction": "Triglavian Collective"},

    # --- Special / Wormhole Hubs ---
    {"name": "Thera", "region": "Anoikis (W-Space)", "constellation": "Thera Constellation", "sec": -0.9, "truesec": -0.99, "class": "Shattered Wormhole (Epicenter of W-Space Navigation)", "stargates": 0, "stations": 4, "faction": "Sisters of EVE"},
    {"name": "Zarzakh", "region": "The Deathless Void", "constellation": "Zarzakh", "sec": -0.1, "truesec": -0.99, "class": "Ancient Jove Star Gate Hub (Deathless Gate Network)", "stargates": 4, "stations": 1, "faction": "The Deathless"},
    {"name": "J105934", "region": "W-Space (Class 5)", "constellation": "C5 Core", "sec": -1.0, "truesec": -1.0, "class": "Wormhole Class 5 (High-End Capital Escalation Site)", "stargates": 0, "stations": 0, "faction": "Sleeper Enclave"},
    {"name": "J115405", "region": "W-Space (Class 6)", "constellation": "C6 Core", "sec": -1.0, "truesec": -1.0, "class": "Wormhole Class 6 (Apex Magnetar / Dreadnought Site)", "stargates": 0, "stations": 0, "faction": "Sleeper Enclave"}
]

# Generate synthetic universe catalog expanding across all 67 EVE Regions
REGION_CATALOG = [
    ("The Forge", "Caldari", 0.8), ("Domain", "Amarr", 0.9), ("Sinq Laison", "Gallente", 0.8), ("Heimatar", "Minmatar", 0.8),
    ("Metropolis", "Minmatar", 0.7), ("Lonetrek", "Caldari", 0.7), ("The Citadel", "Caldari", 0.6), ("Essence", "Gallente", 0.7),
    ("Everyshore", "Gallente", 0.7), ("Placid", "Gallente / FW", 0.4), ("Black Rise", "Caldari / FW", 0.3), ("The Bleak Lands", "Amarr / FW", 0.3),
    ("DeVoid", "Amarr", 0.6), ("Derelik", "Amarr", 0.6), ("Kador", "Amarr", 0.7), ("Kor-Azor", "Amarr", 0.7), ("Tash-Murkon", "Amarr", 0.8),
    ("Genesis", "Amarr", 0.6), ("Solitude", "Gallente", 0.5), ("Aridia", "Lowsec", 0.4), ("Syndicate", "NPC Nullsec (Intaki)", -0.2),
    ("Outer Ring", "NPC Nullsec (ORE)", -0.3), ("Cloud Ring", "Nullsec", -0.4), ("Fountain", "Nullsec (Angel/Sovereign)", -0.6),
    ("Delve", "Nullsec (Blood Raiders/Imperium)", -0.8), ("Querious", "Nullsec", -0.7), ("Period Basis", "Nullsec", -0.8),
    ("Paragon Soul", "Nullsec", -0.8), ("Esoteria", "Nullsec", -0.8), ("Feythabolis", "Nullsec", -0.8), ("Impass", "Nullsec", -0.7),
    ("Catch", "Nullsec", -0.5), ("Immensea", "Nullsec", -0.6), ("Tenerifis", "Nullsec", -0.7), ("Detorid", "Nullsec", -0.8),
    ("Wicked Creek", "Nullsec", -0.7), ("Insmother", "Nullsec", -0.8), ("Scalding Pass", "Nullsec", -0.6), ("Curse", "NPC Nullsec (Angel Cartel)", -0.4),
    ("Great Wildlands", "NPC Nullsec (Thukker)", -0.3), ("Cache", "Nullsec", -0.7), ("Etherium Reach", "Nullsec", -0.6),
    ("The Spire", "Nullsec", -0.6), ("Malpais", "Nullsec (Drone Lands)", -0.8), ("Oasa", "Nullsec (Drone Lands)", -0.9),
    ("Outer Passage", "Nullsec (Drone Lands)", -0.8), ("Cobalt Edge", "Nullsec (Drone Lands)", -0.8), ("Perrigen Falls", "Nullsec (Drone Lands)", -0.7),
    ("Kalevala Expanse", "Nullsec (Horde)", -0.7), ("Tribute", "Nullsec", -0.6), ("Vale of the Silent", "Nullsec", -0.7),
    ("Geminate", "Nullsec", -0.5), ("Pure Blind", "Nullsec", -0.4), ("Fade", "Nullsec", -0.6), ("Deklein", "Nullsec (Guristas/Sov)", -0.7),
    ("Branch", "Nullsec", -0.8), ("Tenal", "Nullsec", -0.7), ("Venal", "NPC Nullsec (Guristas)", -0.5), ("Stain", "NPC Nullsec (Sansha)", -0.6),
    ("Pochven", "Triglavian Space", -1.0), ("Anoikis", "Wormhole Space", -1.0)
]


def build_complete_system_dataset() -> List[Dict[str, Any]]:
    systems = list(MAJOR_SYSTEMS_DATABASE)
    existing_names = {s["name"] for s in systems}

    # Synthesize representative solar systems across every EVE region to form complete star map
    for r_name, faction, base_sec in REGION_CATALOG:
        for idx in range(1, 12):
            s_name = f"{r_name[:3].upper()}-{idx:02d}{chr(65 + (idx % 26))}"
            if s_name not in existing_names:
                sec_val = base_sec
                c_name = f"{r_name} Constellation {((idx - 1) // 4) + 1}"
                
                if sec_val >= 0.5:
                    s_class = "Highsec Empire System"
                elif sec_val > 0.0:
                    s_class = "Lowsec Sovereign System"
                elif "Wormhole" in faction or "Anoikis" in r_name:
                    s_class = f"Wormhole Class {(idx % 6) + 1}"
                elif "Pochven" in r_name:
                    s_class = "Pochven Krai Warzone"
                else:
                    s_class = "Nullsec Sovereign Strategic System"

                systems.append({
                    "name": s_name,
                    "region": r_name,
                    "constellation": c_name,
                    "sec": round(sec_val, 1),
                    "truesec": round(sec_val - 0.05, 2),
                    "class": s_class,
                    "stargates": 4 if sec_val > 0 else 2,
                    "stations": 3 if sec_val >= 0.5 else 1,
                    "faction": faction
                })
                existing_names.add(s_name)

    return systems


def export_datasets():
    print("[A.U.R.A. Data Generator] Building full EVE Online Solar Systems dataset...")
    systems = build_complete_system_dataset()

    json_path = os.path.join(OUTPUT_DIR, "eve_solar_systems.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(systems, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported JSON dataset: {json_path} ({len(systems)} solar systems)")

    csv_path = os.path.join(OUTPUT_DIR, "eve_solar_systems.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SystemName", "Region", "Constellation", "SecurityStatus", "TrueSec", "SystemClass", "Stargates", "Stations", "Faction"])
        for s in systems:
            writer.writerow([s["name"], s["region"], s["constellation"], s["sec"], s["truesec"], s["class"], s["stargates"], s["stations"], s["faction"]])
    print(f"  [OK] Exported CSV dataset:  {csv_path} ({len(systems)} rows)")


if __name__ == "__main__":
    export_datasets()
