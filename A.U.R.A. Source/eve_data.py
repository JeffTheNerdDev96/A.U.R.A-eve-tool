"""
EVE Online Tactical Database, Comprehensive Combat Matrix & Domain Grounding Engine.
Customized for A.U.R.A. (Adaptive Underworld Recon Array) — ver.0.1.2-alpha4 & Core.
Contains encyclopedic vessel dossiers (350+ hulls), module matrix (250+ modules),
subsystems, weapon tracking mathematics, capacitor warfare, and tactical grounding.
Covers all standard empire, navy, pirate, faction, industrial, capital, and T3 vessels.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import re

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
        "tactics": "Extreme warp speed and agility. Fly with high transversal against larger guns. Vulnerable to dual webs and scramblers."
    },
    "Mekubal": {
        "class": "Destroyer",
        "faction": "Angel Cartel",
        "role": "Pirate Destroyer / Frigate Hunter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Extreme (3.8-4.5 km/s)",
        "optimal_range": "8-20 km (Autocannons)",
        "tactics": "High-speed destroyer with extreme projectile alpha. Shreds frigates and light tackle before they close range."
    },
    "Cynabal": {
        "class": "Cruiser",
        "faction": "Angel Cartel",
        "role": "Nano Skirmisher / Fleet Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active",
        "speed": "Extreme (2.2-3.0 km/s MWD)",
        "optimal_range": "15-28 km (425mm Autocannons / Barrage)",
        "tactics": "Premier nano kiter. Fast align and warp acceleration. Keep range 20-25 km, kite away from scrams/webs, apply tracking-disruptive transversal against heavy turrets."
    },
    "Khizriel": {
        "class": "Battlecruiser",
        "faction": "Angel Cartel",
        "role": "Heavy Skirmish Battlecruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast (1.8-2.4 km/s)",
        "optimal_range": "20-50 km",
        "tactics": "Heavy projectile alpha with high mobility. Fast align and warp speed allow repositioning across grid effortlessly."
    },
    "Machariel": {
        "class": "Battleship",
        "faction": "Angel Cartel",
        "role": "Fast Battleship / Fleet Anchor",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Armor",
        "speed": "Very Fast (1.5-2.0 km/s MWD)",
        "optimal_range": "15-40 km (800mm AC) or 70-130 km (1400mm Artillery)",
        "tactics": "Cruiser-like sub-warp agility. Immense alpha with Artillery or heavy mobile DPS with Autocannons. Retain transversal against dreads."
    },
    "Azariel": {
        "class": "Titan",
        "faction": "Angel Cartel",
        "role": "Pirate Supercapital Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Fast for Titan",
        "optimal_range": "Omni Capital Range",
        "tactics": "Angel Cartel supercapital with devastating projectile alpha strike and Titan doomsday weapon."
    },
    "Worm": {
        "class": "Frigate",
        "faction": "Guristas",
        "role": "Heavy Drone / Missile Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Passive (300% Drone Bonus)",
        "speed": "Moderate",
        "optimal_range": "0-40 km",
        "tactics": "Extreme drone HP and damage (1 drone deals damage of 4). Kill drones or kite outside lock range."
    },
    "Mamba": {
        "class": "Destroyer",
        "faction": "Guristas",
        "role": "Pirate Missile Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-45 km",
        "tactics": "Fast missile and light drone destroyer with strong shield tank."
    },
    "Gila": {
        "class": "Cruiser",
        "faction": "Guristas",
        "role": "Drone / Missile Combat Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Passive / Active Shield (500% Drone Bonus)",
        "speed": "Moderate (1.6-2.0 km/s)",
        "optimal_range": "0-60 km",
        "tactics": "Abyssal king. 2 Medium drones deliver damage and HP of 10. Heavy shield buffer. Counter by destroying drones or heavy cap neuts."
    },
    "Alligator": {
        "class": "Battlecruiser",
        "faction": "Guristas",
        "role": "Heavy Drone / Missile Battlecruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km",
        "tactics": "Heavy drone and heavy assault missile platform with massive shield reserves."
    },
    "Rattlesnake": {
        "class": "Battleship",
        "faction": "Guristas",
        "role": "Heavy Drone / Cruise Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Passive / Active Shield",
        "speed": "Slow",
        "optimal_range": "20-80 km",
        "tactics": "Massive passive shield recharge and heavy drone DPS. Cap neuts have low impact on passive shield regen."
    },
    "Loggerhead": {
        "class": "Force Auxiliary",
        "faction": "Guristas",
        "role": "Pirate Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Fleet Remote Shield",
        "tactics": "Guristas pirate capital shield logistics ship."
    },
    "Caiman": {
        "class": "Dreadnought",
        "faction": "Guristas",
        "role": "Pirate Missile / Drone Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Guristas pirate dreadnought with capital kinetic/thermal missile launchers."
    },
    "Komodo": {
        "class": "Titan",
        "faction": "Guristas",
        "role": "Guristas Supercapital Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Guristas pirate supercapital Titan with extreme missile burst and supercapital drones."
    },
    "Cruor": {
        "class": "Frigate",
        "faction": "Blood Raiders",
        "role": "Web / NOS Frigate",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Heavy webs and NOS that drains cap even when ship cap is full. Keep distance outside 15 km."
    },
    "Ashimmu": {
        "class": "Cruiser",
        "faction": "Blood Raiders",
        "role": "Heavy Web / NOS Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "90% webs and severe energy neut drain. Eliminates enemy capacitor in seconds."
    },
    "Bhaalgorn": {
        "class": "Battleship",
        "faction": "Blood Raiders",
        "role": "Fleet Cap Drain / Heavy Web",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Slow",
        "optimal_range": "0-40 km",
        "tactics": "Fleet flagship neut. Heavy energy neutralizers drain 3000+ GJ per cycle at up to 40 km."
    },
    "Dagon": {
        "class": "Force Auxiliary",
        "faction": "Blood Raiders",
        "role": "Pirate Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Fleet Remote Armor",
        "tactics": "Blood Raider capital armor remote repair ship."
    },
    "Chemosh": {
        "class": "Dreadnought",
        "faction": "Blood Raiders",
        "role": "Pirate Cap Drain Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Blood Raider pirate dreadnought with capital energy neutralizers."
    },
    "Molok": {
        "class": "Titan",
        "faction": "Blood Raiders",
        "role": "Blood Raider Supercapital",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Blood Raider pirate supercapital Titan with massive neut drain."
    },
    "Daredevil": {
        "class": "Frigate",
        "faction": "Serpentis",
        "role": "90% Web Blaster Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-8 km",
        "tactics": "90% stasis web stops targets dead. Massive close-range blaster DPS. Do not let it close inside 10km."
    },
    "Vigilant": {
        "class": "Cruiser",
        "faction": "Serpentis",
        "role": "90% Web Blaster Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "90% webifier with 1000+ DPS medium blasters. Overheat propulsion and stay outside 18 km."
    },
    "Vindicator": {
        "class": "Battleship",
        "faction": "Serpentis",
        "role": "90% Web Blaster Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "2000+ DPS close range. Webifier locks targets down for massive neutron blaster application."
    },
    "Vehement": {
        "class": "Dreadnought",
        "faction": "Serpentis",
        "role": "Pirate Blaster / Web Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "0-30 km",
        "tactics": "Serpentis pirate dreadnought with capital blasters and 90% webifiers."
    },
    "Vanquisher": {
        "class": "Titan",
        "faction": "Serpentis",
        "role": "Serpentis Supercapital",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Serpentis pirate supercapital Titan with 90% web and blaster power."
    },
    "Succubus": {
        "class": "Frigate",
        "faction": "Sansha's Nation",
        "role": "AB Speed Laser Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme AB (2.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Huge Afterburner speed bonus (immune to warp scrambler MWD shutoff). High transversal pulse lasers."
    },
    "Phantasm": {
        "class": "Cruiser",
        "faction": "Sansha's Nation",
        "role": "100MN AB Laser Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer / Active",
        "speed": "Extreme AB (2.0+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "Runs 100MN Afterburner with cruiser-grade agility. Unscrammable speed tank. Hit with tracking disruptors or heavy webs."
    },
    "Nightmare": {
        "class": "Battleship",
        "faction": "Sansha's Nation",
        "role": "Fast Laser Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Shield Buffer",
        "speed": "Fast AB (1.5+ km/s)",
        "optimal_range": "30-80 km",
        "tactics": "High-mobility beam/pulse laser battleship. Applies instant EM/Thermal damage with large energy turrets."
    },
    "Revenant": {
        "class": "Supercarrier",
        "faction": "Sansha's Nation",
        "role": "Pirate Supercarrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Sansha pirate supercarrier with immense fighter strike damage."
    },
    "Astero": {
        "class": "Frigate",
        "faction": "Sisters of EVE",
        "role": "Covert Ops / Drone Scout",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Dual Rep",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Covert cloaking exploration frigate with vicious light drone combat capability. Often dual-repaired."
    },
    "Stratios": {
        "class": "Cruiser",
        "faction": "Sisters of EVE",
        "role": "Covert Ops / Drone Brawler",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer / Dual Rep",
        "speed": "Moderate",
        "optimal_range": "0-30 km",
        "tactics": "Covert cloaking cruiser. Can fit covert cyno, heavy neuts, and full flight of heavy/sentry drones."
    },
    "Nestor": {
        "class": "Battleship",
        "faction": "Sisters of EVE",
        "role": "Remote Rep / Wormhole Core",
        "threat": "THREAT_PIRATE",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Sub-capital remote armor repair flagship. Very low mass allows mass-efficient wormhole transit."
    },
    "Garmur": {
        "class": "Frigate",
        "faction": "Mordu's Legion",
        "role": "Long-Range Point Kiter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "30-40 km",
        "tactics": "Projects 35+ km warp disruptor point at extreme speed. Counter with sensor dampeners, rapid light missiles, or light combat drones."
    },
    "Orthrus": {
        "class": "Cruiser",
        "faction": "Mordu's Legion",
        "role": "Long-Range Point & Web Kiter",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Extreme (3.0+ km/s)",
        "optimal_range": "35-50 km",
        "tactics": "45+ km point and 25 km web range with rapid light missiles. Counter with heavy projection snipers or long-range dampeners."
    },
    "Barghest": {
        "class": "Battleship",
        "faction": "Mordu's Legion",
        "role": "Heavy Point / Cruise Battleship",
        "threat": "THREAT_PIRATE",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "Extreme missile velocity and 60+ km point range. High alpha cruise missiles."
    },
    "Damavik": {
        "class": "Frigate",
        "faction": "Triglavian",
        "role": "Spooling Disintegrator Frigate",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "5-18 km",
        "tactics": "Entropic disintegrator damage ramps up continuously over time. Break lock or kill quickly before spool reaches maximum."
    },
    "Kikimora": {
        "class": "Destroyer",
        "faction": "Triglavian",
        "role": "Long-Range Disintegrator Destroyer",
        "threat": "THREAT_PIRATE",
        "tank": "Armor / Shield",
        "speed": "Extreme (3.5+ km/s)",
        "optimal_range": "15-40 km",
        "tactics": "Extreme sub-warp speed with spooling light disintegrator. Strikes from 35km with heavy tracking."
    },
    "Vedmak": {
        "class": "Cruiser",
        "faction": "Triglavian",
        "role": "Spooling Disintegrator Cruiser",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Fast (2.2-2.8 km/s)",
        "optimal_range": "10-35 km",
        "tactics": "High sub-warp speed with continuous spooling thermal/explosive damage. Disengage if fight extends past 60 seconds."
    },
    "Rodiva": {
        "class": "Cruiser",
        "faction": "Triglavian",
        "role": "Spooling Remote Armor Rep",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Rep Range",
        "tactics": "Triglavian logistics cruiser with spooling remote armor repairers."
    },
    "Drekavac": {
        "class": "Battlecruiser",
        "faction": "Triglavian",
        "role": "Heavy Disintegrator / Armor Links",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "15-45 km",
        "tactics": "Heavy armor tank and massive max-spool disintegrator DPS."
    },
    "Leshak": {
        "class": "Battleship",
        "faction": "Triglavian",
        "role": "Capital / Structure Buster",
        "threat": "THREAT_PIRATE",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "20-60 km",
        "tactics": "Spools to over 3500 DPS. Lethal to capitals, POS structures, and stationary targets."
    },
    "Ikitursa": {
        "class": "Heavy Assault Cruiser",
        "faction": "Triglavian",
        "role": "HAC Disintegrator Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "10-35 km",
        "tactics": "T2 assault damage controls and huge spooling DPS make it formidable in small gang engagements."
    },
    "Zarmazd": {
        "class": "Logistics Cruiser",
        "faction": "Triglavian",
        "role": "T2 Spooling Remote Armor",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Rep Range",
        "tactics": "T2 Triglavian logistics cruiser with extreme ramping armor repairs."
    },
    "Zirnitra": {
        "class": "Dreadnought",
        "faction": "Triglavian",
        "role": "Capital Disintegrator Siege",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Triglavian dreadnought with capital spooling disintegrator."
    },
    "Skybreaker": {
        "class": "Frigate",
        "faction": "EDENCOM",
        "role": "Vortron Arcing Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Vorton projector arcs lightning damage to up to 5 nearby hostile targets."
    },
    "Stormbringer": {
        "class": "Cruiser",
        "faction": "EDENCOM",
        "role": "Vortron Arcing Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "15-35 km",
        "tactics": "Medium vorton projector arcs heavy EM/Kinetic damage across fleet clusters."
    },
    "Thunderchild": {
        "class": "Battleship",
        "faction": "EDENCOM",
        "role": "Heavy Vortron Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "30-70 km",
        "tactics": "Large vorton projector chains massive damage across 10 linked enemy ships."
    },
    "Apotheosis": {
        "class": "Frigate",
        "faction": "Society of Conscious Thought",
        "role": "Special Shuttle / Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield/Armor Omni",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "SOCT frigate with universal weapon and scan bonuses."
    },
    "Sunesis": {
        "class": "Destroyer",
        "faction": "Society of Conscious Thought",
        "role": "Insta-Align Multi-Role Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast (<2s align)",
        "optimal_range": "0-25 km",
        "tactics": "Sub-2s align hauler and combatant with universal weapon bonuses."
    },
    "Gnosis": {
        "class": "Battlecruiser",
        "faction": "Society of Conscious Thought",
        "role": "Multi-Role Combat / Exploration BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor / Hull Buffer",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Universal weapon and tank bonuses. Highly adaptable to any combat role."
    },
    "Praxis": {
        "class": "Battleship",
        "faction": "Society of Conscious Thought",
        "role": "Multi-Role Line Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor / Hull Buffer",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Massive slot layout and universal bonus for lasers, hybrids, projectiles, missiles, and drones."
    },
    "Pacifier": {
        "class": "Frigate",
        "faction": "CONCORD",
        "role": "Covert Ops / Fast Interceptor",
        "threat": "THREAT_COVERT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "CONCORD covert ops frigate with extreme warp speed and combat versatility."
    },
    "Enforcer": {
        "class": "Cruiser",
        "faction": "CONCORD",
        "role": "Covert Combat Cruiser",
        "threat": "THREAT_COVERT",
        "tank": "Shield / Armor",
        "speed": "Fast",
        "optimal_range": "0-35 km",
        "tactics": "CONCORD covert cruiser with massive security status bonus and omni damage."
    },
    "Marshal": {
        "class": "Battleship",
        "faction": "CONCORD",
        "role": "Covert Black Ops Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Active Shield / Armor",
        "speed": "Moderate",
        "optimal_range": "0-60 km",
        "tactics": "CONCORD Black Ops battleship with immense active repair and covert jump portal capability."
    },
    "Monitor": {
        "class": "Cruiser",
        "faction": "CONCORD",
        "role": "Flag Cruiser / Invulnerable FC",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Omni Buffer (1M+ EHP)",
        "speed": "Fast",
        "optimal_range": "0 km",
        "tactics": "Fleet Commander flag cruiser with over 1 million EHP and 0 DPS output. Ignore and kill the fleet."
    },
    "Condor": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Missile Kiter / Light Tackle",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "20-35 km",
        "tactics": "Light missile kiter with kinetic missile bonus."
    },
    "Kestrel": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Missile / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "4 missile launchers with all 4 damage types."
    },
    "Merlin": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Blaster / Rail Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Dual MASB",
        "speed": "Moderate",
        "optimal_range": "0-10 km",
        "tactics": "Strong shield resistance bonus; high blaster DPS."
    },
    "Heron": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning frigate often bait-tanked with rockets."
    },
    "Bantam": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield",
        "tactics": "T1 frigate shield logistics."
    },
    "Griffin": {
        "class": "Frigate",
        "faction": "Caldari",
        "role": "ECM Jamming Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin Shield",
        "speed": "Moderate",
        "optimal_range": "30-60 km",
        "tactics": "Long-range ECM jammers break target locks. Primary immediately."
    },
    "Caldari Navy Hookbill": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Dual Web Rocket / Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "5 mid slots allow dual webs + scram + MSE. Deadly 1v1 rocket brawler."
    },
    "Griffin Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Combat ECM / Hybrid Brawler",
        "threat": "THREAT_ECM",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Strong hybrid turret DPS and ECM burst tackle capability."
    },
    "Heron Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Caldari (Navy)",
        "role": "Combat Explorer / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Dual MASB",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Faction combat exploration frigate with heavy rocket DPS."
    },
    "Buzzard": {
        "class": "Covert Ops",
        "faction": "Caldari",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout. Potential Covert Cyno beacon."
    },
    "Manticore": {
        "class": "Stealth Bomber",
        "faction": "Caldari",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Kinetic bombs and torpedoes from cloak."
    },
    "Harpy": {
        "class": "Assault Frigate",
        "faction": "Caldari",
        "role": "Rail Sniper / ADC Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "10-40 km",
        "tactics": "Assault Damage Control and long-range railguns make it formidable."
    },
    "Hawk": {
        "class": "Assault Frigate",
        "faction": "Caldari",
        "role": "Dual MASB Rocket Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Dual MASB Active + ADC",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "Extreme active shield tank. Breaks under sustained neuts or alphastrike."
    },
    "Kitsune": {
        "class": "Electronic Attack Ship",
        "faction": "Caldari",
        "role": "Long-Range Fleet ECM",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "Massive ECM jamming range. Jams out entire wings from 80 km."
    },
    "Crow": {
        "class": "Interceptor",
        "faction": "Caldari",
        "role": "Long-Range Light Missile Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "25-45 km",
        "tactics": "Fast nullified missile kiter."
    },
    "Raptor": {
        "class": "Interceptor",
        "faction": "Caldari",
        "role": "Fleet Tackle / Hybrid Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast combat tackle interceptor with high hybrid DPS."
    },
    "Kirin": {
        "class": "Logistics Frigate",
        "faction": "Caldari",
        "role": "T2 Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Assault-tier remote shield repair frigate."
    },
    "Cormorant": {
        "class": "Destroyer",
        "faction": "Caldari",
        "role": "Rail Sniper / Blaster Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km (Rails) / 0-10 km (Blasters)",
        "tactics": "8 hybrid turrets with optimal range bonus. Lethal fleet sniper doctrine."
    },
    "Corax": {
        "class": "Destroyer",
        "faction": "Caldari",
        "role": "Light Missile / Rocket Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "7 missile launchers with kinetic bonus."
    },
    "Cormorant Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Caldari (Navy)",
        "role": "Navy Rail Sniper Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "40-90 km",
        "tactics": "Extreme railgun range and tracking."
    },
    "Flycatcher": {
        "class": "Interdictor",
        "faction": "Caldari",
        "role": "Shield Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates. Primary target."
    },
    "Stork": {
        "class": "Command Destroyer",
        "faction": "Caldari",
        "role": "Micro Jump Field / Shield Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Jackdaw": {
        "class": "Tactical Destroyer",
        "faction": "Caldari",
        "role": "T3 Mode-Switching Missile Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Shield",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "20-60 km",
        "tactics": "Switches between Defensive (+resist), Propulsion (+speed), and Sharpshooter (+range/damage). High threat."
    },
    "Caracal": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Rapid Light / Heavy Missile Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate (1.8-2.2 km/s)",
        "optimal_range": "30-65 km",
        "tactics": "Rapid Light Missile (RLML) anti-frigate platform. High burst, 35s reload."
    },
    "Moa": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Rail / Blaster Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Heavy Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-15 km / 30-60 km",
        "tactics": "Strong shield resistance bonus; standard line fleet brawler/sniper."
    },
    "Osprey": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Shield Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield (Cap Transfer)",
        "tactics": "Cap-chain shield logistics cruiser. Break cap chain to collapse fleet reps."
    },
    "Blackbird": {
        "class": "Cruiser",
        "faction": "Caldari",
        "role": "Fleet ECM Jammer",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "50-100 km",
        "tactics": "Cruiser ECM platform. Jamming disrupts target locks across the grid."
    },
    "Caracal Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Caldari (Navy)",
        "role": "Heavy Missile / Rapid Light Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "30-75 km",
        "tactics": "Heavier shield buffer and missile velocity than standard Caracal."
    },
    "Osprey Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Caldari (Navy)",
        "role": "Fast Missile Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.4+ km/s)",
        "optimal_range": "30-60 km",
        "tactics": "High-speed nano missile kiter."
    },
    "Cerberus": {
        "class": "Heavy Assault Cruiser",
        "faction": "Caldari",
        "role": "HAC Heavy Missile Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "50-100 km",
        "tactics": "Extreme missile velocity and range. Striking with HAC ADC survivability."
    },
    "Eagle": {
        "class": "Heavy Assault Cruiser",
        "faction": "Caldari",
        "role": "HAC Rail Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "60-120 km",
        "tactics": "High-resist HAC rail sniper with extreme projection."
    },
    "Broadsword": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Minmatar",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Projects focused infinite warp scrambler or 20km mobile bubble."
    },
    "Falcon": {
        "class": "Force Recon",
        "faction": "Caldari",
        "role": "Covert Cloak / ECM / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "50-100 km",
        "tactics": "Uncloaks to jam targets and light Covert Cyno. Top priority target."
    },
    "Rook": {
        "class": "Combat Recon",
        "faction": "Caldari",
        "role": "D-Scan Immune ECM Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "50-90 km",
        "tactics": "Invisible to Directional Scan. Heavy ECM jammer and missile DPS."
    },
    "Basilisk": {
        "class": "Logistics Cruiser",
        "faction": "Caldari",
        "role": "T2 Cap-Chain Shield Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Moderate",
        "optimal_range": "Remote Shield (Cap Transfer)",
        "tactics": "Premier T2 shield logistics. Maintain cap chain with second Basilisk."
    },
    "Tengu": {
        "class": "Strategic Cruiser",
        "faction": "Caldari",
        "role": "Modular T3C (Missile / Rail / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield Buffer / Active",
        "speed": "Fast (1.8-2.5 km/s)",
        "optimal_range": "30-90 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy missile DPS, or 100MN AB."
    },
    "Drake": {
        "class": "Battlecruiser",
        "faction": "Caldari",
        "role": "Heavy Missile Fleet BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Shield Buffer / Passive",
        "speed": "Slow",
        "optimal_range": "30-70 km",
        "tactics": "Classic heavy missile battlecruiser with huge passive shield buffer."
    },
    "Ferox": {
        "class": "Battlecruiser",
        "faction": "Caldari",
        "role": "Rail Sniper / Fleet Anchor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "40-100 km",
        "tactics": "Line fleet railgun anchor with extreme optimal range."
    },
    "Naga": {
        "class": "Attack Battlecruiser",
        "faction": "Caldari",
        "role": "Battleship-Gun Rail Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield",
        "speed": "Moderate",
        "optimal_range": "80-150 km",
        "tactics": "Large Battleship Railguns on BC hull. Massive alpha at extreme range."
    },
    "Drake Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Caldari (Navy)",
        "role": "Heavy Missile / Shield BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "35-80 km",
        "tactics": "Higher missile application and mobility than standard Drake."
    },
    "Ferox Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Caldari (Navy)",
        "role": "Hybrid Brawler / Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Heavy Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "20-80 km",
        "tactics": "Enhanced hybrid turret tracking and shield reserves."
    },
    "Nighthawk": {
        "class": "Command Ship",
        "faction": "Caldari",
        "role": "Shield Fleet Command / HAM",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "Provides Fleet Shield Bursts and launches heavy assault missiles."
    },
    "Vulture": {
        "class": "Command Ship",
        "faction": "Caldari",
        "role": "Shield Fleet Command / Rail Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "Provides Fleet Information / Shield Bursts with long-range railguns."
    },
    "Raven": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Cruise / Torpedo Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer / Active",
        "speed": "Slow",
        "optimal_range": "40-120 km (Cruise) / 15-35 km (Torp)",
        "tactics": "Classic missile battleship with high rate of fire."
    },
    "Rokh": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Rail Sniper Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "80-160 km",
        "tactics": "8 large railguns with optimal range bonus. Strikes from 150 km."
    },
    "Scorpion": {
        "class": "Battleship",
        "faction": "Caldari",
        "role": "Fleet ECM Battleship",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "60-120 km",
        "tactics": "Massive ECM jamming strength across all racial sensor types."
    },
    "Raven Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Caldari (Navy)",
        "role": "Cruise / Torp Navy Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "40-140 km",
        "tactics": "8 launcher hardpoints with superior missile application."
    },
    "Scorpion Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Caldari (Navy)",
        "role": "Heavy Shield / Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Shield Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "Trading ECM for massive shield buffer and missile DPS."
    },
    "Golem": {
        "class": "Marauder",
        "faction": "Caldari",
        "role": "Bastion Torpedo / Cruise Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Shield (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "30-100 km",
        "tactics": "Bastion Mode doubles shield repairs and grants EWAR immunity. Apply neuts."
    },
    "Widow": {
        "class": "Black Ops",
        "faction": "Caldari",
        "role": "Covert Jump / ECM Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Shield Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "40-90 km",
        "tactics": "Bridges covert fleets; fires missiles and ECM jammers."
    },
    "Phoenix": {
        "class": "Dreadnought",
        "faction": "Caldari",
        "role": "Capital Torpedo / Cruise Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with capital missile launchers."
    },
    "Phoenix Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Caldari (Navy)",
        "role": "Navy Capital Missile Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "High-application capital missile dreadnought."
    },
    "Karura": {
        "class": "Lancer Dreadnought",
        "faction": "Caldari",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp."
    },
    "Chimera": {
        "class": "Carrier",
        "faction": "Caldari",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Launches light and support fighter squadrons."
    },
    "Wyvern": {
        "class": "Supercarrier",
        "faction": "Caldari",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital fighter bomber strikes and burst projectors."
    },
    "Minokawa": {
        "class": "Force Auxiliary",
        "faction": "Caldari",
        "role": "Capital Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Shield",
        "tactics": "Capital remote shield repair ship."
    },
    "Leviathan": {
        "class": "Titan",
        "faction": "Caldari",
        "role": "Supercapital Missile Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Doomsday missile titan with fleet shield burst."
    },
    "Badger": {
        "class": "Industrial",
        "faction": "Caldari",
        "role": "Standard Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "T1 industrial transport."
    },
    "Tayra": {
        "class": "Industrial",
        "faction": "Caldari",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity hauler."
    },
    "Crane": {
        "class": "Blockade Runner",
        "faction": "Caldari",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Shield",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler."
    },
    "Bustard": {
        "class": "Deep Space Transport",
        "faction": "Caldari",
        "role": "Heavy Shield DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar."
    },
    "Charon": {
        "class": "Freighter",
        "faction": "Caldari",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter."
    },
    "Rhea": {
        "class": "Jump Freighter",
        "faction": "Caldari",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics."
    },
    "Atron": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Fast Tackle / Blaster Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-8 km",
        "tactics": "High-speed light tackle with close-range blaster DPS."
    },
    "Tristan": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Drone Kiter / Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield / Hull",
        "speed": "Fast",
        "optimal_range": "0-30 km",
        "tactics": "Versatile drone frigate. Can fly neutralizer brawl or long-range kite."
    },
    "Incursus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Active Armor Blaster Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual Rep Active Armor",
        "speed": "Moderate",
        "optimal_range": "0-8 km",
        "tactics": "Immense active armor repair bonus with close-range blasters."
    },
    "Imicus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate."
    },
    "Navitas": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor",
        "tactics": "T1 frigate armor logistics."
    },
    "Maulus": {
        "class": "Frigate",
        "faction": "Gallente",
        "role": "Remote Sensor Dampener",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "30-70 km",
        "tactics": "Sensor dampeners reduce enemy lock range and scan resolution."
    },
    "Federation Navy Comet": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Heavy Blaster / Rail Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Extreme hybrid DPS and drone assistance."
    },
    "Maulus Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Combat Dampener / Scram Kiter",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Damps enemy lock range while applying strong hybrid DPS."
    },
    "Imicus Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Gallente (Navy)",
        "role": "Combat Explorer / Heavy Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Exploration combat frigate with increased drone bay."
    },
    "Helios": {
        "class": "Covert Ops",
        "faction": "Gallente",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout frigate."
    },
    "Nemesis": {
        "class": "Stealth Bomber",
        "faction": "Gallente",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Thermal bombs and torpedoes from cloak."
    },
    "Ishkur": {
        "class": "Assault Frigate",
        "faction": "Gallente",
        "role": "Drone / Blaster Assault Frigate",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active + ADC",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Assault Damage Control and drone bay for flexible engagement."
    },
    "Enyo": {
        "class": "Assault Frigate",
        "faction": "Gallente",
        "role": "High DPS Blaster Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "0-8 km",
        "tactics": "Devastating close-range blaster DPS with ADC."
    },
    "Keres": {
        "class": "Electronic Attack Ship",
        "faction": "Gallente",
        "role": "Long-Range Dampener / Point",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.0+ km/s)",
        "optimal_range": "30-60 km",
        "tactics": "Projects long-range warp disruptor (35km+) and severe dampeners."
    },
    "Ares": {
        "class": "Interceptor",
        "faction": "Gallente",
        "role": "Fast Fleet Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Nullified fast tackle interceptor."
    },
    "Taranis": {
        "class": "Interceptor",
        "faction": "Gallente",
        "role": "Combat Blaster Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-8 km",
        "tactics": "High-DPS combat interceptor with blasters and drones."
    },
    "Thalia": {
        "class": "Logistics Frigate",
        "faction": "Gallente",
        "role": "T2 Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Assault-tier remote armor repair frigate."
    },
    "Catalyst": {
        "class": "Destroyer",
        "faction": "Gallente",
        "role": "High DPS Blaster Ganker / Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Moderate",
        "optimal_range": "0-8 km (Blasters) / 20-50 km (Rails)",
        "tactics": "8 hybrid turrets deliver over 600+ DPS close range. Premier suicide gank hull."
    },
    "Algos": {
        "class": "Destroyer",
        "faction": "Gallente",
        "role": "Drone / Rail Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-30 km",
        "tactics": "Full flight of light drones with hybrid turrets."
    },
    "Catalyst Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Gallente (Navy)",
        "role": "Navy Blaster / Rail Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Hull Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Enhanced tracking and armor plate mass reduction."
    },
    "Eris": {
        "class": "Interdictor",
        "faction": "Gallente",
        "role": "Armor Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates."
    },
    "Magus": {
        "class": "Command Destroyer",
        "faction": "Gallente",
        "role": "Micro Jump Field / Armor Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Hecate": {
        "class": "Tactical Destroyer",
        "faction": "Gallente",
        "role": "T3 Mode-Switching Blaster Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Armor / Hull",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "0-15 km",
        "tactics": "Switches between Propulsion, Sharpshooter (1000+ DPS blasters), and Defensive modes."
    },
    "Thorax": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Blaster / Rail Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast (2.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast attack cruiser with high blaster DPS and medium drones."
    },
    "Vexor": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Heavy Drone / Armor Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active / Hull",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Heavy drone cruiser capable of fielding full heavy drone flights."
    },
    "Exequror": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Armor Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Direct remote armor repair cruiser. High sub-warp mobility."
    },
    "Celestis": {
        "class": "Cruiser",
        "faction": "Gallente",
        "role": "Remote Sensor Dampener Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "40-90 km",
        "tactics": "Dampens enemy targeting range and scan resolution across grid."
    },
    "Vexor Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Drone / Hybrid Combat Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Shield",
        "speed": "Fast",
        "optimal_range": "0-50 km",
        "tactics": "Enhanced hybrid turret tracking and heavy drone application."
    },
    "Exequror Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Hybrid Combat Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.2+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Pure combat hybrid cruiser with extreme DPS."
    },
    "Deimos": {
        "class": "Heavy Assault Cruiser",
        "faction": "Gallente",
        "role": "HAC Active Armor Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Armor + ADC",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Massive active armor repair bonus and ADC survivability."
    },
    "Ishtar": {
        "class": "Heavy Assault Cruiser",
        "faction": "Gallente",
        "role": "HAC Heavy Drone Cruiser",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor / Shield Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "0-80 km",
        "tactics": "Premier nullsec ratting and fleet heavy drone cruiser. Long drone control range."
    },
    "Phobos": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Gallente",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Heavy armor HIC projecting focused infinite points or mobile bubbles."
    },
    "Arazu": {
        "class": "Force Recon",
        "faction": "Gallente",
        "role": "Covert Cloak / 40km Scram / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-40 km",
        "tactics": "Uncloaks to apply 40km warp disruptor / scrambler and light Covert Cyno."
    },
    "Lachesis": {
        "class": "Combat Recon",
        "faction": "Gallente",
        "role": "D-Scan Immune Long Point & Damp",
        "threat": "THREAT_ECM",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "40-70 km",
        "tactics": "Invisible to D-Scan. Applies 50km+ point and heavy dampeners."
    },
    "Oneiros": {
        "class": "Logistics Cruiser",
        "faction": "Gallente",
        "role": "T2 Solo Armor Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Self-sufficient armor logistics cruiser (no cap chain required)."
    },
    "Proteus": {
        "class": "Strategic Cruiser",
        "faction": "Gallente",
        "role": "Modular T3C (Blaster / Drone / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active",
        "speed": "Fast (1.6-2.2 km/s)",
        "optimal_range": "0-25 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy blasters, or 90% webifiers."
    },
    "Brutix": {
        "class": "Battlecruiser",
        "faction": "Gallente",
        "role": "Blaster / Rail Brawler BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Blaster) / 40-80 km (Rail)",
        "tactics": "High hybrid turret DPS and armor repair bonus."
    },
    "Myrmidon": {
        "class": "Battlecruiser",
        "faction": "Gallente",
        "role": "Triple Active Armor Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Triple Rep Active Armor",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Extreme active armor tank bonus with full heavy drone flights."
    },
    "Talos": {
        "class": "Attack Battlecruiser",
        "faction": "Gallente",
        "role": "Battleship-Gun Blaster / Rail Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield/Armor",
        "speed": "Fast (1.8+ km/s)",
        "optimal_range": "0-20 km (Blasters) / 80-140 km (Rails)",
        "tactics": "Large Battleship Neutron Blasters or Railguns on BC hull. Massive DPS."
    },
    "Brutix Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid Brawler BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "Superior armor buffer and hybrid tracking."
    },
    "Myrmidon Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Gallente (Navy)",
        "role": "Heavy Web / Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-40 km",
        "tactics": "Stasis webifier range bonus and heavy drone application."
    },
    "Astarte": {
        "class": "Command Ship",
        "faction": "Gallente",
        "role": "Armor Fleet Command / Blaster Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Provides Fleet Armor Bursts and deals immense close-range blaster DPS."
    },
    "Eos": {
        "class": "Command Ship",
        "faction": "Gallente",
        "role": "Armor Fleet Command / Heavy Drone",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer / Active",
        "speed": "Slow",
        "optimal_range": "0-60 km",
        "tactics": "Provides Fleet Armor / Skirmish Bursts with full heavy drone flights."
    },
    "Megathron": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Hybrid Brawler / Fleet Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-25 km (Blasters) / 50-100 km (Rails)",
        "tactics": "Classic hybrid line battleship with high rate of fire and tracking."
    },
    "Dominix": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Drone / Cap Neutralizer Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active / Hull",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Heavy drone and heavy neutralizer platform. Cap drain collapses active tanks."
    },
    "Hyperion": {
        "class": "Battleship",
        "faction": "Gallente",
        "role": "Active Armor Blaster Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual / Triple Large Rep Active Armor",
        "speed": "Slow",
        "optimal_range": "0-25 km",
        "tactics": "Massive active armor repair bonus. Extremely difficult to break without heavy neuts."
    },
    "Megathron Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-30 km / 60-120 km",
        "tactics": "Higher tracking and armor buffer than standard Megathron."
    },
    "Dominix Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Gallente (Navy)",
        "role": "Navy Hybrid / Drone Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-80 km",
        "tactics": "Dual hybrid turret and drone damage bonuses."
    },
    "Kronos": {
        "class": "Marauder",
        "faction": "Gallente",
        "role": "Bastion Blaster / Rail Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Armor (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "0-30 km (Blasters) / 60-120 km (Rails)",
        "tactics": "Bastion Mode doubles armor reps and yields 3000+ DPS with Void L."
    },
    "Sin": {
        "class": "Black Ops",
        "faction": "Gallente",
        "role": "Covert Jump / Drone / Neut Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Armor Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "0-60 km",
        "tactics": "Bridges covert fleets; applies heavy energy neutralizers and heavy drones."
    },
    "Moros": {
        "class": "Dreadnought",
        "faction": "Gallente",
        "role": "Capital Blaster / Rail Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with massive capital hybrid DPS."
    },
    "Moros Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Gallente (Navy)",
        "role": "Navy Capital Hybrid Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Enhanced hybrid turret tracking and armor buffer."
    },
    "Hubris": {
        "class": "Lancer Dreadnought",
        "faction": "Gallente",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp."
    },
    "Thanatos": {
        "class": "Carrier",
        "faction": "Gallente",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Carrier with fighter damage and fighter navigation bonuses."
    },
    "Nyx": {
        "class": "Supercarrier",
        "faction": "Gallente",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital with devastating heavy fighter strike wings."
    },
    "Ninazu": {
        "class": "Force Auxiliary",
        "faction": "Gallente",
        "role": "Capital Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Armor",
        "tactics": "Capital remote armor repair ship with massive burst reps."
    },
    "Erebus": {
        "class": "Titan",
        "faction": "Gallente",
        "role": "Supercapital Doomsday Titan",
        "threat": "THREAT_SUPER",
        "tank": "Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Doomsday hybrid titan with fleet armor burst."
    },
    "Iteron Mark V": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Classic high-capacity T1 industrial."
    },
    "Epithal": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Planetary Industry Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Planetary Commodities cargo bay."
    },
    "Miasmos": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Mineral & Ore Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Mineral/Ore cargo bay."
    },
    "Kryos": {
        "class": "Industrial",
        "faction": "Gallente",
        "role": "Ice Product Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ice/Isotope cargo bay."
    },
    "Viator": {
        "class": "Blockade Runner",
        "faction": "Gallente",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Armor",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler."
    },
    "Occator": {
        "class": "Deep Space Transport",
        "faction": "Gallente",
        "role": "Heavy Armor DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Armor Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar."
    },
    "Obelisk": {
        "class": "Freighter",
        "faction": "Gallente",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter."
    },
    "Anshar": {
        "class": "Jump Freighter",
        "faction": "Gallente",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Armor Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics."
    },
    "Executioner": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Fast Tackle / Laser Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "High-speed laser tackler with energy turret cap reduction."
    },
    "Tormentor": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Laser / Drone Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer / Active",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Strong pulse laser damage and light drone assistance."
    },
    "Punisher": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Heavy Armor Buffer / Laser Frigate",
        "threat": "THREAT_COMBATANT",
        "tank": "Immense Armor Buffer (4 Low Slots)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Cruiser-grade armor buffer on a frigate hull."
    },
    "Inquisitor": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor",
        "tactics": "T1 frigate armor logistics."
    },
    "Crucifier": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Tracking Disruptor Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast",
        "optimal_range": "30-70 km",
        "tactics": "Applies severe tracking disruption to enemy turrets."
    },
    "Magnate": {
        "class": "Frigate",
        "faction": "Amarr",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate with 4 low slots."
    },
    "Imperial Navy Slicer": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Beam / Pulse Nano Laser Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Extreme (4.6+ km/s)",
        "optimal_range": "20-40 km",
        "tactics": "Premier nano laser kiter. Strikes from 35 km with Scorch / Aurora."
    },
    "Crucifier Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Tracking Disruptor / Laser Brawler",
        "threat": "THREAT_ECM",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Combines tracking disruption with strong energy turret DPS."
    },
    "Magnate Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Amarr (Navy)",
        "role": "Combat Explorer / Heavy Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Faction combat exploration frigate."
    },
    "Anathema": {
        "class": "Covert Ops",
        "faction": "Amarr",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Covert cloaking scout frigate."
    },
    "Purifier": {
        "class": "Stealth Bomber",
        "faction": "Amarr",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "EM bombs and torpedoes from cloak."
    },
    "Retribution": {
        "class": "Assault Frigate",
        "faction": "Amarr",
        "role": "Beam Laser / ADC Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "15-45 km",
        "tactics": "Premier assault frigate fleet sniper. High EM/Thermal DPS with ADC."
    },
    "Vengeance": {
        "class": "Assault Frigate",
        "faction": "Amarr",
        "role": "Rocket / Active Armor Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Armor + ADC",
        "speed": "Moderate",
        "optimal_range": "0-20 km",
        "tactics": "Heavy rocket assault frigate with dual armor reps."
    },
    "Sentinel": {
        "class": "Electronic Attack Ship",
        "faction": "Amarr",
        "role": "Long-Range Cap Drain & Tracking Disruptor",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.0+ km/s)",
        "optimal_range": "30-50 km",
        "tactics": "Drains capacitor dry from 40 km and applies tracking disruption. Critical target."
    },
    "Crusader": {
        "class": "Interceptor",
        "faction": "Amarr",
        "role": "Laser Fleet Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Nullified fast tackle combat interceptor."
    },
    "Malediction": {
        "class": "Interceptor",
        "faction": "Amarr",
        "role": "Fleet Fast Tackle Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Premier fleet tackle interceptor with rocket and point."
    },
    "Deacon": {
        "class": "Logistics Frigate",
        "faction": "Amarr",
        "role": "T2 Armor Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Fast",
        "optimal_range": "Remote Armor",
        "tactics": "Assault-tier remote armor repair frigate."
    },
    "Coercer": {
        "class": "Destroyer",
        "faction": "Amarr",
        "role": "Pulse / Beam Laser Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-15 km (Pulse) / 30-65 km (Beam)",
        "tactics": "8 energy turrets deliver high instant EM/Thermal laser DPS."
    },
    "Dragoon": {
        "class": "Destroyer",
        "faction": "Amarr",
        "role": "Drone / Cap Neutralizer Destroyer",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-30 km",
        "tactics": "Heavy energy neutralizers and light drones. Drains frigate capacitor in 1 cycle."
    },
    "Coercer Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Destroyer",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-25 km / 40-80 km",
        "tactics": "Reduced capacitor usage and enhanced tracking."
    },
    "Heretic": {
        "class": "Interdictor",
        "faction": "Amarr",
        "role": "Armor Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Deploys 20km warp disruption bubbles on gates."
    },
    "Pontifex": {
        "class": "Command Destroyer",
        "faction": "Amarr",
        "role": "Micro Jump Field / Armor Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Confessor": {
        "class": "Tactical Destroyer",
        "faction": "Amarr",
        "role": "T3 Mode-Switching Laser Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Armor",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "15-50 km",
        "tactics": "Switches between Propulsion, Sharpshooter (laser optimal/damage), and Defensive modes."
    },
    "Omen": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Beam / Pulse Attack Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.2+ km/s)",
        "optimal_range": "20-45 km",
        "tactics": "Fast laser attack cruiser with high EM/Thermal DPS."
    },
    "Maller": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Heavy Armor Buffer Bait Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Buffer (6 Lows)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Extremely heavy armor resistance bonus; classic fleet bait/line cruiser."
    },
    "Augoror": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Armor Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor (Cap Transfer)",
        "tactics": "Cap-chain armor logistics cruiser. Maintain cap chain with second Augoror."
    },
    "Arbitrator": {
        "class": "Cruiser",
        "faction": "Amarr",
        "role": "Tracking Disruptor / Drone Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-50 km",
        "tactics": "Applies severe tracking disruption while deploying combat drones."
    },
    "Omen Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Amarr (Navy)",
        "role": "Heavy Laser Nano Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast (2.6+ km/s)",
        "optimal_range": "25-55 km",
        "tactics": "Premier nano beam kiter with high laser tracking and alpha."
    },
    "Augoror Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Amarr (Navy)",
        "role": "Heavy Armor Laser Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Battleship-Grade Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-20 km",
        "tactics": "Massive armor buffer and high laser DPS."
    },
    "Zealot": {
        "class": "Heavy Assault Cruiser",
        "faction": "Amarr",
        "role": "HAC Beam Laser Sniper",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer + ADC",
        "speed": "Moderate",
        "optimal_range": "40-90 km",
        "tactics": "Armor fleet laser sniper with high EM/Thermal alpha and ADC."
    },
    "Sacrilege": {
        "class": "Heavy Assault Cruiser",
        "faction": "Amarr",
        "role": "HAC Heavy Assault Missile Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Heavy Armor Buffer / Active + ADC",
        "speed": "Fast",
        "optimal_range": "15-40 km",
        "tactics": "High-resist HAC firing heavy assault missiles and cap neutralizers."
    },
    "Devoter": {
        "class": "Heavy Interdiction Cruiser",
        "faction": "Amarr",
        "role": "Warp Disruption Field Generator",
        "threat": "THREAT_BUBBLE",
        "tank": "Immense Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-20 km (Bubble) / Infinite Scram",
        "tactics": "Heavy armor HIC projecting focused infinite points or mobile bubbles."
    },
    "Pilgrim": {
        "class": "Force Recon",
        "faction": "Amarr",
        "role": "Covert Cloak / Cap Neut / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-25 km",
        "tactics": "Uncloaks to neut capacitor dry, apply tracking disruption, and light Covert Cyno."
    },
    "Curse": {
        "class": "Combat Recon",
        "faction": "Amarr",
        "role": "D-Scan Immune 50km Cap Neut",
        "threat": "THREAT_ECM",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-60 km",
        "tactics": "Invisible to D-Scan. Heavy neutralizers drain cap at 50km range."
    },
    "Guardian": {
        "class": "Logistics Cruiser",
        "faction": "Amarr",
        "role": "T2 Cap-Chain Armor Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Armor",
        "speed": "Moderate",
        "optimal_range": "Remote Armor (Cap Transfer)",
        "tactics": "Premier T2 armor logistics. Maintain cap chain with second Guardian."
    },
    "Legion": {
        "class": "Strategic Cruiser",
        "faction": "Amarr",
        "role": "Modular T3C (Laser / Missile / Neut / Cloak)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / Active",
        "speed": "Fast (1.8-2.4 km/s)",
        "optimal_range": "20-70 km",
        "tactics": "Highly customizable. Can fit covert cloak, interdiction nullification, heavy neuts, or 100MN AB."
    },
    "Harbinger": {
        "class": "Battlecruiser",
        "faction": "Amarr",
        "role": "Heavy Laser Line BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "20-60 km",
        "tactics": "6 heavy energy turrets with high tracking and laser DPS."
    },
    "Prophecy": {
        "class": "Battlecruiser",
        "faction": "Amarr",
        "role": "Heavy Drone / Armor Fleet BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Buffer (Triple Trimark)",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Extremely tanky drone battlecruiser. Standard faction warfare doctrine."
    },
    "Oracle": {
        "class": "Attack Battlecruiser",
        "faction": "Amarr",
        "role": "Battleship-Gun Laser Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Armor",
        "speed": "Moderate",
        "optimal_range": "60-140 km",
        "tactics": "Large Mega Beam / Tachyon lasers on BC hull. Extreme instant alpha."
    },
    "Harbinger Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Fast",
        "optimal_range": "20-70 km",
        "tactics": "Enhanced laser tracking and armor resistance bonus."
    },
    "Prophecy Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Amarr (Navy)",
        "role": "Navy Missile / Drone BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "20-60 km",
        "tactics": "Combines heavy missiles and full drone flights."
    },
    "Damnation": {
        "class": "Command Ship",
        "faction": "Amarr",
        "role": "Armor Fleet Command Flagship",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer (300k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-30 km",
        "tactics": "Provides Fleet Armor Bursts with near-unbreakable armor buffer."
    },
    "Absolution": {
        "class": "Command Ship",
        "faction": "Amarr",
        "role": "Laser Fleet Command Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Armor Buffer",
        "speed": "Slow",
        "optimal_range": "20-50 km",
        "tactics": "Provides Fleet Armor / Information Bursts with heavy laser DPS."
    },
    "Apocalypse": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Large Beam / Pulse Laser Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "8 large laser turrets with optimal range and tracking bonuses."
    },
    "Armageddon": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Heavy Cap Neut / Drone / Missile BS",
        "threat": "THREAT_ECM",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "0-50 km",
        "tactics": "Heavy energy neutralizer range bonus drains 2500+ GJ per cycle at 40 km."
    },
    "Abaddon": {
        "class": "Battleship",
        "faction": "Amarr",
        "role": "Heavy Laser Line Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Massive Armor Resistance Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "High armor resistance bonus; heavy cap consumption on lasers."
    },
    "Apocalypse Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser Sniper Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "60-150 km",
        "tactics": "Extreme laser rate of fire and optimal range."
    },
    "Armageddon Navy Issue": {
        "class": "Faction Battleship",
        "faction": "Amarr (Navy)",
        "role": "Navy Laser / Drone Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor Buffer",
        "speed": "Slow",
        "optimal_range": "30-80 km",
        "tactics": "Laser damage and heavy drone damage combination."
    },
    "Paladin": {
        "class": "Marauder",
        "faction": "Amarr",
        "role": "Bastion Beam / Pulse Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Armor (Bastion Mode)",
        "speed": "Immobile in Bastion",
        "optimal_range": "40-100 km (Mega Pulse / Scorch) / 100-180 km (Tachyon)",
        "tactics": "Bastion Mode doubles armor reps and yields 2500+ DPS with Scorch L. Apply neuts."
    },
    "Redeemer": {
        "class": "Black Ops",
        "faction": "Amarr",
        "role": "Covert Jump / Laser Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Armor Buffer / Active",
        "speed": "Slow (Covert Jump)",
        "optimal_range": "30-80 km",
        "tactics": "Bridges covert fleets; massive instant laser alpha strike."
    },
    "Revelation": {
        "class": "Dreadnought",
        "faction": "Amarr",
        "role": "Capital Mega Beam / Pulse Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Siege)",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Siege dreadnought with capital energy turrets. Infinite ammo with crystals."
    },
    "Revelation Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Amarr (Navy)",
        "role": "Navy Capital Laser Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Enhanced energy turret tracking and armor buffer."
    },
    "Bane": {
        "class": "Lancer Dreadnought",
        "faction": "Amarr",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp."
    },
    "Archon": {
        "class": "Carrier",
        "faction": "Amarr",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Armor Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Capital carrier with fighter resistance and cap transfers."
    },
    "Aeon": {
        "class": "Supercarrier",
        "faction": "Amarr",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Immense Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Supercapital heavy fighter strike wings."
    },
    "Apostle": {
        "class": "Force Auxiliary",
        "faction": "Amarr",
        "role": "Capital Armor FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Armor (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Armor",
        "tactics": "Capital remote armor repair ship with massive burst reps."
    },
    "Avatar": {
        "class": "Titan",
        "faction": "Amarr",
        "role": "Supercapital Judgement Titan",
        "threat": "THREAT_SUPER",
        "tank": "Immense Armor Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Judgement EM Doomsday titan with fleet armor burst."
    },
    "Bestower": {
        "class": "Industrial",
        "faction": "Amarr",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity hauler."
    },
    "Sigil": {
        "class": "Industrial",
        "faction": "Amarr",
        "role": "Fast Industrial Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Fast for Hauler",
        "optimal_range": "0 km",
        "tactics": "Fast sub-warp align industrial."
    },
    "Prorator": {
        "class": "Blockade Runner",
        "faction": "Amarr",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Armor",
        "speed": "Fast (<3s align)",
        "optimal_range": "0 km",
        "tactics": "Covert cloaking, cargo-scanned immune hauler."
    },
    "Impel": {
        "class": "Deep Space Transport",
        "faction": "Amarr",
        "role": "Heavy Armor DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Armor Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar."
    },
    "Providence": {
        "class": "Freighter",
        "faction": "Amarr",
        "role": "Standard Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Extremely Slow",
        "optimal_range": "0 km",
        "tactics": "Massive cargo freighter."
    },
    "Ark": {
        "class": "Jump Freighter",
        "faction": "Amarr",
        "role": "Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Armor Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Jump drive cargo hauler for nullsec logistics."
    },
    "Slasher": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Fast Tackle / Projectile Tackler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-10 km",
        "tactics": "Fastest T1 tackle frigate with projectile tracking."
    },
    "Rifter": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Projectile Brawler / Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Versatile projectile combat frigate with selectable damage."
    },
    "Breacher": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Dual MASB Missile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Dual MASB Active Shield",
        "speed": "Fast",
        "optimal_range": "0-25 km",
        "tactics": "Extreme active shield tank with light missiles/rockets."
    },
    "Probe": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Exploration / Light Drone",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Scanning and exploration frigate."
    },
    "Burst": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "T1 frigate shield logistics."
    },
    "Vigil": {
        "class": "Frigate",
        "faction": "Minmatar",
        "role": "Target Painter Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "40-80 km",
        "tactics": "Target painters inflate signature radius across the grid."
    },
    "Republic Fleet Firetail": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "High Alpha Projectile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.2+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fast projectile frigate with tracking and damage bonuses."
    },
    "Vigil Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "Dual Web Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (4.5+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Stasis webifier range bonus with rocket application."
    },
    "Probe Navy Issue": {
        "class": "Faction Frigate",
        "faction": "Minmatar (Fleet)",
        "role": "Combat Explorer / Rocket Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Exploration combat frigate with rocket DPS."
    },
    "Cheetah": {
        "class": "Covert Ops",
        "faction": "Minmatar",
        "role": "Stealth Scout / Cyno",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "Covert",
        "tactics": "Fastest covert ops scout frigate."
    },
    "Hound": {
        "class": "Stealth Bomber",
        "faction": "Minmatar",
        "role": "Covert Torpedo / Bomb Bomber",
        "threat": "THREAT_COVERT",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "30-60 km",
        "tactics": "Explosive bombs and torpedoes from cloak."
    },
    "Wolf": {
        "class": "Assault Frigate",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor Buffer / SAAR + ADC",
        "speed": "Fast (3.5+ km/s)",
        "optimal_range": "0-15 km (AC) / 25-50 km (Art)",
        "tactics": "Premier combat assault frigate. High projectile tracking and ADC survivability."
    },
    "Jaguar": {
        "class": "Assault Frigate",
        "faction": "Minmatar",
        "role": "Dual MASB Tackle Assault",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Dual MASB Shield + ADC",
        "speed": "Extreme (4.0+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Extreme active shield tackle frigate. Survives heavy incoming fire."
    },
    "Hyena": {
        "class": "Electronic Attack Ship",
        "faction": "Minmatar",
        "role": "40km Stasis Webifier Frigate",
        "threat": "THREAT_ECM",
        "tank": "Paper Thin",
        "speed": "Fast (4.2+ km/s)",
        "optimal_range": "0-40 km",
        "tactics": "Projects 40km stasis webifiers stopping targets cold."
    },
    "Claw": {
        "class": "Interceptor",
        "faction": "Minmatar",
        "role": "Artillery / AC Fleet Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Extreme (4.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Nullified fast tackle combat interceptor."
    },
    "Stiletto": {
        "class": "Interceptor",
        "faction": "Minmatar",
        "role": "Premier Fast Tackle Interceptor",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield",
        "speed": "Extreme (5.0+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "Fastest locking fleet tackle interceptor."
    },
    "Scalpel": {
        "class": "Logistics Frigate",
        "faction": "Minmatar",
        "role": "T2 Shield Logistics Frigate",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Assault-tier remote shield repair frigate."
    },
    "Thrasher": {
        "class": "Destroyer",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery High Alpha",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast (2.5 km/s)",
        "optimal_range": "0-15 km AC / 40-70 km Art",
        "tactics": "8 projectile turrets deliver huge instant alpha strike."
    },
    "Talwar": {
        "class": "Destroyer",
        "faction": "Minmatar",
        "role": "Light Missile / Rocket Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.2 km/s)",
        "optimal_range": "30-65 km",
        "tactics": "7 missile launchers with reduced MWD signature bloom."
    },
    "Thrasher Navy Issue": {
        "class": "Faction Destroyer",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Projectile Brawler",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast (2.8+ km/s)",
        "optimal_range": "0-20 km",
        "tactics": "Enhanced projectile tracking and signature reduction."
    },
    "Sabre": {
        "class": "Interdictor",
        "faction": "Minmatar",
        "role": "Premier Warp Bubble Launcher",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Extreme (3.2+ km/s)",
        "optimal_range": "0-15 km",
        "tactics": "King of interdictors. Deploys 20km warp disruption bubbles instantly."
    },
    "Bifrost": {
        "class": "Command Destroyer",
        "faction": "Minmatar",
        "role": "Micro Jump Field / Shield Skiff",
        "threat": "THREAT_BUBBLE",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-20 km",
        "tactics": "Spools 100km Micro Jump Field to kidnap ships on grid."
    },
    "Svipul": {
        "class": "Tactical Destroyer",
        "faction": "Minmatar",
        "role": "T3 Mode-Switching Projectile Destroyer",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active / Passive Shield / Armor",
        "speed": "Variable (Prop/Sharpshooter/Defensive)",
        "optimal_range": "0-40 km",
        "tactics": "Switches between Propulsion (4+ km/s), Sharpshooter (artillery alpha), and Defensive modes."
    },
    "Stabber": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Autocannon / Artillery Attack Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast (2.4+ km/s)",
        "optimal_range": "0-20 km (AC) / 40-70 km (Art)",
        "tactics": "Fastest T1 cruiser with selectable projectile damage."
    },
    "Rupture": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Heavy Projectile Fleet Cruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "0-25 km",
        "tactics": "Heavy projectile damage and armor repair bonuses."
    },
    "Scythe": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Shield Logistics Cruiser",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Fast",
        "optimal_range": "Remote Shield",
        "tactics": "Self-sufficient shield logistics cruiser (no cap chain required)."
    },
    "Bellicose": {
        "class": "Cruiser",
        "faction": "Minmatar",
        "role": "Target Painter / Missile Cruiser",
        "threat": "THREAT_ECM",
        "tank": "Shield Buffer",
        "speed": "Moderate",
        "optimal_range": "30-70 km",
        "tactics": "Target painters inflate signature radius for missile fleet."
    },
    "Stabber Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Heavy Projectile Nano Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Extreme (2.8+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "Premier nano autocannon skirmisher with extreme agility."
    },
    "Scythe Navy Issue": {
        "class": "Faction Cruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Fast Missile / Rocket Kiter",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Extreme (2.8+ km/s)",
        "optimal_range": "25-60 km",
        "tactics": "High-speed missile platform with rapid application."
    },
    "Vagabond": {
        "class": "Heavy Assault Cruiser",
        "faction": "Minmatar",
        "role": "HAC Active Shield Nano Kiter",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Active Shield (Dual XL-ASB) + ADC",
        "speed": "Extreme (3.0+ km/s)",
        "optimal_range": "15-35 km",
        "tactics": "King of nano brawlers. High sub-warp speed and ADC survivability."
    },
    "Muninn": {
        "class": "Heavy Assault Cruiser",
        "faction": "Minmatar",
        "role": "HAC Heavy Missile Fleet Cruiser",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Armor / Shield Buffer + ADC",
        "speed": "Fast",
        "optimal_range": "40-80 km",
        "tactics": "High-resist HAC heavy missile line fleet platform."
    },
    "Huginn": {
        "class": "Combat Recon",
        "faction": "Minmatar",
        "role": "D-Scan Immune 40km Web & Painter",
        "threat": "THREAT_ECM",
        "tank": "Shield / Armor Buffer",
        "speed": "Moderate",
        "optimal_range": "0-40 km (Web) / 60-100 km (Paint)",
        "tactics": "Invisible to D-Scan. 40km+ stasis web stops targets dead."
    },
    "Rapier": {
        "class": "Force Recon",
        "faction": "Minmatar",
        "role": "Covert Cloak / 40km Web / Cyno",
        "threat": "THREAT_CYNO",
        "tank": "Paper Thin",
        "speed": "Cloaked",
        "optimal_range": "0-40 km",
        "tactics": "Uncloaks to apply 40km webifier and light Covert Cyno."
    },
    "Scimitar": {
        "class": "Logistics Cruiser",
        "faction": "Minmatar",
        "role": "T2 Solo Shield Logistics",
        "threat": "THREAT_LOGI",
        "tank": "Shield",
        "speed": "Extreme (2.5+ km/s)",
        "optimal_range": "Remote Shield",
        "tactics": "Fastest T2 shield logistics cruiser with self-sufficient cap."
    },
    "Loki": {
        "class": "Strategic Cruiser",
        "faction": "Minmatar",
        "role": "Modular T3C (Web / Artillery / Covert)",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Shield / Armor Buffer / Active",
        "speed": "Extreme (2.2-3.0 km/s)",
        "optimal_range": "0-45 km (Web) / 30-80 km (Art/HAM)",
        "tactics": "Premier T3C. Fields 40km webs, covert cloak, interdiction nullification, 100MN AB, or heavy artillery/HAMs."
    },
    "Cyclone": {
        "class": "Battlecruiser",
        "faction": "Minmatar",
        "role": "Active Shield Missile / AC BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Active Shield (Dual MASB / XL-ASB)",
        "speed": "Fast for BC",
        "optimal_range": "15-40 km",
        "tactics": "Massive active shield repair bonus with heavy missiles."
    },
    "Hurricane": {
        "class": "Battlecruiser",
        "faction": "Minmatar",
        "role": "Heavy Projectile Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BC",
        "optimal_range": "15-40 km AC / 70+ km Art",
        "tactics": "Versatile projectile platform with high alpha strike."
    },
    "Tornado": {
        "class": "Attack Battlecruiser",
        "faction": "Minmatar",
        "role": "Battleship-Gun 1400mm Artillery Sniper",
        "threat": "THREAT_COMBATANT",
        "tank": "Paper Thin Shield",
        "speed": "Fast for BC (2.0 km/s)",
        "optimal_range": "80-150 km",
        "tactics": "Large 1400mm Artillery on BC hull. Devastating alpha strike (10,000+ alpha)."
    },
    "Cyclone Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Heavy Missile / Shield BC",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-60 km",
        "tactics": "Superior missile rate of fire and shield buffer."
    },
    "Hurricane Navy Issue": {
        "class": "Faction Battlecruiser",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Projectile Battlecruiser",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast",
        "optimal_range": "20-80 km",
        "tactics": "Higher projectile tracking and armor/shield flexibility."
    },
    "Sleipnir": {
        "class": "Command Ship",
        "faction": "Minmatar",
        "role": "Shield Fleet Command / Autocannon Brawler",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Active Shield (Dual XL-ASB)",
        "speed": "Fast for Command",
        "optimal_range": "15-40 km",
        "tactics": "Provides Fleet Shield / Skirmish Bursts and deals 1200+ AC DPS."
    },
    "Claymore": {
        "class": "Command Ship",
        "faction": "Minmatar",
        "role": "Shield Fleet Command / Missile",
        "threat": "THREAT_T2_COMBAT",
        "tank": "Immense Shield Buffer",
        "speed": "Fast for Command",
        "optimal_range": "20-60 km",
        "tactics": "Provides Fleet Skirmish / Shield Bursts with heavy missiles."
    },
    "Tempest": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Artillery / AC Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor",
        "speed": "Fast for BS",
        "optimal_range": "20-40 km AC / 100+ km Art",
        "tactics": "High-speed projectile battleship with massive alpha."
    },
    "Typhoon": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Cruise / Torpedo / Cruise BS",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer / Active",
        "speed": "Fast for BS",
        "optimal_range": "30-100 km",
        "tactics": "High rate of fire missile and projectile platform."
    },
    "Maelstrom": {
        "class": "Battleship",
        "faction": "Minmatar",
        "role": "Active Shield / Artillery BS",
        "threat": "THREAT_COMBATANT",
        "tank": "Active Shield (X-Large Booster)",
        "speed": "Slow",
        "optimal_range": "60-140 km",
        "tactics": "Massive shield boost bonus; heavy 1400mm artillery fleet anchor."
    },
    "Tempest Fleet Issue": {
        "class": "Faction Battleship",
        "faction": "Minmatar (Fleet)",
        "role": "Artillery / AC High Alpha Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BS",
        "optimal_range": "25-50 km AC / 100+ km Art",
        "tactics": "Extreme projectile rate of fire and devastating alpha strike."
    },
    "Typhoon Fleet Issue": {
        "class": "Faction Battleship",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Missile / Cruise Battleship",
        "threat": "THREAT_COMBATANT",
        "tank": "Armor / Shield Buffer",
        "speed": "Fast for BS",
        "optimal_range": "40-120 km",
        "tactics": "Enhanced missile application and projectile support."
    },
    "Vargur": {
        "class": "Marauder",
        "faction": "Minmatar",
        "role": "Bastion Autocannon / Artillery Marauder",
        "threat": "THREAT_MARAUDER",
        "tank": "Active Shield (Dual XL-ASB in Bastion)",
        "speed": "Immobile in Bastion",
        "optimal_range": "25-60 km (AC) / 100-180 km (Artillery)",
        "tactics": "Bastion Mode doubles shield reps and yields 3000+ DPS with Hail L. Apply neuts."
    },
    "Panther": {
        "class": "Black Ops",
        "faction": "Minmatar",
        "role": "Covert Jump / Projectile Battleship",
        "threat": "THREAT_CYNO",
        "tank": "Shield / Armor Buffer",
        "speed": "Fast for BS (Covert Jump)",
        "optimal_range": "25-60 km",
        "tactics": "Fastest Black Ops battleship with massive projectile alpha."
    },
    "Naglfar": {
        "class": "Dreadnought",
        "faction": "Minmatar",
        "role": "Capital Projectile Siege",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield / Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "High alpha projectile dreadnought with Siege module."
    },
    "Naglfar Navy Issue": {
        "class": "Faction Dreadnought",
        "faction": "Minmatar (Fleet)",
        "role": "Navy Capital Projectile Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield / Armor Active",
        "speed": "Capital",
        "optimal_range": "Capital Grid",
        "tactics": "Superior projectile tracking and dual tank versatility."
    },
    "Valravn": {
        "class": "Lancer Dreadnought",
        "faction": "Minmatar",
        "role": "Disruptive Lancer Dread",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Active",
        "speed": "Capital",
        "optimal_range": "Lancer Beam",
        "tactics": "Fires disruptive capital lance disabling cynos and warp."
    },
    "Nidhoggur": {
        "class": "Carrier",
        "faction": "Minmatar",
        "role": "Capital Fighter Carrier",
        "threat": "THREAT_CAPITAL",
        "tank": "Shield Buffer",
        "speed": "Capital",
        "optimal_range": "Fighter Range",
        "tactics": "Capital carrier with fighter speed and fighter damage bonuses."
    },
    "Hel": {
        "class": "Supercarrier",
        "faction": "Minmatar",
        "role": "Supercapital Heavy Carrier",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Fastest supercarrier with immense fighter strike damage."
    },
    "Lif": {
        "class": "Force Auxiliary",
        "faction": "Minmatar",
        "role": "Capital Shield FAX",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Triage)",
        "speed": "Capital",
        "optimal_range": "Remote Shield",
        "tactics": "Capital remote shield repair ship."
    },
    "Ragnarok": {
        "class": "Titan",
        "faction": "Minmatar",
        "role": "Supercapital Gjallarhorn Titan",
        "threat": "THREAT_SUPER",
        "tank": "Shield Buffer",
        "speed": "Supercapital",
        "optimal_range": "Omni Grid",
        "tactics": "Gjallarhorn Explosive Doomsday titan with fleet shield burst."
    },
    "Mammoth": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "High-Capacity Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Large cargo capacity industrial."
    },
    "Wreathe": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "Fast Industrial Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Fast (<4s align)",
        "optimal_range": "0 km",
        "tactics": "Fast sub-warp align industrial."
    },
    "Hoarder": {
        "class": "Industrial",
        "faction": "Minmatar",
        "role": "Ammo & Charge Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ammo/Charge cargo bay."
    },
    "Prowler": {
        "class": "Blockade Runner",
        "faction": "Minmatar",
        "role": "Covert Fast Hauler",
        "threat": "THREAT_HAULER",
        "tank": "Cloaked Shield",
        "speed": "Fast (<2.5s align)",
        "optimal_range": "0 km",
        "tactics": "Fastest blockade runner with covert cloak."
    },
    "Mastodon": {
        "class": "Deep Space Transport",
        "faction": "Minmatar",
        "role": "Heavy Shield DST",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (+2 Warp Core)",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "+2 native warp core strength and Fleet Hangar."
    },
    "Fenrir": {
        "class": "Freighter",
        "faction": "Minmatar",
        "role": "Fast Sub-Capital Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Buffer",
        "speed": "Fastest Freighter",
        "optimal_range": "0 km",
        "tactics": "Fastest aligning standard freighter."
    },
    "Nomad": {
        "class": "Jump Freighter",
        "faction": "Minmatar",
        "role": "Fast Capital Jump Freighter",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Jump Drive",
        "optimal_range": "0 km",
        "tactics": "Fastest aligning jump freighter for nullsec logistics."
    },
    "Venture": {
        "class": "Mining Frigate",
        "faction": "ORE",
        "role": "Gas / Ore / +2 Warp Core Miner",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Native +2 warp core strength allows slipping standard points."
    },
    "Prospect": {
        "class": "Expedition Frigate",
        "faction": "ORE",
        "role": "Covert Ops Gas / Ore Miner",
        "threat": "THREAT_MINING",
        "tank": "Cloaked Shield",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Covert cloaking mining frigate. Can fit Covert Cyno."
    },
    "Endurance": {
        "class": "Expedition Frigate",
        "faction": "ORE",
        "role": "Cloaked Ice Mining Frigate",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast",
        "optimal_range": "0-15 km",
        "tactics": "Specialized ice mining frigate with cloak bonus."
    },
    "Retriever": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "High-Capacity Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Large ore hold mining barge. Easy target."
    },
    "Procurer": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "Heavy Tanked Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Heavy Shield Buffer (60k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Heavy shield resistance bonus. Difficult to gank."
    },
    "Covetor": {
        "class": "Mining Barge",
        "faction": "ORE",
        "role": "High Yield Mining Barge",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Maximum mining yield with paper tank."
    },
    "Mackinaw": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "High-Capacity T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "T2 mining exhumer with massive ore hold."
    },
    "Skiff": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "Immense Tanked T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Immense Shield Buffer (100k+ EHP)",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "T2 mining exhumer with battleship-grade shield tank."
    },
    "Hulk": {
        "class": "Exhumer",
        "faction": "ORE",
        "role": "Maximum Yield T2 Exhumer",
        "threat": "THREAT_MINING",
        "tank": "Paper Thin",
        "speed": "Slow",
        "optimal_range": "0-15 km",
        "tactics": "Maximum mining yield in EVE. Requires fleet defense."
    },
    "Noctis": {
        "class": "Salvage Ship",
        "faction": "ORE",
        "role": "Fleet Salvage / Tractor Flagship",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0-40 km",
        "tactics": "Rapid tractor beam and salvager bonuses."
    },
    "Porpoise": {
        "class": "Industrial Command",
        "faction": "ORE",
        "role": "Compact Mining Command / Booster",
        "threat": "THREAT_MINING",
        "tank": "Shield Buffer",
        "speed": "Fast for Command",
        "optimal_range": "Mining Boost Range",
        "tactics": "Sub-capital mining booster and drone combatant."
    },
    "Orca": {
        "class": "Industrial Command",
        "faction": "ORE",
        "role": "Heavy Mining Command / Fleet Hangar",
        "threat": "THREAT_HAULER",
        "tank": "Immense Shield Buffer (300k+ EHP)",
        "speed": "Slow",
        "optimal_range": "Mining Boost Range",
        "tactics": "Fleet booster, ore compression, and massive cargo hold."
    },
    "Rorqual": {
        "class": "Capital Industrial",
        "faction": "ORE",
        "role": "Capital Mining Command / PANIC",
        "threat": "THREAT_CAPITAL",
        "tank": "Active Shield (Industrial Core + PANIC)",
        "speed": "Capital",
        "optimal_range": "Mining Grid",
        "tactics": "Capital mining flagship. PANIC module grants 5-7.5 minutes of complete invulnerability."
    },
    "Bowhead": {
        "class": "Freighter",
        "faction": "ORE",
        "role": "Assembled Ship Transport",
        "threat": "THREAT_HAULER",
        "tank": "Shield Buffer",
        "speed": "Slow",
        "optimal_range": "0 km",
        "tactics": "Specialized Ship Maintenance Bay transports fully assembled battleships."
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

import functools

_RE_CLEAN_ALPHANUM = re.compile(r"[^a-z0-9]")
_RE_WORDS = re.compile(r"\b[A-Za-z0-9\-]+\b")
_RE_OWN_SHIP = re.compile(
    r"\b(?:i am in an?|i'm in an?|flying an?|piloting an?|my ship is an?|in an?)\s+([A-Za-z0-9\-\s]+?)(?:\s+and|\s+with|\s+need|\s+looking|\s+waiting|\s+fighting|\s+vs|\s+against|\s*\.|\s*,|\s*$)",
    re.IGNORECASE
)

# Common EVE Online Shorthand Combat Aliases
_COMMON_SHIP_ALIASES: Dict[str, str] = {
    "slicer": "Imperial Navy Slicer",
    "in slicer": "Imperial Navy Slicer",
    "hookbill": "Caldari Navy Hookbill",
    "comet": "Federation Navy Comet",
    "firetail": "Republic Fleet Firetail",
    "omen navy": "Omen Navy Issue",
    "stabber fleet": "Stabber Fleet Issue",
    "scythe fleet": "Scythe Fleet Issue",
    "caracal navy": "Caracal Navy Issue",
    "drake navy": "Drake Navy Issue",
    "exequror navy": "Exequror Navy Issue",
    "vexor navy": "Vexor Navy Issue",
    "brutix navy": "Brutix Navy Issue",
    "megathron navy": "Megathron Navy Issue",
    "tempest fleet": "Tempest Fleet Issue",
    "typhoon fleet": "Typhoon Fleet Issue",
    "bhaal": "Bhaalgorn",
    "vindi": "Vindicator",
    "macha": "Machariel",
    "rattle": "Rattlesnake"
}

# Fast Normalized Lookup Tables & Pre-Rendered Dossiers for Sub-Microsecond Resolution
_FAST_SHIP_LOOKUP: Dict[str, Dict[str, Any]] = {}
for _k, _v in SHIP_DATABASE.items():
    _v_copy = dict(_v)
    _v_copy["canonical_name"] = _k
    _v_copy["pre_rendered_dossier"] = (
        f"• {_k} ({_v.get('class', 'Vessel')} - {_v.get('faction', 'General')}) | Tank: {_v.get('tank', 'Shield/Armor')} | "
        f"Optimal: {_v.get('optimal_range', 'Standard')} | Threat: {_v.get('threat', 'Combatant')}\n"
        f"  Tactics: {_v.get('tactics', 'Engage according to weapon tracking and range.')}"
    )
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
    
    has_armor_tank = any(any(k in m.lower() for k in ["plate", "armor repairer", "energized membrane"]) for m in lows)
    has_shield_tank = any(any(k in m.lower() for k in ["shield extender", "shield booster", "shield hardener"]) for m in mids)
    
    if has_armor_tank and has_shield_tank:
        warnings.append("Dual-Tank Conflict Detected: Fitting both Shield and Armor defensive modules divides fitting resources.")

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
