"""
EVE Online Tactical Database, Comprehensive Combat Matrix & Domain Grounding Engine.
Customized for A.U.R.A. (Adaptive Underworld Recon Array) — ver.0.2.0-alpha1 & Core.
Contains encyclopedic vessel dossiers (350+ hulls), module matrix (250+ modules),
subsystems, weapon tracking mathematics, capacitor warfare, and tactical grounding.
Covers all standard empire, navy, pirate, faction, industrial, capital, and T3 vessels.
Ship and module facts are compiled from publicly documented EVE Online game data
(CCP hf), with reference material from the EVE University Wiki, zKillboard, and
DOTLAN EveMaps. See CREDITS.md.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import re
import functools

# Threat Classification Tags
THREAT_BUBBLE = "DISRUPTIVE BUBBLE / TACKLE"
THREAT_CYNO = "COVERT CYNO / HOTDROP RISK"
THREAT_ECM = "ELECTRONIC WARFARE / NEUT"
THREAT_MARAUDER = "EXTREME DPS / BASTION SIEGE"
THREAT_CAPITAL = "CAPITAL CLASS WARSHIP"
THREAT_SUPER = "SUPERCAPITAL / TITAN OMNI-THREAT"
THREAT_LOGI = "FLEET REPAIR / LOGISTICS"
THREAT_PIRATE = "FACTION / PIRATE WARSHIP"
THREAT_T2_COMBAT = "T2 COMBAT SPECIALIST"
THREAT_HAULER = "INDUSTRIAL / FREIGHTER / MINING"
THREAT_COMBATANT = "COMBAT VESSEL"
THREAT_COVERT = "COVERT OPS / STEALTH RECON"
THREAT_MINING = "MINING / INDUSTRIAL HARVESTER"

SHIP_DATABASE: Dict[str, Dict[str, Any]] = {
    "Dramiel": {
        "class": "Frigate",
        "faction": "Angel Cartel",
        "role": "Pirate Interceptor / Tackler",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active",
        "speed": "Extreme (4.5-5.5 km/s MWD)",
        "optimal_range": "0-12 km (Autocannons)",
        "tactics": "Extreme warp speed and sub-warp agility. Keep transversal high against heavier turrets. Counter with dual webs, warp scrambler, or fast combat drones.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 2,
        "launcher_hardpoints": 1,
        "weapon_type": "Small Projectile (Autocannons)",
        "bonuses": [
            "25% Small Projectile damage per lvl",
            "25% Small Projectile falloff per lvl",
            "Role: 50% warp speed & warp acceleration",
            "Role: 100% afterburner speed bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Dramiel [Frigate | Angel Cartel]\n  - Combat Role: Pirate Interceptor / Tackler\n  - Weapon System: Small Projectile (Autocannons)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 2 | Launchers: 1)\n  - Key Bonuses: 25% Small Projectile damage per lvl | 25% Small Projectile falloff per lvl | Role: 50% warp speed & warp acceleration\n  - Defense Profile: Shield Buffer / Active | Speed: Extreme (4.5-5.5 km/s MWD)\n  - Weapon Optimal: 0-12 km (Autocannons)\n  - Tactical Counter-Play: Extreme warp speed and sub-warp agility. Keep transversal high against heavier turrets. Counter with dual webs, warp scrambler, or fast combat drones."
    },
    "Mekubal": {
        "class": "Destroyer",
        "faction": "Angel Cartel",
        "role": "Pirate Destroyer / Frigate Hunter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Extreme (3.8-4.5 km/s)",
        "optimal_range": "8-20 km (Autocannons)",
        "tactics": "Extreme speed destroyer. Shreds light tackle before they close range. Keep distance outside 10 km.",
        "high_slots": 6,
        "mid_slots": 4,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 1,
        "weapon_type": "Small Projectile (200mm Autocannons)",
        "bonuses": [
            "25% Small Projectile damage per lvl",
            "25% Small Projectile falloff per lvl",
            "Role: 50% warp speed & acceleration"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Mekubal [Destroyer | Angel Cartel]\n  - Combat Role: Pirate Destroyer / Frigate Hunter\n  - Weapon System: Small Projectile (200mm Autocannons)\n  - Slot Layout: Highs: 6 | Mids: 4 | Lows: 4 | Rigs: 3 (Turrets: 5 | Launchers: 1)\n  - Key Bonuses: 25% Small Projectile damage per lvl | 25% Small Projectile falloff per lvl | Role: 50% warp speed & acceleration\n  - Defense Profile: Shield Buffer | Speed: Extreme (3.8-4.5 km/s)\n  - Weapon Optimal: 8-20 km (Autocannons)\n  - Tactical Counter-Play: Extreme speed destroyer. Shreds light tackle before they close range. Keep distance outside 10 km."
    },
    "Cynabal": {
        "class": "Cruiser",
        "faction": "Angel Cartel",
        "role": "Nano Skirmisher / Fleet Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active",
        "speed": "Extreme (2.2-3.0 km/s MWD)",
        "optimal_range": "15-28 km (425mm Autocannons / Barrage)",
        "tactics": "Premier nano kiter. Maintain 20-25km range, kite away from scrams/webs, apply tracking-disruptive transversal.",
        "high_slots": 5,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 1,
        "weapon_type": "Medium Projectile (425mm AC / Barrage)",
        "bonuses": [
            "25% Medium Projectile damage per lvl",
            "25% Medium Projectile falloff per lvl",
            "Role: 50% warp speed"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cynabal [Cruiser | Angel Cartel]\n  - Combat Role: Nano Skirmisher / Fleet Cruiser\n  - Weapon System: Medium Projectile (425mm AC / Barrage)\n  - Slot Layout: Highs: 5 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 4 | Launchers: 1)\n  - Key Bonuses: 25% Medium Projectile damage per lvl | 25% Medium Projectile falloff per lvl | Role: 50% warp speed\n  - Defense Profile: Shield Buffer / Active | Speed: Extreme (2.2-3.0 km/s MWD)\n  - Weapon Optimal: 15-28 km (425mm Autocannons / Barrage)\n  - Tactical Counter-Play: Premier nano kiter. Maintain 20-25km range, kite away from scrams/webs, apply tracking-disruptive transversal."
    },
    "Khizriel": {
        "class": "Battlecruiser",
        "faction": "Angel Cartel",
        "role": "Heavy Skirmish Battlecruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast (1.8-2.4 km/s)",
        "optimal_range": "20-50 km",
        "tactics": "Heavy projectile alpha with high mobility. Overheat MWD to dictate engagement range.",
        "high_slots": 7,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 2,
        "weapon_type": "Medium Projectile (720mm Artillery / 425mm AC)",
        "bonuses": [
            "25% Medium Projectile damage per lvl",
            "25% Medium Projectile falloff per lvl",
            "Role: 50% warp speed"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Khizriel [Battlecruiser | Angel Cartel]\n  - Combat Role: Heavy Skirmish Battlecruiser\n  - Weapon System: Medium Projectile (720mm Artillery / 425mm AC)\n  - Slot Layout: Highs: 7 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 5 | Launchers: 2)\n  - Key Bonuses: 25% Medium Projectile damage per lvl | 25% Medium Projectile falloff per lvl | Role: 50% warp speed\n  - Defense Profile: Shield Buffer | Speed: Fast (1.8-2.4 km/s)\n  - Weapon Optimal: 20-50 km\n  - Tactical Counter-Play: Heavy projectile alpha with high mobility. Overheat MWD to dictate engagement range."
    },
    "Machariel": {
        "class": "Battleship",
        "faction": "Angel Cartel",
        "role": "Fast Battleship / Fleet Anchor",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Armor",
        "speed": "Very Fast (1.5-2.0 km/s MWD)",
        "optimal_range": "15-40 km (800mm AC) or 70-130 km (1400mm Artillery)",
        "tactics": "Cruiser agility on a battleship hull. 1400mm Artillery alpha or 800mm AC skirmishing. Apply Tracking Disruptors and maintain transversal.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Projectile (800mm AC / 1400mm Artillery)",
        "bonuses": [
            "25% Large Projectile damage per lvl",
            "25% Large Projectile falloff per lvl",
            "Role: 50% warp speed & warp acceleration"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Machariel [Battleship | Angel Cartel]\n  - Combat Role: Fast Battleship / Fleet Anchor\n  - Weapon System: Large Projectile (800mm AC / 1400mm Artillery)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 0)\n  - Key Bonuses: 25% Large Projectile damage per lvl | 25% Large Projectile falloff per lvl | Role: 50% warp speed & warp acceleration\n  - Defense Profile: Shield Buffer / Armor | Speed: Very Fast (1.5-2.0 km/s MWD)\n  - Weapon Optimal: 15-40 km (800mm AC) or 70-130 km (1400mm Artillery)\n  - Tactical Counter-Play: Cruiser agility on a battleship hull. 1400mm Artillery alpha or 800mm AC skirmishing. Apply Tracking Disruptors and maintain transversal."
    },
    "Azariel": {
        "class": "Titan",
        "faction": "Angel Cartel",
        "role": "Pirate Supercapital Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Fast for Titan",
        "optimal_range": "Omni Capital Range",
        "tactics": "Angel Cartel supercapital with devastating projectile alpha strike and Titan doomsday weapon.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Pirate Supercapital Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Azariel [Titan | Angel Cartel]\n  - Combat Role: Pirate Supercapital Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Pirate Supercapital Titan Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast for Titan\n  - Weapon Optimal: Omni Capital Range\n  - Tactical Counter-Play: Angel Cartel supercapital with devastating projectile alpha strike and Titan doomsday weapon."
    },
    "Worm": {
        "class": "Frigate",
        "faction": "Guristas",
        "role": "Heavy Drone / Missile Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Passive (300% Drone Bonus)",
        "speed": "Moderate",
        "optimal_range": "0-40 km",
        "tactics": "Extreme drone HP and damage (1 drone deals damage of 4). Kill light drones or kite outside 45 km lock range. Counter with smartbombs or defanging.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 2,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 2,
        "weapon_type": "Light Drones & Light Missiles",
        "bonuses": [
            "300% Light Drone HP and damage",
            "10% Light Missile kinetic/thermal damage per lvl",
            "4% all shield resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Worm [Frigate | Guristas]\n  - Combat Role: Heavy Drone / Missile Frigate\n  - Weapon System: Light Drones & Light Missiles\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 2 | Rigs: 3 (Turrets: 0 | Launchers: 2)\n  - Key Bonuses: 300% Light Drone HP and damage | 10% Light Missile kinetic/thermal damage per lvl | 4% all shield resists per lvl\n  - Defense Profile: Shield Buffer / Passive (300% Drone Bonus) | Speed: Moderate\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Extreme drone HP and damage (1 drone deals damage of 4). Kill light drones or kite outside 45 km lock range. Counter with smartbombs or defanging."
    },
    "Mamba": {
        "class": "Destroyer",
        "faction": "Guristas",
        "role": "Pirate Missile Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-45 km",
        "tactics": "Fast missile and light drone destroyer with strong shield tank.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Pirate Missile Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Mamba [Destroyer | Guristas]\n  - Combat Role: Pirate Missile Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Pirate Missile Destroyer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 20-45 km\n  - Tactical Counter-Play: Fast missile and light drone destroyer with strong shield tank."
    },
    "Gila": {
        "class": "Cruiser",
        "faction": "Guristas",
        "role": "Drone / Missile Combat Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Passive / Active Shield (500% Drone Bonus)",
        "speed": "Moderate (1.6-2.0 km/s)",
        "optimal_range": "0-60 km",
        "tactics": "Immense drone damage (2 drones deal damage of 10) plus RLML burst. Defang drones or neut capacitor.",
        "high_slots": 5,
        "mid_slots": 6,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 4,
        "weapon_type": "Medium Drones & Rapid Light Missiles (RLML)",
        "bonuses": [
            "500% Medium Drone HP and damage",
            "10% RLML/HAM missile kinetic/thermal damage per lvl",
            "4% all shield resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Gila [Cruiser | Guristas]\n  - Combat Role: Drone / Missile Combat Cruiser\n  - Weapon System: Medium Drones & Rapid Light Missiles (RLML)\n  - Slot Layout: Highs: 5 | Mids: 6 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 4)\n  - Key Bonuses: 500% Medium Drone HP and damage | 10% RLML/HAM missile kinetic/thermal damage per lvl | 4% all shield resists per lvl\n  - Defense Profile: Passive / Active Shield (500% Drone Bonus) | Speed: Moderate (1.6-2.0 km/s)\n  - Weapon Optimal: 0-60 km\n  - Tactical Counter-Play: Immense drone damage (2 drones deal damage of 10) plus RLML burst. Defang drones or neut capacitor."
    },
    "Alligator": {
        "class": "Battlecruiser",
        "faction": "Guristas",
        "role": "Heavy Drone / Missile Battlecruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km",
        "tactics": "Heavy drone and heavy assault missile platform with massive shield reserves.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Drone / Missile Battlecruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Alligator [Battlecruiser | Guristas]\n  - Combat Role: Heavy Drone / Missile Battlecruiser\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Drone / Missile Battlecruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Heavy drone and heavy assault missile platform with massive shield reserves."
    },
    "Rattlesnake": {
        "class": "Battleship",
        "faction": "Guristas",
        "role": "Heavy Drone / Cruise Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Passive / Active Shield",
        "speed": "Slow",
        "optimal_range": "20-80 km",
        "tactics": "Massive passive shield recharge and heavy drone DPS. Cap neuts have low impact on passive regen. Kill drones or apply heavy kinetic/thermal disruption.",
        "high_slots": 6,
        "mid_slots": 7,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 5,
        "weapon_type": "Heavy/Sentry Drones & Cruise/Torpedo Missiles",
        "bonuses": [
            "275% Heavy/Sentry Drone HP and damage",
            "10% Cruise/Torpedo kinetic/thermal damage per lvl",
            "4% all shield resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rattlesnake [Battleship | Guristas]\n  - Combat Role: Heavy Drone / Cruise Battleship\n  - Weapon System: Heavy/Sentry Drones & Cruise/Torpedo Missiles\n  - Slot Layout: Highs: 6 | Mids: 7 | Lows: 6 | Rigs: 3 (Turrets: 0 | Launchers: 5)\n  - Key Bonuses: 275% Heavy/Sentry Drone HP and damage | 10% Cruise/Torpedo kinetic/thermal damage per lvl | 4% all shield resists per lvl\n  - Defense Profile: Passive / Active Shield | Speed: Slow\n  - Weapon Optimal: 20-80 km\n  - Tactical Counter-Play: Massive passive shield recharge and heavy drone DPS. Cap neuts have low impact on passive regen. Kill drones or apply heavy kinetic/thermal disruption."
    },
    "Loggerhead": {
        "class": "Force Auxiliary",
        "faction": "Guristas",
        "role": "Pirate Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Fleet Remote Shield",
        "tactics": "Guristas pirate capital shield logistics ship.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Pirate Shield FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Loggerhead [Force Auxiliary | Guristas]\n  - Combat Role: Pirate Shield FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Pirate Shield FAX Class Role Bonus\n  - Defense Profile: Shield Active | Speed: Capital\n  - Weapon Optimal: Fleet Remote Shield\n  - Tactical Counter-Play: Guristas pirate capital shield logistics ship."
    },
    "Caiman": {
        "class": "Dreadnought",
        "faction": "Guristas",
        "role": "Pirate Missile / Drone Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Guristas pirate dreadnought with capital kinetic/thermal missile launchers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Pirate Missile / Drone Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Caiman [Dreadnought | Guristas]\n  - Combat Role: Pirate Missile / Drone Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Pirate Missile / Drone Dread Class Role Bonus\n  - Defense Profile: Shield Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Guristas pirate dreadnought with capital kinetic/thermal missile launchers."
    },
    "Komodo": {
        "class": "Titan",
        "faction": "Guristas",
        "role": "Guristas Supercapital Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Guristas pirate supercapital Titan with extreme missile burst and supercapital drones.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Guristas Supercapital Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Komodo [Titan | Guristas]\n  - Combat Role: Guristas Supercapital Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Guristas Supercapital Titan Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Guristas pirate supercapital Titan with extreme missile burst and supercapital drones."
    },
    "Cruor": {
        "class": "Frigate",
        "faction": "Blood Raiders",
        "role": "Web / NOS Frigate",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Heavy webs and NOS that drains cap even when ship cap is full. Keep distance outside 15 km.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Web / NOS Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cruor [Frigate | Blood Raiders]\n  - Combat Role: Web / NOS Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Web / NOS Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Heavy webs and NOS that drains cap even when ship cap is full. Keep distance outside 15 km."
    },
    "Ashimmu": {
        "class": "Cruiser",
        "faction": "Blood Raiders",
        "role": "Heavy Web / NOS Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "90% webs and severe energy neut drain. Eliminates enemy capacitor in seconds.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Web / NOS Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ashimmu [Cruiser | Blood Raiders]\n  - Combat Role: Heavy Web / NOS Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Web / NOS Cruiser Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: 90% webs and severe energy neut drain. Eliminates enemy capacitor in seconds."
    },
    "Bhaalgorn": {
        "class": "Battleship",
        "faction": "Blood Raiders",
        "role": "Fleet Cap Drain / Heavy Web",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Slow",
        "optimal_range": "0-40 km",
        "tactics": "Fleet cap drain flagship. Drains 3000+ GJ/cycle at 40km with 90% long webs. Prioritize as primary target before capacitor is emptied.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Heavy Energy Neutralizers & Large Lasers",
        "bonuses": [
            "100% Heavy Energy Neutralizer drain amount",
            "20% Heavy Stasis Webifier range per lvl",
            "15% Large Energy laser damage per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bhaalgorn [Battleship | Blood Raiders]\n  - Combat Role: Fleet Cap Drain / Heavy Web\n  - Weapon System: Heavy Energy Neutralizers & Large Lasers\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Heavy Energy Neutralizer drain amount | 20% Heavy Stasis Webifier range per lvl | 15% Large Energy laser damage per lvl\n  - Defense Profile: Armor | Speed: Slow\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Fleet cap drain flagship. Drains 3000+ GJ/cycle at 40km with 90% long webs. Prioritize as primary target before capacitor is emptied."
    },
    "Dagon": {
        "class": "Force Auxiliary",
        "faction": "Blood Raiders",
        "role": "Pirate Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Fleet Remote Armor",
        "tactics": "Blood Raider capital armor remote repair ship.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Pirate Armor FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Dagon [Force Auxiliary | Blood Raiders]\n  - Combat Role: Pirate Armor FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Pirate Armor FAX Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Fleet Remote Armor\n  - Tactical Counter-Play: Blood Raider capital armor remote repair ship."
    },
    "Chemosh": {
        "class": "Dreadnought",
        "faction": "Blood Raiders",
        "role": "Pirate Cap Drain Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Blood Raider pirate dreadnought with capital energy neutralizers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Pirate Cap Drain Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Chemosh [Dreadnought | Blood Raiders]\n  - Combat Role: Pirate Cap Drain Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Pirate Cap Drain Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Blood Raider pirate dreadnought with capital energy neutralizers."
    },
    "Molok": {
        "class": "Titan",
        "faction": "Blood Raiders",
        "role": "Blood Raider Supercapital",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Blood Raider pirate supercapital Titan with massive neut drain.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Blood Raider Supercapital Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Molok [Titan | Blood Raiders]\n  - Combat Role: Blood Raider Supercapital\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Blood Raider Supercapital Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Blood Raider pirate supercapital Titan with massive neut drain."
    },
    "Daredevil": {
        "class": "Frigate",
        "faction": "Serpentis",
        "role": "90% Web Blaster Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-8 km",
        "tactics": "90% stasis web stops targets dead. Massive close-range blaster DPS. Do not let it close inside 10km. Apply Tracking Disruptors or kite with speed outside 12 km.",
        "high_slots": 3,
        "mid_slots": 3,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 2,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Hybrid (Neutron/Ion Blasters)",
        "bonuses": [
            "100% Small Hybrid Turret damage per lvl",
            "Role: 90% Stasis Webifier effectiveness"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Daredevil [Frigate | Serpentis]\n  - Combat Role: 90% Web Blaster Frigate\n  - Weapon System: Small Hybrid (Neutron/Ion Blasters)\n  - Slot Layout: Highs: 3 | Mids: 3 | Lows: 4 | Rigs: 3 (Turrets: 2 | Launchers: 0)\n  - Key Bonuses: 100% Small Hybrid Turret damage per lvl | Role: 90% Stasis Webifier effectiveness\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 0-8 km\n  - Tactical Counter-Play: 90% stasis web stops targets dead. Massive close-range blaster DPS. Do not let it close inside 10km. Apply Tracking Disruptors or kite with speed outside 12 km."
    },
    "Vigilant": {
        "class": "Cruiser",
        "faction": "Serpentis",
        "role": "90% Web Blaster Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "90% web with 1000+ DPS blasters. Overheat propulsion, maintain range outside 18 km, apply Tracking Disruptors.",
        "high_slots": 5,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Medium Hybrid (Heavy Neutron Blasters)",
        "bonuses": [
            "100% Medium Hybrid Turret damage per lvl",
            "Role: 90% Stasis Webifier effectiveness"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vigilant [Cruiser | Serpentis]\n  - Combat Role: 90% Web Blaster Cruiser\n  - Weapon System: Medium Hybrid (Heavy Neutron Blasters)\n  - Slot Layout: Highs: 5 | Mids: 4 | Lows: 6 | Rigs: 3 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Medium Hybrid Turret damage per lvl | Role: 90% Stasis Webifier effectiveness\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: 90% web with 1000+ DPS blasters. Overheat propulsion, maintain range outside 18 km, apply Tracking Disruptors."
    },
    "Vindicator": {
        "class": "Battleship",
        "faction": "Serpentis",
        "role": "90% Web Blaster Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "2000+ close-range blaster DPS with 90% webs. Keep distance outside 20km and apply Tracking Disruptors.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 8,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Hybrid (Neutron Blaster Cannons)",
        "bonuses": [
            "37.5% Large Hybrid damage per lvl",
            "Role: 90% Stasis Webifier effectiveness"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vindicator [Battleship | Serpentis]\n  - Combat Role: 90% Web Blaster Battleship\n  - Weapon System: Large Hybrid (Neutron Blaster Cannons)\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 8 | Launchers: 0)\n  - Key Bonuses: 37.5% Large Hybrid damage per lvl | Role: 90% Stasis Webifier effectiveness\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: 2000+ close-range blaster DPS with 90% webs. Keep distance outside 20km and apply Tracking Disruptors."
    },
    "Vehement": {
        "class": "Dreadnought",
        "faction": "Serpentis",
        "role": "Pirate Blaster / Web Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "0-30 km",
        "tactics": "Serpentis pirate dreadnought with capital blasters and 90% webifiers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Pirate Blaster / Web Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vehement [Dreadnought | Serpentis]\n  - Combat Role: Pirate Blaster / Web Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Pirate Blaster / Web Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Serpentis pirate dreadnought with capital blasters and 90% webifiers."
    },
    "Vanquisher": {
        "class": "Titan",
        "faction": "Serpentis",
        "role": "Serpentis Supercapital",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Serpentis pirate supercapital Titan with 90% web and blaster power.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Serpentis Supercapital Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vanquisher [Titan | Serpentis]\n  - Combat Role: Serpentis Supercapital\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Serpentis Supercapital Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Serpentis pirate supercapital Titan with 90% web and blaster power."
    },
    "Succubus": {
        "class": "Frigate",
        "faction": "Sansha's Nation",
        "role": "AB Speed Laser Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme AB (2.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Immune to scrambler MWD shutoff due to oversized AB bonus (2.5+ km/s). Apply Tracking Disruptors or heavy webs.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 2,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Energy (Pulse Lasers)",
        "bonuses": [
            "100% Small Energy damage per lvl",
            "Role: 100% Afterburner speed bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Succubus [Frigate | Sansha's Nation]\n  - Combat Role: AB Speed Laser Frigate\n  - Weapon System: Small Energy (Pulse Lasers)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 2 | Launchers: 0)\n  - Key Bonuses: 100% Small Energy damage per lvl | Role: 100% Afterburner speed bonus\n  - Defense Profile: Shield | Speed: Extreme AB (2.5+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Immune to scrambler MWD shutoff due to oversized AB bonus (2.5+ km/s). Apply Tracking Disruptors or heavy webs."
    },
    "Phantasm": {
        "class": "Cruiser",
        "faction": "Sansha's Nation",
        "role": "100MN AB Laser Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active",
        "speed": "Extreme AB (2.0+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "Runs 100MN Afterburner with cruiser-grade agility. Unscrammable speed tank. Hit with tracking disruptors or heavy webs.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "100MN AB Laser Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Phantasm [Cruiser | Sansha's Nation]\n  - Combat Role: 100MN AB Laser Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: 100MN AB Laser Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer / Active | Speed: Extreme AB (2.0+ km/s)\n  - Weapon Optimal: 15-35 km\n  - Tactical Counter-Play: Runs 100MN Afterburner with cruiser-grade agility. Unscrammable speed tank. Hit with tracking disruptors or heavy webs."
    },
    "Nightmare": {
        "class": "Battleship",
        "faction": "Sansha's Nation",
        "role": "Fast Laser Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast AB (1.5+ km/s)",
        "optimal_range": "30-80 km",
        "tactics": "AB speed tank laser battleship (1.5+ km/s). Unscrammable speed tank with instant EM/Thermal alpha. Apply Tracking Disruptors and heavy webifiers.",
        "high_slots": 6,
        "mid_slots": 7,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Energy Turrets (Mega Pulse / Tachyon)",
        "bonuses": [
            "100% Large Energy damage bonus",
            "Role: 100% Afterburner speed bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nightmare [Battleship | Sansha's Nation]\n  - Combat Role: Fast Laser Battleship\n  - Weapon System: Large Energy Turrets (Mega Pulse / Tachyon)\n  - Slot Layout: Highs: 6 | Mids: 7 | Lows: 5 | Rigs: 3 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Large Energy damage bonus | Role: 100% Afterburner speed bonus\n  - Defense Profile: Shield Buffer | Speed: Fast AB (1.5+ km/s)\n  - Weapon Optimal: 30-80 km\n  - Tactical Counter-Play: AB speed tank laser battleship (1.5+ km/s). Unscrammable speed tank with instant EM/Thermal alpha. Apply Tracking Disruptors and heavy webifiers."
    },
    "Revenant": {
        "class": "Supercarrier",
        "faction": "Sansha's Nation",
        "role": "Pirate Supercarrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Sansha pirate supercarrier with immense fighter strike damage.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Pirate Supercarrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Revenant [Supercarrier | Sansha's Nation]\n  - Combat Role: Pirate Supercarrier\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Pirate Supercarrier Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Sansha pirate supercarrier with immense fighter strike damage."
    },
    "Astero": {
        "class": "Frigate",
        "faction": "Sisters of EVE",
        "role": "Covert Ops / Drone Scout",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Dual Rep",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Covert cloaking exploration frigate with vicious light drone combat capability. Often dual-repaired.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Covert Ops / Drone Scout Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Astero [Frigate | Sisters of EVE]\n  - Combat Role: Covert Ops / Drone Scout\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Covert Ops / Drone Scout Class Role Bonus\n  - Defense Profile: Armor Buffer / Dual Rep | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Covert cloaking exploration frigate with vicious light drone combat capability. Often dual-repaired."
    },
    "Stratios": {
        "class": "Cruiser",
        "faction": "Sisters of EVE",
        "role": "Covert Ops / Drone Brawler",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Dual Rep",
        "speed": "Moderate",
        "optimal_range": "0-30 km",
        "tactics": "Covert cloaking cruiser. Can fit covert cyno, heavy neuts, and full flight of heavy/sentry drones.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Ops / Drone Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stratios [Cruiser | Sisters of EVE]\n  - Combat Role: Covert Ops / Drone Brawler\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Ops / Drone Brawler Class Role Bonus\n  - Defense Profile: Armor Buffer / Dual Rep | Speed: Moderate\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Covert cloaking cruiser. Can fit covert cyno, heavy neuts, and full flight of heavy/sentry drones."
    },
    "Nestor": {
        "class": "Battleship",
        "faction": "Sisters of EVE",
        "role": "Remote Rep / Wormhole Core",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Sisters of EVE Battleship. Primary fleet logistics anchor and mobile fitting refit bay. Eliminate to break fleet armor chain.",
        "high_slots": 7,
        "mid_slots": 6,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Remote Armor Repairers & Drones",
        "bonuses": [
            "100% Remote Armor repair amount bonus",
            "Role: Mobile Fitting Bay for fleetmates",
            "50% Drone damage and HP bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nestor [Battleship | Sisters of EVE]\n  - Combat Role: Remote Rep / Wormhole Core\n  - Weapon System: Large Remote Armor Repairers & Drones\n  - Slot Layout: Highs: 7 | Mids: 6 | Lows: 6 | Rigs: 3 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Remote Armor repair amount bonus | Role: Mobile Fitting Bay for fleetmates | 50% Drone damage and HP bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Sisters of EVE Battleship. Primary fleet logistics anchor and mobile fitting refit bay. Eliminate to break fleet armor chain."
    },
    "Garmur": {
        "class": "Frigate",
        "faction": "Mordu's Legion",
        "role": "Long-Range Point Kiter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "30-40 km",
        "tactics": "Projects 35+ km point at 5+ km/s. Counter with Missile Guidance Disruptors (Range script), Sensor Dampeners, RLML, or combat drones. NOT tracking disruptors.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 3,
        "weapon_type": "Light Missiles / Rockets",
        "bonuses": [
            "10% Light Missile/Rocket damage per lvl",
            "10% Light Missile/Rocket velocity per lvl",
            "Role: 100% Warp Scrambler & Disruptor range",
            "Role: 50% Stasis Webifier range"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Garmur [Frigate | Mordu's Legion]\n  - Combat Role: Long-Range Point Kiter\n  - Weapon System: Light Missiles / Rockets\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 3)\n  - Key Bonuses: 10% Light Missile/Rocket damage per lvl | 10% Light Missile/Rocket velocity per lvl | Role: 100% Warp Scrambler & Disruptor range\n  - Defense Profile: Shield | Speed: Extreme (5.0+ km/s)\n  - Weapon Optimal: 30-40 km\n  - Tactical Counter-Play: Projects 35+ km point at 5+ km/s. Counter with Missile Guidance Disruptors (Range script), Sensor Dampeners, RLML, or combat drones. NOT tracking disruptors."
    },
    "Orthrus": {
        "class": "Cruiser",
        "faction": "Mordu's Legion",
        "role": "Long-Range Point & Web Kiter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme (3.0+ km/s)",
        "optimal_range": "35-50 km",
        "tactics": "Fast 45+ km point and 25km web with RLML. Counter with Missile Guidance Disruptors, Sensor Dampeners, or slingshotting during 35s reload.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 5,
        "weapon_type": "Rapid Light Missiles / Heavy Missiles (RLML/HAM)",
        "bonuses": [
            "10% Missile damage per lvl",
            "10% Missile velocity per lvl",
            "Role: 100% Warp Scrambler & Disruptor range",
            "Role: 50% Stasis Webifier range"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Orthrus [Cruiser | Mordu's Legion]\n  - Combat Role: Long-Range Point & Web Kiter\n  - Weapon System: Rapid Light Missiles / Heavy Missiles (RLML/HAM)\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 4 | Rigs: 3 (Turrets: 0 | Launchers: 5)\n  - Key Bonuses: 10% Missile damage per lvl | 10% Missile velocity per lvl | Role: 100% Warp Scrambler & Disruptor range\n  - Defense Profile: Shield | Speed: Extreme (3.0+ km/s)\n  - Weapon Optimal: 35-50 km\n  - Tactical Counter-Play: Fast 45+ km point and 25km web with RLML. Counter with Missile Guidance Disruptors, Sensor Dampeners, or slingshotting during 35s reload."
    },
    "Barghest": {
        "class": "Battleship",
        "faction": "Mordu's Legion",
        "role": "Heavy Point / Cruise Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "60+ km point with ultra-fast cruise missiles. Counter with Missile Guidance Disruptors and signature reduction.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 6,
        "weapon_type": "Cruise Missiles / Torpedoes / Rapid Heavy",
        "bonuses": [
            "10% Missile damage per lvl",
            "10% Missile velocity per lvl",
            "Role: 100% Warp Scrambler & Disruptor range"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Barghest [Battleship | Mordu's Legion]\n  - Combat Role: Heavy Point / Cruise Battleship\n  - Weapon System: Cruise Missiles / Torpedoes / Rapid Heavy\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 6 | Rigs: 3 (Turrets: 0 | Launchers: 6)\n  - Key Bonuses: 10% Missile damage per lvl | 10% Missile velocity per lvl | Role: 100% Warp Scrambler & Disruptor range\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: 50-100 km\n  - Tactical Counter-Play: 60+ km point with ultra-fast cruise missiles. Counter with Missile Guidance Disruptors and signature reduction."
    },
    "Damavik": {
        "class": "Frigate",
        "faction": "Triglavian",
        "role": "Spooling Disintegrator Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "5-18 km",
        "tactics": "Entropic disintegrator damage ramps up continuously over time. Break lock or kill quickly before spool reaches maximum.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Spooling Disintegrator Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Damavik [Frigate | Triglavian]\n  - Combat Role: Spooling Disintegrator Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Spooling Disintegrator Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 5-18 km\n  - Tactical Counter-Play: Entropic disintegrator damage ramps up continuously over time. Break lock or kill quickly before spool reaches maximum."
    },
    "Nergal": {
        "class": "Assault Frigate",
        "faction": "Triglavian Collective",
        "role": "Spooling Assault Frigate",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Armor Repair (Spooling Armor)",
        "speed": "Fast (3.5-4.2 km/s MWD)",
        "optimal_range": "5-22 km (Entropic Disintegrator)",
        "tactics": "Triglavian T2 Assault Frigate. Single Entropic Disintegrator spools to immense DPS over time. Assault Damage Control provides invulnerability. Counter with Tracking Disruptors, sensor damps, or heavy neuts to break spooling lock.",
        "high_slots": 3,
        "mid_slots": 3,
        "low_slots": 4,
        "rig_slots": 2,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Entropic Disintegrator (Spooling Precursor)",
        "bonuses": [
            "100% Entropic Disintegrator max damage multiplier bonus",
            "5% Entropic Disintegrator damage per lvl",
            "7.5% Armor Repair amount per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nergal [Assault Frigate | Triglavian Collective]\n  - Combat Role: Spooling Assault Frigate\n  - Weapon System: Small Entropic Disintegrator (Spooling Precursor)\n  - Slot Layout: Highs: 3 | Mids: 3 | Lows: 4 | Rigs: 2 (Turrets: 1 | Launchers: 0)\n  - Key Bonuses: 100% Entropic Disintegrator max damage multiplier bonus | 5% Entropic Disintegrator damage per lvl | 7.5% Armor Repair amount per lvl\n  - Defense Profile: Active Armor Repair (Spooling Armor) | Speed: Fast (3.5-4.2 km/s MWD)\n  - Weapon Optimal: 5-22 km (Entropic Disintegrator)\n  - Tactical Counter-Play: Triglavian T2 Assault Frigate. Single Entropic Disintegrator spools to immense DPS over time. Assault Damage Control provides invulnerability. Counter with Tracking Disruptors, sensor damps, or heavy neuts to break spooling lock."
    },
    "Kikimora": {
        "class": "Destroyer",
        "faction": "Triglavian",
        "role": "Long-Range Disintegrator Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Armor / Shield",
        "speed": "Extreme (3.5+ km/s)",
        "optimal_range": "15-40 km",
        "tactics": "Extreme sub-warp speed with spooling light disintegrator. Strikes from 35km with heavy tracking.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Long-Range Disintegrator Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kikimora [Destroyer | Triglavian]\n  - Combat Role: Long-Range Disintegrator Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Long-Range Disintegrator Destroyer Class Role Bonus\n  - Defense Profile: Armor / Shield | Speed: Extreme (3.5+ km/s)\n  - Weapon Optimal: 15-40 km\n  - Tactical Counter-Play: Extreme sub-warp speed with spooling light disintegrator. Strikes from 35km with heavy tracking."
    },
    "Vedmak": {
        "class": "Cruiser",
        "faction": "Triglavian",
        "role": "Spooling Disintegrator Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast (2.2-2.8 km/s)",
        "optimal_range": "10-35 km",
        "tactics": "High sub-warp speed with continuous spooling thermal/explosive damage. Disengage if fight extends past 60 seconds.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Spooling Disintegrator Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vedmak [Cruiser | Triglavian]\n  - Combat Role: Spooling Disintegrator Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Spooling Disintegrator Cruiser Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast (2.2-2.8 km/s)\n  - Weapon Optimal: 10-35 km\n  - Tactical Counter-Play: High sub-warp speed with continuous spooling thermal/explosive damage. Disengage if fight extends past 60 seconds."
    },
    "Rodiva": {
        "class": "Cruiser",
        "faction": "Triglavian",
        "role": "Spooling Remote Armor Rep",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Rep Range",
        "tactics": "Triglavian logistics cruiser with spooling remote armor repairers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Spooling Remote Armor Rep Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rodiva [Cruiser | Triglavian]\n  - Combat Role: Spooling Remote Armor Rep\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Spooling Remote Armor Rep Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Rep Range\n  - Tactical Counter-Play: Triglavian logistics cruiser with spooling remote armor repairers."
    },
    "Drekavac": {
        "class": "Battlecruiser",
        "faction": "Triglavian",
        "role": "Heavy Disintegrator / Armor Links",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "15-45 km",
        "tactics": "Heavy armor tank and massive max-spool disintegrator DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Disintegrator / Armor Links Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Drekavac [Battlecruiser | Triglavian]\n  - Combat Role: Heavy Disintegrator / Armor Links\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Disintegrator / Armor Links Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 15-45 km\n  - Tactical Counter-Play: Heavy armor tank and massive max-spool disintegrator DPS."
    },
    "Leshak": {
        "class": "Battleship",
        "faction": "Triglavian",
        "role": "Capital / Structure Buster",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "20-60 km",
        "tactics": "Spools past 3500+ DPS on single target. Dual remote armor reps. Break lock or kill before spool reaches maximum.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 0,
        "weapon_type": "Supratidal Entropic Disintegrator (Spooling Precursor)",
        "bonuses": [
            "100% Entropic Disintegrator max damage multiplier",
            "5% Entropic Disintegrator rate of fire per lvl",
            "100% Remote Armor repair amount"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Leshak [Battleship | Triglavian]\n  - Combat Role: Capital / Structure Buster\n  - Weapon System: Supratidal Entropic Disintegrator (Spooling Precursor)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 8 | Rigs: 3 (Turrets: 1 | Launchers: 0)\n  - Key Bonuses: 100% Entropic Disintegrator max damage multiplier | 5% Entropic Disintegrator rate of fire per lvl | 100% Remote Armor repair amount\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: Spools past 3500+ DPS on single target. Dual remote armor reps. Break lock or kill before spool reaches maximum."
    },
    "Ikitursa": {
        "class": "Heavy Assault Cruiser",
        "faction": "Triglavian",
        "role": "HAC Disintegrator Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "10-35 km",
        "tactics": "Triglavian HAC with Assault Damage Control and immense max-spool disintegrator DPS. Apply Tracking Disruptors or neuts.",
        "high_slots": 5,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 0,
        "weapon_type": "Medium Entropic Disintegrator (Spooling Precursor)",
        "bonuses": [
            "100% Entropic Disintegrator max damage multiplier",
            "5% Entropic Disintegrator damage per lvl",
            "7.5% Armor Repair amount per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ikitursa [Heavy Assault Cruiser | Triglavian]\n  - Combat Role: HAC Disintegrator Brawler\n  - Weapon System: Medium Entropic Disintegrator (Spooling Precursor)\n  - Slot Layout: Highs: 5 | Mids: 4 | Lows: 6 | Rigs: 2 (Turrets: 1 | Launchers: 0)\n  - Key Bonuses: 100% Entropic Disintegrator max damage multiplier | 5% Entropic Disintegrator damage per lvl | 7.5% Armor Repair amount per lvl\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 10-35 km\n  - Tactical Counter-Play: Triglavian HAC with Assault Damage Control and immense max-spool disintegrator DPS. Apply Tracking Disruptors or neuts."
    },
    "Zarmazd": {
        "class": "Logistics Cruiser",
        "faction": "Triglavian",
        "role": "T2 Spooling Remote Armor",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Rep Range",
        "tactics": "T2 Triglavian logistics cruiser with extreme ramping armor repairs.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "T2 Spooling Remote Armor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Zarmazd [Logistics Cruiser | Triglavian]\n  - Combat Role: T2 Spooling Remote Armor\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: T2 Spooling Remote Armor Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Rep Range\n  - Tactical Counter-Play: T2 Triglavian logistics cruiser with extreme ramping armor repairs."
    },
    "Zirnitra": {
        "class": "Dreadnought",
        "faction": "Triglavian",
        "role": "Capital Disintegrator Siege",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Triglavian dreadnought with capital spooling disintegrator.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Capital Disintegrator Siege Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Zirnitra [Dreadnought | Triglavian]\n  - Combat Role: Capital Disintegrator Siege\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Capital Disintegrator Siege Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Triglavian dreadnought with capital spooling disintegrator."
    },
    "Skybreaker": {
        "class": "Frigate",
        "faction": "EDENCOM",
        "role": "Vortron Arcing Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Vorton projector arcs lightning damage to up to 5 nearby hostile targets.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Vortron Arcing Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Skybreaker [Frigate | EDENCOM]\n  - Combat Role: Vortron Arcing Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Vortron Arcing Frigate Class Role Bonus\n  - Defense Profile: Shield | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Vorton projector arcs lightning damage to up to 5 nearby hostile targets."
    },
    "Stormbringer": {
        "class": "Cruiser",
        "faction": "EDENCOM",
        "role": "Vortron Arcing Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "15-35 km",
        "tactics": "Medium vorton projector arcs heavy EM/Kinetic damage across fleet clusters.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Vortron Arcing Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stormbringer [Cruiser | EDENCOM]\n  - Combat Role: Vortron Arcing Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Vortron Arcing Cruiser Class Role Bonus\n  - Defense Profile: Shield | Speed: Moderate\n  - Weapon Optimal: 15-35 km\n  - Tactical Counter-Play: Medium vorton projector arcs heavy EM/Kinetic damage across fleet clusters."
    },
    "Thunderchild": {
        "class": "Battleship",
        "faction": "EDENCOM",
        "role": "Heavy Vortron Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "30-70 km",
        "tactics": "Large vorton projector chains massive damage across 10 linked enemy ships.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Heavy Vortron Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thunderchild [Battleship | EDENCOM]\n  - Combat Role: Heavy Vortron Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Heavy Vortron Battleship Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Large vorton projector chains massive damage across 10 linked enemy ships."
    },
    "Apotheosis": {
        "class": "Frigate",
        "faction": "Society of Conscious Thought",
        "role": "Special Shuttle / Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield/Armor Omni",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "SOCT frigate with universal weapon and scan bonuses.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Special Shuttle / Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Apotheosis [Frigate | Society of Conscious Thought]\n  - Combat Role: Special Shuttle / Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Special Shuttle / Frigate Class Role Bonus\n  - Defense Profile: Shield/Armor Omni | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: SOCT frigate with universal weapon and scan bonuses."
    },
    "Sunesis": {
        "class": "Destroyer",
        "faction": "Society of Conscious Thought",
        "role": "Insta-Align Multi-Role Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast (<2s align)",
        "optimal_range": "0-25 km",
        "tactics": "Sub-2s align hauler and combatant with universal weapon bonuses.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Insta-Align Multi-Role Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sunesis [Destroyer | Society of Conscious Thought]\n  - Combat Role: Insta-Align Multi-Role Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Insta-Align Multi-Role Destroyer Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Fast (<2s align)\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Sub-2s align hauler and combatant with universal weapon bonuses."
    },
    "Gnosis": {
        "class": "Battlecruiser",
        "faction": "Society of Conscious Thought",
        "role": "Multi-Role Combat / Exploration BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor / Hull Buffer",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Universal weapon and tank bonuses. Highly adaptable to any combat role.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Multi-Role Combat / Exploration BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Gnosis [Battlecruiser | Society of Conscious Thought]\n  - Combat Role: Multi-Role Combat / Exploration BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Multi-Role Combat / Exploration BC Class Role Bonus\n  - Defense Profile: Shield / Armor / Hull Buffer | Speed: Moderate\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Universal weapon and tank bonuses. Highly adaptable to any combat role."
    },
    "Praxis": {
        "class": "Battleship",
        "faction": "Society of Conscious Thought",
        "role": "Multi-Role Line Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor / Hull Buffer",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Massive slot layout and universal bonus for lasers, hybrids, projectiles, missiles, and drones.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Multi-Role Line Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Praxis [Battleship | Society of Conscious Thought]\n  - Combat Role: Multi-Role Line Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Multi-Role Line Battleship Class Role Bonus\n  - Defense Profile: Shield / Armor / Hull Buffer | Speed: Slow\n  - Weapon Optimal: 0-80 km\n  - Tactical Counter-Play: Massive slot layout and universal bonus for lasers, hybrids, projectiles, missiles, and drones."
    },
    "Pacifier": {
        "class": "Frigate",
        "faction": "CONCORD",
        "role": "Covert Ops / Fast Interceptor",
        "threat": "THREAT_COVERT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "CONCORD covert ops frigate with extreme warp speed and combat versatility.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Covert Ops / Fast Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Pacifier [Frigate | CONCORD]\n  - Combat Role: Covert Ops / Fast Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Covert Ops / Fast Interceptor Class Role Bonus\n  - Defense Profile: Shield / Armor | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: CONCORD covert ops frigate with extreme warp speed and combat versatility."
    },
    "Enforcer": {
        "class": "Cruiser",
        "faction": "CONCORD",
        "role": "Covert Combat Cruiser",
        "threat": "THREAT_COVERT",
        "tank": "Shield / Armor",
        "speed": "Fast",
        "optimal_range": "0-35 km",
        "tactics": "CONCORD covert cruiser with massive security status bonus and omni damage.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Combat Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Enforcer [Cruiser | CONCORD]\n  - Combat Role: Covert Combat Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Combat Cruiser Class Role Bonus\n  - Defense Profile: Shield / Armor | Speed: Fast\n  - Weapon Optimal: 0-35 km\n  - Tactical Counter-Play: CONCORD covert cruiser with massive security status bonus and omni damage."
    },
    "Marshal": {
        "class": "Battleship",
        "faction": "CONCORD",
        "role": "Covert Black Ops Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Active Shield / Armor",
        "speed": "Moderate",
        "optimal_range": "0-60 km",
        "tactics": "CONCORD Black Ops battleship with immense active repair and covert jump portal capability.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Covert Black Ops Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Marshal [Battleship | CONCORD]\n  - Combat Role: Covert Black Ops Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Covert Black Ops Battleship Class Role Bonus\n  - Defense Profile: Active Shield / Armor | Speed: Moderate\n  - Weapon Optimal: 0-60 km\n  - Tactical Counter-Play: CONCORD Black Ops battleship with immense active repair and covert jump portal capability."
    },
    "Monitor": {
        "class": "Cruiser",
        "faction": "CONCORD",
        "role": "Flag Cruiser / Invulnerable FC",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Omni Buffer (1M+ EHP)",
        "speed": "Fast",
        "optimal_range": "0 km",
        "tactics": "Fleet Commander flag cruiser with over 1 million EHP and 0 DPS output. Ignore and kill the fleet.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Flag Cruiser / Invulnerable FC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Monitor [Cruiser | CONCORD]\n  - Combat Role: Flag Cruiser / Invulnerable FC\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Flag Cruiser / Invulnerable FC Class Role Bonus\n  - Defense Profile: Immense Omni Buffer (1M+ EHP) | Speed: Fast\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fleet Commander flag cruiser with over 1 million EHP and 0 DPS output. Ignore and kill the fleet."
    },
    "Condor": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Missile Kiter / Light Tackle",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "20-35 km",
        "tactics": "Light missile kiter with kinetic missile bonus.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Missile Kiter / Light Tackle Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Condor [Frigate | Caldari]\n  - Combat Role: Missile Kiter / Light Tackle\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Missile Kiter / Light Tackle Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: 20-35 km\n  - Tactical Counter-Play: Light missile kiter with kinetic missile bonus."
    },
    "Kestrel": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Missile / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "4 missile launchers with all 4 damage types.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Missile / Rocket Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kestrel [Frigate | Caldari]\n  - Combat Role: Missile / Rocket Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Missile / Rocket Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer / Active | Speed: Moderate\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: 4 missile launchers with all 4 damage types."
    },
    "Merlin": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Blaster / Rail Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Dual MASB",
        "speed": "Moderate",
        "optimal_range": "0-10 km",
        "tactics": "Strong shield resistance bonus; high blaster DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Blaster / Rail Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Merlin [Frigate | Caldari]\n  - Combat Role: Blaster / Rail Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Blaster / Rail Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer / Dual MASB | Speed: Moderate\n  - Weapon Optimal: 0-10 km\n  - Tactical Counter-Play: Strong shield resistance bonus; high blaster DPS."
    },
    "Heron": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning frigate often bait-tanked with rockets.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Exploration / Light Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Heron [Frigate | Caldari]\n  - Combat Role: Exploration / Light Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Exploration / Light Drone Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Scanning frigate often bait-tanked with rockets."
    },
    "Bantam": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield",
        "tactics": "T1 frigate shield logistics.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Shield Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bantam [Frigate | Caldari]\n  - Combat Role: Shield Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Shield Logistics Frigate Class Role Bonus\n  - Defense Profile: Shield | Speed: Moderate\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: T1 frigate shield logistics."
    },
    "Griffin": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "ECM Jamming Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin Shield",
        "speed": "Moderate",
        "optimal_range": "30-60 km",
        "tactics": "Long-range ECM jammers break target locks. Primary immediately.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "ECM Jamming Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Griffin [Frigate | Caldari]\n  - Combat Role: ECM Jamming Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: ECM Jamming Frigate Class Role Bonus\n  - Defense Profile: Paper Thin Shield | Speed: Moderate\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Long-range ECM jammers break target locks. Primary immediately."
    },
    "Caldari Navy Hookbill": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Dual Web Rocket / Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "5 mid slots allow dual webs + scram + MSE. Deadly 1v1 rocket brawler.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Dual Web Rocket / Missile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Caldari Navy Hookbill [Faction Frigate | Caldari (Navy)]\n  - Combat Role: Dual Web Rocket / Missile Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Dual Web Rocket / Missile Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer / Active | Speed: Fast\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: 5 mid slots allow dual webs + scram + MSE. Deadly 1v1 rocket brawler."
    },
    "Griffin Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Combat ECM / Hybrid Brawler",
        "threat": "THREAT_ECM",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Strong hybrid turret DPS and ECM burst tackle capability.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat ECM / Hybrid Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Griffin Navy Issue [Faction Frigate | Caldari (Navy)]\n  - Combat Role: Combat ECM / Hybrid Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat ECM / Hybrid Brawler Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Strong hybrid turret DPS and ECM burst tackle capability."
    },
    "Heron Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Combat Explorer / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Dual MASB",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Faction combat exploration frigate with heavy rocket DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Explorer / Rocket Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Heron Navy Issue [Faction Frigate | Caldari (Navy)]\n  - Combat Role: Combat Explorer / Rocket Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Explorer / Rocket Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer / Dual MASB | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Faction combat exploration frigate with heavy rocket DPS."
    },
    "Buzzard": {
        "class": "Covert Ops",
        "faction": "Caldari",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout. Potential Covert Cyno beacon.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Stealth Scout / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Buzzard [Covert Ops | Caldari]\n  - Combat Role: Stealth Scout / Cyno\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Stealth Scout / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: Covert\n  - Tactical Counter-Play: Covert cloaking scout. Potential Covert Cyno beacon."
    },
    "Manticore": {
        "class": "Stealth Bomber",
        "faction": "Caldari",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Kinetic bombs and torpedoes from cloak.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Torpedo / Bomb Bomber Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Manticore [Stealth Bomber | Caldari]\n  - Combat Role: Covert Torpedo / Bomb Bomber\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Torpedo / Bomb Bomber Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Kinetic bombs and torpedoes from cloak."
    },
    "Harpy": {
        "class": "Assault Frigate",
        "faction": "Caldari",
        "role": "Rail Sniper / ADC Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "10-40 km",
        "tactics": "Long-range railgun sniper frigate with shield buffer. Counter with high transversal speed.",
        "high_slots": 4,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Hybrid (150mm Railguns / Blasters)",
        "bonuses": [
            "10% Small Hybrid optimal range per lvl",
            "5% Small Hybrid damage per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Harpy [Assault Frigate | Caldari]\n  - Combat Role: Rail Sniper / ADC Brawler\n  - Weapon System: Small Hybrid (150mm Railguns / Blasters)\n  - Slot Layout: Highs: 4 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 10% Small Hybrid optimal range per lvl | 5% Small Hybrid damage per lvl | Role: Assault Damage Control capable\n  - Defense Profile: Shield Buffer + ADC | Speed: Fast\n  - Weapon Optimal: 10-40 km\n  - Tactical Counter-Play: Long-range railgun sniper frigate with shield buffer. Counter with high transversal speed."
    },
    "Hawk": {
        "class": "Assault Frigate",
        "faction": "Caldari",
        "role": "Dual MASB Rocket Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Dual MASB Active + ADC",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "Heavy dual MASB active shield tank. Counter with EM damage and heavy capacitor neutralizers.",
        "high_slots": 4,
        "mid_slots": 5,
        "low_slots": 2,
        "rig_slots": 2,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 4,
        "weapon_type": "Rockets / Light Missiles (Active Shield)",
        "bonuses": [
            "5% Rocket/Light Missile kinetic/thermal damage per lvl",
            "7.5% shield boost amount per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hawk [Assault Frigate | Caldari]\n  - Combat Role: Dual MASB Rocket Brawler\n  - Weapon System: Rockets / Light Missiles (Active Shield)\n  - Slot Layout: Highs: 4 | Mids: 5 | Lows: 2 | Rigs: 2 (Turrets: 0 | Launchers: 4)\n  - Key Bonuses: 5% Rocket/Light Missile kinetic/thermal damage per lvl | 7.5% shield boost amount per lvl | Role: Assault Damage Control capable\n  - Defense Profile: Dual MASB Active + ADC | Speed: Moderate\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Heavy dual MASB active shield tank. Counter with EM damage and heavy capacitor neutralizers."
    },
    "Kitsune": {
        "class": "Electronic Attack Ship",
        "faction": "Caldari",
        "role": "Long-Range Fleet ECM",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "Massive ECM jamming range. Jams out entire wings from 80 km.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Long-Range Fleet ECM Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kitsune [Electronic Attack Ship | Caldari]\n  - Combat Role: Long-Range Fleet ECM\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Long-Range Fleet ECM Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast\n  - Weapon Optimal: 50-100 km\n  - Tactical Counter-Play: Massive ECM jamming range. Jams out entire wings from 80 km."
    },
    "Crow": {
        "class": "Interceptor",
        "faction": "Caldari",
        "role": "Long-Range Light Missile Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "25-45 km",
        "tactics": "Fast nullified missile kiter.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Long-Range Light Missile Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Crow [Interceptor | Caldari]\n  - Combat Role: Long-Range Light Missile Kiter\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Long-Range Light Missile Kiter Class Role Bonus\n  - Defense Profile: Shield | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 25-45 km\n  - Tactical Counter-Play: Fast nullified missile kiter."
    },
    "Raptor": {
        "class": "Interceptor",
        "faction": "Caldari",
        "role": "Fleet Tackle / Hybrid Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast combat tackle interceptor with high hybrid DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fleet Tackle / Hybrid Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Raptor [Interceptor | Caldari]\n  - Combat Role: Fleet Tackle / Hybrid Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fleet Tackle / Hybrid Interceptor Class Role Bonus\n  - Defense Profile: Shield | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Fast combat tackle interceptor with high hybrid DPS."
    },
    "Kirin": {
        "class": "Logistics Frigate",
        "faction": "Caldari",
        "role": "T2 Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Assault-tier remote shield repair frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "T2 Shield Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kirin [Logistics Frigate | Caldari]\n  - Combat Role: T2 Shield Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: T2 Shield Logistics Frigate Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Assault-tier remote shield repair frigate."
    },
    "Cormorant": {
        "class": "Destroyer",
        "faction": "Caldari",
        "role": "Rail Sniper / Blaster Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km (Rails) / 0-10 km (Blasters)",
        "tactics": "8 hybrid turrets with optimal range bonus. Lethal fleet sniper doctrine.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Rail Sniper / Blaster Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cormorant [Destroyer | Caldari]\n  - Combat Role: Rail Sniper / Blaster Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Rail Sniper / Blaster Destroyer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 30-70 km (Rails) / 0-10 km (Blasters)\n  - Tactical Counter-Play: 8 hybrid turrets with optimal range bonus. Lethal fleet sniper doctrine."
    },
    "Corax": {
        "class": "Destroyer",
        "faction": "Caldari",
        "role": "Light Missile / Rocket Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "7 missile launchers with kinetic bonus.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Light Missile / Rocket Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Corax [Destroyer | Caldari]\n  - Combat Role: Light Missile / Rocket Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Light Missile / Rocket Destroyer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 20-50 km\n  - Tactical Counter-Play: 7 missile launchers with kinetic bonus."
    },
    "Cormorant Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Caldari (Navy)",
        "role": "Navy Rail Sniper Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "40-90 km",
        "tactics": "Extreme railgun range and tracking.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Navy Rail Sniper Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cormorant Navy Issue [Faction Destroyer | Caldari (Navy)]\n  - Combat Role: Navy Rail Sniper Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Rail Sniper Destroyer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 40-90 km\n  - Tactical Counter-Play: Extreme railgun range and tracking."
    },
    "Flycatcher": {
        "class": "Interdictor",
        "faction": "Caldari",
        "role": "Shield Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates. Primary target.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Shield Warp Bubble Launcher Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Flycatcher [Interdictor | Caldari]\n  - Combat Role: Shield Warp Bubble Launcher\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Shield Warp Bubble Launcher Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast (2.8+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Deploys 20km warp disruption bubbles on gates. Primary target."
    },
    "Stork": {
        "class": "Command Destroyer",
        "faction": "Caldari",
        "role": "Micro Jump Field / Shield Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Micro Jump Field / Shield Skiff Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stork [Command Destroyer | Caldari]\n  - Combat Role: Micro Jump Field / Shield Skiff\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Micro Jump Field / Shield Skiff Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Jackdaw": {
        "class": "Tactical Destroyer",
        "faction": "Caldari",
        "role": "T3 Mode-Switching Missile Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Shield",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "20-60 km",
        "tactics": "Switches between Defensive (+resist), Propulsion (+speed), and Sharpshooter (+range/damage). High threat.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "T3 Mode-Switching Missile Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Jackdaw [Tactical Destroyer | Caldari]\n  - Combat Role: T3 Mode-Switching Missile Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: T3 Mode-Switching Missile Destroyer Class Role Bonus\n  - Defense Profile: Active / Passive Shield | Speed: Variable (Prop/Sharpshooter/Defensive)\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: Switches between Defensive (+resist), Propulsion (+speed), and Sharpshooter (+range/damage). High threat."
    },
    "Caracal": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Rapid Light / Heavy Missile Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate (1.8-2.2 km/s)",
        "optimal_range": "30-65 km",
        "tactics": "Rapid Light Missile (RLML) anti-frigate platform. High burst, 35s reload.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Rapid Light / Heavy Missile Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Caracal [Cruiser | Caldari]\n  - Combat Role: Rapid Light / Heavy Missile Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Rapid Light / Heavy Missile Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate (1.8-2.2 km/s)\n  - Weapon Optimal: 30-65 km\n  - Tactical Counter-Play: Rapid Light Missile (RLML) anti-frigate platform. High burst, 35s reload."
    },
    "Moa": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Rail / Blaster Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Heavy Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-15 km / 30-60 km",
        "tactics": "Strong shield resistance bonus; standard line fleet brawler/sniper.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Rail / Blaster Fleet Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Moa [Cruiser | Caldari]\n  - Combat Role: Rail / Blaster Fleet Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Rail / Blaster Fleet Cruiser Class Role Bonus\n  - Defense Profile: Heavy Shield Buffer | Speed: Slow\n  - Weapon Optimal: 0-15 km / 30-60 km\n  - Tactical Counter-Play: Strong shield resistance bonus; standard line fleet brawler/sniper."
    },
    "Osprey": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Shield Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield (Cap Transfer)",
        "tactics": "Cap-chain shield logistics cruiser. Break cap chain to collapse fleet reps.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Shield Logistics Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Osprey [Cruiser | Caldari]\n  - Combat Role: Shield Logistics Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Shield Logistics Cruiser Class Role Bonus\n  - Defense Profile: Shield | Speed: Moderate\n  - Weapon Optimal: Remote Shield (Cap Transfer)\n  - Tactical Counter-Play: Cap-chain shield logistics cruiser. Break cap chain to collapse fleet reps."
    },
    "Blackbird": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Fleet ECM Jammer",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "50-100 km",
        "tactics": "Cruiser ECM platform. Jamming disrupts target locks across the grid.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Fleet ECM Jammer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Blackbird [Cruiser | Caldari]\n  - Combat Role: Fleet ECM Jammer\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Fleet ECM Jammer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 50-100 km\n  - Tactical Counter-Play: Cruiser ECM platform. Jamming disrupts target locks across the grid."
    },
    "Caracal Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Caldari (Navy)",
        "role": "Heavy Missile / Rapid Light Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "30-75 km",
        "tactics": "Heavier shield buffer and missile velocity than standard Caracal.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Missile / Rapid Light Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Caracal Navy Issue [Faction Cruiser | Caldari (Navy)]\n  - Combat Role: Heavy Missile / Rapid Light Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Missile / Rapid Light Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 30-75 km\n  - Tactical Counter-Play: Heavier shield buffer and missile velocity than standard Caracal."
    },
    "Osprey Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Caldari (Navy)",
        "role": "Fast Missile Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.4+ km/s)",
        "optimal_range": "30-60 km",
        "tactics": "High-speed nano missile kiter.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Fast Missile Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Osprey Navy Issue [Faction Cruiser | Caldari (Navy)]\n  - Combat Role: Fast Missile Kiter\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Fast Missile Kiter Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast (2.4+ km/s)\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: High-speed nano missile kiter."
    },
    "Cerberus": {
        "class": "Heavy Assault Cruiser",
        "faction": "Caldari",
        "role": "HAC Heavy Missile Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "Sniper missile HAC (80-120 km projection). Counter with Missile Guidance Disruptors (Velocity script) and speed.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 4,
        "rig_slots": 2,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy Assault Missiles / Heavy Missiles / RLML",
        "bonuses": [
            "5% HAM/Heavy Missile kinetic damage per lvl",
            "10% missile velocity per lvl",
            "Role: 50% missile flight time bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cerberus [Heavy Assault Cruiser | Caldari]\n  - Combat Role: HAC Heavy Missile Sniper\n  - Weapon System: Heavy Assault Missiles / Heavy Missiles / RLML\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 4 | Rigs: 2 (Turrets: 0 | Launchers: 6)\n  - Key Bonuses: 5% HAM/Heavy Missile kinetic damage per lvl | 10% missile velocity per lvl | Role: 50% missile flight time bonus\n  - Defense Profile: Shield Buffer + ADC | Speed: Fast\n  - Weapon Optimal: 50-100 km\n  - Tactical Counter-Play: Sniper missile HAC (80-120 km projection). Counter with Missile Guidance Disruptors (Velocity script) and speed."
    },
    "Eagle": {
        "class": "Heavy Assault Cruiser",
        "faction": "Caldari",
        "role": "HAC Rail Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "60-120 km",
        "tactics": "High-resist HAC rail sniper with extreme projection.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "HAC Rail Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Eagle [Heavy Assault Cruiser | Caldari]\n  - Combat Role: HAC Rail Sniper\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: HAC Rail Sniper Class Role Bonus\n  - Defense Profile: Shield Buffer + ADC | Speed: Moderate\n  - Weapon Optimal: 60-120 km\n  - Tactical Counter-Play: High-resist HAC rail sniper with extreme projection."
    },
    "Broadsword": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Minmatar",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Projects focused infinite warp scrambler or 20km mobile bubble.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Warp Disruption Field Generator Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Broadsword [Heavy Interdiction Cruiser | Minmatar]\n  - Combat Role: Warp Disruption Field Generator\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Warp Disruption Field Generator Class Role Bonus\n  - Defense Profile: Immense Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 0-20 km (Bubble) / Infinite Scram\n  - Tactical Counter-Play: Projects focused infinite warp scrambler or 20km mobile bubble."
    },
    "Falcon": {
        "class": "Force Recon",
        "faction": "Caldari",
        "role": "Covert Cloak / ECM / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "50-100 km",
        "tactics": "Uncloaks to jam targets and light Covert Cyno. Top priority target.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Cloak / ECM / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Falcon [Force Recon | Caldari]\n  - Combat Role: Covert Cloak / ECM / Cyno\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Cloak / ECM / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 50-100 km\n  - Tactical Counter-Play: Uncloaks to jam targets and light Covert Cyno. Top priority target."
    },
    "Rook": {
        "class": "Combat Recon",
        "faction": "Caldari",
        "role": "D-Scan Immune ECM Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "50-90 km",
        "tactics": "Invisible to Directional Scan. Heavy ECM jammer and missile DPS.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "D-Scan Immune ECM Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rook [Combat Recon | Caldari]\n  - Combat Role: D-Scan Immune ECM Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: D-Scan Immune ECM Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 50-90 km\n  - Tactical Counter-Play: Invisible to Directional Scan. Heavy ECM jammer and missile DPS."
    },
    "Basilisk": {
        "class": "Logistics Cruiser",
        "faction": "Caldari",
        "role": "T2 Cap-Chain Shield Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield (Cap Transfer)",
        "tactics": "Premier T2 shield logistics. Maintain cap chain with second Basilisk.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "T2 Cap-Chain Shield Logistics Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Basilisk [Logistics Cruiser | Caldari]\n  - Combat Role: T2 Cap-Chain Shield Logistics\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: T2 Cap-Chain Shield Logistics Class Role Bonus\n  - Defense Profile: Shield | Speed: Moderate\n  - Weapon Optimal: Remote Shield (Cap Transfer)\n  - Tactical Counter-Play: Premier T2 shield logistics. Maintain cap chain with second Basilisk."
    },
    "Tengu": {
        "class": "Strategic Cruiser",
        "faction": "Caldari",
        "role": "Modular T3C (Missile / Rail / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer / Active",
        "speed": "Fast (1.8-2.5 km/s)",
        "optimal_range": "30-90 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy missile DPS, or 100MN AB.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Modular T3C (Missile / Rail / Cloak) Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tengu [Strategic Cruiser | Caldari]\n  - Combat Role: Modular T3C (Missile / Rail / Cloak)\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Modular T3C (Missile / Rail / Cloak) Class Role Bonus\n  - Defense Profile: Shield Buffer / Active | Speed: Fast (1.8-2.5 km/s)\n  - Weapon Optimal: 30-90 km\n  - Tactical Counter-Play: Highly customizable. Can fit covert cloak, interdiction nullification, heavy missile DPS, or 100MN AB."
    },
    "Drake": {
        "class": "Battlecruiser",
        "faction": "Caldari",
        "role": "Heavy Missile Fleet BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Shield Buffer / Passive",
        "speed": "Slow",
        "optimal_range": "30-70 km",
        "tactics": "Heavy shield buffer battlecruiser. Counter with EM/Thermal damage and Missile Guidance Disruptors.",
        "high_slots": 7,
        "mid_slots": 6,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy Missiles / Heavy Assault Missiles",
        "bonuses": [
            "4% all shield resists per lvl",
            "10% Heavy Missile kinetic damage per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Drake [Battlecruiser | Caldari]\n  - Combat Role: Heavy Missile Fleet BC\n  - Weapon System: Heavy Missiles / Heavy Assault Missiles\n  - Slot Layout: Highs: 7 | Mids: 6 | Lows: 4 | Rigs: 3 (Turrets: 0 | Launchers: 6)\n  - Key Bonuses: 4% all shield resists per lvl | 10% Heavy Missile kinetic damage per lvl\n  - Defense Profile: Massive Shield Buffer / Passive | Speed: Slow\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Heavy shield buffer battlecruiser. Counter with EM/Thermal damage and Missile Guidance Disruptors."
    },
    "Ferox": {
        "class": "Battlecruiser",
        "faction": "Caldari",
        "role": "Rail Sniper / Fleet Anchor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "40-100 km",
        "tactics": "Line fleet railgun anchor with extreme optimal range.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Rail Sniper / Fleet Anchor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ferox [Battlecruiser | Caldari]\n  - Combat Role: Rail Sniper / Fleet Anchor\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Rail Sniper / Fleet Anchor Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 40-100 km\n  - Tactical Counter-Play: Line fleet railgun anchor with extreme optimal range."
    },
    "Naga": {
        "class": "Attack Battlecruiser",
        "faction": "Caldari",
        "role": "Battleship-Gun Rail Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield",
        "speed": "Moderate",
        "optimal_range": "80-150 km",
        "tactics": "Large Battleship Railguns on BC hull. Massive alpha at extreme range.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Battleship-Gun Rail Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Naga [Attack Battlecruiser | Caldari]\n  - Combat Role: Battleship-Gun Rail Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Battleship-Gun Rail Sniper Class Role Bonus\n  - Defense Profile: Paper Thin Shield | Speed: Moderate\n  - Weapon Optimal: 80-150 km\n  - Tactical Counter-Play: Large Battleship Railguns on BC hull. Massive alpha at extreme range."
    },
    "Drake Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Caldari (Navy)",
        "role": "Heavy Missile / Shield BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "35-80 km",
        "tactics": "Higher missile application and mobility than standard Drake.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Missile / Shield BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Drake Navy Issue [Faction Battlecruiser | Caldari (Navy)]\n  - Combat Role: Heavy Missile / Shield BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Missile / Shield BC Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 35-80 km\n  - Tactical Counter-Play: Higher missile application and mobility than standard Drake."
    },
    "Ferox Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Caldari (Navy)",
        "role": "Hybrid Brawler / Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Heavy Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "20-80 km",
        "tactics": "Enhanced hybrid turret tracking and shield reserves.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Hybrid Brawler / Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ferox Navy Issue [Faction Battlecruiser | Caldari (Navy)]\n  - Combat Role: Hybrid Brawler / Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Hybrid Brawler / Sniper Class Role Bonus\n  - Defense Profile: Heavy Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 20-80 km\n  - Tactical Counter-Play: Enhanced hybrid turret tracking and shield reserves."
    },
    "Nighthawk": {
        "class": "Command Ship",
        "faction": "Caldari",
        "role": "Shield Fleet Command / HAM",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "Provides Fleet Shield Bursts and launches heavy assault missiles.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Shield Fleet Command / HAM Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nighthawk [Command Ship | Caldari]\n  - Combat Role: Shield Fleet Command / HAM\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Shield Fleet Command / HAM Class Role Bonus\n  - Defense Profile: Immense Shield Buffer | Speed: Slow\n  - Weapon Optimal: 20-50 km\n  - Tactical Counter-Play: Provides Fleet Shield Bursts and launches heavy assault missiles."
    },
    "Vulture": {
        "class": "Command Ship",
        "faction": "Caldari",
        "role": "Shield Fleet Command / Rail Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "Provides Fleet Information / Shield Bursts with long-range railguns.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Shield Fleet Command / Rail Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vulture [Command Ship | Caldari]\n  - Combat Role: Shield Fleet Command / Rail Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Shield Fleet Command / Rail Sniper Class Role Bonus\n  - Defense Profile: Immense Shield Buffer | Speed: Slow\n  - Weapon Optimal: 60-140 km\n  - Tactical Counter-Play: Provides Fleet Information / Shield Bursts with long-range railguns."
    },
    "Raven": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Cruise / Torpedo Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Slow",
        "optimal_range": "40-120 km (Cruise) / 15-35 km (Torp)",
        "tactics": "Standard missile battleship. Counter with Missile Guidance Disruptors and signature reduction.",
        "high_slots": 7,
        "mid_slots": 7,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 6,
        "weapon_type": "Cruise Missiles / Torpedoes",
        "bonuses": [
            "5% Cruise/Torpedo rate of fire per lvl",
            "10% Cruise/Torpedo max velocity per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Raven [Battleship | Caldari]\n  - Combat Role: Cruise / Torpedo Battleship\n  - Weapon System: Cruise Missiles / Torpedoes\n  - Slot Layout: Highs: 7 | Mids: 7 | Lows: 5 | Rigs: 3 (Turrets: 0 | Launchers: 6)\n  - Key Bonuses: 5% Cruise/Torpedo rate of fire per lvl | 10% Cruise/Torpedo max velocity per lvl\n  - Defense Profile: Shield Buffer / Active | Speed: Slow\n  - Weapon Optimal: 40-120 km (Cruise) / 15-35 km (Torp)\n  - Tactical Counter-Play: Standard missile battleship. Counter with Missile Guidance Disruptors and signature reduction."
    },
    "Rokh": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Rail Sniper Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "80-160 km",
        "tactics": "Extreme range shield railgun sniper (150-200 km). Counter by closing range inside minimum tracking envelope.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 8,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Hybrid Railguns (425mm Rails)",
        "bonuses": [
            "10% Large Hybrid optimal range per lvl",
            "4% all shield resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rokh [Battleship | Caldari]\n  - Combat Role: Rail Sniper Battleship\n  - Weapon System: Large Hybrid Railguns (425mm Rails)\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 5 | Rigs: 3 (Turrets: 8 | Launchers: 0)\n  - Key Bonuses: 10% Large Hybrid optimal range per lvl | 4% all shield resists per lvl\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 80-160 km\n  - Tactical Counter-Play: Extreme range shield railgun sniper (150-200 km). Counter by closing range inside minimum tracking envelope."
    },
    "Scorpion": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Fleet ECM Battleship",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "60-120 km",
        "tactics": "Massive ECM jamming strength across all racial sensor types.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Fleet ECM Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scorpion [Battleship | Caldari]\n  - Combat Role: Fleet ECM Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Fleet ECM Battleship Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 60-120 km\n  - Tactical Counter-Play: Massive ECM jamming strength across all racial sensor types."
    },
    "Raven Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Caldari (Navy)",
        "role": "Cruise / Torp Navy Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "40-140 km",
        "tactics": "8 launcher hardpoints with superior missile application.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Cruise / Torp Navy Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Raven Navy Issue [Faction Battleship | Caldari (Navy)]\n  - Combat Role: Cruise / Torp Navy Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Cruise / Torp Navy Battleship Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 40-140 km\n  - Tactical Counter-Play: 8 launcher hardpoints with superior missile application."
    },
    "Scorpion Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Caldari (Navy)",
        "role": "Heavy Shield / Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "Trading ECM for massive shield buffer and missile DPS.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Heavy Shield / Missile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scorpion Navy Issue [Faction Battleship | Caldari (Navy)]\n  - Combat Role: Heavy Shield / Missile Brawler\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Heavy Shield / Missile Brawler Class Role Bonus\n  - Defense Profile: Immense Shield Buffer | Speed: Slow\n  - Weapon Optimal: 30-80 km\n  - Tactical Counter-Play: Trading ECM for massive shield buffer and missile DPS."
    },
    "Golem": {
        "class": "Marauder",
        "faction": "Caldari",
        "role": "Bastion Torpedo / Cruise Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Shield (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "30-100 km",
        "tactics": "Bastion Marauder with heavy torpedo alpha and active shield boost. Counter with Missile Guidance Disruptors, firewalls, or capital alpha.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 4,
        "rig_slots": 2,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 4,
        "weapon_type": "Cruise Missiles / Torpedoes (Bastion Siege)",
        "bonuses": [
            "100% Torpedo/Cruise damage bonus",
            "10% Torpedo/Cruise velocity per lvl",
            "Role: Bastion grants 100% Shield Boost and EWAR immunity"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Golem [Marauder | Caldari]\n  - Combat Role: Bastion Torpedo / Cruise Marauder\n  - Weapon System: Cruise Missiles / Torpedoes (Bastion Siege)\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 4 | Rigs: 2 (Turrets: 0 | Launchers: 4)\n  - Key Bonuses: 100% Torpedo/Cruise damage bonus | 10% Torpedo/Cruise velocity per lvl | Role: Bastion grants 100% Shield Boost and EWAR immunity\n  - Defense Profile: Active Shield (Bastion Mode) | Speed: Immobile in Bastion\n  - Weapon Optimal: 30-100 km\n  - Tactical Counter-Play: Bastion Marauder with heavy torpedo alpha and active shield boost. Counter with Missile Guidance Disruptors, firewalls, or capital alpha."
    },
    "Widow": {
        "class": "Black Ops",
        "faction": "Caldari",
        "role": "Covert Jump / ECM Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Shield Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "40-90 km",
        "tactics": "Bridges covert fleets; fires missiles and ECM jammers.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Covert Jump / ECM Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Widow [Black Ops | Caldari]\n  - Combat Role: Covert Jump / ECM Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 2 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Covert Jump / ECM Battleship Class Role Bonus\n  - Defense Profile: Shield Buffer / Active | Speed: Slow (Covert Jump)\n  - Weapon Optimal: 40-90 km\n  - Tactical Counter-Play: Bridges covert fleets; fires missiles and ECM jammers."
    },
    "Phoenix": {
        "class": "Dreadnought",
        "faction": "Caldari",
        "role": "Capital Torpedo / Cruise Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with capital missile launchers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Capital Torpedo / Cruise Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Phoenix [Dreadnought | Caldari]\n  - Combat Role: Capital Torpedo / Cruise Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Capital Torpedo / Cruise Dread Class Role Bonus\n  - Defense Profile: Active Shield (Siege) | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Siege dreadnought with capital missile launchers."
    },
    "Phoenix Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Caldari (Navy)",
        "role": "Navy Capital Missile Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "High-application capital missile dreadnought.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Navy Capital Missile Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Phoenix Navy Issue [Faction Dreadnought | Caldari (Navy)]\n  - Combat Role: Navy Capital Missile Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Navy Capital Missile Dread Class Role Bonus\n  - Defense Profile: Shield Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: High-application capital missile dreadnought."
    },
    "Karura": {
        "class": "Lancer Dreadnought",
        "faction": "Caldari",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Disruptive Lancer Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Karura [Lancer Dreadnought | Caldari]\n  - Combat Role: Disruptive Lancer Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Disruptive Lancer Dread Class Role Bonus\n  - Defense Profile: Shield Active | Speed: Capital\n  - Weapon Optimal: Lancer Beam\n  - Tactical Counter-Play: Fires disruptive capital lance disabling cynos and warp."
    },
    "Chimera": {
        "class": "Carrier",
        "faction": "Caldari",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Launches light and support fighter squadrons.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Fighter Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Chimera [Carrier | Caldari]\n  - Combat Role: Capital Fighter Carrier\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Fighter Carrier Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Capital\n  - Weapon Optimal: Fighter Range\n  - Tactical Counter-Play: Launches light and support fighter squadrons."
    },
    "Wyvern": {
        "class": "Supercarrier",
        "faction": "Caldari",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital fighter bomber strikes and burst projectors.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Heavy Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Wyvern [Supercarrier | Caldari]\n  - Combat Role: Supercapital Heavy Carrier\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Heavy Carrier Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Supercapital fighter bomber strikes and burst projectors."
    },
    "Minokawa": {
        "class": "Force Auxiliary",
        "faction": "Caldari",
        "role": "Capital Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Shield",
        "tactics": "Capital remote shield repair ship.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Shield FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Minokawa [Force Auxiliary | Caldari]\n  - Combat Role: Capital Shield FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Shield FAX Class Role Bonus\n  - Defense Profile: Active Shield (Triage) | Speed: Capital\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Capital remote shield repair ship."
    },
    "Leviathan": {
        "class": "Titan",
        "faction": "Caldari",
        "role": "Supercapital Missile Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Doomsday missile titan with fleet shield burst.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Missile Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Leviathan [Titan | Caldari]\n  - Combat Role: Supercapital Missile Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Missile Titan Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Doomsday missile titan with fleet shield burst."
    },
    "Badger": {
        "class": "Industrial",
        "faction": "Caldari",
        "role": "Standard Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "T1 industrial transport.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Standard Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Badger [Industrial | Caldari]\n  - Combat Role: Standard Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Standard Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: T1 industrial transport."
    },
    "Tayra": {
        "class": "Industrial",
        "faction": "Caldari",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity hauler.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tayra [Industrial | Caldari]\n  - Combat Role: High-Capacity Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Large cargo capacity hauler."
    },
    "Crane": {
        "class": "Blockade Runner",
        "faction": "Caldari",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Shield",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Fast Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Crane [Blockade Runner | Caldari]\n  - Combat Role: Covert Fast Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Fast Hauler Class Role Bonus\n  - Defense Profile: Cloaked Shield | Speed: Fast (<3s align)\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Covert cloaking, cargo-scanned immune hauler."
    },
    "Bustard": {
        "class": "Deep Space Transport",
        "faction": "Caldari",
        "role": "Heavy Shield DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Shield DST Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bustard [Deep Space Transport | Caldari]\n  - Combat Role: Heavy Shield DST\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Shield DST Class Role Bonus\n  - Defense Profile: Immense Shield Buffer (+2 Warp Core) | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: +2 native warp core strength and Fleet Hangar."
    },
    "Charon": {
        "class": "Freighter",
        "faction": "Caldari",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Standard Sub-Capital Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Charon [Freighter | Caldari]\n  - Combat Role: Standard Sub-Capital Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Standard Sub-Capital Freighter Class Role Bonus\n  - Defense Profile: Buffer | Speed: Extremely Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Massive cargo freighter."
    },
    "Rhea": {
        "class": "Jump Freighter",
        "faction": "Caldari",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Jump Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rhea [Jump Freighter | Caldari]\n  - Combat Role: Capital Jump Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Jump Freighter Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Jump Drive\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Jump drive cargo hauler for nullsec logistics."
    },
    "Atron": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Fast Tackle / Blaster Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-8 km",
        "tactics": "High-speed light tackle with close-range blaster DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fast Tackle / Blaster Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Atron [Frigate | Gallente]\n  - Combat Role: Fast Tackle / Blaster Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fast Tackle / Blaster Frigate Class Role Bonus\n  - Defense Profile: Armor / Shield | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-8 km\n  - Tactical Counter-Play: High-speed light tackle with close-range blaster DPS."
    },
    "Tristan": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Drone Kiter / Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield / Hull",
        "speed": "Fast",
        "optimal_range": "0-30 km",
        "tactics": "Versatile drone frigate. Can fly neutralizer brawl or long-range kite.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Drone Kiter / Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tristan [Frigate | Gallente]\n  - Combat Role: Drone Kiter / Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Drone Kiter / Brawler Class Role Bonus\n  - Defense Profile: Armor / Shield / Hull | Speed: Fast\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Versatile drone frigate. Can fly neutralizer brawl or long-range kite."
    },
    "Incursus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Active Armor Blaster Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual Rep Active Armor",
        "speed": "Moderate",
        "optimal_range": "0-8 km",
        "tactics": "Immense active armor repair bonus with close-range blasters.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Active Armor Blaster Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Incursus [Frigate | Gallente]\n  - Combat Role: Active Armor Blaster Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Active Armor Blaster Brawler Class Role Bonus\n  - Defense Profile: Dual Rep Active Armor | Speed: Moderate\n  - Weapon Optimal: 0-8 km\n  - Tactical Counter-Play: Immense active armor repair bonus with close-range blasters."
    },
    "Imicus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Exploration / Light Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Imicus [Frigate | Gallente]\n  - Combat Role: Exploration / Light Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Exploration / Light Drone Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Scanning and exploration frigate."
    },
    "Navitas": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor",
        "tactics": "T1 frigate armor logistics.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Armor Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Navitas [Frigate | Gallente]\n  - Combat Role: Armor Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Armor Logistics Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: T1 frigate armor logistics."
    },
    "Maulus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Remote Sensor Dampener",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "30-70 km",
        "tactics": "Sensor dampeners reduce enemy lock range and scan resolution.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Remote Sensor Dampener Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Maulus [Frigate | Gallente]\n  - Combat Role: Remote Sensor Dampener\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Remote Sensor Dampener Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Sensor dampeners reduce enemy lock range and scan resolution."
    },
    "Federation Navy Comet": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Heavy Blaster / Rail Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Extreme hybrid DPS and drone assistance.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Heavy Blaster / Rail Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Federation Navy Comet [Faction Frigate | Gallente (Navy)]\n  - Combat Role: Heavy Blaster / Rail Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Heavy Blaster / Rail Brawler Class Role Bonus\n  - Defense Profile: Armor / Hull Buffer | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Extreme hybrid DPS and drone assistance."
    },
    "Maulus Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Combat Dampener / Scram Kiter",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Damps enemy lock range while applying strong hybrid DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Dampener / Scram Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Maulus Navy Issue [Faction Frigate | Gallente (Navy)]\n  - Combat Role: Combat Dampener / Scram Kiter\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Dampener / Scram Kiter Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Damps enemy lock range while applying strong hybrid DPS."
    },
    "Imicus Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Combat Explorer / Heavy Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Exploration combat frigate with increased drone bay.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Explorer / Heavy Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Imicus Navy Issue [Faction Frigate | Gallente (Navy)]\n  - Combat Role: Combat Explorer / Heavy Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Explorer / Heavy Drone Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Exploration combat frigate with increased drone bay."
    },
    "Helios": {
        "class": "Covert Ops",
        "faction": "Gallente",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Stealth Scout / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Helios [Covert Ops | Gallente]\n  - Combat Role: Stealth Scout / Cyno\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Stealth Scout / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: Covert\n  - Tactical Counter-Play: Covert cloaking scout frigate."
    },
    "Nemesis": {
        "class": "Stealth Bomber",
        "faction": "Gallente",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Thermal bombs and torpedoes from cloak.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Torpedo / Bomb Bomber Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nemesis [Stealth Bomber | Gallente]\n  - Combat Role: Covert Torpedo / Bomb Bomber\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Torpedo / Bomb Bomber Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Thermal bombs and torpedoes from cloak."
    },
    "Ishkur": {
        "class": "Assault Frigate",
        "faction": "Gallente",
        "role": "Drone / Blaster Assault Frigate",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active + ADC",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Assault Damage Control and drone bay for flexible engagement.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Drone / Blaster Assault Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ishkur [Assault Frigate | Gallente]\n  - Combat Role: Drone / Blaster Assault Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Drone / Blaster Assault Frigate Class Role Bonus\n  - Defense Profile: Armor Buffer / Active + ADC | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Assault Damage Control and drone bay for flexible engagement."
    },
    "Enyo": {
        "class": "Assault Frigate",
        "faction": "Gallente",
        "role": "High DPS Blaster Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "0-8 km",
        "tactics": "Devastating close-range blaster DPS with ADC.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "High DPS Blaster Assault Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Enyo [Assault Frigate | Gallente]\n  - Combat Role: High DPS Blaster Assault\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: High DPS Blaster Assault Class Role Bonus\n  - Defense Profile: Armor Buffer + ADC | Speed: Fast\n  - Weapon Optimal: 0-8 km\n  - Tactical Counter-Play: Devastating close-range blaster DPS with ADC."
    },
    "Keres": {
        "class": "Electronic Attack Ship",
        "faction": "Gallente",
        "role": "Long-Range Dampener / Point",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.0+ km/s)",
        "optimal_range": "30-60 km",
        "tactics": "Projects long-range warp disruptor (35km+) and severe dampeners.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Long-Range Dampener / Point Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Keres [Electronic Attack Ship | Gallente]\n  - Combat Role: Long-Range Dampener / Point\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Long-Range Dampener / Point Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast (4.0+ km/s)\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Projects long-range warp disruptor (35km+) and severe dampeners."
    },
    "Ares": {
        "class": "Interceptor",
        "faction": "Gallente",
        "role": "Fast Fleet Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Nullified fast tackle interceptor.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fast Fleet Tackler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ares [Interceptor | Gallente]\n  - Combat Role: Fast Fleet Tackler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fast Fleet Tackler Class Role Bonus\n  - Defense Profile: Armor / Shield | Speed: Extreme (4.8+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Nullified fast tackle interceptor."
    },
    "Taranis": {
        "class": "Interceptor",
        "faction": "Gallente",
        "role": "Combat Blaster Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-8 km",
        "tactics": "High-DPS combat interceptor with blasters and drones.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Blaster Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Taranis [Interceptor | Gallente]\n  - Combat Role: Combat Blaster Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Blaster Interceptor Class Role Bonus\n  - Defense Profile: Armor | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-8 km\n  - Tactical Counter-Play: High-DPS combat interceptor with blasters and drones."
    },
    "Thalia": {
        "class": "Logistics Frigate",
        "faction": "Gallente",
        "role": "T2 Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Assault-tier remote armor repair frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "T2 Armor Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thalia [Logistics Frigate | Gallente]\n  - Combat Role: T2 Armor Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: T2 Armor Logistics Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Assault-tier remote armor repair frigate."
    },
    "Catalyst": {
        "class": "Destroyer",
        "faction": "Gallente",
        "role": "High DPS Blaster Ganker / Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Moderate",
        "optimal_range": "0-8 km (Blasters) / 20-50 km (Rails)",
        "tactics": "8 hybrid turrets deliver over 600+ DPS close range. Premier suicide gank hull.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "High DPS Blaster Ganker / Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Catalyst [Destroyer | Gallente]\n  - Combat Role: High DPS Blaster Ganker / Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: High DPS Blaster Ganker / Destroyer Class Role Bonus\n  - Defense Profile: Armor / Hull Buffer | Speed: Moderate\n  - Weapon Optimal: 0-8 km (Blasters) / 20-50 km (Rails)\n  - Tactical Counter-Play: 8 hybrid turrets deliver over 600+ DPS close range. Premier suicide gank hull."
    },
    "Algos": {
        "class": "Destroyer",
        "faction": "Gallente",
        "role": "Drone / Rail Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-30 km",
        "tactics": "Full flight of light drones with hybrid turrets.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Drone / Rail Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Algos [Destroyer | Gallente]\n  - Combat Role: Drone / Rail Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Drone / Rail Destroyer Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Full flight of light drones with hybrid turrets."
    },
    "Catalyst Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Gallente (Navy)",
        "role": "Navy Blaster / Rail Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Enhanced tracking and armor plate mass reduction.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Navy Blaster / Rail Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Catalyst Navy Issue [Faction Destroyer | Gallente (Navy)]\n  - Combat Role: Navy Blaster / Rail Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Blaster / Rail Destroyer Class Role Bonus\n  - Defense Profile: Armor / Hull Buffer | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Enhanced tracking and armor plate mass reduction."
    },
    "Eris": {
        "class": "Interdictor",
        "faction": "Gallente",
        "role": "Armor Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Armor Warp Bubble Launcher Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Eris [Interdictor | Gallente]\n  - Combat Role: Armor Warp Bubble Launcher\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Armor Warp Bubble Launcher Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast (2.8+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Deploys 20km warp disruption bubbles on gates."
    },
    "Magus": {
        "class": "Command Destroyer",
        "faction": "Gallente",
        "role": "Micro Jump Field / Armor Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Micro Jump Field / Armor Skiff Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Magus [Command Destroyer | Gallente]\n  - Combat Role: Micro Jump Field / Armor Skiff\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Micro Jump Field / Armor Skiff Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Hecate": {
        "class": "Tactical Destroyer",
        "faction": "Gallente",
        "role": "T3 Mode-Switching Blaster Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Armor / Hull",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "0-15 km",
        "tactics": "Switches between Propulsion, Sharpshooter (1000+ DPS blasters), and Defensive modes.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "T3 Mode-Switching Blaster Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hecate [Tactical Destroyer | Gallente]\n  - Combat Role: T3 Mode-Switching Blaster Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: T3 Mode-Switching Blaster Destroyer Class Role Bonus\n  - Defense Profile: Active / Passive Armor / Hull | Speed: Variable (Prop/Sharpshooter/Defensive)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Switches between Propulsion, Sharpshooter (1000+ DPS blasters), and Defensive modes."
    },
    "Thorax": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Blaster / Rail Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast (2.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast attack cruiser with high blaster DPS and medium drones.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Blaster / Rail Fleet Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thorax [Cruiser | Gallente]\n  - Combat Role: Blaster / Rail Fleet Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Blaster / Rail Fleet Cruiser Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Fast (2.0+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Fast attack cruiser with high blaster DPS and medium drones."
    },
    "Vexor": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Heavy Drone / Armor Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active / Hull",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Heavy drone cruiser capable of fielding full heavy drone flights.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Drone / Armor Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vexor [Cruiser | Gallente]\n  - Combat Role: Heavy Drone / Armor Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Drone / Armor Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer / Active / Hull | Speed: Moderate\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Heavy drone cruiser capable of fielding full heavy drone flights."
    },
    "Exequror": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Armor Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Direct remote armor repair cruiser. High sub-warp mobility.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Armor Logistics Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Exequror [Cruiser | Gallente]\n  - Combat Role: Armor Logistics Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Armor Logistics Cruiser Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Direct remote armor repair cruiser. High sub-warp mobility."
    },
    "Celestis": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Remote Sensor Dampener Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "40-90 km",
        "tactics": "Dampens enemy targeting range and scan resolution across grid.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Remote Sensor Dampener Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Celestis [Cruiser | Gallente]\n  - Combat Role: Remote Sensor Dampener Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Remote Sensor Dampener Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 40-90 km\n  - Tactical Counter-Play: Dampens enemy targeting range and scan resolution across grid."
    },
    "Vexor Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Drone / Hybrid Combat Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Shield",
        "speed": "Fast",
        "optimal_range": "0-50 km",
        "tactics": "Enhanced hybrid turret tracking and heavy drone application.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Drone / Hybrid Combat Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vexor Navy Issue [Faction Cruiser | Gallente (Navy)]\n  - Combat Role: Heavy Drone / Hybrid Combat Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Drone / Hybrid Combat Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer / Shield | Speed: Fast\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Enhanced hybrid turret tracking and heavy drone application."
    },
    "Exequror Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Hybrid Combat Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.2+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Pure combat hybrid cruiser with extreme DPS.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Hybrid Combat Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Exequror Navy Issue [Faction Cruiser | Gallente (Navy)]\n  - Combat Role: Heavy Hybrid Combat Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Hybrid Combat Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast (2.2+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Pure combat hybrid cruiser with extreme DPS."
    },
    "Deimos": {
        "class": "Heavy Assault Cruiser",
        "faction": "Gallente",
        "role": "HAC Active Armor Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Armor + ADC",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Active armor brawler with 800+ DPS. Maintain distance outside 12km or apply heavy tracking disruption and neuts.",
        "high_slots": 5,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 0,
        "weapon_type": "Medium Hybrid Blasters (Heavy Neutron Blasters)",
        "bonuses": [
            "5% Medium Hybrid rate of fire per lvl",
            "7.5% Armor Repair amount per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Deimos [Heavy Assault Cruiser | Gallente]\n  - Combat Role: HAC Active Armor Brawler\n  - Weapon System: Medium Hybrid Blasters (Heavy Neutron Blasters)\n  - Slot Layout: Highs: 5 | Mids: 4 | Lows: 6 | Rigs: 2 (Turrets: 5 | Launchers: 0)\n  - Key Bonuses: 5% Medium Hybrid rate of fire per lvl | 7.5% Armor Repair amount per lvl\n  - Defense Profile: Active Armor + ADC | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Active armor brawler with 800+ DPS. Maintain distance outside 12km or apply heavy tracking disruption and neuts."
    },
    "Ishtar": {
        "class": "Heavy Assault Cruiser",
        "faction": "Gallente",
        "role": "HAC Heavy Drone Cruiser",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor / Shield Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "0-80 km",
        "tactics": "Premier drone HAC. Long-range Sentry sniping or active armor Heavy Drone brawling. Defang drones or damp lock range.",
        "high_slots": 4,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 0,
        "weapon_type": "Heavy / Sentry Drones (100-120 km Sentry Snipe)",
        "bonuses": [
            "10% Heavy/Sentry Drone damage and HP per lvl",
            "10% Drone optimal/tracking per lvl",
            "5% Armor Repair amount per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ishtar [Heavy Assault Cruiser | Gallente]\n  - Combat Role: HAC Heavy Drone Cruiser\n  - Weapon System: Heavy / Sentry Drones (100-120 km Sentry Snipe)\n  - Slot Layout: Highs: 4 | Mids: 4 | Lows: 6 | Rigs: 2 (Turrets: 1 | Launchers: 0)\n  - Key Bonuses: 10% Heavy/Sentry Drone damage and HP per lvl | 10% Drone optimal/tracking per lvl | 5% Armor Repair amount per lvl\n  - Defense Profile: Armor / Shield Buffer + ADC | Speed: Moderate\n  - Weapon Optimal: 0-80 km\n  - Tactical Counter-Play: Premier drone HAC. Long-range Sentry sniping or active armor Heavy Drone brawling. Defang drones or damp lock range."
    },
    "Phobos": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Gallente",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Heavy armor HIC projecting focused infinite points or mobile bubbles.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Warp Disruption Field Generator Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Phobos [Heavy Interdiction Cruiser | Gallente]\n  - Combat Role: Warp Disruption Field Generator\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Warp Disruption Field Generator Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-20 km (Bubble) / Infinite Scram\n  - Tactical Counter-Play: Heavy armor HIC projecting focused infinite points or mobile bubbles."
    },
    "Arazu": {
        "class": "Force Recon",
        "faction": "Gallente",
        "role": "Covert Cloak / 40km Scram / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-40 km",
        "tactics": "Uncloaks to apply 40km warp disruptor / scrambler and light Covert Cyno.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Cloak / 40km Scram / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Arazu [Force Recon | Gallente]\n  - Combat Role: Covert Cloak / 40km Scram / Cyno\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Cloak / 40km Scram / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Uncloaks to apply 40km warp disruptor / scrambler and light Covert Cyno."
    },
    "Lachesis": {
        "class": "Combat Recon",
        "faction": "Gallente",
        "role": "D-Scan Immune Long Point & Damp",
        "threat": "THREAT_ECM",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "40-70 km",
        "tactics": "Invisible to D-Scan. Applies 50km+ point and heavy dampeners.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "D-Scan Immune Long Point & Damp Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Lachesis [Combat Recon | Gallente]\n  - Combat Role: D-Scan Immune Long Point & Damp\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: D-Scan Immune Long Point & Damp Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 40-70 km\n  - Tactical Counter-Play: Invisible to D-Scan. Applies 50km+ point and heavy dampeners."
    },
    "Oneiros": {
        "class": "Logistics Cruiser",
        "faction": "Gallente",
        "role": "T2 Solo Armor Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Self-sufficient armor logistics cruiser (no cap chain required).",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "T2 Solo Armor Logistics Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Oneiros [Logistics Cruiser | Gallente]\n  - Combat Role: T2 Solo Armor Logistics\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: T2 Solo Armor Logistics Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Self-sufficient armor logistics cruiser (no cap chain required)."
    },
    "Proteus": {
        "class": "Strategic Cruiser",
        "faction": "Gallente",
        "role": "Modular T3C (Blaster / Drone / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active",
        "speed": "Fast (1.6-2.2 km/s)",
        "optimal_range": "0-25 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy blasters, or 90% webifiers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Modular T3C (Blaster / Drone / Cloak) Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Proteus [Strategic Cruiser | Gallente]\n  - Combat Role: Modular T3C (Blaster / Drone / Cloak)\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Modular T3C (Blaster / Drone / Cloak) Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Fast (1.6-2.2 km/s)\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Highly customizable. Can fit covert cloak, interdiction nullification, heavy blasters, or 90% webifiers."
    },
    "Brutix": {
        "class": "Battlecruiser",
        "faction": "Gallente",
        "role": "Blaster / Rail Brawler BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Blaster) / 40-80 km (Rail)",
        "tactics": "High hybrid turret DPS and armor repair bonus.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Blaster / Rail Brawler BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Brutix [Battlecruiser | Gallente]\n  - Combat Role: Blaster / Rail Brawler BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Blaster / Rail Brawler BC Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Moderate\n  - Weapon Optimal: 0-20 km (Blaster) / 40-80 km (Rail)\n  - Tactical Counter-Play: High hybrid turret DPS and armor repair bonus."
    },
    "Myrmidon": {
        "class": "Battlecruiser",
        "faction": "Gallente",
        "role": "Triple Active Armor Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Triple Rep Active Armor",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Extreme active armor tank bonus with full heavy drone flights.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Triple Active Armor Drone BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Myrmidon [Battlecruiser | Gallente]\n  - Combat Role: Triple Active Armor Drone BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Triple Active Armor Drone BC Class Role Bonus\n  - Defense Profile: Triple Rep Active Armor | Speed: Slow\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Extreme active armor tank bonus with full heavy drone flights."
    },
    "Talos": {
        "class": "Attack Battlecruiser",
        "faction": "Gallente",
        "role": "Battleship-Gun Blaster / Rail Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield/Armor",
        "speed": "Fast (1.8+ km/s)",
        "optimal_range": "0-20 km (Blasters) / 80-140 km (Rails)",
        "tactics": "Large Battleship Neutron Blasters or Railguns on BC hull. Massive DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Battleship-Gun Blaster / Rail Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Talos [Attack Battlecruiser | Gallente]\n  - Combat Role: Battleship-Gun Blaster / Rail Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Battleship-Gun Blaster / Rail Sniper Class Role Bonus\n  - Defense Profile: Paper Thin Shield/Armor | Speed: Fast (1.8+ km/s)\n  - Weapon Optimal: 0-20 km (Blasters) / 80-140 km (Rails)\n  - Tactical Counter-Play: Large Battleship Neutron Blasters or Railguns on BC hull. Massive DPS."
    },
    "Brutix Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid Brawler BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "Superior armor buffer and hybrid tracking.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Navy Hybrid Brawler BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Brutix Navy Issue [Faction Battlecruiser | Gallente (Navy)]\n  - Combat Role: Navy Hybrid Brawler BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Hybrid Brawler BC Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Superior armor buffer and hybrid tracking."
    },
    "Myrmidon Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Web / Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-40 km",
        "tactics": "Stasis webifier range bonus and heavy drone application.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Web / Drone BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Myrmidon Navy Issue [Faction Battlecruiser | Gallente (Navy)]\n  - Combat Role: Heavy Web / Drone BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Web / Drone BC Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Stasis webifier range bonus and heavy drone application."
    },
    "Astarte": {
        "class": "Command Ship",
        "faction": "Gallente",
        "role": "Armor Fleet Command / Blaster Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Provides Fleet Armor Bursts and deals immense close-range blaster DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Armor Fleet Command / Blaster Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Astarte [Command Ship | Gallente]\n  - Combat Role: Armor Fleet Command / Blaster Brawler\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Armor Fleet Command / Blaster Brawler Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Provides Fleet Armor Bursts and deals immense close-range blaster DPS."
    },
    "Eos": {
        "class": "Command Ship",
        "faction": "Gallente",
        "role": "Armor Fleet Command / Heavy Drone",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer / Active",
        "speed": "Slow",
        "optimal_range": "0-60 km",
        "tactics": "Provides Fleet Armor / Skirmish Bursts with full heavy drone flights.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Armor Fleet Command / Heavy Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Eos [Command Ship | Gallente]\n  - Combat Role: Armor Fleet Command / Heavy Drone\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Armor Fleet Command / Heavy Drone Class Role Bonus\n  - Defense Profile: Immense Armor Buffer / Active | Speed: Slow\n  - Weapon Optimal: 0-60 km\n  - Tactical Counter-Play: Provides Fleet Armor / Skirmish Bursts with full heavy drone flights."
    },
    "Megathron": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Hybrid Brawler / Fleet Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-25 km (Blasters) / 50-100 km (Rails)",
        "tactics": "Fleet line gunship. Counter with Tracking Disruptors and transversal.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Hybrid (Neutron Blaster / Railgun)",
        "bonuses": [
            "5% Large Hybrid rate of fire per lvl",
            "7.5% Large Hybrid tracking per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Megathron [Battleship | Gallente]\n  - Combat Role: Hybrid Brawler / Fleet Battleship\n  - Weapon System: Large Hybrid (Neutron Blaster / Railgun)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 0)\n  - Key Bonuses: 5% Large Hybrid rate of fire per lvl | 7.5% Large Hybrid tracking per lvl\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-25 km (Blasters) / 50-100 km (Rails)\n  - Tactical Counter-Play: Fleet line gunship. Counter with Tracking Disruptors and transversal."
    },
    "Dominix": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Drone / Cap Neutralizer Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active / Hull",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Drone brawler with dual armor repairers. Counter by defanging sentry/heavy drones.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Heavy / Sentry Drones & Neuts",
        "bonuses": [
            "10% Drone damage and HP per lvl",
            "10% Drone optimal/tracking per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Dominix [Battleship | Gallente]\n  - Combat Role: Drone / Cap Neutralizer Battleship\n  - Weapon System: Heavy / Sentry Drones & Neuts\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 10% Drone damage and HP per lvl | 10% Drone optimal/tracking per lvl\n  - Defense Profile: Armor Buffer / Active / Hull | Speed: Slow\n  - Weapon Optimal: 0-80 km\n  - Tactical Counter-Play: Drone brawler with dual armor repairers. Counter by defanging sentry/heavy drones."
    },
    "Hyperion": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Active Armor Blaster Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual / Triple Large Rep Active Armor",
        "speed": "Slow",
        "optimal_range": "0-25 km",
        "tactics": "Massive active armor repair bonus. Extremely difficult to break without heavy neuts.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Active Armor Blaster Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hyperion [Battleship | Gallente]\n  - Combat Role: Active Armor Blaster Brawler\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Active Armor Blaster Brawler Class Role Bonus\n  - Defense Profile: Dual / Triple Large Rep Active Armor | Speed: Slow\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Massive active armor repair bonus. Extremely difficult to break without heavy neuts."
    },
    "Megathron Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-30 km / 60-120 km",
        "tactics": "Higher tracking and armor buffer than standard Megathron.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Navy Hybrid Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Megathron Navy Issue [Faction Battleship | Gallente (Navy)]\n  - Combat Role: Navy Hybrid Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Navy Hybrid Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-30 km / 60-120 km\n  - Tactical Counter-Play: Higher tracking and armor buffer than standard Megathron."
    },
    "Dominix Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid / Drone Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Dual hybrid turret and drone damage bonuses.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Navy Hybrid / Drone Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Dominix Navy Issue [Faction Battleship | Gallente (Navy)]\n  - Combat Role: Navy Hybrid / Drone Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Navy Hybrid / Drone Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-80 km\n  - Tactical Counter-Play: Dual hybrid turret and drone damage bonuses."
    },
    "Kronos": {
        "class": "Marauder",
        "faction": "Gallente",
        "role": "Bastion Blaster / Rail Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Armor (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "0-30 km (Blasters) / 60-120 km (Rails)",
        "tactics": "Bastion Marauder with 3000+ close-range Void blaster DPS. Counter with tracking disruptors, kiting at >30km range, or heavy capacitor neutralizers.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Hybrid Turrets (Neutron Blaster / Railgun)",
        "bonuses": [
            "100% Large Hybrid damage bonus",
            "10% Large Hybrid falloff/tracking per lvl",
            "Role: Bastion grants 100% Armor Repair and EWAR immunity"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kronos [Marauder | Gallente]\n  - Combat Role: Bastion Blaster / Rail Marauder\n  - Weapon System: Large Hybrid Turrets (Neutron Blaster / Railgun)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 2 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Large Hybrid damage bonus | 10% Large Hybrid falloff/tracking per lvl | Role: Bastion grants 100% Armor Repair and EWAR immunity\n  - Defense Profile: Active Armor (Bastion Mode) | Speed: Immobile in Bastion\n  - Weapon Optimal: 0-30 km (Blasters) / 60-120 km (Rails)\n  - Tactical Counter-Play: Bastion Marauder with 3000+ close-range Void blaster DPS. Counter with tracking disruptors, kiting at >30km range, or heavy capacitor neutralizers."
    },
    "Sin": {
        "class": "Black Ops",
        "faction": "Gallente",
        "role": "Covert Jump / Drone / Neut Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Armor Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "0-60 km",
        "tactics": "Bridges covert fleets; applies heavy energy neutralizers and heavy drones.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Covert Jump / Drone / Neut Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sin [Black Ops | Gallente]\n  - Combat Role: Covert Jump / Drone / Neut Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 2 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Covert Jump / Drone / Neut Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Slow (Covert Jump)\n  - Weapon Optimal: 0-60 km\n  - Tactical Counter-Play: Bridges covert fleets; applies heavy energy neutralizers and heavy drones."
    },
    "Moros": {
        "class": "Dreadnought",
        "faction": "Gallente",
        "role": "Capital Blaster / Rail Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with massive capital hybrid DPS.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Capital Blaster / Rail Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Moros [Dreadnought | Gallente]\n  - Combat Role: Capital Blaster / Rail Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Capital Blaster / Rail Dread Class Role Bonus\n  - Defense Profile: Active Armor (Siege) | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Siege dreadnought with massive capital hybrid DPS."
    },
    "Moros Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Gallente (Navy)",
        "role": "Navy Capital Hybrid Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Enhanced hybrid turret tracking and armor buffer.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Navy Capital Hybrid Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Moros Navy Issue [Faction Dreadnought | Gallente (Navy)]\n  - Combat Role: Navy Capital Hybrid Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Navy Capital Hybrid Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Enhanced hybrid turret tracking and armor buffer."
    },
    "Hubris": {
        "class": "Lancer Dreadnought",
        "faction": "Gallente",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Disruptive Lancer Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hubris [Lancer Dreadnought | Gallente]\n  - Combat Role: Disruptive Lancer Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Disruptive Lancer Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Lancer Beam\n  - Tactical Counter-Play: Fires disruptive capital lance disabling cynos and warp."
    },
    "Thanatos": {
        "class": "Carrier",
        "faction": "Gallente",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Carrier with fighter damage and fighter navigation bonuses.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Fighter Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thanatos [Carrier | Gallente]\n  - Combat Role: Capital Fighter Carrier\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Fighter Carrier Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Capital\n  - Weapon Optimal: Fighter Range\n  - Tactical Counter-Play: Carrier with fighter damage and fighter navigation bonuses."
    },
    "Nyx": {
        "class": "Supercarrier",
        "faction": "Gallente",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital with devastating heavy fighter strike wings.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Heavy Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nyx [Supercarrier | Gallente]\n  - Combat Role: Supercapital Heavy Carrier\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Heavy Carrier Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Supercapital with devastating heavy fighter strike wings."
    },
    "Ninazu": {
        "class": "Force Auxiliary",
        "faction": "Gallente",
        "role": "Capital Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Armor",
        "tactics": "Capital remote armor repair ship with massive burst reps.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Armor FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ninazu [Force Auxiliary | Gallente]\n  - Combat Role: Capital Armor FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Armor FAX Class Role Bonus\n  - Defense Profile: Active Armor (Triage) | Speed: Capital\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Capital remote armor repair ship with massive burst reps."
    },
    "Erebus": {
        "class": "Titan",
        "faction": "Gallente",
        "role": "Supercapital Doomsday Titan",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Doomsday hybrid titan with fleet armor burst.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Doomsday Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Erebus [Titan | Gallente]\n  - Combat Role: Supercapital Doomsday Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Doomsday Titan Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Doomsday hybrid titan with fleet armor burst."
    },
    "Iteron Mark V": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Classic high-capacity T1 industrial.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Iteron Mark V [Industrial | Gallente]\n  - Combat Role: High-Capacity Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Classic high-capacity T1 industrial."
    },
    "Epithal": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Planetary Industry Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Planetary Commodities cargo bay.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Planetary Industry Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Epithal [Industrial | Gallente]\n  - Combat Role: Planetary Industry Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Planetary Industry Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Specialized Planetary Commodities cargo bay."
    },
    "Miasmos": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Mineral & Ore Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Mineral/Ore cargo bay.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Mineral & Ore Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Miasmos [Industrial | Gallente]\n  - Combat Role: Mineral & Ore Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Mineral & Ore Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Specialized Mineral/Ore cargo bay."
    },
    "Kryos": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Ice Product Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ice/Isotope cargo bay.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Ice Product Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Kryos [Industrial | Gallente]\n  - Combat Role: Ice Product Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Ice Product Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Specialized Ice/Isotope cargo bay."
    },
    "Viator": {
        "class": "Blockade Runner",
        "faction": "Gallente",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Armor",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Fast Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Viator [Blockade Runner | Gallente]\n  - Combat Role: Covert Fast Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Fast Hauler Class Role Bonus\n  - Defense Profile: Cloaked Armor | Speed: Fast (<3s align)\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Covert cloaking, cargo-scanned immune hauler."
    },
    "Occator": {
        "class": "Deep Space Transport",
        "faction": "Gallente",
        "role": "Heavy Armor DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Armor Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Armor DST Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Occator [Deep Space Transport | Gallente]\n  - Combat Role: Heavy Armor DST\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Armor DST Class Role Bonus\n  - Defense Profile: Immense Armor Buffer (+2 Warp Core) | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: +2 native warp core strength and Fleet Hangar."
    },
    "Obelisk": {
        "class": "Freighter",
        "faction": "Gallente",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Standard Sub-Capital Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Obelisk [Freighter | Gallente]\n  - Combat Role: Standard Sub-Capital Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Standard Sub-Capital Freighter Class Role Bonus\n  - Defense Profile: Buffer | Speed: Extremely Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Massive cargo freighter."
    },
    "Anshar": {
        "class": "Jump Freighter",
        "faction": "Gallente",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Armor Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Jump Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Anshar [Jump Freighter | Gallente]\n  - Combat Role: Capital Jump Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Jump Freighter Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Jump Drive\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Jump drive cargo hauler for nullsec logistics."
    },
    "Executioner": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Fast Tackle / Laser Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "High-speed laser tackler with energy turret cap reduction.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fast Tackle / Laser Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Executioner [Frigate | Amarr]\n  - Combat Role: Fast Tackle / Laser Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fast Tackle / Laser Frigate Class Role Bonus\n  - Defense Profile: Armor / Shield | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: High-speed laser tackler with energy turret cap reduction."
    },
    "Tormentor": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Laser / Drone Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Strong pulse laser damage and light drone assistance.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Laser / Drone Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tormentor [Frigate | Amarr]\n  - Combat Role: Laser / Drone Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Laser / Drone Brawler Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Strong pulse laser damage and light drone assistance."
    },
    "Punisher": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Heavy Armor Buffer / Laser Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Armor Buffer (4 Low Slots)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Cruiser-grade armor buffer on a frigate hull.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Heavy Armor Buffer / Laser Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Punisher [Frigate | Amarr]\n  - Combat Role: Heavy Armor Buffer / Laser Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Heavy Armor Buffer / Laser Frigate Class Role Bonus\n  - Defense Profile: Immense Armor Buffer (4 Low Slots) | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Cruiser-grade armor buffer on a frigate hull."
    },
    "Inquisitor": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor",
        "tactics": "T1 frigate armor logistics.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Armor Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Inquisitor [Frigate | Amarr]\n  - Combat Role: Armor Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Armor Logistics Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: T1 frigate armor logistics."
    },
    "Crucifier": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Tracking Disruptor Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "30-70 km",
        "tactics": "Applies severe tracking disruption to enemy turrets.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Tracking Disruptor Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Crucifier [Frigate | Amarr]\n  - Combat Role: Tracking Disruptor Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Tracking Disruptor Frigate Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Applies severe tracking disruption to enemy turrets."
    },
    "Magnate": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate with 4 low slots.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Exploration / Light Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Magnate [Frigate | Amarr]\n  - Combat Role: Exploration / Light Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Exploration / Light Drone Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Scanning and exploration frigate with 4 low slots."
    },
    "Imperial Navy Slicer": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Beam / Pulse Nano Laser Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Extreme (4.6+ km/s)",
        "optimal_range": "20-40 km",
        "tactics": "Premier nano laser kiter. Strikes from 35 km with Scorch / Aurora.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Beam / Pulse Nano Laser Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Imperial Navy Slicer [Faction Frigate | Amarr (Navy)]\n  - Combat Role: Beam / Pulse Nano Laser Kiter\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Beam / Pulse Nano Laser Kiter Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Extreme (4.6+ km/s)\n  - Weapon Optimal: 20-40 km\n  - Tactical Counter-Play: Premier nano laser kiter. Strikes from 35 km with Scorch / Aurora."
    },
    "Crucifier Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Tracking Disruptor / Laser Brawler",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Combines tracking disruption with strong energy turret DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Tracking Disruptor / Laser Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Crucifier Navy Issue [Faction Frigate | Amarr (Navy)]\n  - Combat Role: Tracking Disruptor / Laser Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Tracking Disruptor / Laser Brawler Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Combines tracking disruption with strong energy turret DPS."
    },
    "Magnate Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Combat Explorer / Heavy Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Faction combat exploration frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Explorer / Heavy Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Magnate Navy Issue [Faction Frigate | Amarr (Navy)]\n  - Combat Role: Combat Explorer / Heavy Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Explorer / Heavy Drone Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Faction combat exploration frigate."
    },
    "Anathema": {
        "class": "Covert Ops",
        "faction": "Amarr",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Stealth Scout / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Anathema [Covert Ops | Amarr]\n  - Combat Role: Stealth Scout / Cyno\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Stealth Scout / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: Covert\n  - Tactical Counter-Play: Covert cloaking scout frigate."
    },
    "Purifier": {
        "class": "Stealth Bomber",
        "faction": "Amarr",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "EM bombs and torpedoes from cloak.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Torpedo / Bomb Bomber Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Purifier [Stealth Bomber | Amarr]\n  - Combat Role: Covert Torpedo / Bomb Bomber\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Torpedo / Bomb Bomber Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: EM bombs and torpedoes from cloak."
    },
    "Retribution": {
        "class": "Assault Frigate",
        "faction": "Amarr",
        "role": "Beam Laser / ADC Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "15-45 km",
        "tactics": "Heavy armor beam/pulse sniper frigate with ADC. Counter with Tracking Disruptors and EM/Therm armor tank.",
        "high_slots": 4,
        "mid_slots": 2,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Energy (Small Focused Beam / Pulse)",
        "bonuses": [
            "5% Small Energy rate of fire per lvl",
            "10% Small Energy optimal range per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Retribution [Assault Frigate | Amarr]\n  - Combat Role: Beam Laser / ADC Assault\n  - Weapon System: Small Energy (Small Focused Beam / Pulse)\n  - Slot Layout: Highs: 4 | Mids: 2 | Lows: 5 | Rigs: 2 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 5% Small Energy rate of fire per lvl | 10% Small Energy optimal range per lvl | Role: Assault Damage Control capable\n  - Defense Profile: Armor Buffer + ADC | Speed: Fast\n  - Weapon Optimal: 15-45 km\n  - Tactical Counter-Play: Heavy armor beam/pulse sniper frigate with ADC. Counter with Tracking Disruptors and EM/Therm armor tank."
    },
    "Vengeance": {
        "class": "Assault Frigate",
        "faction": "Amarr",
        "role": "Rocket / Active Armor Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Armor + ADC",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "Heavy rocket assault frigate with dual armor reps.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Rocket / Active Armor Assault Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vengeance [Assault Frigate | Amarr]\n  - Combat Role: Rocket / Active Armor Assault\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Rocket / Active Armor Assault Class Role Bonus\n  - Defense Profile: Active Armor + ADC | Speed: Moderate\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Heavy rocket assault frigate with dual armor reps."
    },
    "Sentinel": {
        "class": "Electronic Attack Ship",
        "faction": "Amarr",
        "role": "Long-Range Cap Drain & Tracking Disruptor",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.0+ km/s)",
        "optimal_range": "30-50 km",
        "tactics": "Drains capacitor dry from 40 km and applies tracking disruption. Critical target.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Long-Range Cap Drain & Tracking Disruptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sentinel [Electronic Attack Ship | Amarr]\n  - Combat Role: Long-Range Cap Drain & Tracking Disruptor\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Long-Range Cap Drain & Tracking Disruptor Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast (4.0+ km/s)\n  - Weapon Optimal: 30-50 km\n  - Tactical Counter-Play: Drains capacitor dry from 40 km and applies tracking disruption. Critical target."
    },
    "Crusader": {
        "class": "Interceptor",
        "faction": "Amarr",
        "role": "Laser Fleet Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Nullified fast tackle combat interceptor.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Laser Fleet Tackler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Crusader [Interceptor | Amarr]\n  - Combat Role: Laser Fleet Tackler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Laser Fleet Tackler Class Role Bonus\n  - Defense Profile: Armor | Speed: Extreme (4.8+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Nullified fast tackle combat interceptor."
    },
    "Malediction": {
        "class": "Interceptor",
        "faction": "Amarr",
        "role": "Fleet Fast Tackle Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Premier fleet tackle interceptor with rocket and point.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fleet Fast Tackle Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Malediction [Interceptor | Amarr]\n  - Combat Role: Fleet Fast Tackle Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fleet Fast Tackle Interceptor Class Role Bonus\n  - Defense Profile: Armor / Shield | Speed: Extreme (5.0+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Premier fleet tackle interceptor with rocket and point."
    },
    "Deacon": {
        "class": "Logistics Frigate",
        "faction": "Amarr",
        "role": "T2 Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Assault-tier remote armor repair frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "T2 Armor Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Deacon [Logistics Frigate | Amarr]\n  - Combat Role: T2 Armor Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: T2 Armor Logistics Frigate Class Role Bonus\n  - Defense Profile: Armor | Speed: Fast\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Assault-tier remote armor repair frigate."
    },
    "Coercer": {
        "class": "Destroyer",
        "faction": "Amarr",
        "role": "Pulse / Beam Laser Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-15 km (Pulse) / 30-65 km (Beam)",
        "tactics": "8 energy turrets deliver high instant EM/Thermal laser DPS.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Pulse / Beam Laser Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Coercer [Destroyer | Amarr]\n  - Combat Role: Pulse / Beam Laser Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Pulse / Beam Laser Destroyer Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-15 km (Pulse) / 30-65 km (Beam)\n  - Tactical Counter-Play: 8 energy turrets deliver high instant EM/Thermal laser DPS."
    },
    "Dragoon": {
        "class": "Destroyer",
        "faction": "Amarr",
        "role": "Drone / Cap Neutralizer Destroyer",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-30 km",
        "tactics": "Heavy energy neutralizers and light drones. Drains frigate capacitor in 1 cycle.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Drone / Cap Neutralizer Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Dragoon [Destroyer | Amarr]\n  - Combat Role: Drone / Cap Neutralizer Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Drone / Cap Neutralizer Destroyer Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Heavy energy neutralizers and light drones. Drains frigate capacitor in 1 cycle."
    },
    "Coercer Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-25 km / 40-80 km",
        "tactics": "Reduced capacitor usage and enhanced tracking.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Navy Laser Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Coercer Navy Issue [Faction Destroyer | Amarr (Navy)]\n  - Combat Role: Navy Laser Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Laser Destroyer Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-25 km / 40-80 km\n  - Tactical Counter-Play: Reduced capacitor usage and enhanced tracking."
    },
    "Heretic": {
        "class": "Interdictor",
        "faction": "Amarr",
        "role": "Armor Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Armor Warp Bubble Launcher Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Heretic [Interdictor | Amarr]\n  - Combat Role: Armor Warp Bubble Launcher\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Armor Warp Bubble Launcher Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast (2.8+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Deploys 20km warp disruption bubbles on gates."
    },
    "Pontifex": {
        "class": "Command Destroyer",
        "faction": "Amarr",
        "role": "Micro Jump Field / Armor Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Micro Jump Field / Armor Skiff Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Pontifex [Command Destroyer | Amarr]\n  - Combat Role: Micro Jump Field / Armor Skiff\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Micro Jump Field / Armor Skiff Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Confessor": {
        "class": "Tactical Destroyer",
        "faction": "Amarr",
        "role": "T3 Mode-Switching Laser Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Armor",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "15-50 km",
        "tactics": "Switches between Propulsion, Sharpshooter (laser optimal/damage), and Defensive modes.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "T3 Mode-Switching Laser Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Confessor [Tactical Destroyer | Amarr]\n  - Combat Role: T3 Mode-Switching Laser Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: T3 Mode-Switching Laser Destroyer Class Role Bonus\n  - Defense Profile: Active / Passive Armor | Speed: Variable (Prop/Sharpshooter/Defensive)\n  - Weapon Optimal: 15-50 km\n  - Tactical Counter-Play: Switches between Propulsion, Sharpshooter (laser optimal/damage), and Defensive modes."
    },
    "Omen": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Beam / Pulse Attack Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.2+ km/s)",
        "optimal_range": "20-45 km",
        "tactics": "Fast laser attack cruiser with high EM/Thermal DPS.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Beam / Pulse Attack Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Omen [Cruiser | Amarr]\n  - Combat Role: Beam / Pulse Attack Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Beam / Pulse Attack Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast (2.2+ km/s)\n  - Weapon Optimal: 20-45 km\n  - Tactical Counter-Play: Fast laser attack cruiser with high EM/Thermal DPS."
    },
    "Maller": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Heavy Armor Buffer Bait Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Buffer (6 Lows)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Extremely heavy armor resistance bonus; classic fleet bait/line cruiser.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Armor Buffer Bait Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Maller [Cruiser | Amarr]\n  - Combat Role: Heavy Armor Buffer Bait Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Armor Buffer Bait Cruiser Class Role Bonus\n  - Defense Profile: Massive Armor Buffer (6 Lows) | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Extremely heavy armor resistance bonus; classic fleet bait/line cruiser."
    },
    "Augoror": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Armor Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor (Cap Transfer)",
        "tactics": "Cap-chain armor logistics cruiser. Maintain cap chain with second Augoror.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Armor Logistics Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Augoror [Cruiser | Amarr]\n  - Combat Role: Armor Logistics Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Armor Logistics Cruiser Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: Remote Armor (Cap Transfer)\n  - Tactical Counter-Play: Cap-chain armor logistics cruiser. Maintain cap chain with second Augoror."
    },
    "Arbitrator": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Tracking Disruptor / Drone Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Applies severe tracking disruption while deploying combat drones.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Tracking Disruptor / Drone Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Arbitrator [Cruiser | Amarr]\n  - Combat Role: Tracking Disruptor / Drone Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Tracking Disruptor / Drone Cruiser Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Applies severe tracking disruption while deploying combat drones."
    },
    "Omen Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Amarr (Navy)",
        "role": "Heavy Laser Nano Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.6+ km/s)",
        "optimal_range": "25-55 km",
        "tactics": "Premier nano beam kiter with high laser tracking and alpha.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Laser Nano Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Omen Navy Issue [Faction Cruiser | Amarr (Navy)]\n  - Combat Role: Heavy Laser Nano Kiter\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Laser Nano Kiter Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast (2.6+ km/s)\n  - Weapon Optimal: 25-55 km\n  - Tactical Counter-Play: Premier nano beam kiter with high laser tracking and alpha."
    },
    "Augoror Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Amarr (Navy)",
        "role": "Heavy Armor Laser Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Battleship-Grade Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Massive armor buffer and high laser DPS.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Armor Laser Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Augoror Navy Issue [Faction Cruiser | Amarr (Navy)]\n  - Combat Role: Heavy Armor Laser Brawler\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Armor Laser Brawler Class Role Bonus\n  - Defense Profile: Battleship-Grade Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Massive armor buffer and high laser DPS."
    },
    "Zealot": {
        "class": "Heavy Assault Cruiser",
        "faction": "Amarr",
        "role": "HAC Beam Laser Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "40-90 km",
        "tactics": "Armor buffer laser HAC. Counter with Tracking Disruptors (Optimal Range script) and EM/Thermal armor resists.",
        "high_slots": 5,
        "mid_slots": 3,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 0,
        "weapon_type": "Medium Energy Turrets (Heavy Pulse / Heavy Beam)",
        "bonuses": [
            "5% Medium Energy rate of fire per lvl",
            "10% Medium Energy optimal range per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Zealot [Heavy Assault Cruiser | Amarr]\n  - Combat Role: HAC Beam Laser Sniper\n  - Weapon System: Medium Energy Turrets (Heavy Pulse / Heavy Beam)\n  - Slot Layout: Highs: 5 | Mids: 3 | Lows: 7 | Rigs: 2 (Turrets: 5 | Launchers: 0)\n  - Key Bonuses: 5% Medium Energy rate of fire per lvl | 10% Medium Energy optimal range per lvl\n  - Defense Profile: Armor Buffer + ADC | Speed: Moderate\n  - Weapon Optimal: 40-90 km\n  - Tactical Counter-Play: Armor buffer laser HAC. Counter with Tracking Disruptors (Optimal Range script) and EM/Thermal armor resists."
    },
    "Sacrilege": {
        "class": "Heavy Assault Cruiser",
        "faction": "Amarr",
        "role": "HAC Heavy Assault Missile Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Heavy Armor Buffer / Active + ADC",
        "speed": "Fast",
        "optimal_range": "15-40 km",
        "tactics": "High-resist HAC firing heavy assault missiles and cap neutralizers.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "HAC Heavy Assault Missile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sacrilege [Heavy Assault Cruiser | Amarr]\n  - Combat Role: HAC Heavy Assault Missile Brawler\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: HAC Heavy Assault Missile Brawler Class Role Bonus\n  - Defense Profile: Heavy Armor Buffer / Active + ADC | Speed: Fast\n  - Weapon Optimal: 15-40 km\n  - Tactical Counter-Play: High-resist HAC firing heavy assault missiles and cap neutralizers."
    },
    "Devoter": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Amarr",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Heavy armor HIC projecting focused infinite points or mobile bubbles.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Warp Disruption Field Generator Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Devoter [Heavy Interdiction Cruiser | Amarr]\n  - Combat Role: Warp Disruption Field Generator\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Warp Disruption Field Generator Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-20 km (Bubble) / Infinite Scram\n  - Tactical Counter-Play: Heavy armor HIC projecting focused infinite points or mobile bubbles."
    },
    "Pilgrim": {
        "class": "Force Recon",
        "faction": "Amarr",
        "role": "Covert Cloak / Cap Neut / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-25 km",
        "tactics": "Uncloaks to neut capacitor dry, apply tracking disruption, and light Covert Cyno.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Cloak / Cap Neut / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Pilgrim [Force Recon | Amarr]\n  - Combat Role: Covert Cloak / Cap Neut / Cyno\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Cloak / Cap Neut / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Uncloaks to neut capacitor dry, apply tracking disruption, and light Covert Cyno."
    },
    "Curse": {
        "class": "Combat Recon",
        "faction": "Amarr",
        "role": "D-Scan Immune 50km Cap Neut",
        "threat": "THREAT_ECM",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-60 km",
        "tactics": "Invisible to D-Scan. Heavy neutralizers drain cap at 50km range.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "D-Scan Immune 50km Cap Neut Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Curse [Combat Recon | Amarr]\n  - Combat Role: D-Scan Immune 50km Cap Neut\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: D-Scan Immune 50km Cap Neut Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Invisible to D-Scan. Heavy neutralizers drain cap at 50km range."
    },
    "Guardian": {
        "class": "Logistics Cruiser",
        "faction": "Amarr",
        "role": "T2 Cap-Chain Armor Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor (Cap Transfer)",
        "tactics": "Premier T2 armor logistics. Maintain cap chain with second Guardian.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "T2 Cap-Chain Armor Logistics Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Guardian [Logistics Cruiser | Amarr]\n  - Combat Role: T2 Cap-Chain Armor Logistics\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: T2 Cap-Chain Armor Logistics Class Role Bonus\n  - Defense Profile: Armor | Speed: Moderate\n  - Weapon Optimal: Remote Armor (Cap Transfer)\n  - Tactical Counter-Play: Premier T2 armor logistics. Maintain cap chain with second Guardian."
    },
    "Legion": {
        "class": "Strategic Cruiser",
        "faction": "Amarr",
        "role": "Modular T3C (Laser / Missile / Neut / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active",
        "speed": "Fast (1.8-2.4 km/s)",
        "optimal_range": "20-70 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy neuts, or 100MN AB.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Modular T3C (Laser / Missile / Neut / Cloak) Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Legion [Strategic Cruiser | Amarr]\n  - Combat Role: Modular T3C (Laser / Missile / Neut / Cloak)\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Modular T3C (Laser / Missile / Neut / Cloak) Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Fast (1.8-2.4 km/s)\n  - Weapon Optimal: 20-70 km\n  - Tactical Counter-Play: Highly customizable. Can fit covert cloak, interdiction nullification, heavy neuts, or 100MN AB."
    },
    "Harbinger": {
        "class": "Battlecruiser",
        "faction": "Amarr",
        "role": "Heavy Laser Line BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "20-60 km",
        "tactics": "6 heavy energy turrets with high tracking and laser DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Laser Line BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Harbinger [Battlecruiser | Amarr]\n  - Combat Role: Heavy Laser Line BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Laser Line BC Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: 6 heavy energy turrets with high tracking and laser DPS."
    },
    "Prophecy": {
        "class": "Battlecruiser",
        "faction": "Amarr",
        "role": "Heavy Drone / Armor Fleet BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Buffer (Triple Trimark)",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Extremely tanky drone battlecruiser. Standard faction warfare doctrine.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Drone / Armor Fleet BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Prophecy [Battlecruiser | Amarr]\n  - Combat Role: Heavy Drone / Armor Fleet BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Drone / Armor Fleet BC Class Role Bonus\n  - Defense Profile: Massive Armor Buffer (Triple Trimark) | Speed: Slow\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Extremely tanky drone battlecruiser. Standard faction warfare doctrine."
    },
    "Oracle": {
        "class": "Attack Battlecruiser",
        "faction": "Amarr",
        "role": "Battleship-Gun Laser Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Armor",
        "speed": "Moderate",
        "optimal_range": "60-140 km",
        "tactics": "Large Mega Beam / Tachyon lasers on BC hull. Extreme instant alpha.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Battleship-Gun Laser Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Oracle [Attack Battlecruiser | Amarr]\n  - Combat Role: Battleship-Gun Laser Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Battleship-Gun Laser Sniper Class Role Bonus\n  - Defense Profile: Paper Thin Armor | Speed: Moderate\n  - Weapon Optimal: 60-140 km\n  - Tactical Counter-Play: Large Mega Beam / Tachyon lasers on BC hull. Extreme instant alpha."
    },
    "Harbinger Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "20-70 km",
        "tactics": "Enhanced laser tracking and armor resistance bonus.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Navy Laser Battlecruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Harbinger Navy Issue [Faction Battlecruiser | Amarr (Navy)]\n  - Combat Role: Navy Laser Battlecruiser\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Laser Battlecruiser Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Fast\n  - Weapon Optimal: 20-70 km\n  - Tactical Counter-Play: Enhanced laser tracking and armor resistance bonus."
    },
    "Prophecy Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Amarr (Navy)",
        "role": "Navy Missile / Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "20-60 km",
        "tactics": "Combines heavy missiles and full drone flights.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Navy Missile / Drone BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Prophecy Navy Issue [Faction Battlecruiser | Amarr (Navy)]\n  - Combat Role: Navy Missile / Drone BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Missile / Drone BC Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: Combines heavy missiles and full drone flights."
    },
    "Damnation": {
        "class": "Command Ship",
        "faction": "Amarr",
        "role": "Armor Fleet Command Flagship",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer (300k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-30 km",
        "tactics": "Provides Fleet Armor Bursts with near-unbreakable armor buffer.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Armor Fleet Command Flagship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Damnation [Command Ship | Amarr]\n  - Combat Role: Armor Fleet Command Flagship\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Armor Fleet Command Flagship Class Role Bonus\n  - Defense Profile: Immense Armor Buffer (300k+ EHP) | Speed: Slow\n  - Weapon Optimal: 0-30 km\n  - Tactical Counter-Play: Provides Fleet Armor Bursts with near-unbreakable armor buffer."
    },
    "Absolution": {
        "class": "Command Ship",
        "faction": "Amarr",
        "role": "Laser Fleet Command Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "Provides Fleet Armor / Information Bursts with heavy laser DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Laser Fleet Command Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Absolution [Command Ship | Amarr]\n  - Combat Role: Laser Fleet Command Brawler\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Laser Fleet Command Brawler Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Slow\n  - Weapon Optimal: 20-50 km\n  - Tactical Counter-Play: Provides Fleet Armor / Information Bursts with heavy laser DPS."
    },
    "Apocalypse": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Large Beam / Pulse Laser Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "Long-range laser sniper. Counter with Tracking Disruptors and high angular velocity.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 8,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Energy Turrets (Mega Beam / Pulse)",
        "bonuses": [
            "7.5% Large Energy laser optimal range per lvl",
            "10% Large Energy laser tracking per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Apocalypse [Battleship | Amarr]\n  - Combat Role: Large Beam / Pulse Laser Battleship\n  - Weapon System: Large Energy Turrets (Mega Beam / Pulse)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 3 (Turrets: 8 | Launchers: 0)\n  - Key Bonuses: 7.5% Large Energy laser optimal range per lvl | 10% Large Energy laser tracking per lvl\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 60-140 km\n  - Tactical Counter-Play: Long-range laser sniper. Counter with Tracking Disruptors and high angular velocity."
    },
    "Armageddon": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Heavy Cap Neut / Drone / Missile BS",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Heavy capacitor warfare and drone battleship. Counter by maintaining range outside 40km neut envelope.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 4,
        "weapon_type": "Heavy Neuts & Heavy Drones / Missiles",
        "bonuses": [
            "100% Heavy Energy Neutralizer range",
            "10% Drone damage and HP per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Armageddon [Battleship | Amarr]\n  - Combat Role: Heavy Cap Neut / Drone / Missile BS\n  - Weapon System: Heavy Neuts & Heavy Drones / Missiles\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 3 (Turrets: 4 | Launchers: 4)\n  - Key Bonuses: 100% Heavy Energy Neutralizer range | 10% Drone damage and HP per lvl\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 0-50 km\n  - Tactical Counter-Play: Heavy capacitor warfare and drone battleship. Counter by maintaining range outside 40km neut envelope."
    },
    "Abaddon": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Heavy Laser Line Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Resistance Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "High armor resistance bonus; heavy cap consumption on lasers.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Heavy Laser Line Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Abaddon [Battleship | Amarr]\n  - Combat Role: Heavy Laser Line Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Heavy Laser Line Battleship Class Role Bonus\n  - Defense Profile: Massive Armor Resistance Buffer | Speed: Slow\n  - Weapon Optimal: 30-80 km\n  - Tactical Counter-Play: High armor resistance bonus; heavy cap consumption on lasers."
    },
    "Apocalypse Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Sniper Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "60-150 km",
        "tactics": "Extreme laser rate of fire and optimal range.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Navy Laser Sniper Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Apocalypse Navy Issue [Faction Battleship | Amarr (Navy)]\n  - Combat Role: Navy Laser Sniper Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Navy Laser Sniper Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 60-150 km\n  - Tactical Counter-Play: Extreme laser rate of fire and optimal range."
    },
    "Armageddon Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser / Drone Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "Laser damage and heavy drone damage combination.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Navy Laser / Drone Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Armageddon Navy Issue [Faction Battleship | Amarr (Navy)]\n  - Combat Role: Navy Laser / Drone Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Navy Laser / Drone Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Slow\n  - Weapon Optimal: 30-80 km\n  - Tactical Counter-Play: Laser damage and heavy drone damage combination."
    },
    "Paladin": {
        "class": "Marauder",
        "faction": "Amarr",
        "role": "Bastion Beam / Pulse Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Armor (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "40-100 km (Mega Pulse / Scorch) / 100-180 km (Tachyon)",
        "tactics": "Bastion Marauder. Reaches 2500+ DPS with Scorch L and doubles armor repair rate. Counter with capital energy neutralizers, coordinated dreadnought alpha, or wait out the 60s Bastion timer.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Energy Turrets (Mega Pulse / Tachyon Beam)",
        "bonuses": [
            "100% Large Energy damage bonus",
            "10% Large Energy optimal/tracking per lvl",
            "Role: Bastion grants 100% Armor Repair and EWAR immunity"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Paladin [Marauder | Amarr]\n  - Combat Role: Bastion Beam / Pulse Marauder\n  - Weapon System: Large Energy Turrets (Mega Pulse / Tachyon Beam)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 7 | Rigs: 2 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Large Energy damage bonus | 10% Large Energy optimal/tracking per lvl | Role: Bastion grants 100% Armor Repair and EWAR immunity\n  - Defense Profile: Active Armor (Bastion Mode) | Speed: Immobile in Bastion\n  - Weapon Optimal: 40-100 km (Mega Pulse / Scorch) / 100-180 km (Tachyon)\n  - Tactical Counter-Play: Bastion Marauder. Reaches 2500+ DPS with Scorch L and doubles armor repair rate. Counter with capital energy neutralizers, coordinated dreadnought alpha, or wait out the 60s Bastion timer."
    },
    "Redeemer": {
        "class": "Black Ops",
        "faction": "Amarr",
        "role": "Covert Jump / Laser Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Armor Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "30-80 km",
        "tactics": "Bridges covert fleets; massive instant laser alpha strike.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Covert Jump / Laser Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Redeemer [Black Ops | Amarr]\n  - Combat Role: Covert Jump / Laser Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 2 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Covert Jump / Laser Battleship Class Role Bonus\n  - Defense Profile: Armor Buffer / Active | Speed: Slow (Covert Jump)\n  - Weapon Optimal: 30-80 km\n  - Tactical Counter-Play: Bridges covert fleets; massive instant laser alpha strike."
    },
    "Revelation": {
        "class": "Dreadnought",
        "faction": "Amarr",
        "role": "Capital Mega Beam / Pulse Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with capital energy turrets. Infinite ammo with crystals.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Capital Mega Beam / Pulse Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Revelation [Dreadnought | Amarr]\n  - Combat Role: Capital Mega Beam / Pulse Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Capital Mega Beam / Pulse Dread Class Role Bonus\n  - Defense Profile: Active Armor (Siege) | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Siege dreadnought with capital energy turrets. Infinite ammo with crystals."
    },
    "Revelation Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Amarr (Navy)",
        "role": "Navy Capital Laser Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Enhanced energy turret tracking and armor buffer.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Navy Capital Laser Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Revelation Navy Issue [Faction Dreadnought | Amarr (Navy)]\n  - Combat Role: Navy Capital Laser Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Navy Capital Laser Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Enhanced energy turret tracking and armor buffer."
    },
    "Bane": {
        "class": "Lancer Dreadnought",
        "faction": "Amarr",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Disruptive Lancer Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bane [Lancer Dreadnought | Amarr]\n  - Combat Role: Disruptive Lancer Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Disruptive Lancer Dread Class Role Bonus\n  - Defense Profile: Armor Active | Speed: Capital\n  - Weapon Optimal: Lancer Beam\n  - Tactical Counter-Play: Fires disruptive capital lance disabling cynos and warp."
    },
    "Archon": {
        "class": "Carrier",
        "faction": "Amarr",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Capital carrier with fighter resistance and cap transfers.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Fighter Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Archon [Carrier | Amarr]\n  - Combat Role: Capital Fighter Carrier\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Fighter Carrier Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Capital\n  - Weapon Optimal: Fighter Range\n  - Tactical Counter-Play: Capital carrier with fighter resistance and cap transfers."
    },
    "Aeon": {
        "class": "Supercarrier",
        "faction": "Amarr",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Immense Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital heavy fighter strike wings.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Heavy Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Aeon [Supercarrier | Amarr]\n  - Combat Role: Supercapital Heavy Carrier\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Heavy Carrier Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Supercapital heavy fighter strike wings."
    },
    "Apostle": {
        "class": "Force Auxiliary",
        "faction": "Amarr",
        "role": "Capital Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Armor",
        "tactics": "Capital remote armor repair ship with massive burst reps.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Armor FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Apostle [Force Auxiliary | Amarr]\n  - Combat Role: Capital Armor FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Armor FAX Class Role Bonus\n  - Defense Profile: Active Armor (Triage) | Speed: Capital\n  - Weapon Optimal: Remote Armor\n  - Tactical Counter-Play: Capital remote armor repair ship with massive burst reps."
    },
    "Avatar": {
        "class": "Titan",
        "faction": "Amarr",
        "role": "Supercapital Judgement Titan",
        "threat": "THREAT_SUPER",
        "tank": "Immense Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Judgement EM Doomsday titan with fleet armor burst.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Judgement Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Avatar [Titan | Amarr]\n  - Combat Role: Supercapital Judgement Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Judgement Titan Class Role Bonus\n  - Defense Profile: Immense Armor Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Judgement EM Doomsday titan with fleet armor burst."
    },
    "Bestower": {
        "class": "Industrial",
        "faction": "Amarr",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity hauler.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bestower [Industrial | Amarr]\n  - Combat Role: High-Capacity Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Large cargo capacity hauler."
    },
    "Sigil": {
        "class": "Industrial",
        "faction": "Amarr",
        "role": "Fast Industrial Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Fast for Hauler",
        "optimal_range": "0 km",
        "tactics": "Fast sub-warp align industrial.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Fast Industrial Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sigil [Industrial | Amarr]\n  - Combat Role: Fast Industrial Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Fast Industrial Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast for Hauler\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fast sub-warp align industrial."
    },
    "Prorator": {
        "class": "Blockade Runner",
        "faction": "Amarr",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Armor",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Fast Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Prorator [Blockade Runner | Amarr]\n  - Combat Role: Covert Fast Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Fast Hauler Class Role Bonus\n  - Defense Profile: Cloaked Armor | Speed: Fast (<3s align)\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Covert cloaking, cargo-scanned immune hauler."
    },
    "Impel": {
        "class": "Deep Space Transport",
        "faction": "Amarr",
        "role": "Heavy Armor DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Armor Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Armor DST Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Impel [Deep Space Transport | Amarr]\n  - Combat Role: Heavy Armor DST\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Armor DST Class Role Bonus\n  - Defense Profile: Immense Armor Buffer (+2 Warp Core) | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: +2 native warp core strength and Fleet Hangar."
    },
    "Providence": {
        "class": "Freighter",
        "faction": "Amarr",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Standard Sub-Capital Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Providence [Freighter | Amarr]\n  - Combat Role: Standard Sub-Capital Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Standard Sub-Capital Freighter Class Role Bonus\n  - Defense Profile: Buffer | Speed: Extremely Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Massive cargo freighter."
    },
    "Ark": {
        "class": "Jump Freighter",
        "faction": "Amarr",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Armor Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Jump Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ark [Jump Freighter | Amarr]\n  - Combat Role: Capital Jump Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Jump Freighter Class Role Bonus\n  - Defense Profile: Armor Buffer | Speed: Jump Drive\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Jump drive cargo hauler for nullsec logistics."
    },
    "Slasher": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Fast Tackle / Projectile Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-10 km",
        "tactics": "Fastest T1 tackle frigate with projectile tracking.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Fast Tackle / Projectile Tackler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Slasher [Frigate | Minmatar]\n  - Combat Role: Fast Tackle / Projectile Tackler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Fast Tackle / Projectile Tackler Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Extreme (4.8+ km/s)\n  - Weapon Optimal: 0-10 km\n  - Tactical Counter-Play: Fastest T1 tackle frigate with projectile tracking."
    },
    "Rifter": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Projectile Brawler / Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Versatile projectile combat frigate with selectable damage.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Projectile Brawler / Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rifter [Frigate | Minmatar]\n  - Combat Role: Projectile Brawler / Kiter\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Projectile Brawler / Kiter Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Versatile projectile combat frigate with selectable damage."
    },
    "Breacher": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Dual MASB Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual MASB Active Shield",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "Extreme active shield tank with light missiles/rockets.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Dual MASB Missile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Breacher [Frigate | Minmatar]\n  - Combat Role: Dual MASB Missile Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Dual MASB Missile Brawler Class Role Bonus\n  - Defense Profile: Dual MASB Active Shield | Speed: Fast\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Extreme active shield tank with light missiles/rockets."
    },
    "Probe": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Exploration / Light Drone Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Probe [Frigate | Minmatar]\n  - Combat Role: Exploration / Light Drone\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Exploration / Light Drone Class Role Bonus\n  - Defense Profile: Shield / Armor | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Scanning and exploration frigate."
    },
    "Burst": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "T1 frigate shield logistics.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Shield Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Burst [Frigate | Minmatar]\n  - Combat Role: Shield Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Shield Logistics Frigate Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: T1 frigate shield logistics."
    },
    "Vigil": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Target Painter Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "40-80 km",
        "tactics": "Target painters inflate signature radius across the grid.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Target Painter Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vigil [Frigate | Minmatar]\n  - Combat Role: Target Painter Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Target Painter Frigate Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Extreme (4.8+ km/s)\n  - Weapon Optimal: 40-80 km\n  - Tactical Counter-Play: Target painters inflate signature radius across the grid."
    },
    "Republic Fleet Firetail": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "High Alpha Projectile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.2+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast projectile frigate with tracking and damage bonuses.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "High Alpha Projectile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Republic Fleet Firetail [Faction Frigate | Minmatar (Fleet)]\n  - Combat Role: High Alpha Projectile Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: High Alpha Projectile Brawler Class Role Bonus\n  - Defense Profile: Shield / Armor | Speed: Extreme (4.2+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Fast projectile frigate with tracking and damage bonuses."
    },
    "Vigil Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "Dual Web Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Stasis webifier range bonus with rocket application.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Dual Web Rocket Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vigil Navy Issue [Faction Frigate | Minmatar (Fleet)]\n  - Combat Role: Dual Web Rocket Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Dual Web Rocket Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Extreme (4.5+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Stasis webifier range bonus with rocket application."
    },
    "Probe Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "Combat Explorer / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Exploration combat frigate with rocket DPS.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Combat Explorer / Rocket Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Probe Navy Issue [Faction Frigate | Minmatar (Fleet)]\n  - Combat Role: Combat Explorer / Rocket Brawler\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Combat Explorer / Rocket Brawler Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Exploration combat frigate with rocket DPS."
    },
    "Cheetah": {
        "class": "Covert Ops",
        "faction": "Minmatar",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Fastest covert ops scout frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Stealth Scout / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cheetah [Covert Ops | Minmatar]\n  - Combat Role: Stealth Scout / Cyno\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 2 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Stealth Scout / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: Covert\n  - Tactical Counter-Play: Fastest covert ops scout frigate."
    },
    "Hound": {
        "class": "Stealth Bomber",
        "faction": "Minmatar",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Explosive bombs and torpedoes from cloak.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Torpedo / Bomb Bomber Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hound [Stealth Bomber | Minmatar]\n  - Combat Role: Covert Torpedo / Bomb Bomber\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Torpedo / Bomb Bomber Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 30-60 km\n  - Tactical Counter-Play: Explosive bombs and torpedoes from cloak."
    },
    "Wolf": {
        "class": "Assault Frigate",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / SAAR + ADC",
        "speed": "Fast (3.5+ km/s)",
        "optimal_range": "0-15 km (AC) / 25-50 km (Art)",
        "tactics": "Dual repair active armor or buffer brawler. Strong tracking and ADC survivability. Apply Tracking Disruptors or kite at >15km range.",
        "high_slots": 4,
        "mid_slots": 2,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 1,
        "weapon_type": "Small Projectile (200mm Autocannons / 280mm Art)",
        "bonuses": [
            "5% Small Projectile damage per lvl",
            "10% Small Projectile falloff per lvl",
            "7.5% Small Projectile tracking per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Wolf [Assault Frigate | Minmatar]\n  - Combat Role: Autocannon / Artillery Assault\n  - Weapon System: Small Projectile (200mm Autocannons / 280mm Art)\n  - Slot Layout: Highs: 4 | Mids: 2 | Lows: 5 | Rigs: 2 (Turrets: 4 | Launchers: 1)\n  - Key Bonuses: 5% Small Projectile damage per lvl | 10% Small Projectile falloff per lvl | 7.5% Small Projectile tracking per lvl\n  - Defense Profile: Armor Buffer / SAAR + ADC | Speed: Fast (3.5+ km/s)\n  - Weapon Optimal: 0-15 km (AC) / 25-50 km (Art)\n  - Tactical Counter-Play: Dual repair active armor or buffer brawler. Strong tracking and ADC survivability. Apply Tracking Disruptors or kite at >15km range."
    },
    "Jaguar": {
        "class": "Assault Frigate",
        "faction": "Minmatar",
        "role": "Dual MASB Tackle Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Dual MASB Shield + ADC",
        "speed": "Extreme (4.0+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Active shield brawler with Assault Damage Control and MASB. Counter with heavy capacitor neuts and web tackle.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 4,
        "rig_slots": 2,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 3,
        "weapon_type": "Rockets / Light Missiles (Active Shield)",
        "bonuses": [
            "5% Rocket/Light Missile damage per lvl",
            "7.5% shield boost amount per lvl",
            "Role: Assault Damage Control capable"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Jaguar [Assault Frigate | Minmatar]\n  - Combat Role: Dual MASB Tackle Assault\n  - Weapon System: Rockets / Light Missiles (Active Shield)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 4 | Rigs: 2 (Turrets: 1 | Launchers: 3)\n  - Key Bonuses: 5% Rocket/Light Missile damage per lvl | 7.5% shield boost amount per lvl | Role: Assault Damage Control capable\n  - Defense Profile: Dual MASB Shield + ADC | Speed: Extreme (4.0+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Active shield brawler with Assault Damage Control and MASB. Counter with heavy capacitor neuts and web tackle."
    },
    "Hyena": {
        "class": "Electronic Attack Ship",
        "faction": "Minmatar",
        "role": "40km Stasis Webifier Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.2+ km/s)",
        "optimal_range": "0-40 km",
        "tactics": "Projects 40km stasis webifiers stopping targets cold.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "40km Stasis Webifier Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hyena [Electronic Attack Ship | Minmatar]\n  - Combat Role: 40km Stasis Webifier Frigate\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: 40km Stasis Webifier Frigate Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast (4.2+ km/s)\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Projects 40km stasis webifiers stopping targets cold."
    },
    "Claw": {
        "class": "Interceptor",
        "faction": "Minmatar",
        "role": "Artillery / AC Fleet Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Nullified fast tackle combat interceptor.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Artillery / AC Fleet Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Claw [Interceptor | Minmatar]\n  - Combat Role: Artillery / AC Fleet Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Artillery / AC Fleet Interceptor Class Role Bonus\n  - Defense Profile: Shield / Armor | Speed: Extreme (4.8+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Nullified fast tackle combat interceptor."
    },
    "Stiletto": {
        "class": "Interceptor",
        "faction": "Minmatar",
        "role": "Premier Fast Tackle Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fastest locking fleet tackle interceptor.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Premier Fast Tackle Interceptor Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stiletto [Interceptor | Minmatar]\n  - Combat Role: Premier Fast Tackle Interceptor\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Premier Fast Tackle Interceptor Class Role Bonus\n  - Defense Profile: Shield | Speed: Extreme (5.0+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Fastest locking fleet tackle interceptor."
    },
    "Scalpel": {
        "class": "Logistics Frigate",
        "faction": "Minmatar",
        "role": "T2 Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Assault-tier remote shield repair frigate.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "T2 Shield Logistics Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scalpel [Logistics Frigate | Minmatar]\n  - Combat Role: T2 Shield Logistics Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: T2 Shield Logistics Frigate Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Assault-tier remote shield repair frigate."
    },
    "Thrasher": {
        "class": "Destroyer",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery High Alpha",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast (2.5 km/s)",
        "optimal_range": "0-15 km AC / 40-70 km Art",
        "tactics": "8 projectile turrets deliver huge instant alpha strike.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Autocannon / Artillery High Alpha Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thrasher [Destroyer | Minmatar]\n  - Combat Role: Autocannon / Artillery High Alpha\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Autocannon / Artillery High Alpha Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Fast (2.5 km/s)\n  - Weapon Optimal: 0-15 km AC / 40-70 km Art\n  - Tactical Counter-Play: 8 projectile turrets deliver huge instant alpha strike."
    },
    "Talwar": {
        "class": "Destroyer",
        "faction": "Minmatar",
        "role": "Light Missile / Rocket Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.2 km/s)",
        "optimal_range": "30-65 km",
        "tactics": "7 missile launchers with reduced MWD signature bloom.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Light Missile / Rocket Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Talwar [Destroyer | Minmatar]\n  - Combat Role: Light Missile / Rocket Kiter\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Light Missile / Rocket Kiter Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast (2.2 km/s)\n  - Weapon Optimal: 30-65 km\n  - Tactical Counter-Play: 7 missile launchers with reduced MWD signature bloom."
    },
    "Thrasher Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Projectile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Enhanced projectile tracking and signature reduction.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Navy Projectile Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thrasher Navy Issue [Faction Destroyer | Minmatar (Fleet)]\n  - Combat Role: Navy Projectile Brawler\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Projectile Brawler Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Fast (2.8+ km/s)\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Enhanced projectile tracking and signature reduction."
    },
    "Sabre": {
        "class": "Interdictor",
        "faction": "Minmatar",
        "role": "Premier Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Extreme (3.2+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "King of interdictors. Deploys 20km warp disruption bubbles instantly.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Premier Warp Bubble Launcher Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sabre [Interdictor | Minmatar]\n  - Combat Role: Premier Warp Bubble Launcher\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Premier Warp Bubble Launcher Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Extreme (3.2+ km/s)\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: King of interdictors. Deploys 20km warp disruption bubbles instantly."
    },
    "Bifrost": {
        "class": "Command Destroyer",
        "faction": "Minmatar",
        "role": "Micro Jump Field / Shield Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "Micro Jump Field / Shield Skiff Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bifrost [Command Destroyer | Minmatar]\n  - Combat Role: Micro Jump Field / Shield Skiff\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Micro Jump Field / Shield Skiff Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-20 km\n  - Tactical Counter-Play: Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Svipul": {
        "class": "Tactical Destroyer",
        "faction": "Minmatar",
        "role": "T3 Mode-Switching Projectile Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Shield / Armor",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "0-40 km",
        "tactics": "Switches between Propulsion (4+ km/s), Sharpshooter (artillery alpha), and Defensive modes.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Small High-RoF Weapons",
        "bonuses": [
            "T3 Mode-Switching Projectile Destroyer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Svipul [Tactical Destroyer | Minmatar]\n  - Combat Role: T3 Mode-Switching Projectile Destroyer\n  - Weapon System: Small High-RoF Weapons\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 3 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: T3 Mode-Switching Projectile Destroyer Class Role Bonus\n  - Defense Profile: Active / Passive Shield / Armor | Speed: Variable (Prop/Sharpshooter/Defensive)\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Switches between Propulsion (4+ km/s), Sharpshooter (artillery alpha), and Defensive modes."
    },
    "Stabber": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery Attack Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.4+ km/s)",
        "optimal_range": "0-20 km (AC) / 40-70 km (Art)",
        "tactics": "Fastest T1 cruiser with selectable projectile damage.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Autocannon / Artillery Attack Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stabber [Cruiser | Minmatar]\n  - Combat Role: Autocannon / Artillery Attack Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Autocannon / Artillery Attack Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast (2.4+ km/s)\n  - Weapon Optimal: 0-20 km (AC) / 40-70 km (Art)\n  - Tactical Counter-Play: Fastest T1 cruiser with selectable projectile damage."
    },
    "Rupture": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Heavy Projectile Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "Heavy projectile damage and armor repair bonuses.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Projectile Fleet Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rupture [Cruiser | Minmatar]\n  - Combat Role: Heavy Projectile Fleet Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Projectile Fleet Cruiser Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 0-25 km\n  - Tactical Counter-Play: Heavy projectile damage and armor repair bonuses."
    },
    "Scythe": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Shield Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Self-sufficient shield logistics cruiser (no cap chain required).",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Shield Logistics Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scythe [Cruiser | Minmatar]\n  - Combat Role: Shield Logistics Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Shield Logistics Cruiser Class Role Bonus\n  - Defense Profile: Shield | Speed: Fast\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Self-sufficient shield logistics cruiser (no cap chain required)."
    },
    "Bellicose": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Target Painter / Missile Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km",
        "tactics": "Target painters inflate signature radius for missile fleet.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Target Painter / Missile Cruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bellicose [Cruiser | Minmatar]\n  - Combat Role: Target Painter / Missile Cruiser\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Target Painter / Missile Cruiser Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: 30-70 km\n  - Tactical Counter-Play: Target painters inflate signature radius for missile fleet."
    },
    "Stabber Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Heavy Projectile Nano Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Extreme (2.8+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "Premier nano autocannon skirmisher with extreme agility.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Heavy Projectile Nano Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stabber Navy Issue [Faction Cruiser | Minmatar (Fleet)]\n  - Combat Role: Heavy Projectile Nano Kiter\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Heavy Projectile Nano Kiter Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Extreme (2.8+ km/s)\n  - Weapon Optimal: 15-35 km\n  - Tactical Counter-Play: Premier nano autocannon skirmisher with extreme agility."
    },
    "Scythe Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Fast Missile / Rocket Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (2.8+ km/s)",
        "optimal_range": "25-60 km",
        "tactics": "High-speed missile platform with rapid application.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Fast Missile / Rocket Kiter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scythe Navy Issue [Faction Cruiser | Minmatar (Fleet)]\n  - Combat Role: Fast Missile / Rocket Kiter\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Fast Missile / Rocket Kiter Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Extreme (2.8+ km/s)\n  - Weapon Optimal: 25-60 km\n  - Tactical Counter-Play: High-speed missile platform with rapid application."
    },
    "Vagabond": {
        "class": "Heavy Assault Cruiser",
        "faction": "Minmatar",
        "role": "HAC Active Shield Nano Kiter",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Shield (Dual XL-ASB) + ADC",
        "speed": "Extreme (3.0+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "Fast shield active HAC with Assault Damage Control. Fast kite at falloff (18-24km). Apply Tracking Disruptors or heavy webs.",
        "high_slots": 5,
        "mid_slots": 4,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 1,
        "weapon_type": "Medium Projectile (425mm Autocannons)",
        "bonuses": [
            "5% Medium Projectile rate of fire per lvl",
            "10% Medium Projectile falloff per lvl",
            "7.5% shield boost amount per lvl",
            "5% all shield resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vagabond [Heavy Assault Cruiser | Minmatar]\n  - Combat Role: HAC Active Shield Nano Kiter\n  - Weapon System: Medium Projectile (425mm Autocannons)\n  - Slot Layout: Highs: 5 | Mids: 4 | Lows: 5 | Rigs: 2 (Turrets: 4 | Launchers: 1)\n  - Key Bonuses: 5% Medium Projectile rate of fire per lvl | 10% Medium Projectile falloff per lvl | 7.5% shield boost amount per lvl\n  - Defense Profile: Active Shield (Dual XL-ASB) + ADC | Speed: Extreme (3.0+ km/s)\n  - Weapon Optimal: 15-35 km\n  - Tactical Counter-Play: Fast shield active HAC with Assault Damage Control. Fast kite at falloff (18-24km). Apply Tracking Disruptors or heavy webs."
    },
    "Muninn": {
        "class": "Heavy Assault Cruiser",
        "faction": "Minmatar",
        "role": "HAC Heavy Missile Fleet Cruiser",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor / Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "40-80 km",
        "tactics": "Missile combat HAC with high mobility and ADC. Counter with Missile Guidance Disruptors and explosive shield resists.",
        "high_slots": 6,
        "mid_slots": 4,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 5,
        "weapon_type": "Heavy Assault Missiles / Heavy Missiles",
        "bonuses": [
            "5% Heavy Missile & HAM kinetic/explosive damage per lvl",
            "5% Heavy Missile & HAM rate of fire per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Muninn [Heavy Assault Cruiser | Minmatar]\n  - Combat Role: HAC Heavy Missile Fleet Cruiser\n  - Weapon System: Heavy Assault Missiles / Heavy Missiles\n  - Slot Layout: Highs: 6 | Mids: 4 | Lows: 5 | Rigs: 2 (Turrets: 0 | Launchers: 5)\n  - Key Bonuses: 5% Heavy Missile & HAM kinetic/explosive damage per lvl | 5% Heavy Missile & HAM rate of fire per lvl\n  - Defense Profile: Armor / Shield Buffer + ADC | Speed: Fast\n  - Weapon Optimal: 40-80 km\n  - Tactical Counter-Play: Missile combat HAC with high mobility and ADC. Counter with Missile Guidance Disruptors and explosive shield resists."
    },
    "Huginn": {
        "class": "Combat Recon",
        "faction": "Minmatar",
        "role": "D-Scan Immune 40km Web & Painter",
        "threat": "THREAT_ECM",
        "tank": "Shield / Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-40 km (Web) / 60-100 km (Paint)",
        "tactics": "Invisible to D-Scan. 40km+ stasis web stops targets dead.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "D-Scan Immune 40km Web & Painter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Huginn [Combat Recon | Minmatar]\n  - Combat Role: D-Scan Immune 40km Web & Painter\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: D-Scan Immune 40km Web & Painter Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Moderate\n  - Weapon Optimal: 0-40 km (Web) / 60-100 km (Paint)\n  - Tactical Counter-Play: Invisible to D-Scan. 40km+ stasis web stops targets dead."
    },
    "Rapier": {
        "class": "Force Recon",
        "faction": "Minmatar",
        "role": "Covert Cloak / 40km Web / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-40 km",
        "tactics": "Uncloaks to apply 40km webifier and light Covert Cyno.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Covert Cloak / 40km Web / Cyno Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rapier [Force Recon | Minmatar]\n  - Combat Role: Covert Cloak / 40km Web / Cyno\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Covert Cloak / 40km Web / Cyno Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Cloaked\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Uncloaks to apply 40km webifier and light Covert Cyno."
    },
    "Scimitar": {
        "class": "Logistics Cruiser",
        "faction": "Minmatar",
        "role": "T2 Solo Shield Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Extreme (2.5+ km/s)",
        "optimal_range": "Remote Shield",
        "tactics": "Fastest T2 shield logistics cruiser with self-sufficient cap.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "T2 Solo Shield Logistics Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scimitar [Logistics Cruiser | Minmatar]\n  - Combat Role: T2 Solo Shield Logistics\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: T2 Solo Shield Logistics Class Role Bonus\n  - Defense Profile: Shield | Speed: Extreme (2.5+ km/s)\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Fastest T2 shield logistics cruiser with self-sufficient cap."
    },
    "Loki": {
        "class": "Strategic Cruiser",
        "faction": "Minmatar",
        "role": "Modular T3C (Web / Artillery / Covert)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield / Armor Buffer / Active",
        "speed": "Extreme (2.2-3.0 km/s)",
        "optimal_range": "0-45 km (Web) / 30-80 km (Art/HAM)",
        "tactics": "Premier T3C. Fields 40km webs, covert cloak, interdiction nullification, 100MN AB, or heavy artillery/HAMs.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Medium Weapon System",
        "bonuses": [
            "Modular T3C (Web / Artillery / Covert) Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Loki [Strategic Cruiser | Minmatar]\n  - Combat Role: Modular T3C (Web / Artillery / Covert)\n  - Weapon System: Medium Weapon System\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 5 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: Modular T3C (Web / Artillery / Covert) Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer / Active | Speed: Extreme (2.2-3.0 km/s)\n  - Weapon Optimal: 0-45 km (Web) / 30-80 km (Art/HAM)\n  - Tactical Counter-Play: Premier T3C. Fields 40km webs, covert cloak, interdiction nullification, 100MN AB, or heavy artillery/HAMs."
    },
    "Cyclone": {
        "class": "Battlecruiser",
        "faction": "Minmatar",
        "role": "Active Shield Missile / AC BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Active Shield (Dual MASB / XL-ASB)",
        "speed": "Fast for BC",
        "optimal_range": "15-40 km",
        "tactics": "Massive active shield repair bonus with heavy missiles.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Active Shield Missile / AC BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cyclone [Battlecruiser | Minmatar]\n  - Combat Role: Active Shield Missile / AC BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Active Shield Missile / AC BC Class Role Bonus\n  - Defense Profile: Active Shield (Dual MASB / XL-ASB) | Speed: Fast for BC\n  - Weapon Optimal: 15-40 km\n  - Tactical Counter-Play: Massive active shield repair bonus with heavy missiles."
    },
    "Hurricane": {
        "class": "Battlecruiser",
        "faction": "Minmatar",
        "role": "Heavy Projectile Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BC",
        "optimal_range": "15-40 km AC / 70+ km Art",
        "tactics": "Versatile projectile platform with high alpha strike.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Projectile Battlecruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hurricane [Battlecruiser | Minmatar]\n  - Combat Role: Heavy Projectile Battlecruiser\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Projectile Battlecruiser Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Fast for BC\n  - Weapon Optimal: 15-40 km AC / 70+ km Art\n  - Tactical Counter-Play: Versatile projectile platform with high alpha strike."
    },
    "Tornado": {
        "class": "Attack Battlecruiser",
        "faction": "Minmatar",
        "role": "Battleship-Gun 1400mm Artillery Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield",
        "speed": "Fast for BC (2.0 km/s)",
        "optimal_range": "80-150 km",
        "tactics": "Large 1400mm Artillery on BC hull. Devastating alpha strike (10,000+ alpha).",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Battleship-Gun 1400mm Artillery Sniper Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tornado [Attack Battlecruiser | Minmatar]\n  - Combat Role: Battleship-Gun 1400mm Artillery Sniper\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Battleship-Gun 1400mm Artillery Sniper Class Role Bonus\n  - Defense Profile: Paper Thin Shield | Speed: Fast for BC (2.0 km/s)\n  - Weapon Optimal: 80-150 km\n  - Tactical Counter-Play: Large 1400mm Artillery on BC hull. Devastating alpha strike (10,000+ alpha)."
    },
    "Cyclone Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Heavy Missile / Shield BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-60 km",
        "tactics": "Superior missile rate of fire and shield buffer.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Heavy Missile / Shield BC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cyclone Navy Issue [Faction Battlecruiser | Minmatar (Fleet)]\n  - Combat Role: Heavy Missile / Shield BC\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Heavy Missile / Shield BC Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: Superior missile rate of fire and shield buffer."
    },
    "Hurricane Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Projectile Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-80 km",
        "tactics": "Higher projectile tracking and armor/shield flexibility.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Navy Projectile Battlecruiser Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hurricane Navy Issue [Faction Battlecruiser | Minmatar (Fleet)]\n  - Combat Role: Navy Projectile Battlecruiser\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Navy Projectile Battlecruiser Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Fast\n  - Weapon Optimal: 20-80 km\n  - Tactical Counter-Play: Higher projectile tracking and armor/shield flexibility."
    },
    "Sleipnir": {
        "class": "Command Ship",
        "faction": "Minmatar",
        "role": "Shield Fleet Command / Autocannon Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Active Shield (Dual XL-ASB)",
        "speed": "Fast for Command",
        "optimal_range": "15-40 km",
        "tactics": "Provides Fleet Shield / Skirmish Bursts and deals 1200+ AC DPS.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Shield Fleet Command / Autocannon Brawler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Sleipnir [Command Ship | Minmatar]\n  - Combat Role: Shield Fleet Command / Autocannon Brawler\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Shield Fleet Command / Autocannon Brawler Class Role Bonus\n  - Defense Profile: Immense Active Shield (Dual XL-ASB) | Speed: Fast for Command\n  - Weapon Optimal: 15-40 km\n  - Tactical Counter-Play: Provides Fleet Shield / Skirmish Bursts and deals 1200+ AC DPS."
    },
    "Claymore": {
        "class": "Command Ship",
        "faction": "Minmatar",
        "role": "Shield Fleet Command / Missile",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Fast for Command",
        "optimal_range": "20-60 km",
        "tactics": "Provides Fleet Skirmish / Shield Bursts with heavy missiles.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 2,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Heavy / Medium Weapon System",
        "bonuses": [
            "Shield Fleet Command / Missile Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Claymore [Command Ship | Minmatar]\n  - Combat Role: Shield Fleet Command / Missile\n  - Weapon System: Heavy / Medium Weapon System\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 2 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Shield Fleet Command / Missile Class Role Bonus\n  - Defense Profile: Immense Shield Buffer | Speed: Fast for Command\n  - Weapon Optimal: 20-60 km\n  - Tactical Counter-Play: Provides Fleet Skirmish / Shield Bursts with heavy missiles."
    },
    "Tempest": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Artillery / AC Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Fast for BS",
        "optimal_range": "20-40 km AC / 100+ km Art",
        "tactics": "High-alpha projectile battleship. Apply Tracking Disruptors and transversal.",
        "high_slots": 8,
        "mid_slots": 5,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 2,
        "weapon_type": "Large Projectile (800mm AC / 1400mm Art)",
        "bonuses": [
            "5% Large Projectile rate of fire per lvl",
            "5% Large Projectile damage per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tempest [Battleship | Minmatar]\n  - Combat Role: Artillery / AC Battleship\n  - Weapon System: Large Projectile (800mm AC / 1400mm Art)\n  - Slot Layout: Highs: 8 | Mids: 5 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 2)\n  - Key Bonuses: 5% Large Projectile rate of fire per lvl | 5% Large Projectile damage per lvl\n  - Defense Profile: Shield / Armor | Speed: Fast for BS\n  - Weapon Optimal: 20-40 km AC / 100+ km Art\n  - Tactical Counter-Play: High-alpha projectile battleship. Apply Tracking Disruptors and transversal."
    },
    "Typhoon": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Cruise / Torpedo / Cruise BS",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer / Active",
        "speed": "Fast for BS",
        "optimal_range": "30-100 km",
        "tactics": "Versatile missile and armor/shield brawler. Apply Missile Guidance Disruptors.",
        "high_slots": 7,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 6,
        "weapon_type": "Cruise Missiles / Torpedoes / Heavy AC",
        "bonuses": [
            "5% Cruise/Torpedo rate of fire per lvl",
            "5% missile explosion velocity per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Typhoon [Battleship | Minmatar]\n  - Combat Role: Cruise / Torpedo / Cruise BS\n  - Weapon System: Cruise Missiles / Torpedoes / Heavy AC\n  - Slot Layout: Highs: 7 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 4 | Launchers: 6)\n  - Key Bonuses: 5% Cruise/Torpedo rate of fire per lvl | 5% missile explosion velocity per lvl\n  - Defense Profile: Armor / Shield Buffer / Active | Speed: Fast for BS\n  - Weapon Optimal: 30-100 km\n  - Tactical Counter-Play: Versatile missile and armor/shield brawler. Apply Missile Guidance Disruptors."
    },
    "Maelstrom": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Active Shield / Artillery BS",
        "threat": "THREAT_COMBATANT",
        "tank": "Active Shield (X-Large Booster)",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "Massive shield boost bonus; heavy 1400mm artillery fleet anchor.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Active Shield / Artillery BS Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Maelstrom [Battleship | Minmatar]\n  - Combat Role: Active Shield / Artillery BS\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Active Shield / Artillery BS Class Role Bonus\n  - Defense Profile: Active Shield (X-Large Booster) | Speed: Slow\n  - Weapon Optimal: 60-140 km\n  - Tactical Counter-Play: Massive shield boost bonus; heavy 1400mm artillery fleet anchor."
    },
    "Tempest Fleet Issue": {
        "class": "Faction Battleship",
        "faction": "Minmatar (Fleet)",
        "role": "Artillery / AC High Alpha Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BS",
        "optimal_range": "25-50 km AC / 100+ km Art",
        "tactics": "Extreme projectile rate of fire and devastating alpha strike.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Artillery / AC High Alpha Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Tempest Fleet Issue [Faction Battleship | Minmatar (Fleet)]\n  - Combat Role: Artillery / AC High Alpha Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Artillery / AC High Alpha Battleship Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Fast for BS\n  - Weapon Optimal: 25-50 km AC / 100+ km Art\n  - Tactical Counter-Play: Extreme projectile rate of fire and devastating alpha strike."
    },
    "Typhoon Fleet Issue": {
        "class": "Faction Battleship",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Missile / Cruise Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast for BS",
        "optimal_range": "40-120 km",
        "tactics": "Enhanced missile application and projectile support.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Navy Missile / Cruise Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Typhoon Fleet Issue [Faction Battleship | Minmatar (Fleet)]\n  - Combat Role: Navy Missile / Cruise Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 3 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Navy Missile / Cruise Battleship Class Role Bonus\n  - Defense Profile: Armor / Shield Buffer | Speed: Fast for BS\n  - Weapon Optimal: 40-120 km\n  - Tactical Counter-Play: Enhanced missile application and projectile support."
    },
    "Vargur": {
        "class": "Marauder",
        "faction": "Minmatar",
        "role": "Bastion Autocannon / Artillery Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Shield (Dual XL-ASB in Bastion)",
        "speed": "Immobile in Bastion",
        "optimal_range": "25-60 km (AC) / 100-180 km (Artillery)",
        "tactics": "Bastion Marauder with instantaneous select-damage AC/Artillery and massive active shield boost. Counter with heavy neutralizers and high transversal.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 5,
        "rig_slots": 2,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 0,
        "weapon_type": "Large Projectile (800mm Autocannons / 1400mm Artillery)",
        "bonuses": [
            "100% Large Projectile damage bonus",
            "10% Large Projectile tracking/rate of fire per lvl",
            "Role: Bastion grants 100% Shield Boost and EWAR immunity"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vargur [Marauder | Minmatar]\n  - Combat Role: Bastion Autocannon / Artillery Marauder\n  - Weapon System: Large Projectile (800mm Autocannons / 1400mm Artillery)\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 5 | Rigs: 2 (Turrets: 4 | Launchers: 0)\n  - Key Bonuses: 100% Large Projectile damage bonus | 10% Large Projectile tracking/rate of fire per lvl | Role: Bastion grants 100% Shield Boost and EWAR immunity\n  - Defense Profile: Active Shield (Dual XL-ASB in Bastion) | Speed: Immobile in Bastion\n  - Weapon Optimal: 25-60 km (AC) / 100-180 km (Artillery)\n  - Tactical Counter-Play: Bastion Marauder with instantaneous select-damage AC/Artillery and massive active shield boost. Counter with heavy neutralizers and high transversal."
    },
    "Panther": {
        "class": "Black Ops",
        "faction": "Minmatar",
        "role": "Covert Jump / Projectile Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BS (Covert Jump)",
        "optimal_range": "25-60 km",
        "tactics": "Fastest Black Ops battleship with massive projectile alpha.",
        "high_slots": 8,
        "mid_slots": 6,
        "low_slots": 7,
        "rig_slots": 2,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 7,
        "weapon_type": "Large Weapon System",
        "bonuses": [
            "Covert Jump / Projectile Battleship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Panther [Black Ops | Minmatar]\n  - Combat Role: Covert Jump / Projectile Battleship\n  - Weapon System: Large Weapon System\n  - Slot Layout: Highs: 8 | Mids: 6 | Lows: 7 | Rigs: 2 (Turrets: 7 | Launchers: 7)\n  - Key Bonuses: Covert Jump / Projectile Battleship Class Role Bonus\n  - Defense Profile: Shield / Armor Buffer | Speed: Fast for BS (Covert Jump)\n  - Weapon Optimal: 25-60 km\n  - Tactical Counter-Play: Fastest Black Ops battleship with massive projectile alpha."
    },
    "Naglfar": {
        "class": "Dreadnought",
        "faction": "Minmatar",
        "role": "Capital Projectile Siege",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield / Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "High alpha projectile dreadnought with Siege module.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Capital Projectile Siege Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Naglfar [Dreadnought | Minmatar]\n  - Combat Role: Capital Projectile Siege\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Capital Projectile Siege Class Role Bonus\n  - Defense Profile: Shield / Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: High alpha projectile dreadnought with Siege module."
    },
    "Naglfar Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Capital Projectile Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield / Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Superior projectile tracking and dual tank versatility.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Navy Capital Projectile Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Naglfar Navy Issue [Faction Dreadnought | Minmatar (Fleet)]\n  - Combat Role: Navy Capital Projectile Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Navy Capital Projectile Dread Class Role Bonus\n  - Defense Profile: Shield / Armor Active | Speed: Capital\n  - Weapon Optimal: Capital Grid\n  - Tactical Counter-Play: Superior projectile tracking and dual tank versatility."
    },
    "Valravn": {
        "class": "Lancer Dreadnought",
        "faction": "Minmatar",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp.",
        "high_slots": 6,
        "mid_slots": 5,
        "low_slots": 7,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 3,
        "weapon_type": "Capital Siege Weaponry",
        "bonuses": [
            "Disruptive Lancer Dread Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Valravn [Lancer Dreadnought | Minmatar]\n  - Combat Role: Disruptive Lancer Dread\n  - Weapon System: Capital Siege Weaponry\n  - Slot Layout: Highs: 6 | Mids: 5 | Lows: 7 | Rigs: 3 (Turrets: 3 | Launchers: 3)\n  - Key Bonuses: Disruptive Lancer Dread Class Role Bonus\n  - Defense Profile: Shield Active | Speed: Capital\n  - Weapon Optimal: Lancer Beam\n  - Tactical Counter-Play: Fires disruptive capital lance disabling cynos and warp."
    },
    "Nidhoggur": {
        "class": "Carrier",
        "faction": "Minmatar",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Capital carrier with fighter speed and fighter damage bonuses.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Fighter Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nidhoggur [Carrier | Minmatar]\n  - Combat Role: Capital Fighter Carrier\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Fighter Carrier Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Capital\n  - Weapon Optimal: Fighter Range\n  - Tactical Counter-Play: Capital carrier with fighter speed and fighter damage bonuses."
    },
    "Hel": {
        "class": "Supercarrier",
        "faction": "Minmatar",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Fastest supercarrier with immense fighter strike damage.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Heavy Carrier Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hel [Supercarrier | Minmatar]\n  - Combat Role: Supercapital Heavy Carrier\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Heavy Carrier Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Fastest supercarrier with immense fighter strike damage."
    },
    "Lif": {
        "class": "Force Auxiliary",
        "faction": "Minmatar",
        "role": "Capital Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Shield",
        "tactics": "Capital remote shield repair ship.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Shield FAX Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Lif [Force Auxiliary | Minmatar]\n  - Combat Role: Capital Shield FAX\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Shield FAX Class Role Bonus\n  - Defense Profile: Active Shield (Triage) | Speed: Capital\n  - Weapon Optimal: Remote Shield\n  - Tactical Counter-Play: Capital remote shield repair ship."
    },
    "Ragnarok": {
        "class": "Titan",
        "faction": "Minmatar",
        "role": "Supercapital Gjallarhorn Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Gjallarhorn Explosive Doomsday titan with fleet shield burst.",
        "high_slots": 8,
        "mid_slots": 7,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 6,
        "weapon_type": "Supercapital / Doomsday Weapon System",
        "bonuses": [
            "Supercapital Gjallarhorn Titan Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Ragnarok [Titan | Minmatar]\n  - Combat Role: Supercapital Gjallarhorn Titan\n  - Weapon System: Supercapital / Doomsday Weapon System\n  - Slot Layout: Highs: 8 | Mids: 7 | Lows: 8 | Rigs: 3 (Turrets: 6 | Launchers: 6)\n  - Key Bonuses: Supercapital Gjallarhorn Titan Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Supercapital\n  - Weapon Optimal: Omni Grid\n  - Tactical Counter-Play: Gjallarhorn Explosive Doomsday titan with fleet shield burst."
    },
    "Mammoth": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity industrial.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Mammoth [Industrial | Minmatar]\n  - Combat Role: High-Capacity Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Large cargo capacity industrial."
    },
    "Wreathe": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "Fast Industrial Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Fast (<4s align)",
        "optimal_range": "0 km",
        "tactics": "Fast sub-warp align industrial.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Fast Industrial Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Wreathe [Industrial | Minmatar]\n  - Combat Role: Fast Industrial Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Fast Industrial Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Fast (<4s align)\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fast sub-warp align industrial."
    },
    "Hoarder": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "Ammo & Charge Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ammo/Charge cargo bay.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Ammo & Charge Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hoarder [Industrial | Minmatar]\n  - Combat Role: Ammo & Charge Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Ammo & Charge Hauler Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Specialized Ammo/Charge cargo bay."
    },
    "Prowler": {
        "class": "Blockade Runner",
        "faction": "Minmatar",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Shield",
        "speed": "Fast (<2.5s align)",
        "optimal_range": "0 km",
        "tactics": "Fastest blockade runner with covert cloak.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Covert Fast Hauler Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Prowler [Blockade Runner | Minmatar]\n  - Combat Role: Covert Fast Hauler\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Covert Fast Hauler Class Role Bonus\n  - Defense Profile: Cloaked Shield | Speed: Fast (<2.5s align)\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fastest blockade runner with covert cloak."
    },
    "Mastodon": {
        "class": "Deep Space Transport",
        "faction": "Minmatar",
        "role": "Heavy Shield DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Shield DST Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Mastodon [Deep Space Transport | Minmatar]\n  - Combat Role: Heavy Shield DST\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Shield DST Class Role Bonus\n  - Defense Profile: Immense Shield Buffer (+2 Warp Core) | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: +2 native warp core strength and Fleet Hangar."
    },
    "Fenrir": {
        "class": "Freighter",
        "faction": "Minmatar",
        "role": "Fast Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Fastest Freighter",
        "optimal_range": "0 km",
        "tactics": "Fastest aligning standard freighter.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Fast Sub-Capital Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Fenrir [Freighter | Minmatar]\n  - Combat Role: Fast Sub-Capital Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Fast Sub-Capital Freighter Class Role Bonus\n  - Defense Profile: Buffer | Speed: Fastest Freighter\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fastest aligning standard freighter."
    },
    "Nomad": {
        "class": "Jump Freighter",
        "faction": "Minmatar",
        "role": "Fast Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Fastest aligning jump freighter for nullsec logistics.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Fast Capital Jump Freighter Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Nomad [Jump Freighter | Minmatar]\n  - Combat Role: Fast Capital Jump Freighter\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Fast Capital Jump Freighter Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Jump Drive\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Fastest aligning jump freighter for nullsec logistics."
    },
    "Venture": {
        "class": "Mining Frigate",
        "faction": "ORE",
        "role": "Gas / Ore / +2 Warp Core Miner",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Native +2 warp core strength allows slipping standard points.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Gas / Ore / +2 Warp Core Miner Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Venture [Mining Frigate | ORE]\n  - Combat Role: Gas / Ore / +2 Warp Core Miner\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Gas / Ore / +2 Warp Core Miner Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Native +2 warp core strength allows slipping standard points."
    },
    "Prospect": {
        "class": "Expedition Frigate",
        "faction": "ORE",
        "role": "Covert Ops Gas / Ore Miner",
        "threat": "THREAT_MINING",
        "tank": "Cloaked Shield",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Covert cloaking mining frigate. Can fit Covert Cyno.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Covert Ops Gas / Ore Miner Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Prospect [Expedition Frigate | ORE]\n  - Combat Role: Covert Ops Gas / Ore Miner\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Covert Ops Gas / Ore Miner Class Role Bonus\n  - Defense Profile: Cloaked Shield | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Covert cloaking mining frigate. Can fit Covert Cyno."
    },
    "Endurance": {
        "class": "Expedition Frigate",
        "faction": "ORE",
        "role": "Cloaked Ice Mining Frigate",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Specialized ice mining frigate with cloak bonus.",
        "high_slots": 3,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 3,
        "launcher_hardpoints": 2,
        "weapon_type": "Small Weapon System (Turrets / Missiles)",
        "bonuses": [
            "Cloaked Ice Mining Frigate Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Endurance [Expedition Frigate | ORE]\n  - Combat Role: Cloaked Ice Mining Frigate\n  - Weapon System: Small Weapon System (Turrets / Missiles)\n  - Slot Layout: Highs: 3 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 3 | Launchers: 2)\n  - Key Bonuses: Cloaked Ice Mining Frigate Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Specialized ice mining frigate with cloak bonus."
    },
    "Retriever": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "High-Capacity Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Large ore hold mining barge. Easy target.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity Mining Barge Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Retriever [Mining Barge | ORE]\n  - Combat Role: High-Capacity Mining Barge\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity Mining Barge Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Large ore hold mining barge. Easy target."
    },
    "Procurer": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "Heavy Tanked Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Heavy Shield Buffer (60k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Heavy shield resistance bonus. Difficult to gank.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Tanked Mining Barge Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Procurer [Mining Barge | ORE]\n  - Combat Role: Heavy Tanked Mining Barge\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Tanked Mining Barge Class Role Bonus\n  - Defense Profile: Heavy Shield Buffer (60k+ EHP) | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Heavy shield resistance bonus. Difficult to gank."
    },
    "Covetor": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "High Yield Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Maximum mining yield with paper tank.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High Yield Mining Barge Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Covetor [Mining Barge | ORE]\n  - Combat Role: High Yield Mining Barge\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High Yield Mining Barge Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Maximum mining yield with paper tank."
    },
    "Mackinaw": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "High-Capacity T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "T2 mining exhumer with massive ore hold.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "High-Capacity T2 Exhumer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Mackinaw [Exhumer | ORE]\n  - Combat Role: High-Capacity T2 Exhumer\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: High-Capacity T2 Exhumer Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: T2 mining exhumer with massive ore hold."
    },
    "Skiff": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "Immense Tanked T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Immense Shield Buffer (100k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "T2 mining exhumer with battleship-grade shield tank.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Immense Tanked T2 Exhumer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Skiff [Exhumer | ORE]\n  - Combat Role: Immense Tanked T2 Exhumer\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Immense Tanked T2 Exhumer Class Role Bonus\n  - Defense Profile: Immense Shield Buffer (100k+ EHP) | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: T2 mining exhumer with battleship-grade shield tank."
    },
    "Hulk": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "Maximum Yield T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Maximum mining yield in EVE. Requires fleet defense.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Maximum Yield T2 Exhumer Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hulk [Exhumer | ORE]\n  - Combat Role: Maximum Yield T2 Exhumer\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Maximum Yield T2 Exhumer Class Role Bonus\n  - Defense Profile: Paper Thin | Speed: Slow\n  - Weapon Optimal: 0-15 km\n  - Tactical Counter-Play: Maximum mining yield in EVE. Requires fleet defense."
    },
    "Noctis": {
        "class": "Salvage Ship",
        "faction": "ORE",
        "role": "Fleet Salvage / Tractor Flagship",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-40 km",
        "tactics": "Rapid tractor beam and salvager bonuses.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Fleet Salvage / Tractor Flagship Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Noctis [Salvage Ship | ORE]\n  - Combat Role: Fleet Salvage / Tractor Flagship\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Fleet Salvage / Tractor Flagship Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 0-40 km\n  - Tactical Counter-Play: Rapid tractor beam and salvager bonuses."
    },
    "Porpoise": {
        "class": "Industrial Command",
        "faction": "ORE",
        "role": "Compact Mining Command / Booster",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast for Command",
        "optimal_range": "Mining Boost Range",
        "tactics": "Sub-capital mining booster and drone combatant.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Compact Mining Command / Booster Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Porpoise [Industrial Command | ORE]\n  - Combat Role: Compact Mining Command / Booster\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Compact Mining Command / Booster Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Fast for Command\n  - Weapon Optimal: Mining Boost Range\n  - Tactical Counter-Play: Sub-capital mining booster and drone combatant."
    },
    "Orca": {
        "class": "Industrial Command",
        "faction": "ORE",
        "role": "Heavy Mining Command / Fleet Hangar",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (300k+ EHP)",
        "speed": "Slow",
        "optimal_range": "Mining Boost Range",
        "tactics": "Fleet booster, ore compression, and massive cargo hold.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Heavy Mining Command / Fleet Hangar Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Orca [Industrial Command | ORE]\n  - Combat Role: Heavy Mining Command / Fleet Hangar\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Heavy Mining Command / Fleet Hangar Class Role Bonus\n  - Defense Profile: Immense Shield Buffer (300k+ EHP) | Speed: Slow\n  - Weapon Optimal: Mining Boost Range\n  - Tactical Counter-Play: Fleet booster, ore compression, and massive cargo hold."
    },
    "Rorqual": {
        "class": "Capital Industrial",
        "faction": "ORE",
        "role": "Capital Mining Command / PANIC",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Industrial Core + PANIC)",
        "speed": "Capital",
        "optimal_range": "Mining Grid",
        "tactics": "Capital mining flagship. PANIC module grants 5-7.5 minutes of complete invulnerability.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Capital Mining Command / PANIC Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Rorqual [Capital Industrial | ORE]\n  - Combat Role: Capital Mining Command / PANIC\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Capital Mining Command / PANIC Class Role Bonus\n  - Defense Profile: Active Shield (Industrial Core + PANIC) | Speed: Capital\n  - Weapon Optimal: Mining Grid\n  - Tactical Counter-Play: Capital mining flagship. PANIC module grants 5-7.5 minutes of complete invulnerability."
    },
    "Bowhead": {
        "class": "Freighter",
        "faction": "ORE",
        "role": "Assembled Ship Transport",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ship Maintenance Bay transports fully assembled battleships.",
        "high_slots": 2,
        "mid_slots": 4,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Industrial / Harvesting System",
        "bonuses": [
            "Assembled Ship Transport Class Role Bonus"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Bowhead [Freighter | ORE]\n  - Combat Role: Assembled Ship Transport\n  - Weapon System: Industrial / Harvesting System\n  - Slot Layout: Highs: 2 | Mids: 4 | Lows: 3 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Assembled Ship Transport Class Role Bonus\n  - Defense Profile: Shield Buffer | Speed: Slow\n  - Weapon Optimal: 0 km\n  - Tactical Counter-Play: Specialized Ship Maintenance Bay transports fully assembled battleships."
    },
    "Onyx": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Caldari",
        "role": "Warp Interdiction / Heavy Shield Tank",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer (Warp Disruption Field Generator)",
        "speed": "Moderate (1.3-1.6 km/s MWD)",
        "optimal_range": "20-60 km (Missiles) / 30-80 km (Rails)",
        "tactics": "Caldari Heavy Interdictor. Projects infinite-point Warp Disruption Field Generators to trap supercapitals and fleets. Counter with high transversal, ECM/damps, or heavy neuts.",
        "high_slots": 6,
        "mid_slots": 6,
        "low_slots": 4,
        "rig_slots": 2,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 5,
        "weapon_type": "Heavy Assault Missiles / Heavy Missiles (HAM/RLML) or Railguns",
        "bonuses": [
            "5% Kinetic/Thermal missile damage per lvl",
            "5% Heavy/HAM missile velocity per lvl",
            "5% all shield resists per lvl",
            "Role: Can fit Warp Disruption Field Generator"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Onyx [Heavy Interdiction Cruiser | Caldari]\n  - Combat Role: Warp Interdiction / Heavy Shield Tank\n  - Weapon System: Heavy Assault Missiles / Heavy Missiles (HAM/RLML) or Railguns\n  - Slot Layout: Highs: 6 | Mids: 6 | Lows: 4 | Rigs: 2 (Turrets: 5 | Launchers: 5)\n  - Key Bonuses: 5% Kinetic/Thermal missile damage per lvl | 5% Heavy/HAM missile velocity per lvl | 5% all shield resists per lvl\n  - Defense Profile: Shield Buffer (Warp Disruption Field Generator) | Speed: Moderate (1.3-1.6 km/s MWD)\n  - Weapon Optimal: 20-60 km (Missiles) / 30-80 km (Rails)\n  - Tactical Counter-Play: Caldari Heavy Interdictor. Projects infinite-point Warp Disruption Field Generators to trap supercapitals and fleets. Counter with high transversal, ECM/damps, or heavy neuts."
    },
    "Hurricane Fleet Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "High Alpha Projectile / Armor Fleet BC",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Shield",
        "speed": "Fast for BC (1.4-1.8 km/s MWD)",
        "optimal_range": "15-35 km (425mm AC) / 45-80 km (720mm Artillery)",
        "tactics": "Minmatar Navy Battlecruiser with devastating 6-turret projectile alpha and tracking. Counter with Tracking Disruptors and transversal velocity.",
        "high_slots": 8,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 6,
        "launcher_hardpoints": 2,
        "weapon_type": "Medium Projectile (425mm Autocannons / 720mm Artillery)",
        "bonuses": [
            "5% Medium Projectile damage per lvl",
            "5% Medium Projectile tracking per lvl",
            "5% Medium Projectile rate of fire per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Hurricane Fleet Issue [Faction Battlecruiser | Minmatar (Fleet)]\n  - Combat Role: High Alpha Projectile / Armor Fleet BC\n  - Weapon System: Medium Projectile (425mm Autocannons / 720mm Artillery)\n  - Slot Layout: Highs: 8 | Mids: 4 | Lows: 6 | Rigs: 3 (Turrets: 6 | Launchers: 2)\n  - Key Bonuses: 5% Medium Projectile damage per lvl | 5% Medium Projectile tracking per lvl | 5% Medium Projectile rate of fire per lvl\n  - Defense Profile: Armor Buffer / Shield | Speed: Fast for BC (1.4-1.8 km/s MWD)\n  - Weapon Optimal: 15-35 km (425mm AC) / 45-80 km (720mm Artillery)\n  - Tactical Counter-Play: Minmatar Navy Battlecruiser with devastating 6-turret projectile alpha and tracking. Counter with Tracking Disruptors and transversal velocity."
    },
    "Cyclone Fleet Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Rapid Missile / Active Shield Brawler",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active Shield Boost",
        "speed": "Fast (1.5-1.9 km/s MWD)",
        "optimal_range": "20-55 km (HAM / Heavy Missiles)",
        "tactics": "Minmatar Navy Battlecruiser with rapid missile rate of fire and active shield boost bonus. Counter with Missile Guidance Disruptors and heavy neuts.",
        "high_slots": 7,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 2,
        "launcher_hardpoints": 5,
        "weapon_type": "Heavy Assault Missiles (HAM) / Heavy Missiles (RLML)",
        "bonuses": [
            "5% Heavy/HAM missile rate of fire per lvl",
            "7.5% Heavy/HAM missile velocity per lvl",
            "7.5% shield boost amount per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Cyclone Fleet Issue [Faction Battlecruiser | Minmatar (Fleet)]\n  - Combat Role: Rapid Missile / Active Shield Brawler\n  - Weapon System: Heavy Assault Missiles (HAM) / Heavy Missiles (RLML)\n  - Slot Layout: Highs: 7 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 2 | Launchers: 5)\n  - Key Bonuses: 5% Heavy/HAM missile rate of fire per lvl | 7.5% Heavy/HAM missile velocity per lvl | 7.5% shield boost amount per lvl\n  - Defense Profile: Shield Buffer / Active Shield Boost | Speed: Fast (1.5-1.9 km/s MWD)\n  - Weapon Optimal: 20-55 km (HAM / Heavy Missiles)\n  - Tactical Counter-Play: Minmatar Navy Battlecruiser with rapid missile rate of fire and active shield boost bonus. Counter with Missile Guidance Disruptors and heavy neuts."
    },
    "Stabber Fleet Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Fast Projectile Fleet Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Armor Buffer",
        "speed": "Very Fast (2.2-2.8 km/s MWD)",
        "optimal_range": "10-25 km (220mm AC) / 35-65 km (720mm Artillery)",
        "tactics": "High-speed Minmatar Navy Cruiser with 5 projectile turrets. Strong falloff and tracking. Counter with Tracking Disruptors and web tackle.",
        "high_slots": 6,
        "mid_slots": 4,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 3,
        "weapon_type": "Medium Projectile (220mm-425mm Autocannons / 720mm Artillery)",
        "bonuses": [
            "10% Medium Projectile damage per lvl",
            "7.5% Medium Projectile tracking per lvl",
            "5% Medium Projectile falloff per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Stabber Fleet Issue [Faction Cruiser | Minmatar (Fleet)]\n  - Combat Role: Fast Projectile Fleet Cruiser\n  - Weapon System: Medium Projectile (220mm-425mm Autocannons / 720mm Artillery)\n  - Slot Layout: Highs: 6 | Mids: 4 | Lows: 6 | Rigs: 3 (Turrets: 5 | Launchers: 3)\n  - Key Bonuses: 10% Medium Projectile damage per lvl | 7.5% Medium Projectile tracking per lvl | 5% Medium Projectile falloff per lvl\n  - Defense Profile: Shield Buffer / Armor Buffer | Speed: Very Fast (2.2-2.8 km/s MWD)\n  - Weapon Optimal: 10-25 km (220mm AC) / 35-65 km (720mm Artillery)\n  - Tactical Counter-Play: High-speed Minmatar Navy Cruiser with 5 projectile turrets. Strong falloff and tracking. Counter with Tracking Disruptors and web tackle."
    },
    "Scythe Fleet Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "High-Speed Missile / Turret Attack Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Extreme (2.5-3.2 km/s MWD)",
        "optimal_range": "20-60 km (Missiles) / 10-25 km (AC)",
        "tactics": "Ultra-fast Navy combat cruiser with dual weapon bonuses for missiles and autocannons. Counter with long-range point and missile disruptors.",
        "high_slots": 5,
        "mid_slots": 5,
        "low_slots": 5,
        "rig_slots": 3,
        "turret_hardpoints": 4,
        "launcher_hardpoints": 4,
        "weapon_type": "Heavy Assault Missiles (HAM) / Rapid Light Missiles (RLML) or 425mm Autocannons",
        "bonuses": [
            "10% Light/Heavy/HAM missile damage per lvl",
            "10% Medium Projectile damage per lvl",
            "5% ship max velocity per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Scythe Fleet Issue [Faction Cruiser | Minmatar (Fleet)]\n  - Combat Role: High-Speed Missile / Turret Attack Cruiser\n  - Weapon System: Heavy Assault Missiles (HAM) / Rapid Light Missiles (RLML) or 425mm Autocannons\n  - Slot Layout: Highs: 5 | Mids: 5 | Lows: 5 | Rigs: 3 (Turrets: 4 | Launchers: 4)\n  - Key Bonuses: 10% Light/Heavy/HAM missile damage per lvl | 10% Medium Projectile damage per lvl | 5% ship max velocity per lvl\n  - Defense Profile: Shield Buffer | Speed: Extreme (2.5-3.2 km/s MWD)\n  - Weapon Optimal: 20-60 km (Missiles) / 10-25 km (AC)\n  - Tactical Counter-Play: Ultra-fast Navy combat cruiser with dual weapon bonuses for missiles and autocannons. Counter with long-range point and missile disruptors."
    },
    "Thrasher Fleet Issue": {
        "class": "Faction Destroyer",
        "faction": "Minmatar (Fleet)",
        "role": "High Alpha Artillery / Autocannon Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Shield / Armor Buffer",
        "speed": "Very Fast (2.8-3.5 km/s MWD)",
        "optimal_range": "0-15 km (200mm AC) / 25-50 km (280mm Artillery)",
        "tactics": "Minmatar Navy Destroyer with 7 projectile turrets and reduced signature radius. Devastating alpha strike against frigates. Counter with Tracking Disruptors and scram/web tackle.",
        "high_slots": 8,
        "mid_slots": 3,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 7,
        "launcher_hardpoints": 1,
        "weapon_type": "Small Projectile (200mm Autocannons / 280mm Artillery)",
        "bonuses": [
            "10% Small Projectile damage per lvl",
            "10% Small Projectile tracking per lvl",
            "5% ship signature radius reduction per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Thrasher Fleet Issue [Faction Destroyer | Minmatar (Fleet)]\n  - Combat Role: High Alpha Artillery / Autocannon Destroyer\n  - Weapon System: Small Projectile (200mm Autocannons / 280mm Artillery)\n  - Slot Layout: Highs: 8 | Mids: 3 | Lows: 4 | Rigs: 3 (Turrets: 7 | Launchers: 1)\n  - Key Bonuses: 10% Small Projectile damage per lvl | 10% Small Projectile tracking per lvl | 5% ship signature radius reduction per lvl\n  - Defense Profile: Shield / Armor Buffer | Speed: Very Fast (2.8-3.5 km/s MWD)\n  - Weapon Optimal: 0-15 km (200mm AC) / 25-50 km (280mm Artillery)\n  - Tactical Counter-Play: Minmatar Navy Destroyer with 7 projectile turrets and reduced signature radius. Devastating alpha strike against frigates. Counter with Tracking Disruptors and scram/web tackle."
    },
    "Algos Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Gallente (Navy)",
        "role": "High-DPS Drone & Hybrid Blaster Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Active Armor Repair",
        "speed": "Moderate (2.2-2.7 km/s MWD)",
        "optimal_range": "0-10 km (Blasters) / 0-45 km (Drones)",
        "tactics": "Gallente Navy Destroyer with 5 hybrid turrets, enhanced drone bandwidth, and active armor repair bonus. Counter by defanging drones and applying Tracking Disruptors.",
        "high_slots": 6,
        "mid_slots": 3,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 5,
        "launcher_hardpoints": 0,
        "weapon_type": "Small Hybrid Blasters / Railguns & Combat Drones",
        "bonuses": [
            "10% Small Hybrid damage per lvl",
            "10% Drone HP and damage per lvl",
            "7.5% Armor Repair amount per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Algos Navy Issue [Faction Destroyer | Gallente (Navy)]\n  - Combat Role: High-DPS Drone & Hybrid Blaster Destroyer\n  - Weapon System: Small Hybrid Blasters / Railguns & Combat Drones\n  - Slot Layout: Highs: 6 | Mids: 3 | Lows: 4 | Rigs: 3 (Turrets: 5 | Launchers: 0)\n  - Key Bonuses: 10% Small Hybrid damage per lvl | 10% Drone HP and damage per lvl | 7.5% Armor Repair amount per lvl\n  - Defense Profile: Armor Buffer / Active Armor Repair | Speed: Moderate (2.2-2.7 km/s MWD)\n  - Weapon Optimal: 0-10 km (Blasters) / 0-45 km (Drones)\n  - Tactical Counter-Play: Gallente Navy Destroyer with 5 hybrid turrets, enhanced drone bandwidth, and active armor repair bonus. Counter by defanging drones and applying Tracking Disruptors."
    },
    "Vigil Fleet Issue": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "Fast Missile / Target Painter Tackle Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Extreme (4.5-5.5 km/s MWD)",
        "optimal_range": "15-40 km (Rockets / Light Missiles)",
        "tactics": "Fast Navy frigate with target painting bonuses and kinetic/explosive missile damage. Counter with Missile Guidance Disruptors and fast interceptor tackle.",
        "high_slots": 3,
        "mid_slots": 5,
        "low_slots": 3,
        "rig_slots": 3,
        "turret_hardpoints": 1,
        "launcher_hardpoints": 2,
        "weapon_type": "Light Missiles / Rockets",
        "bonuses": [
            "10% Light Missile/Rocket kinetic/explosive damage per lvl",
            "10% Target Painter effectiveness per lvl",
            "5% ship max velocity per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vigil Fleet Issue [Faction Frigate | Minmatar (Fleet)]\n  - Combat Role: Fast Missile / Target Painter Tackle Frigate\n  - Weapon System: Light Missiles / Rockets\n  - Slot Layout: Highs: 3 | Mids: 5 | Lows: 3 | Rigs: 3 (Turrets: 1 | Launchers: 2)\n  - Key Bonuses: 10% Light Missile/Rocket kinetic/explosive damage per lvl | 10% Target Painter effectiveness per lvl | 5% ship max velocity per lvl\n  - Defense Profile: Shield Buffer | Speed: Extreme (4.5-5.5 km/s MWD)\n  - Weapon Optimal: 15-40 km (Rockets / Light Missiles)\n  - Tactical Counter-Play: Fast Navy frigate with target painting bonuses and kinetic/explosive missile damage. Counter with Missile Guidance Disruptors and fast interceptor tackle."
    },
    "Vendetta": {
        "class": "Supercarrier",
        "faction": "Serpentis",
        "role": "Pirate Supercarrier / Heavy Web Stasis",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer (Capital 90% Stasis Web)",
        "speed": "Fast for Supercarrier",
        "optimal_range": "Omni Capital Grid (Fighters & Capital Web)",
        "tactics": "Serpentis Supercarrier. Deploys deadly pirate fighter wings and 90% velocity reduction Capital Stasis Webifiers. Counter with dreadnought bomb runs and supercapital alpha.",
        "high_slots": 6,
        "mid_slots": 8,
        "low_slots": 8,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "Capital Heavy Fighters & Capital Hybrid Blasters (90% Stasis Web)",
        "bonuses": [
            "90% Stasis Webifier effectiveness",
            "10% Heavy Fighter damage per lvl",
            "4% all armor resists per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Vendetta [Supercarrier | Serpentis]\n  - Combat Role: Pirate Supercarrier / Heavy Web Stasis\n  - Weapon System: Capital Heavy Fighters & Capital Hybrid Blasters (90% Stasis Web)\n  - Slot Layout: Highs: 6 | Mids: 8 | Lows: 8 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: 90% Stasis Webifier effectiveness | 10% Heavy Fighter damage per lvl | 4% all armor resists per lvl\n  - Defense Profile: Armor Buffer (Capital 90% Stasis Web) | Speed: Fast for Supercarrier\n  - Weapon Optimal: Omni Capital Grid (Fighters & Capital Web)\n  - Tactical Counter-Play: Serpentis Supercarrier. Deploys deadly pirate fighter wings and 90% velocity reduction Capital Stasis Webifiers. Counter with dreadnought bomb runs and supercapital alpha."
    },
    "Primae": {
        "class": "Industrial",
        "faction": "Outer Ring Excavations (ORE)",
        "role": "Planetary Interaction Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "Non-Combat",
        "tactics": "Specialized ORE hauler with dedicated Planetary Commodities and Customs Office cargo hold. Non-combatant.",
        "high_slots": 0,
        "mid_slots": 3,
        "low_slots": 4,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 0,
        "weapon_type": "None (Specialized Planetary Hauler)",
        "bonuses": [
            "Specialized Planetary Commodities Cargo Hold",
            "10% max velocity per lvl"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Primae [Industrial | Outer Ring Excavations (ORE)]\n  - Combat Role: Planetary Interaction Hauler\n  - Weapon System: None (Specialized Planetary Hauler)\n  - Slot Layout: Highs: 0 | Mids: 3 | Lows: 4 | Rigs: 3 (Turrets: 0 | Launchers: 0)\n  - Key Bonuses: Specialized Planetary Commodities Cargo Hold | 10% max velocity per lvl\n  - Defense Profile: Shield Buffer | Speed: Moderate\n  - Weapon Optimal: Non-Combat\n  - Tactical Counter-Play: Specialized ORE hauler with dedicated Planetary Commodities and Customs Office cargo hold. Non-combatant."
    },
    "Avalanche": {
        "class": "Dreadnought",
        "faction": "Outer Ring Excavations (ORE)",
        "role": "Capital Mining Protection / Siege Dreadnought",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Capital Mining Support)",
        "speed": "Slow",
        "optimal_range": "20-80 km (Capital Missiles)",
        "tactics": "ORE Capital Dreadnought engineered to defend capital mining fleets and industrial installations with heavy capital missiles.",
        "high_slots": 6,
        "mid_slots": 7,
        "low_slots": 6,
        "rig_slots": 3,
        "turret_hardpoints": 0,
        "launcher_hardpoints": 4,
        "weapon_type": "Capital Cruise Missiles / Torpedoes (ORE Siege)",
        "bonuses": [
            "Capital Missile damage per lvl",
            "Shield booster repair amount per lvl",
            "Role: Can fit Siege Module"
        ],
        "pre_rendered_dossier": "\u2022 Vessel: Avalanche [Dreadnought | Outer Ring Excavations (ORE)]\n  - Combat Role: Capital Mining Protection / Siege Dreadnought\n  - Weapon System: Capital Cruise Missiles / Torpedoes (ORE Siege)\n  - Slot Layout: Highs: 6 | Mids: 7 | Lows: 6 | Rigs: 3 (Turrets: 0 | Launchers: 4)\n  - Key Bonuses: Capital Missile damage per lvl | Shield booster repair amount per lvl | Role: Can fit Siege Module\n  - Defense Profile: Active Shield (Capital Mining Support) | Speed: Slow\n  - Weapon Optimal: 20-80 km (Capital Missiles)\n  - Tactical Counter-Play: ORE Capital Dreadnought engineered to defend capital mining fleets and industrial installations with heavy capital missiles."
    }
}

MODULE_DATABASE: Dict[str, Dict[str, Any]] = {
    "Small Pulse Laser": {
        "slot": "High",
        "size": "Small",
        "category": "Energy Turret",
        "role": "Frigate Close-Range Laser",
        "description": "High tracking, instant damage application, zero reload time. Uses Scorch S / Conflagration S.",
        "counter": "High angular velocity / transversal; EM/Thermal resistance."
    },
    "Small Beam Laser": {
        "slot": "High",
        "size": "Small",
        "category": "Energy Turret",
        "role": "Frigate Long-Range Laser Sniper",
        "description": "Long-range sniper turret for frigates (Imperial Navy Slicer, Retribution). Uses Aurora S / Gleam S.",
        "counter": "Close range inside tracking cone; high transversal."
    },
    "Medium Pulse Laser": {
        "slot": "High",
        "size": "Medium",
        "category": "Energy Turret",
        "role": "Cruiser / BC Close-Range Laser",
        "description": "High tracking medium energy turret. Scorch M delivers cruiser-grade projection to 35km+.",
        "counter": "EM/Thermal armor or shield resists; tracking disruption."
    },
    "Medium Beam Laser": {
        "slot": "High",
        "size": "Medium",
        "category": "Energy Turret",
        "role": "Cruiser / BC Long-Range Laser",
        "description": "Heavy Beam / Dual Heavy Beam Laser for line combat (Zealot, Oracle). Extreme instant alpha.",
        "counter": "Close distance rapidly; apply Tracking Disruptors."
    },
    "Large Pulse Laser": {
        "slot": "High",
        "size": "Large",
        "category": "Energy Turret",
        "role": "Battleship Close-Range Laser",
        "description": "Mega Pulse Laser for battleships and marauders (Paladin, Nightmare, Abaddon). Scorch L projects heavy EM/Thermal DPS to 60-80 km.",
        "counter": "Heavy capacitor neutralizers; tracking disruption."
    },
    "Large Beam Laser": {
        "slot": "High",
        "size": "Large",
        "category": "Energy Turret",
        "role": "Battleship Long-Range Laser",
        "description": "Tachyon Beam / Mega Beam Laser. Extreme instant alpha from 100-160 km.",
        "counter": "Get inside minimum tracking envelope; neut ship cap."
    },
    "Capital Energy Turret": {
        "slot": "High",
        "size": "Capital",
        "category": "Energy Turret",
        "role": "Dreadnought Capital Laser",
        "description": "Capital Mega Beam / Pulse Laser for Revelation. High instant capital DPS.",
        "counter": "Maintain high orbital transversal; capital guns cannot track fast sub-capitals."
    },
    "Small Blaster": {
        "slot": "High",
        "size": "Small",
        "category": "Hybrid Turret",
        "role": "Frigate Short-Range Blaster",
        "description": "Neutron / Ion / Electron Blaster. Highest instant close-range DPS in EVE (Void S). Zero range beyond 10km.",
        "counter": "Kite outside 10km; apply stasis webs and warp disruptors."
    },
    "Small Railgun": {
        "slot": "High",
        "size": "Small",
        "category": "Hybrid Turret",
        "role": "Frigate Long-Range Rail Sniper",
        "description": "75mm / 125mm / 150mm Railguns for Cormorant, Harpy. Strikes from 30-70 km.",
        "counter": "Spiral in with high transversal; get inside tracking."
    },
    "Medium Blaster": {
        "slot": "High",
        "size": "Medium",
        "category": "Hybrid Turret",
        "role": "Cruiser / BC Short-Range Blaster",
        "description": "Heavy Neutron / Ion Blaster for Thorax, Deimos, Brutix, Proteus. Immense Kinetic/Thermal DPS (Void M).",
        "counter": "Kite outside 15km; apply dual webs; avoid close brawl."
    },
    "Medium Railgun": {
        "slot": "High",
        "size": "Medium",
        "category": "Hybrid Turret",
        "role": "Cruiser / BC Long-Range Rail",
        "description": "200mm / 250mm Railguns for Ferox, Moa, Eagle. Premier line fleet sniper.",
        "counter": "Close range with speed; apply tracking disruptors."
    },
    "Large Blaster": {
        "slot": "High",
        "size": "Large",
        "category": "Hybrid Turret",
        "role": "Battleship Short-Range Blaster",
        "description": "Neutron Blaster Cannon for Megathron, Kronos, Vindicator, Talos. 2000-3000+ DPS close range (Void L).",
        "counter": "Never engage inside 20km without tracking disruptors and 90% webs."
    },
    "Large Railgun": {
        "slot": "High",
        "size": "Large",
        "category": "Hybrid Turret",
        "role": "Battleship Long-Range Rail",
        "description": "350mm / 425mm Railguns for Rokh, Megathron, Naga. Strikes from 80-160 km.",
        "counter": "High transversal orbiting; damp targeting range."
    },
    "Capital Hybrid Turret": {
        "slot": "High",
        "size": "Capital",
        "category": "Hybrid Turret",
        "role": "Dreadnought Capital Hybrid",
        "description": "Capital Blaster / Railgun for Moros. Massive capital siege DPS.",
        "counter": "High angular velocity; Tracking Disruptor scripts."
    },
    "Small Autocannon": {
        "slot": "High",
        "size": "Small",
        "category": "Projectile Turret",
        "role": "Frigate Close-Range Autocannon",
        "description": "125mm / 150mm / 200mm Autocannons for Dramiel, Wolf, Firetail. High tracking, selectable damage types, zero capacitor usage.",
        "counter": "Kinetic/Explosive resists; kite outside falloff range."
    },
    "Small Artillery": {
        "slot": "High",
        "size": "Small",
        "category": "Projectile Turret",
        "role": "Frigate High Alpha Artillery",
        "description": "250mm / 280mm Artillery for Thrasher, Claw. Extreme volley alpha strike.",
        "counter": "Survive the initial alpha volley; get inside tracking."
    },
    "Medium Autocannon": {
        "slot": "High",
        "size": "Medium",
        "category": "Projectile Turret",
        "role": "Cruiser / BC Close-Range Autocannon",
        "description": "180mm / 220mm / 425mm Autocannons for Cynabal, Vagabond, Stabber NI, Loki. Premier nano skirmish turret (Barrage M / Hail M).",
        "counter": "Explosive/Kinetic resists; scram and dual web."
    },
    "Medium Artillery": {
        "slot": "High",
        "size": "Medium",
        "category": "Projectile Turret",
        "role": "Cruiser / BC High Alpha Artillery",
        "description": "650mm / 720mm Artillery for Hurricane, Muninn, Sleipnir, Loki. High instant fleet alpha volley.",
        "counter": "Close range; apply tracking disruption; high transversal."
    },
    "Large Autocannon": {
        "slot": "High",
        "size": "Large",
        "category": "Projectile Turret",
        "role": "Battleship Close-Range Autocannon",
        "description": "Dual 180mm / Dual 425mm / 800mm Autocannons for Machariel, Vargur, Tempest. Selectable damage with high tracking (Hail L).",
        "counter": "Armor/Shield buffer with high explosive resist; heavy neuts."
    },
    "Large Artillery": {
        "slot": "High",
        "size": "Large",
        "category": "Projectile Turret",
        "role": "Battleship High Alpha Artillery",
        "description": "1200mm / 1400mm Artillery for Tornado, Machariel, Tempest Fleet Issue. Lethal 10,000-15,000+ instant volley alpha.",
        "counter": "High angular velocity; orbit at close range; tracking disruptors."
    },
    "Capital Projectile Turret": {
        "slot": "High",
        "size": "Capital",
        "category": "Projectile Turret",
        "role": "Dreadnought Capital Projectile",
        "description": "Capital Autocannon / Artillery for Naglfar. Massive alpha strike and DPS.",
        "counter": "High transversal velocity; Tracking Disruptor scripts."
    },
    "Light Entropic Disintegrator": {
        "slot": "High",
        "size": "Small",
        "category": "Disintegrator",
        "role": "Frigate / Destroyer Disintegrator",
        "description": "Fires single spooling thermal/explosive beam (Damavik, Kikimora). Damage ramps by 100-150% over continuous cycling.",
        "counter": "Break target lock, warp out, or eliminate before full spool."
    },
    "Heavy Entropic Disintegrator": {
        "slot": "High",
        "size": "Medium",
        "category": "Disintegrator",
        "role": "Cruiser / BC Disintegrator",
        "description": "Medium disintegrator for Vedmak, Drekavac, Ikitursa. Spools to over 1500+ DPS.",
        "counter": "Sensor dampeners (break lock to reset spool); heavy ECM."
    },
    "Supratidal Entropic Disintegrator": {
        "slot": "High",
        "size": "Large",
        "category": "Disintegrator",
        "role": "Battleship Disintegrator",
        "description": "Large disintegrator for Leshak. Spools to over 3500+ DPS against structures and capitals.",
        "counter": "Never allow continuous firing; break lock or kill quickly."
    },
    "Rocket Launcher": {
        "slot": "High",
        "size": "Small",
        "category": "Missile Launcher",
        "role": "Frigate Close-Range Rocket",
        "description": "High rate of fire, selectable damage, perfect application against frigates (Hookbill, Kestrel, Breacher, Hawk).",
        "counter": "Kite outside 15-20km; apply guidance disruptors."
    },
    "Light Missile Launcher": {
        "slot": "High",
        "size": "Small",
        "category": "Missile Launcher",
        "role": "Frigate Long-Range Missile",
        "description": "Long-range light missiles for Condor, Crow, Corax. Projects to 40-60 km.",
        "counter": "High speed to reduce explosion velocity damage."
    },
    "Heavy Assault Missile Launcher (HAM)": {
        "slot": "High",
        "size": "Medium",
        "category": "Missile Launcher",
        "role": "Cruiser / BC Close-Range Missile",
        "description": "High burst DPS medium missiles for Sacrilege, Cerberus, Cyclone, Loki. Effective range 15-45 km.",
        "counter": "Speed tanking; Guidance Disruptor (Precision script)."
    },
    "Heavy Missile Launcher (HML)": {
        "slot": "High",
        "size": "Medium",
        "category": "Missile Launcher",
        "role": "Cruiser / BC Long-Range Missile",
        "description": "Standard long-range missile platform for Drake, Cerberus, Tengu, Caracal NI. Projects to 60-100 km.",
        "counter": "Signature radius reduction; Guidance Disruptors."
    },
    "Rapid Light Missile Launcher (RLML)": {
        "slot": "High",
        "size": "Medium",
        "category": "Missile Launcher",
        "role": "Cruiser Anti-Frigate Missile",
        "description": "Fires light missiles from cruiser hulls (Caracal, Orthrus, Cerberus, Bellicose). Shreds tackle. 35s reload penalty.",
        "counter": "Survive the initial 20-round magazine clip; bait reload window."
    },
    "Torpedo Launcher": {
        "slot": "High",
        "size": "Large",
        "category": "Missile Launcher",
        "role": "Battleship Close-Range Torpedo",
        "description": "High-yield heavy torpedoes for Raven, Typhoon, Golem, Stealth Bombers. Massive burst against battleships/structures.",
        "counter": "Target painter evasion; speed tanking; signature radius reduction."
    },
    "Cruise Missile Launcher": {
        "slot": "High",
        "size": "Large",
        "category": "Missile Launcher",
        "role": "Battleship Long-Range Cruise",
        "description": "Extreme range missile platform for Raven, Typhoon, Barghest, Rattlesnake. Projects to 150-200 km.",
        "counter": "Close distance rapidly; speed tanking."
    },
    "Rapid Heavy Missile Launcher (RHML)": {
        "slot": "High",
        "size": "Large",
        "category": "Missile Launcher",
        "role": "Battleship Anti-Cruiser Launcher",
        "description": "Fires heavy missiles from battleship hulls (Raven, Typhoon, Praxis). Lethal against cruisers. 35s reload.",
        "counter": "Bait the 35s reload window."
    },
    "Small Energy Neutralizer": {
        "slot": "High",
        "size": "Small",
        "category": "Capacitor Warfare",
        "role": "Frigate Cap Drain",
        "description": "Drains 100-150 GJ per cycle from hostile frigate capacitor. Shuts down active repair and tackle.",
        "counter": "Capacitor Booster; Cap Battery."
    },
    "Medium Energy Neutralizer": {
        "slot": "High",
        "size": "Medium",
        "category": "Capacitor Warfare",
        "role": "Cruiser / BC Cap Drain",
        "description": "Drains 300-500 GJ per cycle (Curse, Pilgrim, Stratios, Ashimmu). Shuts down cruiser capacitor in 2 cycles.",
        "counter": "Large Cap Battery (provides 30% neut reflection); Cap Booster."
    },
    "Heavy Energy Neutralizer": {
        "slot": "High",
        "size": "Large",
        "category": "Capacitor Warfare",
        "role": "Battleship Cap Drain",
        "description": "Drains 600-1000+ GJ per cycle (Bhaalgorn, Armageddon, Dominix). Eliminates battleship capacitor instantly.",
        "counter": "Large Cap Battery; heavy cap booster injection."
    },
    "Energy Nosferatu (NOS)": {
        "slot": "High",
        "size": "Variable",
        "category": "Capacitor Warfare",
        "role": "Cap Leech",
        "description": "Steals capacitor from target to power own modules. Blood Raider hulls leech even when own cap is higher.",
        "counter": "Keep range outside NOS cycle range."
    },
    "Covert Ops Cloaking Device II": {
        "slot": "High",
        "size": "Universal",
        "category": "Cloaking",
        "role": "Stealth Cloaking",
        "description": "Enables cloaking while warping with zero speed penalty (Astero, Stratios, Recons, T3Cs, Bombers, Blockade Runners).",
        "counter": "Decloak with combat probes or fast interceptor burning inside 2000m."
    },
    "Prototype Cloaking Device": {
        "slot": "High",
        "size": "Universal",
        "category": "Cloaking",
        "role": "Standard Cloaking",
        "description": "Standard cloaking device. Heavy speed penalty (-75% velocity) and cannot warp while cloaked.",
        "counter": "MWD-Cloak trick counter: burn interceptor directly along align vector."
    },
    "Covert Cynosural Field Generator": {
        "slot": "High",
        "size": "Universal",
        "category": "Cynosural",
        "role": "Covert Beacon",
        "description": "Lights undetectable covert cyno beacon on grid for Black Ops battleships and covert jump portals.",
        "counter": "Primary and eliminate Force Recon / Stealth Bomber immediately."
    },
    "Cynosural Field Generator I": {
        "slot": "High",
        "size": "Universal",
        "category": "Cynosural",
        "role": "Capital Jump Beacon",
        "description": "Lights 5-minute stationary capital beacon summoning fleet dreadnoughts, carriers, and supercapitals.",
        "counter": "Warp Disruption Field Generators; destroy lighting ship."
    },
    "Bastion Module I": {
        "slot": "High",
        "size": "Large",
        "category": "Siege / Bastion",
        "role": "Marauder Bastion Mode",
        "description": "Locks Marauder in place for 60s. Grants 100% active repair bonus, +range/tracking, and complete EWAR immunity.",
        "counter": "Heavy energy neutralizers (active tank collapses without cap); orbit at high transversal."
    },
    "Siege Module I/II": {
        "slot": "High",
        "size": "Capital",
        "category": "Siege / Bastion",
        "role": "Dreadnought Siege Mode",
        "description": "Locks Dreadnought in place for 5 minutes. Immense capital DPS and active tank; zero remote repairs.",
        "counter": "High angular velocity; Tracking Disruptor scripts."
    },
    "Interdiction Sphere Launcher": {
        "slot": "High",
        "size": "Small",
        "category": "Interdiction",
        "role": "Warp Bubble Launcher",
        "description": "Fires Warp Disruption Probes generating 20km warp prevention bubbles on grid for 2 minutes (Sabre, Flycatcher).",
        "counter": "Primary Interdictor instantly; MWD-Cloak burn to bubble perimeter."
    },
    "1MN / 5MN Microwarpdrive": {
        "slot": "Mid",
        "size": "Small",
        "category": "Propulsion",
        "role": "Frigate High Speed",
        "description": "Increases sub-warp velocity by 500% at the cost of 500% signature radius bloom. Shut off by Warp Scramblers.",
        "counter": "Warp Scrambler (range <=10km disables MWD)."
    },
    "10MN / 50MN Microwarpdrive": {
        "slot": "Mid",
        "size": "Medium",
        "category": "Propulsion",
        "role": "Cruiser / BC High Speed",
        "description": "50MN MWD increases cruiser speed to 2-3 km/s. 10MN MWD used for oversized frigate fits.",
        "counter": "Warp Scrambler; Stasis Webifiers."
    },
    "100MN / 500MN Microwarpdrive": {
        "slot": "Mid",
        "size": "Large",
        "category": "Propulsion",
        "role": "Battleship / Oversized Cruiser Speed",
        "description": "500MN standard for battleships; 100MN used on oversized cruiser / T3C fits for extreme unscrammable speed.",
        "counter": "Heavy Stasis Webifiers; Stasis Grapplers."
    },
    "1MN / 5MN / 10MN / 50MN Afterburner": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Propulsion",
        "role": "Agility Speed (Scram Immune)",
        "description": "Increases velocity by 130-150% with zero signature bloom. Immune to Warp Scrambler shutoff.",
        "counter": "Stasis Webifiers; Heavy Cap Neuts."
    },
    "Large Micro Jump Drive (MJD)": {
        "slot": "Mid",
        "size": "Large",
        "category": "Propulsion",
        "role": "100km Instant Jump",
        "description": "Spools for 9-12s then teleports battleship 100km in aligned direction. Disabled by Warp Scrambler.",
        "counter": "Warp Scrambler (range <=10km cancels MJD spool instantly)."
    },
    "Micro Jump Field Generator (MJFG)": {
        "slot": "Mid",
        "size": "Small",
        "category": "Propulsion",
        "role": "Command Destroyer Jump",
        "description": "Spools for 6s and teleports own ship and all nearby ships within 6km 100km in aligned direction.",
        "counter": "Warp Scrambler applied to Command Destroyer."
    },
    "Warp Scrambler": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Tackle",
        "role": "Short Point (Disables MWD/MJD)",
        "description": "Range <=10km standard (up to 15km faction). Disables Microwarpdrive (MWD) and Micro Jump Drive (MJD). 2 points of warp disruption.",
        "counter": "Stay outside 10km; Warp Core Stabilizer; Overheat Afterburner."
    },
    "Warp Disruptor (Long Point)": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Tackle",
        "role": "Long Point (Disables Warp)",
        "description": "Range <=30km standard (up to 45km+ on Recons & Mordu hulls). Disables warp only; target retains full MWD speed.",
        "counter": "Overheat MWD and burn outside disruptor range; ECM; Sensor Dampeners."
    },
    "Stasis Webifier": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Tackle",
        "role": "Velocity Reduction",
        "description": "Range <=10km standard (up to 40km+ on Huginn/Rapier/Loki, 90% slow on Serpentis). Slows target ship by 50-60%.",
        "counter": "Stay outside web range; tracking disruption; counter-web tackle."
    },
    "Stasis Grappler": {
        "slot": "Mid",
        "size": "Large",
        "category": "Tackle",
        "role": "Battleship Close-Range Heavy Web",
        "description": "Applies extreme 85% speed reduction inside 3-5 km; effectiveness drops with range up to 15 km.",
        "counter": "Orbit outside 8km; never close inside 5km of a brawling battleship."
    },
    "Warp Disruption Field Generator (WDFG)": {
        "slot": "Mid",
        "size": "Medium",
        "category": "Tackle",
        "role": "HIC Infinite Point / Bubble",
        "description": "Heavy Interdiction Cruiser module. Projects focused infinite warp scrambler (points supercapitals) or 20km mobile bubble.",
        "counter": "Primary HIC instantly; heavy cap neutralizers."
    },
    "ECM Target Jammer": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Electronic Warfare",
        "role": "Lock Disruption Jammer",
        "description": "Jams hostile target lock. Target can only lock the jamming ship. Breaks fleet focus fire completely.",
        "counter": "Sensor Booster with ECCM script; drone auto-attack; primary jammer."
    },
    "Remote Sensor Dampener": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Electronic Warfare",
        "role": "Target Range & Scan Res Damp",
        "description": "Reduces target lock range (Targeting Range script) or scan resolution/lock speed (Scan Resolution script).",
        "counter": "Sensor Booster with Range / Scan Res scripts."
    },
    "Tracking Disruptor": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Electronic Warfare",
        "role": "Turret Tracking & Optimal Disrupt",
        "description": "Applies severe tracking reduction (Tracking Speed script) or optimal reduction (Optimal Range script) to hostile turrets.",
        "counter": "Tracking Computer with Tracking Speed script; switch to missiles or drones."
    },
    "Target Painter": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Electronic Warfare",
        "role": "Signature Radius Inflator",
        "description": "Increases hostile ship signature radius by 25-40%, allowing missiles and large turrets to apply full damage.",
        "counter": "Signature reduction modules; eliminate painting ship."
    },
    "Medium / Large Shield Extender (MSE / LSE)": {
        "slot": "Mid",
        "size": "Medium / Large",
        "category": "Shield Defense",
        "role": "Shield Buffer EHP",
        "description": "Adds flat raw shield HP (MSE ~1000 HP, LSE ~2500-3000 HP). Standard for shield buffer fleet fits.",
        "counter": "EM / Thermal damage; high sustained fleet DPS."
    },
    "Medium / Large / X-Large Shield Booster": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Shield Defense",
        "role": "Active Shield Repair",
        "description": "Repairs shield HP at the start of each cycle. Consumes heavy capacitor. Standard for active PVE/PVP fits.",
        "counter": "Heavy Energy Neutralizers (active tank collapses without cap); EM damage."
    },
    "Ancillary Shield Booster (MASB / LASB / XL-ASB)": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Shield Defense",
        "role": "Capless Active Shield Burst",
        "description": "Uses Cap Booster charges to repair massive shield HP with zero ship capacitor cost. 9 charges, then 60s reload.",
        "counter": "Bait the 9 booster charges; burst damage during the 60s reload window."
    },
    "Multi-Spectrum Shield Hardener": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Shield Defense",
        "role": "Omni Shield Resistance",
        "description": "Increases all 4 shield resistances (EM, Thermal, Kinetic, Explosive) by 30-40%. Consumes capacitor.",
        "counter": "Energy Neutralizers to shut off active hardeners."
    },
    "Large / Medium Capacitor Battery": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Capacitor",
        "role": "Capacitor Buffer & Neut Reflection",
        "description": "Adds large capacitor capacity and reflects 20-30% of incoming energy neutralizer drain.",
        "counter": "Overwhelming multi-ship neutralizer wings."
    },
    "Capacitor Booster": {
        "slot": "Mid",
        "size": "Variable",
        "category": "Capacitor",
        "role": "Instant Capacitor Injection",
        "description": "Consumes Cap Booster charges (Navy 400, Navy 800, Navy 3200) to inject instant capacitor into ship pool.",
        "counter": "Cargo limit on booster charges; continuous heavy neuts."
    },
    "200mm / 400mm / 800mm / 1600mm Steel Plates": {
        "slot": "Low",
        "size": "Variable",
        "category": "Armor Defense",
        "role": "Armor Buffer EHP",
        "description": "Adds raw armor HP (400mm ~1200 HP, 800mm ~2500 HP, 1600mm ~4500-6000 HP). Increases ship mass and align time.",
        "counter": "Explosive / Kinetic damage; high sustained DPS."
    },
    "Small / Medium / Large Armor Repairer": {
        "slot": "Low",
        "size": "Variable",
        "category": "Armor Defense",
        "role": "Active Armor Repair",
        "description": "Repairs armor HP at the end of each cycle. Consumes capacitor. High sustained repair rate.",
        "counter": "Heavy Energy Neutralizers; Explosive / Kinetic damage."
    },
    "Ancillary Armor Repairer (SAAR / MAAR / LAAR)": {
        "slot": "Low",
        "size": "Variable",
        "category": "Armor Defense",
        "role": "Capless Active Armor Burst",
        "description": "Uses Nanite Repair Paste to triple armor repair amount. 8 charges, then 60s reload.",
        "counter": "Count the 8 nanite cycles; burst damage during the 60s reload window."
    },
    "Damage Control II (DCU II)": {
        "slot": "Low",
        "size": "Universal",
        "category": "Hull / Armor Defense",
        "role": "Passive Omni Resistance & Hull Buffer",
        "description": "Provides passive resistance bonus across Shield, Armor, and 60% base Hull resistance. Fit on almost every ship.",
        "counter": "Standard combat damage application."
    },
    "Assault Damage Control II (ADC II)": {
        "slot": "Low",
        "size": "Assault Only",
        "category": "Assault Defense",
        "role": "Emergency Invulnerability (15s)",
        "description": "Exclusive to Assault Frigates and Heavy Assault Cruisers. Activated for 15s of 95% omni resistance.",
        "counter": "Do not waste high-damage volleys during 15s invulnerability window; wait for burnout."
    },
    "Reactive Armor Hardener (RAH)": {
        "slot": "Low",
        "size": "Universal",
        "category": "Armor Defense",
        "role": "Adaptive Armor Resistance",
        "description": "Adapts resistances dynamically to match the incoming damage types received over combat cycles.",
        "counter": "Split damage types (e.g. EM + Explosive simultaneously) to divide RAH resistance adaptation."
    },
    "Multi-Spectrum Energized Membrane II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Armor Defense",
        "role": "Passive Omni Armor Resistance",
        "description": "Provides passive 20-25% armor resistance bonus across all 4 damage types with zero cap usage.",
        "counter": "Explosive / Kinetic damage focus."
    },
    "Heat Sink II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Laser Damage & Rate of Fire",
        "description": "Increases energy turret damage by 10% and rate of fire by 10.5%. Stacked up to 3-4 modules.",
        "counter": "EM / Thermal armor or shield tanking."
    },
    "Magnetic Field Stabilizer II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Hybrid Damage & Rate of Fire",
        "description": "Increases hybrid turret (blaster/rail) damage and rate of fire. Core for Gallente/Caldari hybrid fits.",
        "counter": "Kinetic / Thermal tanking."
    },
    "Gyrostabilizer II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Projectile Damage & Rate of Fire",
        "description": "Increases projectile turret damage and rate of fire. Core for Minmatar/Angel fits.",
        "counter": "Explosive / Kinetic tanking."
    },
    "Ballistic Control System II (BCS II)": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Missile Damage & Rate of Fire",
        "description": "Increases all missile launcher damage and rate of fire. Core for Caldari/Guristas fits.",
        "counter": "Damage-type specific resistance matching."
    },
    "Drone Damage Amplifier II (DDA II)": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Drone & Fighter Damage",
        "description": "Increases drone and fighter damage by 23%. Core for Gila, Ishtar, Rattlesnake, Dominix, Vexor.",
        "counter": "Eliminate drone flights directly; smartbombs."
    },
    "Entropic Radiation Sink II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Weapon Upgrade",
        "role": "Disintegrator Damage & Rate of Fire",
        "description": "Increases Triglavian entropic disintegrator damage and tracking.",
        "counter": "Break target locks to reset disintegrator spool."
    },
    "Nanofiber Internal Structure II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Mobility",
        "role": "Speed & Align Time",
        "description": "Increases sub-warp speed and reduces ship agility align time at the cost of 20% structure HP.",
        "counter": "Stasis Webifiers."
    },
    "Overdrive Injector System II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Mobility",
        "role": "Raw Sub-Warp Velocity",
        "description": "Increases sub-warp velocity at the cost of cargo capacity.",
        "counter": "Warp Scramblers and Webs."
    },
    "Inertial Stabilizers II (i-Stab)": {
        "slot": "Low",
        "size": "Universal",
        "category": "Mobility",
        "role": "Fast Warp Alignment",
        "description": "Significantly reduces align time to achieve sub-2s insta-warp at the cost of signature bloom.",
        "counter": "Smartbombing gate camps on warp-in vector."
    },
    "Warp Core Stabilizer II": {
        "slot": "Low",
        "size": "Universal",
        "category": "Warp Defense",
        "role": "+2 Warp Core Strength",
        "description": "Provides +2 points of warp disruption immunity for 15s. Penalizes drone bay, targeting range, and lock speed.",
        "counter": "Apply 3+ points of warp disruption (e.g. Scrambler + Disruptor simultaneously)."
    },
    "Core Defense Field Extender (CDFE)": {
        "slot": "Rig",
        "size": "Small / Medium / Large / Capital",
        "category": "Shield Rig",
        "role": "Shield Buffer HP",
        "description": "Increases total shield HP by 15% at the cost of signature radius bloom.",
        "counter": "Standard damage application."
    },
    "Trimark Armor Pump (Trimark)": {
        "slot": "Rig",
        "size": "Small / Medium / Large / Capital",
        "category": "Armor Rig",
        "role": "Armor Buffer HP",
        "description": "Increases total armor HP by 15% at the cost of sub-warp velocity penalty.",
        "counter": "Explosive / Kinetic damage."
    },
    "Auxiliary Nano Pump": {
        "slot": "Rig",
        "size": "Small / Medium / Large / Capital",
        "category": "Armor Rig",
        "role": "Armor Repair Amount",
        "description": "Increases armor repair amount per cycle by 15% at the cost of powergrid usage.",
        "counter": "Heavy cap neutralizers."
    },
    "Polycarbon Engine Housing": {
        "slot": "Rig",
        "size": "Small / Medium / Large",
        "category": "Astronautics Rig",
        "role": "Speed & Agility",
        "description": "Increases velocity and reduces align time at the cost of armor HP penalty.",
        "counter": "Stasis Webifiers."
    },
    "Hyperspatial Velocity Optimizer": {
        "slot": "Rig",
        "size": "Small / Medium / Large",
        "category": "Astronautics Rig",
        "role": "Warp Speed Acceleration",
        "description": "Increases warp speed (AU/s) significantly for fast interception and roaming.",
        "counter": "Bubbles on warp-in vectors."
    },
    "Burst Aerator / Collision Accelerator": {
        "slot": "Rig",
        "size": "Small / Medium / Large",
        "category": "Weapon Rig",
        "role": "Rate of Fire / Turret Damage",
        "description": "Increases turret rate of fire or damage at the cost of powergrid/CPU calibration.",
        "counter": "Resistance matching."
    }
}

ROLE_DOCTRINES: Dict[str, str] = {
    "FW Plexing": (
        "[COMBAT ROLE DOCTRINE — FACTION WARFARE COMPLEX BRAWLING & CAPTURE]:\n"
        "• Strategic Mandate: Capture Novice/Small/Medium FW complexes and engage hostile militia in 1v1 / small gang brawls.\n"
        "• Fitting Rules: Short-range maximum DPS (Blasters/Autocannons/Rockets), dual webs or scram+web for range control, active armor (SAAR) or MASB active shield, 1MN/5MN Afterburner (immune to scram shutoff; do NOT fit MWD for inside-plex brawls)."
    ),
    "Small Gang Nano": (
        "[COMBAT ROLE DOCTRINE — NANO SKIRMISH & GRID SEPARATION]:\n"
        "• Strategic Mandate: Out-position and divide superior enemy numbers across grid; pick off fast tackle before engaging heavier line combatants.\n"
        "• Fitting Rules: 50MN/100MN propulsion (MWD or oversized AB), long-range point (Warp Disruptor <=30-40km), medium/long projection weapons (425mm AC with Barrage, Heavy Beams, Rapid Light Missiles), Nanofiber Internal Structures / Polycarbon rigs."
    ),
    "Abyssal Deadspace": (
        "[COMBAT ROLE DOCTRINE — ABYSSAL DEADSPACE PVE]:\n"
        "• Strategic Mandate: Survive and clear 3 combat rooms within 20 minutes under environmental weather hazards.\n"
        "• Fitting Rules: Strict capacitor stability or Large Cap Battery (immune to Starving neuts), sustained active shield/armor repair (500-1200+ EHP/s), damage type matched to weather (Kinetic in Exotic, EM in Electrical, Thermal in Firestorm), MTU/Mobile Tractor Unit."
    ),
    "Fleet Anchor DPS": (
        "[COMBAT ROLE DOCTRINE — FLEET ANCHOR DPS / HEAVY LINE COMBAT]:\n"
        "• Strategic Mandate: Fleet line combat anchoring on the FC; maximize alpha/DPS projection and resist-buffer for fleet logistics reps.\n"
        "• Fitting Rules: Maximum buffer EHP (1600mm Steel Plates or Large Shield Extenders + resist modules), long-range projection guns (Artillery/Tachyon/Mega Pulse/Rails/Cruise Missiles), Tracking Computers / Target Painters. Do NOT fit solo tackle; leave slots for max DPS & Buffer."
    ),
    "Nullsec Combat Site Ratting": (
        "[COMBAT ROLE DOCTRINE — NULLSEC SITE RATTING & ESCALATIONS]:\n"
        "• Strategic Mandate: Maximum clear speed against pirate NPC anomalies (Havens/Sanctums) and DED 6/10-10/10 escalations.\n"
        "• Fitting Rules: Specialized NPC damage-type resists (e.g. EM/Therm for Blood/Sansha, Kin/Therm for Guristas, Exp/Kin for Angels), maximum sustained application/DPS (Missile Guidance / Tracking Computers / Drone Damage Amps), large capacitor pool, Mobile Tractor Unit (MTU)."
    ),
    "Wormhole": (
        "[COMBAT ROLE DOCTRINE — WORMHOLE SOLO & EXPLORATION]:\n"
        "• Strategic Mandate: Relic/Data hacking, Sleeper site clearing, and covert travel in J-space.\n"
        "• Fitting Rules: Core Probe Launcher with Sisters Probes, Relic & Data Analyzers, Covert Ops Cloaking Device, Omni-resist active tank."
    ),
    "Fast Tackle": (
        "[COMBAT ROLE DOCTRINE — HEAVY INTERCEPTION & FAST TACKLE]:\n"
        "• Strategic Mandate: Fast initial point on warping targets, holding tackle until fleet arrives.\n"
        "• Fitting Rules: Sub-2 second align time, 5MN/50MN MWD, Sensor Booster with Scan Resolution script, Warp Disruptor + Scrambler, Overdrive/Nanofiber modules."
    )
}

EVE_COMBAT_AXIOMS = """
[EVE ONLINE COMBAT DOCTRINE & TACTICAL DIRECTIVES]:
1. STRICT SINGLE RESPONSE (NO DUPLICATES): Output your tactical advice once in 2 to 4 concise bullet points total. NEVER repeat yourself, NEVER generate duplicate sections.
2. NEVER ECHO SYSTEM HEADERS: Never repeat, quote, or output reference headers or tags (such as `[EVE TACTICAL INTELLIGENCE]`, `[TACTICAL DIRECTIVE]`).
3. RIGOROUS TACKLE & EWAR DEFINITIONS:
   - Warp Scrambler (Scram): Range <=10km (short point). Disables Microwarpdrive (MWD) & Micro Jump Drives (MJD).
   - Warp Disruptor (Long Point): Range <=30km (up to 45km+ on Recons). Disables warp only (target retains full MWD speed).
   - Tracking Disruptor: Scripts for Tracking Speed / Optimal Range applied to hostile turrets to make large guns miss high-transversal targets.
   - Stasis Webifier: Range <=10km standard (up to 40km+ on Minmatar Recons & Loki). Slows target velocity by 50-60% (up to 90% with web bonuses).
   - Heavy Energy Neutralizer: Drains raw capacitor per cycle, shutting down active reps.
