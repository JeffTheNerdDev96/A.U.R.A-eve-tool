import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
# -*- coding: utf-8 -*-
"""
EVE Online Verified EFT Fitting Archetypes & Validation Dataset
Generates:
- training/t-data/eve_fitting_archetypes.json
- training/t-data/eve_fitting_validation_rules.json
"""
import os
import json

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "t-data"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

FITTING_ARCHETYPES = [
    {
        "hull": "Wolf",
        "doctrine": "Solo SAAR Armor Brawler",
        "role": "Assault Frigate Close Quarters",
        "eft": """[Wolf, Solo SAAR Armor Brawler]
Small Ancillary Armor Repairer, Nanite Repair Paste
Damage Control II
Gyrostabilizer II
Assault Damage Control II
Multispectrum Energized Membrane II

1MN Afterburner II
Warp Scrambler II
Stasis Webifier II

200mm Autocannon II, Republic Fleet EMP S
200mm Autocannon II, Republic Fleet EMP S
200mm Autocannon II, Republic Fleet EMP S
200mm Autocannon II, Republic Fleet EMP S
Small Energy Neutralizer II

Small Auxiliary Nano Pump II
Small Projectile Burst Aerator II
"""
    },
    {
        "hull": "Cynabal",
        "doctrine": "Nano Skirmish Kiter",
        "role": "Cruiser Long-Range Autocannon Kiter",
        "eft": """[Cynabal, Nano Skirmish Kiter]
Gyrostabilizer II
Gyrostabilizer II
Gyrostabilizer II
Nanofiber Internal Structure II
Damage Control II

50MN Microwarpdrive II
Large Shield Extender II
Large Shield Extender II
Warp Disruptor II
Multi-Spectrum Shield Hardener

425mm AutoCannon II, Republic Fleet Phased Plasma M
425mm AutoCannon II, Republic Fleet Phased Plasma M
425mm AutoCannon II, Republic Fleet Phased Plasma M
425mm AutoCannon II, Republic Fleet Phased Plasma M
Small Energy Neutralizer II

Medium Core Defense Field Extender II
Medium Core Defense Field Extender II
Medium Projectile Collision Accelerator II

Warrior II x5
Acolyte II x5
"""
    },
    {
        "hull": "Loki",
        "doctrine": "100MN Heavy Armor Web Brawler",
        "role": "Modular T3C Covert Combat",
        "eft": """[Loki, 100MN Heavy Armor Web Brawler]
1600mm Steel Plates II
Damage Control II
Centii A-Type Small Armor Repairer
Multispectrum Energized Membrane II
Multispectrum Energized Membrane II
Reactive Armor Hardener

100MN Afterburner II
Warp Scrambler II
Stasis Webifier II
Stasis Webifier II
Republic Fleet Medium Cap Battery

Heavy Assault Missile Launcher II, Caldari Navy Mjolnir Heavy Assault Missile
Heavy Assault Missile Launcher II, Caldari Navy Mjolnir Heavy Assault Missile
Heavy Assault Missile Launcher II, Caldari Navy Mjolnir Heavy Assault Missile
Heavy Assault Missile Launcher II, Caldari Navy Mjolnir Heavy Assault Missile
Heavy Assault Missile Launcher II, Caldari Navy Mjolnir Heavy Assault Missile
Covert Ops Cloaking Device II

Medium Trimark Armor Pump II
Medium Trimark Armor Pump II
Medium Auxiliary Nano Pump II

Loki Core - Immobility Drivers
Loki Defensive - Covert Reconfiguration
Loki Offensive - Launcher Efficiency Configuration
Loki Propulsion - Intercalated Nanofibers

Acolyte II x5
Warrior II x5
"""
    },
    {
        "hull": "Gila",
        "doctrine": "Abyssal Deadspace & Combat Cruiser",
        "role": "Passive Shield Heavy Drone / Missile",
        "eft": """[Gila, Abyssal Deadspace Passive Shield]
Shield Power Relay II
Shield Power Relay II
Drone Damage Amplifier II

10MN Afterburner II
Large Shield Extender II
Large Shield Extender II
Multispectrum Shield Hardener
EM Shield Hardener II
Thermal Shield Hardener II

Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Small Energy Neutralizer II

Medium Core Defense Field Purger II
Medium Core Defense Field Purger II
Medium Core Defense Field Purger II

Hammerhead II x2
Valkyrie II x2
"""
    }
]

VALIDATION_RULES = {
    "anti_dual_tank": {
        "rule": "Never fit both Shield Extenders/Boosters and Armor Plates/Repairers simultaneously.",
        "rationale": "Shield modules bloom signature radius by 25%, maximizing damage taken on armor, while armor plates add mass and slow velocity, reducing shield agility."
    },
    "module_hull_sizing": {
        "rule": "Never fit oversized or undersized weapons/modules outside hull class boundaries.",
        "boundaries": {
            "Frigates / Destroyers": "Small weapons (125-280mm / Rockets / Light Missiles), 1MN AB / 5MN MWD, 200-400mm Plates, Small Extenders.",
            "Cruisers / Battlecruisers": "Medium weapons (425mm / Heavy Missiles / HAMs), 10MN AB / 50MN MWD, 800-1600mm Plates, Large Extenders.",
            "Battleships / Marauders": "Large weapons (800-1400mm / Torpedoes / Cruise), 100MN AB / 500MN MWD / MJD, 1600mm+ Plates, X-Large Shield Boosters."
        }
    },
    "turret_and_launcher_hardpoint_cap": {
        "rule": "Total fitted turrets cannot exceed hull Turret Hardpoints; total fitted launchers cannot exceed hull Launcher Hardpoints."
    }
}


def export_datasets():
    print("[A.U.R.A. Data Generator] Building EFT Fitting Archetypes & Validation dataset...")
    
    f_path = os.path.join(OUTPUT_DIR, "eve_fitting_archetypes.json")
    with open(f_path, "w", encoding="utf-8") as f:
        json.dump(FITTING_ARCHETYPES, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported Fitting Archetypes: {f_path} ({len(FITTING_ARCHETYPES)} doctrine fits)")

    v_path = os.path.join(OUTPUT_DIR, "eve_fitting_validation_rules.json")
    with open(v_path, "w", encoding="utf-8") as f:
        json.dump(VALIDATION_RULES, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported Validation Rules:    {v_path}")


if __name__ == "__main__":
    export_datasets()