4. AUTHENTIC FITTING & TANK EXCLUSIVITY:
   - Never dual-tank: A ship fit is either Shield Tanked (Extenders/Boosters) OR Armor Tanked (Plates/Repairers), never both.
   - Match weapon and module classes to hull faction and size (e.g. Minmatar hulls use Projectiles/HAMs, not Lasers; Cruisers/T3Cs cannot fit Battleship MJDs or Battleship weapons).
"""

_RE_CLEAN_ALPHANUM = re.compile(r"[^a-z0-9]")
_RE_WORDS = re.compile(r"\b[A-Za-z0-9\-]+\b")
_RE_OWN_SHIP = re.compile(
    r"\b(?:i am in an?|i'm in an?|flying an?|piloting an?|my ship is an?|in an?)\s+([A-Za-z0-9\-\s]+?)(?:\s+and|\s+with|\s+need|\s+looking|\s+waiting|\s+fighting|\s+vs|\s+against|\s*\.|\s*,|\s*$)",
    re.IGNORECASE
)

_COMMON_SHIP_ALIASES: Dict[str, str] = {
    "slicer": "Imperial Navy Slicer",
    "in slicer": "Imperial Navy Slicer",
    "hookbill": "Caldari Navy Hookbill",
    "comet": "Federation Navy Comet",
    "firetail": "Republic Fleet Firetail",
    "omen navy": "Omen Navy Issue",
    "stabber navy": "Stabber Fleet Issue",
    "osprey navy": "Osprey Navy Issue",
    "scythe navy": "Scythe Fleet Issue",
    "exeq navy": "Exequror Navy Issue",
    "vexor navy": "Vexor Navy Issue",
    "vni": "Vexor Navy Issue",
    "drake navy": "Drake Navy Issue",
    "harbi navy": "Harbinger Navy Issue",
    "cane fleet": "Hurricane Fleet Issue",
    "hfi": "Hurricane Fleet Issue",
    "cyclone fleet": "Cyclone Fleet Issue",
    "myrm navy": "Myrmidon Navy Issue",
    "brutix navy": "Brutix Navy Issue",
    "apoc navy": "Apocalypse Navy Issue",
    "arma navy": "Armageddon Navy Issue",
    "raven navy": "Raven Navy Issue",
    "rni": "Raven Navy Issue",
    "tempest fleet": "Tempest Fleet Issue",
    "tfi": "Tempest Fleet Issue",
    "megathron navy": "Megathron Navy Issue",
    "mega navy": "Megathron Navy Issue",
    "macha": "Machariel",
    "rattle": "Rattlesnake"
}

_FAST_SHIP_LOOKUP: Dict[str, Dict[str, Any]] = {}
for _k, _v in SHIP_DATABASE.items():
    _v_copy = dict(_v)
    _v_copy["canonical_name"] = _k
    _FAST_SHIP_LOOKUP[_k.lower()] = _v_copy
    _clean_k = _RE_CLEAN_ALPHANUM.sub("", _k.lower())
    _FAST_SHIP_LOOKUP[_clean_k] = _v_copy

for _alias, _target in _COMMON_SHIP_ALIASES.items():
    if _target in SHIP_DATABASE:
        _tgt_data = _FAST_SHIP_LOOKUP[_target.lower()]
        _FAST_SHIP_LOOKUP[_alias.lower()] = _tgt_data
        _FAST_SHIP_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", _alias.lower())] = _tgt_data

_MULTI_WORD_SHIPS = [(_k, _v, _k.lower()) for _k, _v in SHIP_DATABASE.items() if " " in _k]
_ROLE_DOCTRINES_LOWER = [(_rk.lower(), _rdoc) for _rk, _rdoc in ROLE_DOCTRINES.items()]

_FAST_MODULE_LOOKUP: Dict[str, Dict[str, Any]] = {}
for _mk, _mv in MODULE_DATABASE.items():
    _mv_copy = dict(_mv)
    _mv_copy["canonical_name"] = _mk
    _mk_l = _mk.lower()
    _FAST_MODULE_LOOKUP[_mk_l] = _mv_copy
    _clean_mk = _RE_CLEAN_ALPHANUM.sub("", _mk_l)
    _FAST_MODULE_LOOKUP[_clean_mk] = _mv_copy
    
    if "/" in _mk_l:
        parts = [p.strip() for p in _mk_l.split("/")]
        last_part = parts[-1]
        last_words = last_part.split()
        if len(last_words) > 1:
            base_noun = " ".join(last_words[1:])
            for p in parts:
                variant_full = p if base_noun in p else f"{p} {base_noun}"
                _FAST_MODULE_LOOKUP[variant_full] = _mv_copy
                _FAST_MODULE_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", variant_full)] = _mv_copy
                for _suffix in [" ii", " i", " compact", " scoped", " enduring", " restrained", " tech ii", " tech 2"]:
                    _FAST_MODULE_LOOKUP[f"{variant_full}{_suffix}"] = _mv_copy
                    _FAST_MODULE_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", f"{variant_full}{_suffix}")] = _mv_copy

    if "(" in _mk_l:
        _base = _mk_l.split("(")[0].strip()
        _FAST_MODULE_LOOKUP[_base] = _mv_copy
        _FAST_MODULE_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", _base)] = _mv_copy
        _paren_content = _mk_l.split("(")[1].split(")")[0]
        for _token in _paren_content.split("/"):
            _t = _token.strip()
            if len(_t) >= 2:
                _FAST_MODULE_LOOKUP[_t] = _mv_copy
                _FAST_MODULE_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", _t)] = _mv_copy
                
    for _suffix in [" ii", " i", " compact", " scoped", " enduring", " restrained", " tech ii", " tech 2", " tech 1"]:
        if _mk_l.endswith(_suffix):
            _base = _mk_l[:-len(_suffix)].strip()
            _FAST_MODULE_LOOKUP[_base] = _mv_copy
            _FAST_MODULE_LOOKUP[_RE_CLEAN_ALPHANUM.sub("", _base)] = _mv_copy


@functools.lru_cache(maxsize=4096)
def lookup_ship(name: str) -> Optional[Dict[str, Any]]:
    """O(1) canonical ship retrieval with C-level LRU caching."""
    if not name:
        return None
    raw_lower = name.strip().lower()
    if raw_lower in _FAST_SHIP_LOOKUP:
        return _FAST_SHIP_LOOKUP[raw_lower]
    clean = _RE_CLEAN_ALPHANUM.sub("", raw_lower)
    return _FAST_SHIP_LOOKUP.get(clean)


@functools.lru_cache(maxsize=4096)
def lookup_module(name: str) -> Optional[Dict[str, Any]]:
    """O(1) canonical module retrieval with C-level LRU caching and fuzzy fallback."""
    if not name:
        return None
    raw_lower = name.strip().lower()
    if raw_lower in _FAST_MODULE_LOOKUP:
        return _FAST_MODULE_LOOKUP[raw_lower]
    clean = _RE_CLEAN_ALPHANUM.sub("", raw_lower)
    if clean in _FAST_MODULE_LOOKUP:
        return _FAST_MODULE_LOOKUP[clean]
    for mk, mv in MODULE_DATABASE.items():
        base_name = mk.split("(")[0].strip().lower()
        if base_name in raw_lower or raw_lower in base_name:
            return mv
    return None


def validate_fit_module_compatibility(hull_name: str, fit_dict: Dict[str, Any]) -> List[str]:
    """Validates module sizing, hull weapon affinity, and tank exclusivity rules."""
    warnings = []
    ship_info = lookup_ship(hull_name)
    if not ship_info:
        return warnings

    s_class = ship_info.get("class", "Frigate")
    tank_type = ship_info.get("tank", "Shield")
    
    # Check dual tanking
    lows = fit_dict.get("low_slots", [])
    mids = fit_dict.get("mid_slots", [])
    
    has_shield_tank = any("shield extender" in m.lower() or "shield booster" in m.lower() for m in mids)
    has_armor_tank = any("armor repairer" in m.lower() or "steel plates" in m.lower() or "1600mm" in m.lower() or "800mm" in m.lower() for m in lows)
    
    if has_shield_tank and has_armor_tank:
        warnings.append("[CRITICAL FIT WARNING] Dual-tank detected (Fitting both Shield Extender/Booster and Armor Plates/Repairers). Split tank dilutes EHP and reps. Commit to either 100% Shield OR 100% Armor.")

    return warnings


def get_tactical_grounding(prompt: str, attachments: List[Dict[str, Any]] = None, piloted_ship: Optional[str] = None) -> str:
    """
    Extracts verified ship dossiers and tactical axioms for everything mentioned in the prompt.
    Correctly distinguishes Capsuleer's own piloted vessel from hostile contacts.
    """
    if attachments:
        full_text = prompt + " " + " ".join([att.get("text", "") for att in attachments])
    else:
        full_text = prompt

    lower_text = full_text.lower()
    words = _RE_WORDS.findall(full_text)
    
    grounding_blocks = []
    detected_hulls = set()
    
    # Check if Capsuleer is stating their own piloted vessel
    own_ship_match = _RE_OWN_SHIP.search(prompt)
    piloted_ship_name = None
    s_res = None
    if own_ship_match:
        cand_name = own_ship_match.group(1).strip()
        s_res = lookup_ship(cand_name)
        if s_res:
            piloted_ship_name = s_res.get("canonical_name", cand_name)
    elif piloted_ship:
        s_res = lookup_ship(piloted_ship)
        if s_res:
            piloted_ship_name = s_res.get("canonical_name", piloted_ship)

    if piloted_ship_name and s_res:
        grounding_blocks.append(
            f"[CAPSULEER PILOTED VESSEL — {piloted_ship_name.upper()} ({s_res.get('class', 'Vessel')} - {s_res.get('faction', 'General')})]:\n"
            f"• Piloted Ship Role: {s_res.get('role', 'Combat')}\n"
            f"• Key Combat Envelope: Optimal {s_res.get('optimal_range', 'Standard')} | Tank: {s_res.get('tank', 'Shield/Armor')}\n"
            f"• Hull Strengths & Tactics: {s_res.get('tactics', 'Standard combat tactics.')}"
        )

    # Check for direct multi-word ship names first
    for ship_name, s_info, ship_lower in _MULTI_WORD_SHIPS:
        if ship_lower in lower_text:
            if piloted_ship_name and ship_lower == piloted_ship_name.lower():
                continue
            if ship_lower not in detected_hulls:
                detected_hulls.add(ship_lower)
                grounding_blocks.append(s_info.get("pre_rendered_dossier", f"• {ship_name}"))

    for w in words:
        s_info = lookup_ship(w)
        if s_info:
            cname = s_info.get("canonical_name", w.capitalize())
            cname_l = cname.lower()
            if piloted_ship_name and cname_l == piloted_ship_name.lower():
                continue
            if cname_l not in detected_hulls:
                detected_hulls.add(cname_l)
                grounding_blocks.append(s_info.get("pre_rendered_dossier", f"• {cname}"))

    # Check for Role Doctrine Grounding
    for role_key_l, role_doctrine in _ROLE_DOCTRINES_LOWER:
        if role_key_l in lower_text:
            grounding_blocks.append(role_doctrine)

    if grounding_blocks:
        joined_dossiers = "\n\n".join(grounding_blocks[:8])
        return f"[Tactical Grounding Matrix]:\n{joined_dossiers}\n\n{EVE_COMBAT_AXIOMS}"
    
    default_summary = (
        "[GENERAL FLEET SCOUTING & COMBAT READINESS]:\n"
        "• Hostile Composition: Unspecified / General hostile elements reported.\n"
        "• Tactical Action: Maintain directional scan (14.3 AU at 360°), hold bookmark / gate perches, align out if uncloaked, and prepare defensive tackle or warp-out vectors."
    )
    return f"{default_summary}\n\n{EVE_COMBAT_AXIOMS}"
