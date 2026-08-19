"""
EVE Online Tactical Database, Comprehensive Combat Matrix & Domain Grounding Engine.
Customized for A.U.R.A. (Adaptive Underworld Recon Array) — ver.0.1.1phi & Core.
Contains encyclopedic vessel dossiers, weapon tracking mathematics, capacitor warfare,
abyssal deadspace environmental hazards, and electronic warfare matrices.
Covers all standard empire, navy, pirate, and industrial vessels while excluding unobtainable AT ships.
"""
from typing import Dict, List, Any, Optional
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

SHIP_DATABASE: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. PIRATE & FACTION VESSELS
    # =========================================================================
    # --- Angel Cartel ---
    "Dramiel": {"class": "Frigate", "faction": "Angel Cartel", "role": "Pirate Interceptor / Tackler", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme (4.5-5.5 km/s MWD)", "optimal_range": "0-12 km (Autocannons)", "tactics": "Extreme warp speed and agility. Fly with high transversal against larger guns. Vulnerable to dual webs and scramblers."},
    "Mekubal": {"class": "Destroyer", "faction": "Angel Cartel", "role": "Pirate Destroyer / Frigate Hunter", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Extreme (3.8-4.5 km/s)", "optimal_range": "8-20 km (Autocannons)", "tactics": "High-speed destroyer with extreme projectile alpha. Shreds frigates and light tackle before they close range."},
    "Cynabal": {"class": "Cruiser", "faction": "Angel Cartel", "role": "Nano Skirmisher / Fleet Cruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme (2.2-3.0 km/s MWD)", "optimal_range": "15-28 km (425mm Autocannons / Barrage)", "tactics": "Premier nano kiter. Fast align and warp acceleration. Keep range 20-25 km, kite away from scrams/webs, apply tracking-disruptive transversal against heavy turrets."},
    "Khizriel": {"class": "Battlecruiser", "faction": "Angel Cartel", "role": "Heavy Skirmish Battlecruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast (1.8-2.4 km/s)", "optimal_range": "20-50 km", "tactics": "Heavy projectile alpha with high mobility. Fast align and warp speed allow repositioning across grid effortlessly."},
    "Machariel": {"class": "Battleship", "faction": "Angel Cartel", "role": "Fast Battleship / Fleet Anchor", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Armor", "speed": "Very Fast (1.5-2.0 km/s MWD)", "optimal_range": "15-40 km (800mm AC) or 70-130 km (1400mm Artillery)", "tactics": "Cruiser-like sub-warp agility. Immense alpha with Artillery or heavy mobile DPS with Autocannons. Retain transversal against dreads."},
    "Azariel": {"class": "Titan", "faction": "Angel Cartel", "role": "Pirate Supercapital Titan", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Fast for Titan", "optimal_range": "Omni Capital Range", "tactics": "Angel Cartel supercapital with devastating projectile alpha strike and Titan doomsday weapon."},

    # --- Guristas ---
    "Worm": {"class": "Frigate", "faction": "Guristas", "role": "Heavy Drone / Missile Frigate", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Passive (300% Drone Bonus)", "speed": "Moderate", "optimal_range": "0-40 km", "tactics": "Extreme drone HP and damage (1 drone deals damage of 4). Kill drones or kite outside lock range."},
    "Mamba": {"class": "Destroyer", "faction": "Guristas", "role": "Pirate Missile Destroyer", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "20-45 km", "tactics": "Fast missile and light drone destroyer with strong shield tank."},
    "Gila": {"class": "Cruiser", "faction": "Guristas", "role": "Drone / Missile Combat Cruiser", "threat": THREAT_PIRATE, "tank": "Passive / Active Shield (500% Drone Bonus)", "speed": "Moderate (1.6-2.0 km/s)", "optimal_range": "0-60 km", "tactics": "Abyssal king. 2 Medium drones deliver damage and HP of 10. Heavy shield buffer. Counter by destroying drones or heavy cap neuts."},
    "Alligator": {"class": "Battlecruiser", "faction": "Guristas", "role": "Heavy Drone / Missile Battlecruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "30-70 km", "tactics": "Heavy drone and heavy assault missile platform with massive shield reserves."},
    "Rattlesnake": {"class": "Battleship", "faction": "Guristas", "role": "Heavy Drone / Cruise Battleship", "threat": THREAT_PIRATE, "tank": "Passive / Active Shield", "speed": "Slow", "optimal_range": "20-80 km", "tactics": "Massive passive shield recharge and heavy drone DPS. Cap neuts have low impact on passive shield regen."},
    "Loggerhead": {"class": "Force Auxiliary", "faction": "Guristas", "role": "Pirate Shield FAX", "threat": THREAT_CAPITAL, "tank": "Shield Active", "speed": "Capital", "optimal_range": "Fleet Remote Shield", "tactics": "Guristas pirate capital shield logistics ship."},
    "Caiman": {"class": "Dreadnought", "faction": "Guristas", "role": "Pirate Missile / Drone Dread", "threat": THREAT_CAPITAL, "tank": "Shield Active", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Guristas pirate dreadnought with capital kinetic/thermal missile launchers."},
    "Komodo": {"class": "Titan", "faction": "Guristas", "role": "Guristas Supercapital Titan", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Guristas pirate supercapital Titan with extreme missile burst and supercapital drones."},

    # --- Blood Raiders ---
    "Cruor": {"class": "Frigate", "faction": "Blood Raiders", "role": "Web / NOS Frigate", "threat": THREAT_ECM, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Heavy webs and NOS that drains cap even when ship cap is full. Keep distance outside 15 km."},
    "Ashimmu": {"class": "Cruiser", "faction": "Blood Raiders", "role": "Heavy Web / NOS Cruiser", "threat": THREAT_ECM, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-25 km", "tactics": "90% webs and severe energy neut drain. Eliminates enemy capacitor in seconds."},
    "Bhaalgorn": {"class": "Battleship", "faction": "Blood Raiders", "role": "Fleet Cap Drain / Heavy Web", "threat": THREAT_ECM, "tank": "Armor", "speed": "Slow", "optimal_range": "0-40 km", "tactics": "Fleet flagship neut. Heavy energy neutralizers drain 3000+ GJ per cycle at up to 40 km."},
    "Dagon": {"class": "Force Auxiliary", "faction": "Blood Raiders", "role": "Pirate Armor FAX", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "Fleet Remote Armor", "tactics": "Blood Raider capital armor remote repair ship."},
    "Chemosh": {"class": "Dreadnought", "faction": "Blood Raiders", "role": "Pirate Cap Drain Dread", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Blood Raider pirate dreadnought with capital energy neutralizers."},
    "Molok": {"class": "Titan", "faction": "Blood Raiders", "role": "Blood Raider Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Blood Raider pirate supercapital Titan with massive neut drain."},

    # --- Serpentis ---
    "Daredevil": {"class": "Frigate", "faction": "Serpentis", "role": "90% Web Blaster Frigate", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "0-8 km", "tactics": "90% stasis web stops targets dead. Massive close-range blaster DPS. Do not let it close inside 10km."},
    "Vigilant": {"class": "Cruiser", "faction": "Serpentis", "role": "90% Web Blaster Cruiser", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "90% webifier with 1000+ DPS medium blasters. Overheat propulsion and stay outside 18 km."},
    "Vindicator": {"class": "Battleship", "faction": "Serpentis", "role": "90% Web Blaster Battleship", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-20 km", "tactics": "2000+ DPS close range. Webifier locks targets down for massive neutron blaster application."},
    "Vehement": {"class": "Dreadnought", "faction": "Serpentis", "role": "Pirate Blaster / Web Dread", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "0-30 km", "tactics": "Serpentis pirate dreadnought with capital blasters and 90% webifiers."},
    "Vanquisher": {"class": "Titan", "faction": "Serpentis", "role": "Serpentis Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Serpentis pirate supercapital Titan with 90% web and blaster power."},

    # --- Sansha's Nation ---
    "Succubus": {"class": "Frigate", "faction": "Sansha's Nation", "role": "AB Speed Laser Frigate", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme AB (2.5+ km/s)", "optimal_range": "0-15 km", "tactics": "Huge Afterburner speed bonus (immune to warp scrambler MWD shutoff). High transversal pulse lasers."},
    "Phantasm": {"class": "Cruiser", "faction": "Sansha's Nation", "role": "100MN AB Laser Cruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme AB (2.0+ km/s)", "optimal_range": "15-35 km", "tactics": "Runs 100MN Afterburner with cruiser-grade agility. Unscrammable speed tank. Hit with tracking disruptors or heavy webs."},
    "Nightmare": {"class": "Battleship", "faction": "Sansha's Nation", "role": "Fast Laser Battleship", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast AB (1.5+ km/s)", "optimal_range": "30-80 km", "tactics": "High-mobility beam/pulse laser battleship. Applies instant EM/Thermal damage with large energy turrets."},
    "Revenant": {"class": "Supercarrier", "faction": "Sansha's Nation", "role": "Pirate Supercarrier", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Sansha pirate supercarrier with immense fighter strike damage."},

    # --- Sisters of EVE ---
    "Astero": {"class": "Frigate", "faction": "Sisters of EVE", "role": "Covert Ops / Drone Scout", "threat": THREAT_PIRATE, "tank": "Armor Buffer / Dual Rep", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Covert cloaking exploration frigate with vicious light drone combat capability. Often dual-repaired."},
    "Stratios": {"class": "Cruiser", "faction": "Sisters of EVE", "role": "Covert Ops / Drone Brawler", "threat": THREAT_PIRATE, "tank": "Armor Buffer / Dual Rep", "speed": "Moderate", "optimal_range": "0-30 km", "tactics": "Covert cloaking cruiser. Can fit covert cyno, heavy neuts, and full flight of heavy/sentry drones."},
    "Nestor": {"class": "Battleship", "faction": "Sisters of EVE", "role": "Remote Rep / Wormhole Core", "threat": THREAT_PIRATE, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-20 km", "tactics": "Sub-capital remote armor repair flagship. Very low mass allows mass-efficient wormhole transit."},

    # --- Mordu's Legion ---
    "Garmur": {"class": "Frigate", "faction": "Mordu's Legion", "role": "Long-Range Point Kiter", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme (5.0+ km/s)", "optimal_range": "30-40 km", "tactics": "Projects 35+ km warp disruptor point at extreme speed. Counter with sensor dampeners, rapid light missiles, or light combat drones."},
    "Orthrus": {"class": "Cruiser", "faction": "Mordu's Legion", "role": "Long-Range Point & Web Kiter", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme (3.0+ km/s)", "optimal_range": "35-50 km", "tactics": "45+ km point and 25 km web range with rapid light missiles. Counter with heavy projection snipers or long-range dampeners."},
    "Barghest": {"class": "Battleship", "faction": "Mordu's Legion", "role": "Heavy Point / Cruise Battleship", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Fast", "optimal_range": "50-100 km", "tactics": "Extreme missile velocity and 60+ km point range. High alpha cruise missiles."},

    # --- Triglavian Collective ---
    "Damavik": {"class": "Frigate", "faction": "Triglavian", "role": "Spooling Disintegrator Frigate", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "5-18 km", "tactics": "Entropic disintegrator damage ramps up continuously over time. Break lock or kill quickly before spool reaches maximum."},
    "Kikimora": {"class": "Destroyer", "faction": "Triglavian", "role": "Long-Range Disintegrator Destroyer", "threat": THREAT_PIRATE, "tank": "Armor / Shield", "speed": "Extreme (3.5+ km/s)", "optimal_range": "15-40 km", "tactics": "Extreme sub-warp speed with spooling light disintegrator. Strikes from 35km with heavy tracking."},
    "Vedmak": {"class": "Cruiser", "faction": "Triglavian", "role": "Spooling Disintegrator Cruiser", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast (2.2-2.8 km/s)", "optimal_range": "10-35 km", "tactics": "High sub-warp speed with continuous spooling thermal/explosive damage. Disengage if fight extends past 60 seconds."},
    "Rodiva": {"class": "Cruiser", "faction": "Triglavian", "role": "Spooling Remote Armor Rep", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Fast", "optimal_range": "Remote Rep Range", "tactics": "Triglavian logistics cruiser with spooling remote armor repairers."},
    "Drekavac": {"class": "Battlecruiser", "faction": "Triglavian", "role": "Heavy Disintegrator / Armor Links", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "15-45 km", "tactics": "Heavy armor tank and massive max-spool disintegrator DPS."},
    "Leshak": {"class": "Battleship", "faction": "Triglavian", "role": "Capital / Structure Buster", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Spools to over 3500 DPS. Lethal to capitals, POS structures, and stationary targets."},
    "Ikitursa": {"class": "Heavy Assault Cruiser", "faction": "Triglavian", "role": "HAC Disintegrator Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor", "speed": "Fast", "optimal_range": "10-35 km", "tactics": "T2 assault damage controls and huge spooling DPS make it formidable in small gang engagements."},
    "Zarmazd": {"class": "Logistics Cruiser", "faction": "Triglavian", "role": "T2 Spooling Remote Armor", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Fast", "optimal_range": "Remote Rep Range", "tactics": "T2 Triglavian logistics cruiser with extreme ramping armor repairs."},
    "Zirnitra": {"class": "Dreadnought", "faction": "Triglavian", "role": "Capital Disintegrator Siege", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Triglavian dreadnought with capital spooling disintegrator."},

    # --- EDENCOM ---
    "Skybreaker": {"class": "Frigate", "faction": "EDENCOM", "role": "Vortron Arcing Frigate", "threat": THREAT_COMBATANT, "tank": "Shield", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Vorton projector arcs lightning damage to up to 5 nearby hostile targets."},
    "Stormbringer": {"class": "Cruiser", "faction": "EDENCOM", "role": "Vortron Arcing Cruiser", "threat": THREAT_COMBATANT, "tank": "Shield", "speed": "Moderate", "optimal_range": "15-35 km", "tactics": "Medium vorton projector arcs heavy EM/Kinetic damage across fleet clusters."},
    "Thunderchild": {"class": "Battleship", "faction": "EDENCOM", "role": "Heavy Vortron Battleship", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "30-70 km", "tactics": "Large vorton projector chains massive damage across 10 linked enemy ships."},

    # =========================================================================
    # 2. CALDARI STATE VESSELS
    # =========================================================================
    # --- Caldari Frigates & T2 ---
    "Condor": {"class": "Frigate", "faction": "Caldari", "role": "Missile Kiter / Light Tackle", "threat": THREAT_COMBATANT, "tank": "Shield", "speed": "Fast", "optimal_range": "20-35 km", "tactics": "Light missile kiter with kinetic missile bonus."},
    "Kestrel": {"class": "Frigate", "faction": "Caldari", "role": "Missile / Rocket Brawler", "threat": THREAT_COMBATANT, "tank": "Shield Buffer / Active", "speed": "Moderate", "optimal_range": "0-25 km", "tactics": "4 missile launchers with all 4 damage types."},
    "Merlin": {"class": "Frigate", "faction": "Caldari", "role": "Blaster / Rail Brawler", "threat": THREAT_COMBATANT, "tank": "Shield Buffer / Dual MASB", "speed": "Moderate", "optimal_range": "0-10 km", "tactics": "Strong shield resistance bonus; high blaster DPS."},
    "Bantam": {"class": "Frigate", "faction": "Caldari", "role": "Shield Logistics Frigate", "threat": THREAT_LOGI, "tank": "Shield", "speed": "Moderate", "optimal_range": "Remote Shield", "tactics": "T1 frigate shield logistics."},
    "Heron": {"class": "Frigate", "faction": "Caldari", "role": "Exploration / Bait Frigate", "threat": "EXPLORATION", "tank": "Dual MASB (Bait) / None", "speed": "Slow", "optimal_range": "0-10 km", "tactics": "Exploration frigate often fitted with dual ancillary shield boosters for combat baiting."},
    "Caldari Navy Hookbill": {"class": "Faction Frigate", "faction": "Caldari (Navy)", "role": "Multi-Range Rocket/Missile Kiter", "threat": THREAT_COMBATANT, "tank": "Shield Dual MASB", "speed": "Fast", "optimal_range": "0-30 km", "tactics": "5 mid slots allow dual webs, scram, and dual shield boosters."},
    "Hawk": {"class": "Assault Frigate", "faction": "Caldari", "role": "Shield Assault Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual MASB + ADC)", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Assault Damage Control and massive active shield boost bonus."},
    "Harpy": {"class": "Assault Frigate", "faction": "Caldari", "role": "Railgun Assault Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer + ADC", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Heavy railgun optimal and damage with ADC."},
    "Crow": {"class": "Interceptor", "faction": "Caldari", "role": "Fleet Interceptor / Fast Point", "threat": "FAST TACKLE", "tank": "Shield", "speed": "Extreme (4.5+ km/s)", "optimal_range": "25-35 km point", "tactics": "Bubble immune fleet interceptor with long point."},
    "Raptor": {"class": "Interceptor", "faction": "Caldari", "role": "Combat Interceptor / Scrambler", "threat": "FAST TACKLE", "tank": "Shield", "speed": "Extreme", "optimal_range": "0-12 km", "tactics": "Combat interceptor with high hybrid damage and tackle."},
    "Buzzard": {"class": "Covert Ops", "faction": "Caldari", "role": "Covert Scout / Cyno", "threat": THREAT_CYNO, "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "Cloak", "tactics": "Covert ops cloaking and covert cynos."},
    "Kitsune": {"class": "Electronic Attack Ship", "faction": "Caldari", "role": "Long-Range ECM Jammer", "threat": THREAT_ECM, "tank": "Paper Thin", "speed": "Moderate", "optimal_range": "50-90 km Jam", "tactics": "Frigate ECM jammer. Jams enemy targets from 80km out."},
    "Manticore": {"class": "Stealth Bomber", "faction": "Caldari", "role": "Covert Torpedo / Bomb Bomber", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Kinetic bombs and torpedoes from cloak."},
    "Kirin": {"class": "Logistics Frigate", "faction": "Caldari", "role": "T2 Shield Logistics Frigate", "threat": THREAT_LOGI, "tank": "Shield", "speed": "Fast", "optimal_range": "Remote Shield", "tactics": "T2 frigate remote shield transfer."},

    # --- Caldari Destroyers & T3D ---
    "Cormorant": {"class": "Destroyer", "faction": "Caldari", "role": "Railgun Fleet Sniper", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "30-80 km (125mm/150mm Rails)", "tactics": "Extreme range railguns with high tracking. Popular low-cost fleet doctrine."},
    "Corax": {"class": "Destroyer", "faction": "Caldari", "role": "Rocket / Light Missile Destroyer", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "20-45 km", "tactics": "7 missile launchers with kinetic missile bonuses."},
    "Cormorant Navy Issue": {"class": "Faction Destroyer", "faction": "Caldari (Navy)", "role": "Navy Hybrid Destroyer", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "20-70 km", "tactics": "Enhanced hybrid tracking and shield hitpoints."},
    "Flycatcher": {"class": "Interdictor", "faction": "Caldari", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Launches 20km warp disruption bubbles with rocket/missile DPS."},
    "Stork": {"class": "Command Destroyer", "faction": "Caldari", "role": "Micro Jump Field Generator / Shield Boosts", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Micro Jump Field jumps all ships within 6km 100km away."},
    "Jackdaw": {"class": "Tactical Destroyer", "faction": "Caldari", "role": "Mode Switching Missile Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Active / Buffer", "speed": "Fast", "optimal_range": "30-70 km", "tactics": "Switches between Propulsion (speed), Defense (resists), and Sharpshooter (range/tracking) modes."},

    # --- Caldari Cruisers & T2 / T3C ---
    "Caracal": {"class": "Cruiser", "faction": "Caldari", "role": "Rapid Light / Heavy Missile Cruiser", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate (1.8 km/s)", "optimal_range": "30-70 km (Rapid Light / Heavy Missiles)", "tactics": "Rapid light missile anti-frigate platform or heavy missile fleet cruiser."},
    "Moa": {"class": "Cruiser", "faction": "Caldari", "role": "Railgun / Blaster Cruiser", "threat": THREAT_COMBATANT, "tank": "Shield Buffer (Resist Bonus)", "speed": "Slow", "optimal_range": "0-15 km Blaster / 40-70 km Rail", "tactics": "Exceptional shield resistance bonus; heavy fleet line brawler."},
    "Osprey": {"class": "Cruiser", "faction": "Caldari", "role": "Shield Logistics Cruiser", "threat": THREAT_LOGI, "tank": "Shield Buffer (Cap Chain)", "speed": "Moderate", "optimal_range": "Remote Shield (40-60 km)", "tactics": "Capacitor-chaining shield logistics cruiser."},
    "Blackbird": {"class": "Cruiser", "faction": "Caldari", "role": "Fleet ECM Jammer Cruiser", "threat": THREAT_ECM, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "60-100 km Jam", "tactics": "Cruiser-grade ECM jammer. Breaks enemy locks across entire grid."},
    "Caracal Navy Issue": {"class": "Faction Cruiser", "faction": "Caldari (Navy)", "role": "Heavy Assault Missile Brawler", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "20-50 km", "tactics": "Heavy missile and heavy assault missile platform with strong shield buffer."},
    "Osprey Navy Issue": {"class": "Faction Cruiser", "faction": "Caldari (Navy)", "role": "High-Speed Missile Kiter", "threat": THREAT_COMBATANT, "tank": "Shield Buffer / Active", "speed": "Fast (2.2+ km/s)", "optimal_range": "30-70 km", "tactics": "Fast missile skirmisher with kinetic missile velocity bonus."},
    "Cerberus": {"class": "Heavy Assault Cruiser", "faction": "Caldari", "role": "Missile Fleet Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer + ADC", "speed": "Fast (2.0 km/s)", "optimal_range": "60-110 km", "tactics": "Heavy assault missile or heavy missile fleet platform with ADC. Counter with close brawling inside minimum range."},
    "Eagle": {"class": "Heavy Assault Cruiser", "faction": "Caldari", "role": "Railgun Fleet Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer + ADC", "speed": "Moderate", "optimal_range": "50-120 km", "tactics": "Extreme railgun range and optimal bonuses. Shield buffer and ADC. Vulnerable to fast high-transversal tackle."},
    "Onyx": {"class": "Heavy Interdiction Cruiser", "faction": "Caldari", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "WDFG projects infinite focused point on capitals or 20km sphere bubble."},
    "Basilisk": {"class": "Logistics Cruiser", "faction": "Caldari", "role": "T2 Shield Logistics (Cap Chain)", "threat": THREAT_LOGI, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "Remote Shield 50-70 km", "tactics": "T2 fleet shield repairer requiring cap transfer chain with partner logi."},
    "Falcon": {"class": "Force Recon", "faction": "Caldari", "role": "Covert Cyno / Jammer", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Moderate", "optimal_range": "50-80 km ECM", "tactics": "Cloaked ECM jammer. Breaks target locks completely. Primary EWAR threat; lock and destroy or neut out."},
    "Rook": {"class": "Combat Recon", "faction": "Caldari", "role": "ECM Jammer / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield", "speed": "Moderate", "optimal_range": "50-80 km Jam", "tactics": "IMMUNE TO D-SCAN. Heavy missile and ECM jammer."},
    "Tengu": {"class": "Strategic Cruiser", "faction": "Caldari", "role": "Missile Sniper / ECM / Nullified", "threat": THREAT_CYNO, "tank": "Shield Buffer / Active", "speed": "Fast", "optimal_range": "40-90 km", "tactics": "Modular T3C. Configurable for covert nullified travel, heavy missile sniping, or ECM jamming."},

    # --- Caldari Battlecruisers & Command Ships ---
    "Drake": {"class": "Battlecruiser", "faction": "Caldari", "role": "Heavy Missile Buffer", "threat": THREAT_COMBATANT, "tank": "Passive / Buffer Shield", "speed": "Slow", "optimal_range": "40-80 km", "tactics": "Iconic shield brick battlecruiser with kinetic heavy missile bonuses."},
    "Ferox": {"class": "Battlecruiser", "faction": "Caldari", "role": "Railgun Line Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "40-90 km", "tactics": "Heavy railgun fleet line platform with shield buffer."},
    "Naga": {"class": "Attack Battlecruiser", "faction": "Caldari", "role": "Battleship-Gun Rail Sniper", "threat": THREAT_COMBATANT, "tank": "Paper Thin Shield", "speed": "Moderate", "optimal_range": "80-150 km", "tactics": "Fits Large Battleship Railguns on a Battlecruiser hull. Massive alpha at extreme range; paper tank."},
    "Drake Navy Issue": {"class": "Faction Battlecruiser", "faction": "Caldari (Navy)", "role": "Heavy Missile Navy BC", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "30-70 km", "tactics": "Enhanced missile application and shield buffer."},
    "Ferox Navy Issue": {"class": "Faction Battlecruiser", "faction": "Caldari (Navy)", "role": "Hybrid Navy Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "30-80 km", "tactics": "Enhanced hybrid blaster/railgun firepower."},
    "Nighthawk": {"class": "Command Ship", "faction": "Caldari", "role": "Shield Command / Heavy Missile DPS", "threat": THREAT_T2_COMBAT, "tank": "Shield Active / Buffer", "speed": "Slow", "optimal_range": "40-80 km", "tactics": "Heavy missile command ship providing fleet shield warfare links."},
    "Vulture": {"class": "Command Ship", "faction": "Caldari", "role": "Shield Command / Railgun Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "60-120 km", "tactics": "Fleet command ship providing massive shield resist links and railgun projection."},

    # --- Caldari Battleships & T2 ---
    "Raven": {"class": "Battleship", "faction": "Caldari", "role": "Cruise / Torpedo Battleship", "threat": THREAT_COMBATANT, "tank": "Shield Buffer / Active", "speed": "Slow", "optimal_range": "40-120 km", "tactics": "Long-range cruise missile or torpedo battleship."},
    "Rokh": {"class": "Battleship", "faction": "Caldari", "role": "Railgun Fleet Sniper", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Very Slow", "optimal_range": "80-180 km", "tactics": "Massive railgun optimal range and shield resistances."},
    "Scorpion": {"class": "Battleship", "faction": "Caldari", "role": "Fleet ECM Battleship", "threat": THREAT_ECM, "tank": "Shield Buffer", "speed": "Very Slow", "optimal_range": "70-130 km Jam", "tactics": "Dedicated fleet ECM jammer battleship. 8 mid slots dedicated to full-grid jamming."},
    "Raven Navy Issue": {"class": "Faction Battleship", "faction": "Caldari (Navy)", "role": "Heavy Missile / Cruise Battleship", "threat": THREAT_COMBATANT, "tank": "Shield Buffer (Large Shield Extenders) / Active Shield", "speed": "Slow (MWD/MJD)", "optimal_range": "40-150 km (Cruise Missiles) or 0-35 km (Torpedoes)", "tactics": "8 missile launchers with application and velocity bonuses. For Skirmish/Kiting: fit Large Micro Jump Drive (MJD) for 100km range resets and Cruise Missiles/RHML with Target Painter / Missile Guidance (no 3000 m/s nano speed on BS). For Brawling: fit Torpedoes, Heavy Cap Booster, Warp Scrambler, and Stasis Grappler."},
    "Scorpion Navy Issue": {"class": "Faction Battleship", "faction": "Caldari (Navy)", "role": "Cruise / Torpedo Shield Brick", "threat": THREAT_COMBATANT, "tank": "Shield Massive Buffer", "speed": "Slow", "optimal_range": "30-100 km", "tactics": "Massive shield buffer hitpoints and missile DPS."},
    "Widow": {"class": "Black Ops", "faction": "Caldari", "role": "Covert Bridge / ECM Jammer", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Jump Drive", "optimal_range": "40-80 km", "tactics": "Long-range ECM jammer and rapid missile battleship."},
    "Golem": {"class": "Marauder", "faction": "Caldari", "role": "Bastion Torpedo/Cruise DPS", "threat": THREAT_MARAUDER, "tank": "Active Shield (2000+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "30-120 km", "tactics": "Target painter bonus applies massive torpedo damage. Fast small-sig ships mitigate missile damage. Bastion grants 100% rep bonus and EWAR immunity."},

    # --- Caldari Capitals & Freighters ---
    "Phoenix": {"class": "Dreadnought", "faction": "Caldari", "role": "Capital Missile Siege", "threat": THREAT_CAPITAL, "tank": "Shield Active / Buffer", "speed": "Capital", "optimal_range": "50-150 km", "tactics": "Capital torpedo/cruise missile dreadnought."},
    "Phoenix Navy Issue": {"class": "Faction Dreadnought", "faction": "Caldari (Navy)", "role": "Navy Missile Dreadnought", "threat": THREAT_CAPITAL, "tank": "Shield Active", "speed": "Capital", "optimal_range": "50-150 km", "tactics": "Enhanced missile application and shield boost capacity."},
    "Karura": {"class": "Lancer Dreadnought", "faction": "Caldari", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Shield", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Caldari disruptive capital lance weapon."},
    "Chimera": {"class": "Carrier", "faction": "Caldari", "role": "Capital Fighter Platform", "threat": THREAT_CAPITAL, "tank": "Shield Buffer", "speed": "Capital", "optimal_range": "Fighter Operations", "tactics": "Caldari fleet carrier deploying light and support fighters."},
    "Minokawa": {"class": "Force Auxiliary", "faction": "Caldari", "role": "Capital Shield Logistics", "threat": THREAT_CAPITAL, "tank": "Shield Active (Triage)", "speed": "Capital", "optimal_range": "Fleet Remote Shield", "tactics": "Capital shield repairer. In Triage mode reps massive EHP per second to fleet."},
    "Wyvern": {"class": "Supercarrier", "faction": "Caldari", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Caldari supercarrier deploying heavy fighter wings and burst projectors."},
    "Leviathan": {"class": "Titan", "faction": "Caldari", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Caldari supercapital Titan with Oblivion Doomsday device."},
    "Badger": {"class": "Industrial", "faction": "Caldari", "role": "T1 Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Slow", "optimal_range": "Hauler", "tactics": "Caldari entry level cargo hauler."},
    "Tayra": {"class": "Industrial", "faction": "Caldari", "role": "High Capacity Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Slow", "optimal_range": "Hauler", "tactics": "High-capacity T1 industrial transport."},
    "Crane": {"class": "Blockade Runner", "faction": "Caldari", "role": "Covert Cloak Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Fast Align / Cloaked", "optimal_range": "Covert Cloak", "tactics": "Covert cloaking blockade runner; immune to cargo scanners."},
    "Bustard": {"class": "Deep Space Transport", "faction": "Caldari", "role": "Heavy Buffer Transport", "threat": THREAT_HAULER, "tank": "Massive Shield Buffer (+2 Warp Core)", "speed": "Slow (MWD-Cloak)", "optimal_range": "Hauler", "tactics": "Fleet hangar transport with +2 passive warp core strength and massive tank."},
    "Charon": {"class": "Freighter", "faction": "Caldari", "role": "Sub-Capital Bulk Freighter", "threat": THREAT_HAULER, "tank": "Shield Buffer", "speed": "Very Slow", "optimal_range": "Freighter", "tactics": "Massive cargo capacity freighter (nearly 1M m3)."},
    "Rhea": {"class": "Jump Freighter", "faction": "Caldari", "role": "Jump Drive Bulk Transport", "threat": THREAT_HAULER, "tank": "Shield Buffer", "speed": "Jump Drive", "optimal_range": "Cyno Jump", "tactics": "Jump drive freighter for logistics across cyno beacons."},

    # =========================================================================
    # 3. AMARR EMPIRE VESSELS
    # =========================================================================
    # --- Amarr Frigates & T2 ---
    "Executioner": {"class": "Frigate", "faction": "Amarr", "role": "Fast Laser Tackler", "threat": THREAT_COMBATANT, "tank": "Armor", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Fast laser tackle frigate."},
    "Tormentor": {"class": "Frigate", "faction": "Amarr", "role": "Laser / Drone Brawler", "threat": THREAT_COMBATANT, "tank": "Armor Buffer / Active", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Heavy pulse laser firepower and light drone bay."},
    "Punisher": {"class": "Frigate", "faction": "Amarr", "role": "Heavy Armor Brick Frigate", "threat": THREAT_COMBATANT, "tank": "Armor Heavy Buffer (400mm Plate)", "speed": "Slow", "optimal_range": "0-15 km", "tactics": "Cruiser-like armor hitpoint buffer; very tanky bait frigate."},
    "Crucifier": {"class": "Frigate", "faction": "Amarr", "role": "Tracking Disruptor Frigate", "threat": THREAT_ECM, "tank": "Armor", "speed": "Fast", "optimal_range": "30-60 km EWAR", "tactics": "Tracking disruption makes hostile turrets and missiles fail to hit."},
    "Inquisitor": {"class": "Frigate", "faction": "Amarr", "role": "Armor Logistics Frigate", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Moderate", "optimal_range": "Remote Armor", "tactics": "T1 frigate remote armor repair."},
    "Magnate": {"class": "Frigate", "faction": "Amarr", "role": "Exploration / Scanner", "threat": "EXPLORATION", "tank": "None", "speed": "Moderate", "optimal_range": "Scanning", "tactics": "Exploration scanning frigate."},
    "Imperial Navy Slicer": {"class": "Faction Frigate", "faction": "Amarr (Navy)", "role": "Beam / Pulse Laser Kiter", "threat": THREAT_COMBATANT, "tank": "Armor Nano", "speed": "Extreme (4.0+ km/s)", "optimal_range": "15-35 km (Beam / Scorch)", "tactics": "Premier T1 kiter. High speed and projection with Scorch / Beam lasers. Keep high transversal outside 20km."},
    "Crucifier Navy Issue": {"class": "Faction Frigate", "faction": "Amarr (Navy)", "role": "Guidance / Tracking Disruptor Brawler", "threat": THREAT_ECM, "tank": "Armor", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "High-damage laser combatant with weapon disruption bonuses."},
    "Retribution": {"class": "Assault Frigate", "faction": "Amarr", "role": "Beam / Pulse Assault Kiter/Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer + ADC", "speed": "Fast", "optimal_range": "10-35 km", "tactics": "Assault Damage Control and heavy beam/pulse laser damage."},
    "Vengeance": {"class": "Assault Frigate", "faction": "Amarr", "role": "Rocket / Cap Neutralizer Assault", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer + ADC", "speed": "Moderate", "optimal_range": "0-12 km", "tactics": "Rocket assault frigate with heavy armor resists and cap drain."},
    "Crusader": {"class": "Interceptor", "faction": "Amarr", "role": "Combat Interceptor / Laser DPS", "threat": "FAST TACKLE", "tank": "Armor", "speed": "Extreme", "optimal_range": "0-10 km", "tactics": "Fast laser combat interceptor."},
    "Malediction": {"class": "Interceptor", "faction": "Amarr", "role": "Fleet Interceptor / Long Point", "threat": "FAST TACKLE", "tank": "Armor", "speed": "Extreme (4.5+ km/s)", "optimal_range": "25-35 km point", "tactics": "Bubble immune fleet interceptor with fast align."},
    "Anathema": {"class": "Covert Ops", "faction": "Amarr", "role": "Covert Scout / Cyno", "threat": THREAT_CYNO, "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "Cloak", "tactics": "Covert ops cloaking and covert cynos."},
    "Sentinel": {"class": "Electronic Attack Ship", "faction": "Amarr", "role": "Cap Drain & Tracking Disruptor", "threat": THREAT_ECM, "tank": "Armor", "speed": "Moderate", "optimal_range": "30-50 km Neut", "tactics": "Extreme range energy neutralizers (35km+) drain enemy capacitors in seconds."},
    "Purifier": {"class": "Stealth Bomber", "faction": "Amarr", "role": "Covert Torpedo / Bomb Bomber", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "EM bombs and torpedoes from cloak."},
    "Deacon": {"class": "Logistics Frigate", "faction": "Amarr", "role": "T2 Armor Logistics Frigate", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Fast", "optimal_range": "Remote Armor", "tactics": "T2 frigate remote armor repair."},

    # --- Amarr Destroyers & T3D ---
    "Coercer": {"class": "Destroyer", "faction": "Amarr", "role": "Pulse / Beam Laser Destroyer", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "10-30 km (Scorch)", "tactics": "8 laser turrets deliver massive instant EM/Thermal damage."},
    "Dragoon": {"class": "Destroyer", "faction": "Amarr", "role": "Drone / Cap Neut Destroyer", "threat": THREAT_ECM, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-20 km Neut", "tactics": "Heavy energy neutralizers and light drones. Shreds frigate tackle capacitors."},
    "Coercer Navy Issue": {"class": "Faction Destroyer", "faction": "Amarr (Navy)", "role": "Navy Laser Destroyer", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "10-35 km", "tactics": "Enhanced laser tracking and armor resistances."},
    "Heretic": {"class": "Interdictor", "faction": "Amarr", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Armor-buffered interdictor with rocket/missile DPS and bubble probes."},
    "Pontifex": {"class": "Command Destroyer", "faction": "Amarr", "role": "Micro Jump Field / Armor Boosts", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Micro Jump Field jumps ships 100km; provides armor warfare links."},
    "Confessor": {"class": "Tactical Destroyer", "faction": "Amarr", "role": "Mode Switching Laser Sniper", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer", "speed": "Fast", "optimal_range": "15-45 km", "tactics": "Switches between Propulsion, Defense, and Sharpshooter modes."},

    # --- Amarr Cruisers & T2 / T3C ---
    "Omen": {"class": "Cruiser", "faction": "Amarr", "role": "Laser Skirmish Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Nano", "speed": "Fast (2.0 km/s)", "optimal_range": "20-40 km (Heavy Pulse / Scorch)", "tactics": "Fast laser kiter with heavy pulse laser firepower."},
    "Maller": {"class": "Cruiser", "faction": "Amarr", "role": "Heavy Armor Brick Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Heavy Buffer (Resist Bonus)", "speed": "Slow", "optimal_range": "0-25 km", "tactics": "Immense armor resistance bonus; standard bait/line cruiser."},
    "Augoror": {"class": "Cruiser", "faction": "Amarr", "role": "Armor Logistics Cruiser", "threat": THREAT_LOGI, "tank": "Armor Buffer (Cap Chain)", "speed": "Slow", "optimal_range": "Remote Armor (40-60 km)", "tactics": "Capacitor-chaining armor logistics cruiser."},
    "Arbitrator": {"class": "Cruiser", "faction": "Amarr", "role": "Drone / Tracking Disruptor / Neut", "threat": THREAT_ECM, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-40 km", "tactics": "Heavy tracking disruption, energy neutralizers, and medium drones."},
    "Omen Navy Issue": {"class": "Faction Cruiser", "faction": "Amarr (Navy)", "role": "Nano Laser Kiter Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Nano Buffer", "speed": "Fast (2.4+ km/s)", "optimal_range": "20-45 km", "tactics": "Premier nano cruiser. High speed and heavy pulse laser Scorch projection."},
    "Augoror Navy Issue": {"class": "Faction Cruiser", "faction": "Amarr (Navy)", "role": "Heavy Armor Brawler Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Brick Buffer", "speed": "Slow", "optimal_range": "0-30 km", "tactics": "Massive armor hitpoints and heavy laser damage."},
    "Zealot": {"class": "Heavy Assault Cruiser", "faction": "Amarr", "role": "Beam / Pulse Laser Sniper", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer + ADC", "speed": "Moderate", "optimal_range": "30-80 km", "tactics": "Armor fleet laser sniper with high EM/Thermal alpha and ADC."},
    "Sacrilege": {"class": "Heavy Assault Cruiser", "faction": "Amarr", "role": "Heavy Missile / Armor Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer / Active + ADC", "speed": "Moderate", "optimal_range": "15-40 km", "tactics": "Exceptional armor resistances and heavy assault missile firepower with neuts."},
    "Devoter": {"class": "Heavy Interdiction Cruiser", "faction": "Amarr", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "Heavy armor tanked HIC with infinite tackle point."},
    "Guardian": {"class": "Logistics Cruiser", "faction": "Amarr", "role": "T2 Armor Logistics (Cap Chain)", "threat": THREAT_LOGI, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "Remote Armor 50-70 km", "tactics": "T2 fleet armor repairer requiring cap transfer chain with partner logi."},
    "Pilgrim": {"class": "Force Recon", "faction": "Amarr", "role": "Covert Cyno / Neut", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-25 km Neut", "tactics": "Cloaked heavy energy neutralizer, tracking disruptor, and drone boat."},
    "Curse": {"class": "Combat Recon", "faction": "Amarr", "role": "Cap Drain / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield / Armor", "speed": "Moderate", "optimal_range": "40-60 km Neut", "tactics": "IMMUNE TO D-SCAN. Heavy energy neutralizer drains enemy capacitor at 50km+."},
    "Legion": {"class": "Strategic Cruiser", "faction": "Amarr", "role": "Neut / Laser DPS / Heavy Tank", "threat": THREAT_CYNO, "tank": "Armor Buffer / Active", "speed": "Moderate", "optimal_range": "15-50 km", "tactics": "Modular T3C. Configurable for covert travel, 600+ DPS lasers, or extreme neut pressure."},

    # --- Amarr Battlecruisers & Command Ships ---
    "Harbinger": {"class": "Battlecruiser", "faction": "Amarr", "role": "Medium Laser Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Heavy pulse/beam laser firepower with strong armor buffer."},
    "Prophecy": {"class": "Battlecruiser", "faction": "Amarr", "role": "Heavy Drone / Armor Brick BC", "threat": THREAT_COMBATANT, "tank": "Armor Heavy Buffer", "speed": "Slow", "optimal_range": "0-60 km", "tactics": "Versatile drone battlecruiser with heavy armor resistances and neuts."},
    "Oracle": {"class": "Attack Battlecruiser", "faction": "Amarr", "role": "Battleship-Gun Laser Sniper", "threat": THREAT_COMBATANT, "tank": "Paper Thin Armor", "speed": "Moderate", "optimal_range": "60-140 km", "tactics": "Large Mega Beam / Tachyon lasers on Battlecruiser hull. Extreme instant alpha."},
    "Harbinger Navy Issue": {"class": "Faction Battlecruiser", "faction": "Amarr (Navy)", "role": "Navy Laser Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "20-65 km", "tactics": "Enhanced laser tracking and capacitor capacity."},
    "Prophecy Navy Issue": {"class": "Faction Battlecruiser", "faction": "Amarr (Navy)", "role": "Heavy Missile / Drone Navy BC", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Heavy assault missile and combat drone platform."},
    "Absolution": {"class": "Command Ship", "faction": "Amarr", "role": "Armor Command / Heavy Laser DPS", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer / Active", "speed": "Slow", "optimal_range": "20-50 km", "tactics": "Heavy laser command ship providing fleet armor warfare links."},
    "Damnation": {"class": "Command Ship", "faction": "Amarr", "role": "Armor Command / Fleet Brick", "threat": THREAT_T2_COMBAT, "tank": "Massive Armor Buffer (500k+ EHP)", "speed": "Very Slow", "optimal_range": "Fleet Command", "tactics": "Fleet command flagship. Immense armor buffer and fleet armor boost links."},

    # --- Amarr Battleships & T2 ---
    "Apocalypse": {"class": "Battleship", "faction": "Amarr", "role": "Laser Sniper Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "60-140 km", "tactics": "Optimal range bonus allows beam lasers to strike beyond 100km effortlessly."},
    "Abaddon": {"class": "Battleship", "faction": "Amarr", "role": "Heavy Laser Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Brick Buffer", "speed": "Slow", "optimal_range": "30-90 km", "tactics": "Extremely heavy armor resistance bonus; cap intensive lasers."},
    "Armageddon": {"class": "Battleship", "faction": "Amarr", "role": "Heavy Drone / Cap Neut Battleship", "threat": THREAT_ECM, "tank": "Armor Buffer / Active", "speed": "Slow", "optimal_range": "0-50 km Neut", "tactics": "Heavy energy neutralizer range and drone damage bonus."},
    "Apocalypse Navy Issue": {"class": "Faction Battleship", "faction": "Amarr (Navy)", "role": "Heavy Laser Line / Combat Battleship", "threat": THREAT_COMBATANT, "tank": "Heavy Armor Buffer (1600mm Plates) / Dual Rep", "speed": "Slow (MWD/MJD)", "optimal_range": "30-100 km (Mega Pulse / Scorch)", "tactics": "Exceptional energy turret tracking speed bonus and optimal range. For Fleet Line Combat: anchor with remote armor logistics, max buffer, and long-range Scorch projection (no solo tackle). For Solo PvP Roaming: fit Heavy Cap Booster 800/3200, Warp Scrambler + Heavy Web or Warp Disruptor, and MJD."},
    "Armageddon Navy Issue": {"class": "Faction Battleship", "faction": "Amarr (Navy)", "role": "Laser / Heavy Drone Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "20-70 km", "tactics": "Heavy laser rate of fire and drone hitpoint bonus."},
    "Redeemer": {"class": "Black Ops", "faction": "Amarr", "role": "Covert Bridge / Laser DPS", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Jump Drive", "optimal_range": "20-60 km", "tactics": "Covert jump bridge conduit and heavy pulse laser DPS."},
    "Paladin": {"class": "Marauder", "faction": "Amarr", "role": "Bastion Pulse/Beam Laser DPS", "threat": THREAT_MARAUDER, "tank": "Active Armor (2500+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "30-100 km", "tactics": "Extreme laser projection. Neuts drain capacitor rapidly due to heavy laser cap use. Bastion mode grants 100% rep bonus and EWAR immunity."},

    # --- Amarr Capitals & Freighters ---
    "Revelation": {"class": "Dreadnought", "faction": "Amarr", "role": "Capital Laser Siege", "threat": THREAT_CAPITAL, "tank": "Armor Active / Buffer", "speed": "Capital", "optimal_range": "30-80 km", "tactics": "Heavy laser siege dreadnought."},
    "Revelation Navy Issue": {"class": "Faction Dreadnought", "faction": "Amarr (Navy)", "role": "Navy Laser Dreadnought", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "30-80 km", "tactics": "Enhanced laser capacitor efficiency and armor repair bonus."},
    "Bane": {"class": "Lancer Dreadnought", "faction": "Amarr", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Amarr disruptive capital lance weapon."},
    "Archon": {"class": "Carrier", "faction": "Amarr", "role": "Capital Fighter Platform", "threat": THREAT_CAPITAL, "tank": "Armor Buffer", "speed": "Capital", "optimal_range": "Fighter Operations", "tactics": "Amarr fleet carrier deploying light and support fighters."},
    "Apostle": {"class": "Force Auxiliary", "faction": "Amarr", "role": "Capital Armor Logistics", "threat": THREAT_CAPITAL, "tank": "Armor Active (Triage)", "speed": "Capital", "optimal_range": "Fleet Remote Armor", "tactics": "Capital armor repairer. In Triage mode reps massive armor EHP per second to fleet."},
    "Aeon": {"class": "Supercarrier", "faction": "Amarr", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Amarr supercarrier deploying heavy fighter wings and burst projectors."},
    "Avatar": {"class": "Titan", "faction": "Amarr", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Amarr supercapital Titan with Judgement Doomsday device."},
    "Bestower": {"class": "Industrial", "faction": "Amarr", "role": "High Capacity Hauler", "threat": THREAT_HAULER, "tank": "Armor", "speed": "Slow", "optimal_range": "Hauler", "tactics": "Amarr high capacity industrial transport."},
    "Sigil": {"class": "Industrial", "faction": "Amarr", "role": "Fast Hauler", "threat": THREAT_HAULER, "tank": "Armor", "speed": "Fast for Hauler", "optimal_range": "Hauler", "tactics": "Fast align Amarr industrial hauler."},
    "Prorator": {"class": "Blockade Runner", "faction": "Amarr", "role": "Covert Cloak Hauler", "threat": THREAT_HAULER, "tank": "Armor", "speed": "Fast Align / Cloaked", "optimal_range": "Covert Cloak", "tactics": "Covert cloaking blockade runner; immune to cargo scanners."},
    "Impel": {"class": "Deep Space Transport", "faction": "Amarr", "role": "Heavy Buffer Transport", "threat": THREAT_HAULER, "tank": "Massive Armor Buffer (+2 Warp Core)", "speed": "Slow (MWD-Cloak)", "optimal_range": "Hauler", "tactics": "Fleet hangar transport with +2 passive warp core strength and heavy armor tank."},
    "Providence": {"class": "Freighter", "faction": "Amarr", "role": "Sub-Capital Bulk Freighter", "threat": THREAT_HAULER, "tank": "Armor Buffer", "speed": "Very Slow", "optimal_range": "Freighter", "tactics": "Amarr empire bulk cargo freighter."},
    "Ark": {"class": "Jump Freighter", "faction": "Amarr", "role": "Jump Drive Bulk Transport", "threat": THREAT_HAULER, "tank": "Armor Buffer", "speed": "Jump Drive", "optimal_range": "Cyno Jump", "tactics": "Jump drive freighter for logistics across cyno beacons."},

    # =========================================================================
    # 4. GALLENTE FEDERATION VESSELS
    # =========================================================================
    # --- Gallente Frigates & T2 ---
    "Atron": {"class": "Frigate", "faction": "Gallente", "role": "Fast Tackle Frigate", "threat": "FAST TACKLE", "tank": "Armor / Hull", "speed": "Extreme (4.0+ km/s)", "optimal_range": "0-8 km", "tactics": "High speed tackle frigate with close range blaster DPS."},
    "Tristan": {"class": "Frigate", "faction": "Gallente", "role": "Drone Kiter / Brawler", "threat": THREAT_COMBATANT, "tank": "Shield / Armor / Hull", "speed": "Fast", "optimal_range": "0-40 km Drones", "tactics": "Premier T1 drone frigate. Kites at 35km while drones attack."},
    "Incursus": {"class": "Frigate", "faction": "Gallente", "role": "Active Armor Blaster Brawler", "threat": THREAT_COMBATANT, "tank": "Active Armor (Dual Rep)", "speed": "Moderate", "optimal_range": "0-8 km", "tactics": "Huge active armor repair bonus. Deadly close range brawler."},
    "Maulus": {"class": "Frigate", "faction": "Gallente", "role": "Sensor Dampener Frigate", "threat": THREAT_ECM, "tank": "Paper Thin", "speed": "Fast", "optimal_range": "40-70 km Damp", "tactics": "Sensor dampeners reduce enemy targeting range and lock speed."},
    "Navitas": {"class": "Frigate", "faction": "Gallente", "role": "Armor Logistics Frigate", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Moderate", "optimal_range": "Remote Armor", "tactics": "T1 frigate remote armor repair."},
    "Imicus": {"class": "Frigate", "faction": "Gallente", "role": "Exploration / Scanner", "threat": "EXPLORATION", "tank": "None", "speed": "Moderate", "optimal_range": "Scanning", "tactics": "Exploration scanning frigate."},
    "Federation Navy Comet": {"class": "Faction Frigate", "faction": "Gallente (Navy)", "role": "High DPS Blaster / Rail Brawler", "threat": THREAT_COMBATANT, "tank": "Armor / Hull", "speed": "Fast", "optimal_range": "0-12 km", "tactics": "Extreme close range blaster DPS and drone bay."},
    "Maulus Navy Issue": {"class": "Faction Frigate", "faction": "Gallente (Navy)", "role": "Scram Range / Damp Tackler", "threat": THREAT_ECM, "tank": "Armor", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Extended warp scrambler range and sensor dampening."},
    "Enyo": {"class": "Assault Frigate", "faction": "Gallente", "role": "Blaster Assault Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer + ADC", "speed": "Fast", "optimal_range": "0-8 km", "tactics": "Monster close-range blaster DPS with ADC."},
    "Ishkur": {"class": "Assault Frigate", "faction": "Gallente", "role": "Drone Assault Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer + ADC", "speed": "Fast", "optimal_range": "0-30 km", "tactics": "Assault frigate with combat drones and blaster support."},
    "Taranis": {"class": "Interceptor", "faction": "Gallente", "role": "Combat Interceptor / Blaster", "threat": "FAST TACKLE", "tank": "Armor / Hull", "speed": "Extreme", "optimal_range": "0-8 km", "tactics": "Combat interceptor with heavy blaster DPS."},
    "Ares": {"class": "Interceptor", "faction": "Gallente", "role": "Fleet Interceptor / Fast Align", "threat": "FAST TACKLE", "tank": "Armor", "speed": "Extreme (4.5+ km/s)", "optimal_range": "25-35 km point", "tactics": "Sub-2 second align bubble immune interceptor."},
    "Helios": {"class": "Covert Ops", "faction": "Gallente", "role": "Covert Scout / Cyno", "threat": THREAT_CYNO, "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "Cloak", "tactics": "Covert ops cloaking and covert cynos."},
    "Keres": {"class": "Electronic Attack Ship", "faction": "Gallente", "role": "Long-Range Point & Dampener", "threat": THREAT_ECM, "tank": "Armor", "speed": "Fast", "optimal_range": "35-50 km Point / Damp", "tactics": "Projects 40km+ point/scram and long range sensor dampeners."},
    "Nemesis": {"class": "Stealth Bomber", "faction": "Gallente", "role": "Covert Torpedo / Bomb Bomber", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Thermal bombs and torpedoes from cloak."},
    "Thalia": {"class": "Logistics Frigate", "faction": "Gallente", "role": "T2 Armor Logistics Frigate", "threat": THREAT_LOGI, "tank": "Armor", "speed": "Fast", "optimal_range": "Remote Armor", "tactics": "T2 frigate remote armor repair."},

    # --- Gallente Destroyers & T3D ---
    "Catalyst": {"class": "Destroyer", "faction": "Gallente", "role": "Blaster High DPS Destroyer", "threat": THREAT_COMBATANT, "tank": "Hull / Armor Buffer", "speed": "Moderate", "optimal_range": "0-8 km (Neutron Blasters)", "tactics": "8 blaster turrets deliver 600+ DPS. Iconic highsec gank and close brawling destroyer."},
    "Algos": {"class": "Destroyer", "faction": "Gallente", "role": "Drone / Rail Destroyer", "threat": THREAT_COMBATANT, "tank": "Armor / Hull Buffer", "speed": "Moderate", "optimal_range": "0-30 km", "tactics": "Heavy light drone DPS with railgun/blaster support."},
    "Catalyst Navy Issue": {"class": "Faction Destroyer", "faction": "Gallente (Navy)", "role": "Navy Blaster Destroyer", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-10 km", "tactics": "Enhanced blaster tracking and armor hitpoints."},
    "Eris": {"class": "Interdictor", "faction": "Gallente", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Armor / Hull Buffer", "speed": "Fast", "optimal_range": "0-8 km", "tactics": "Blaster hull-tanked interdictor with high close-range DPS."},
    "Magus": {"class": "Command Destroyer", "faction": "Gallente", "role": "Micro Jump Field / Armor Boosts", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Micro Jump Field jumps ships 100km; provides armor warfare links."},
    "Hecate": {"class": "Tactical Destroyer", "faction": "Gallente", "role": "Mode Switching Blaster DPS", "threat": THREAT_T2_COMBAT, "tank": "Armor / Hull Active", "speed": "Extreme", "optimal_range": "0-8 km", "tactics": "1000+ DPS blaster destroyer. Switches between Propulsion, Defense, and Sharpshooter modes instantly."},

    # --- Gallente Cruisers & T2 / T3C ---
    "Thorax": {"class": "Cruiser", "faction": "Gallente", "role": "Blaster Brawler Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Fast (2.0 km/s)", "optimal_range": "0-12 km", "tactics": "High speed medium blaster brawler with drone support."},
    "Vexor": {"class": "Cruiser", "faction": "Gallente", "role": "Drone Combat Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor / Shield Buffer", "speed": "Moderate", "optimal_range": "0-60 km Drones", "tactics": "Full flight of medium/heavy drones with hybrid turret support."},
    "Exequror": {"class": "Cruiser", "faction": "Gallente", "role": "Armor Logistics Cruiser", "threat": THREAT_LOGI, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "Remote Armor (40-60 km)", "tactics": "Solo-cap sustained armor logistics cruiser."},
    "Celestis": {"class": "Cruiser", "faction": "Gallente", "role": "Sensor Dampener Cruiser", "threat": THREAT_ECM, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "60-100 km Damp", "tactics": "Cruiser-grade sensor dampening reduces lock range to under 15km."},
    "Thorax Navy Issue": {"class": "Faction Cruiser", "faction": "Gallente (Navy)", "role": "Navy Blaster Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Enhanced blaster damage and tracking speed."},
    "Vexor Navy Issue": {"class": "Faction Cruiser", "faction": "Gallente (Navy)", "role": "Heavy Drone / Blaster Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor / Shield Buffer", "speed": "Fast (2.1 km/s)", "optimal_range": "0-60 km", "tactics": "Premier drone cruiser. High speed and heavy drone tracking."},
    "Exequror Navy Issue": {"class": "Faction Cruiser", "faction": "Gallente (Navy)", "role": "Heavy Blaster / Rail Brawler", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "0-20 km", "tactics": "Massive hybrid damage and armor resistances."},
    "Deimos": {"class": "Heavy Assault Cruiser", "faction": "Gallente", "role": "Active Armor Blaster Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Armor (Dual Rep) + ADC", "speed": "Fast", "optimal_range": "0-10 km", "tactics": "Monster active armor rep with ADC. Extreme close-range blaster DPS. Counter with heavy neuts."},
    "Ishtar": {"class": "Heavy Assault Cruiser", "faction": "Gallente", "role": "Heavy Sentry / Drone Cruiser", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer / Armor + ADC", "speed": "Moderate", "optimal_range": "0-80 km", "tactics": "Heavy drone / sentry combat cruiser. Signature radius reduction makes it hard to hit with heavy guns."},
    "Phobos": {"class": "Heavy Interdiction Cruiser", "faction": "Gallente", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "Blaster armor HIC with infinite tackle point."},
    "Oneiros": {"class": "Logistics Cruiser", "faction": "Gallente", "role": "T2 Armor Logistics (Self-Cap)", "threat": THREAT_LOGI, "tank": "Armor Buffer", "speed": "Fast", "optimal_range": "Remote Armor 50-70 km", "tactics": "T2 fleet armor repairer that is self-sufficient without a cap chain."},
    "Arazu": {"class": "Force Recon", "faction": "Gallente", "role": "Covert Cyno / Long Point", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Moderate", "optimal_range": "35-50 km point", "tactics": "Can cloak and light Covert Cynos for Black Ops hotdrops. Projects 40+ km point. High bait hazard."},
    "Lachesis": {"class": "Combat Recon", "faction": "Gallente", "role": "Long Point / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield / Armor", "speed": "Moderate", "optimal_range": "50-70 km Point", "tactics": "IMMUNE TO D-SCAN. Extreme range warp disruptor point (60+ km)."},
    "Proteus": {"class": "Strategic Cruiser", "faction": "Gallente", "role": "Heavy Scram / Blaster DPS", "threat": THREAT_CYNO, "tank": "Armor Buffer / Active", "speed": "Moderate", "optimal_range": "0-10 km", "tactics": "Modular T3C. Configurable for covert cloaking, 1000+ DPS blasters, or extended scram range."},

    # --- Gallente Battlecruisers & Command Ships ---
    "Brutix": {"class": "Battlecruiser", "faction": "Gallente", "role": "Blaster Brawler", "threat": THREAT_COMBATANT, "tank": "Active / Buffer Armor", "speed": "Moderate", "optimal_range": "0-12 km", "tactics": "Devastating close-range blaster DPS with armor repair bonus."},
    "Myrmidon": {"class": "Battlecruiser", "faction": "Gallente", "role": "Triple Rep Drone Brawler", "threat": THREAT_COMBATANT, "tank": "Active Armor (Triple Rep)", "speed": "Slow", "optimal_range": "0-50 km", "tactics": "Iconic triple-repair armor active tank with full drone flight."},
    "Talos": {"class": "Attack Battlecruiser", "faction": "Gallente", "role": "Battleship-Gun Blaster Sniper", "threat": THREAT_COMBATANT, "tank": "Paper Thin Shield", "speed": "Fast for BC", "optimal_range": "0-20 km Blaster / 60-120 km Rail", "tactics": "Fits Large Battleship Blasters/Rails on Battlecruiser hull. Massive DPS."},
    "Brutix Navy Issue": {"class": "Faction Battlecruiser", "faction": "Gallente (Navy)", "role": "Navy Blaster Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Enhanced hybrid damage and armor resistances."},
    "Myrmidon Navy Issue": {"class": "Faction Battlecruiser", "faction": "Gallente (Navy)", "role": "Navy Drone Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Armor Buffer / Active", "speed": "Moderate", "optimal_range": "0-60 km", "tactics": "Enhanced drone tracking and hybrid turret firepower."},
    "Astarte": {"class": "Command Ship", "faction": "Gallente", "role": "Armor Command / Blaster DPS", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer", "speed": "Slow", "optimal_range": "0-12 km", "tactics": "Heavy blaster command ship providing fleet armor warfare links."},
    "Eos": {"class": "Command Ship", "faction": "Gallente", "role": "Drone Command / Armor Rep", "threat": THREAT_T2_COMBAT, "tank": "Armor Active / Buffer", "speed": "Slow", "optimal_range": "0-60 km", "tactics": "Heavy drone command ship providing fleet armor boost links."},

    # --- Gallente Battleships & T2 ---
    "Megathron": {"class": "Battleship", "faction": "Gallente", "role": "Blaster / Railgun Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-20 km Blaster / 60+ km Rail", "tactics": "Heavy hybrid turret tracking bonus."},
    "Dominix": {"class": "Battleship", "faction": "Gallente", "role": "Drone / Neut Battleship", "threat": THREAT_COMBATANT, "tank": "Dual Armor Rep / Buffer", "speed": "Slow", "optimal_range": "0-70 km", "tactics": "Heavy drone projection and heavy energy neutralizers."},
    "Hyperion": {"class": "Battleship", "faction": "Gallente", "role": "Active Armor Blaster Brawler", "threat": THREAT_COMBATANT, "tank": "Active Armor (Dual Rep)", "speed": "Slow", "optimal_range": "0-15 km", "tactics": "Massive active armor repair bonus. Devastating close-range blaster DPS."},
    "Megathron Navy Issue": {"class": "Faction Battleship", "faction": "Gallente (Navy)", "role": "Heavy Blaster / Rail Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-30 km", "tactics": "Massive hybrid damage and tracking speed bonuses."},
    "Dominix Navy Issue": {"class": "Faction Battleship", "faction": "Gallente (Navy)", "role": "Hybrid / Drone Fleet Battleship", "threat": THREAT_COMBATANT, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-60 km", "tactics": "Heavy railgun/blaster damage alongside combat drones."},
    "Sin": {"class": "Black Ops", "faction": "Gallente", "role": "Covert Bridge / Drone & Neut DPS", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Jump Drive", "optimal_range": "0-30 km", "tactics": "Heavy energy neutralizer and heavy drone combatant."},
    "Kronos": {"class": "Marauder", "faction": "Gallente", "role": "Bastion Blaster/Railgun DPS", "threat": THREAT_MARAUDER, "tank": "Active Armor (2500+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "0-15 km Blaster (2000+ DPS)", "tactics": "Deadly close-range blaster DPS. Stay outside 20km or neutralize capacitor. Bastion mode grants 100% rep bonus and EWAR immunity."},

    # --- Gallente Capitals & Freighters ---
    "Moros": {"class": "Dreadnought", "faction": "Gallente", "role": "Capital Blaster/Rail Siege", "threat": THREAT_CAPITAL, "tank": "Armor Active / Buffer", "speed": "Capital", "optimal_range": "0-40 km", "tactics": "Extreme capital blaster DPS in Siege mode."},
    "Moros Navy Issue": {"class": "Faction Dreadnought", "faction": "Gallente (Navy)", "role": "Navy Blaster Dreadnought", "threat": THREAT_CAPITAL, "tank": "Armor Active", "speed": "Capital", "optimal_range": "0-40 km", "tactics": "Enhanced capital hybrid tracking and armor repair."},
    "Hubris": {"class": "Lancer Dreadnought", "faction": "Gallente", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Gallente disruptive capital lance weapon."},
    "Thanatos": {"class": "Carrier", "faction": "Gallente", "role": "Capital Fighter Platform", "threat": THREAT_CAPITAL, "tank": "Armor Buffer", "speed": "Capital", "optimal_range": "Fighter Operations", "tactics": "Gallente fleet carrier with fighter damage bonus."},
    "Ninazu": {"class": "Force Auxiliary", "faction": "Gallente", "role": "Capital Armor Logistics", "threat": THREAT_CAPITAL, "tank": "Armor Active (Triage)", "speed": "Capital", "optimal_range": "Fleet Remote Armor", "tactics": "Capital armor repairer. In Triage mode reps massive armor EHP per second to fleet."},
    "Nyx": {"class": "Supercarrier", "faction": "Gallente", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Gallente supercarrier deploying heavy fighter wings and burst projectors."},
    "Erebus": {"class": "Titan", "faction": "Gallente", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Gallente supercapital Titan with Aurora Omniphage Doomsday device."},
    "Iteron Mark V": {"class": "Industrial", "faction": "Gallente", "role": "High Capacity Hauler", "threat": THREAT_HAULER, "tank": "Armor", "speed": "Slow", "optimal_range": "Hauler", "tactics": "High-capacity Gallente cargo hauler."},
    "Epithal": {"class": "Industrial", "faction": "Gallente", "role": "Planetary Industry Hauler", "threat": THREAT_HAULER, "tank": "Armor / Shield", "speed": "Slow", "optimal_range": "PI Hauler", "tactics": "Specialized planetary interaction (PI) commodity hauler with 60,000+ m3 bay."},
    "Miasmos": {"class": "Industrial", "faction": "Gallente", "role": "Mineral & Ore Hauler", "threat": THREAT_HAULER, "tank": "Armor / Shield", "speed": "Slow", "optimal_range": "Ore Hauler", "tactics": "Specialized raw ore and ice transport with 60,000+ m3 ore hold."},
    "Viator": {"class": "Blockade Runner", "faction": "Gallente", "role": "Covert Cloak Hauler", "threat": THREAT_HAULER, "tank": "Armor", "speed": "Fast Align / Cloaked", "optimal_range": "Covert Cloak", "tactics": "Covert cloaking blockade runner; immune to cargo scanners."},
    "Occator": {"class": "Deep Space Transport", "faction": "Gallente", "role": "Heavy Buffer Transport", "threat": THREAT_HAULER, "tank": "Massive Armor Buffer (+2 Warp Core)", "speed": "Slow (MWD-Cloak)", "optimal_range": "Hauler", "tactics": "Fleet hangar transport with +2 passive warp core strength and heavy armor tank."},
    "Obelisk": {"class": "Freighter", "faction": "Gallente", "role": "Sub-Capital Bulk Freighter", "threat": THREAT_HAULER, "tank": "Armor Buffer", "speed": "Very Slow", "optimal_range": "Freighter", "tactics": "Massive cargo capacity bulk freighter."},
    "Anshar": {"class": "Jump Freighter", "faction": "Gallente", "role": "Jump Drive Bulk Transport", "threat": THREAT_HAULER, "tank": "Armor Buffer", "speed": "Jump Drive", "optimal_range": "Cyno Jump", "tactics": "Jump drive freighter for logistics across cyno beacons."},

    # =========================================================================
    # 5. MINMATAR REPUBLIC VESSELS
    # =========================================================================
    # --- Minmatar Frigates & T2 ---
    "Rifter": {"class": "Frigate", "faction": "Minmatar", "role": "Autocannon / Artillery Frigate", "threat": THREAT_COMBATANT, "tank": "Armor / Shield Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Iconic Minmatar combat frigate with projectile damage."},
    "Slasher": {"class": "Frigate", "faction": "Minmatar", "role": "Fast Tackle Frigate", "threat": "FAST TACKLE", "tank": "Shield Buffer", "speed": "Extreme (4.5+ km/s)", "optimal_range": "0-10 km", "tactics": "High speed tackle frigate with fast align."},
    "Breacher": {"class": "Frigate", "faction": "Minmatar", "role": "Active Shield Missile Brawler", "threat": THREAT_COMBATANT, "tank": "Active Shield (Dual MASB)", "speed": "Fast", "optimal_range": "0-20 km", "tactics": "Dual ancillary shield boosters and missile firepower."},
    "Vigil": {"class": "Frigate", "faction": "Minmatar", "role": "Target Painter Frigate", "threat": THREAT_ECM, "tank": "Paper Thin", "speed": "Extreme", "optimal_range": "40-70 km Paint", "tactics": "Target painters bloom enemy signature radius for missile application."},
    "Burst": {"class": "Frigate", "faction": "Minmatar", "role": "Shield Logistics Frigate", "threat": THREAT_LOGI, "tank": "Shield", "speed": "Fast", "optimal_range": "Remote Shield", "tactics": "T1 frigate remote shield repair."},
    "Probe": {"class": "Frigate", "faction": "Minmatar", "role": "Exploration / Scanner", "threat": "EXPLORATION", "tank": "None", "speed": "Fast", "optimal_range": "Scanning", "tactics": "Exploration scanning frigate."},
    "Republic Fleet Firetail": {"class": "Faction Frigate", "faction": "Minmatar (Fleet)", "role": "High Alpha Projectile Brawler", "threat": THREAT_COMBATANT, "tank": "Shield / Armor", "speed": "Extreme (4.2+ km/s)", "optimal_range": "0-15 km", "tactics": "Fast projectile frigate with tracking and damage bonuses."},
    "Vigil Fleet Issue": {"class": "Faction Frigate", "faction": "Minmatar (Fleet)", "role": "Rocket / Web Skirmisher", "threat": THREAT_COMBATANT, "tank": "Shield", "speed": "Extreme", "optimal_range": "0-20 km", "tactics": "Extended webifier range and rocket firepower."},
    "Jaguar": {"class": "Assault Frigate", "faction": "Minmatar", "role": "Active Shield / Rocket Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual MASB + ADC)", "speed": "Extreme", "optimal_range": "0-15 km", "tactics": "Massive active shield boost and speed with ADC."},
    "Wolf": {"class": "Assault Frigate", "faction": "Minmatar", "role": "Autocannon Assault Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor / Shield Buffer + ADC", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Heavy autocannon/artillery damage with ADC."},
    "Claw": {"class": "Interceptor", "faction": "Minmatar", "role": "Combat Interceptor / Projectile", "threat": "FAST TACKLE", "tank": "Shield / Armor", "speed": "Extreme", "optimal_range": "0-10 km", "tactics": "Combat interceptor with projectile firepower."},
    "Stiletto": {"class": "Interceptor", "faction": "Minmatar", "role": "Fleet Interceptor / Fast Point", "threat": "FAST TACKLE", "tank": "Shield", "speed": "Extreme (5.0+ km/s)", "optimal_range": "25-35 km point", "tactics": "Sub-2 second align bubble immune fleet interceptor."},
    "Cheetah": {"class": "Covert Ops", "faction": "Minmatar", "role": "Covert Scout / Cyno", "threat": THREAT_CYNO, "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "Cloak", "tactics": "Covert ops cloaking and covert cynos."},
    "Hyena": {"class": "Electronic Attack Ship", "faction": "Minmatar", "role": "Long-Range Stasis Webifier", "threat": THREAT_ECM, "tank": "Shield", "speed": "Fast", "optimal_range": "30-50 km Web", "tactics": "Projects 40km+ stasis webs from frigate hull."},
    "Hound": {"class": "Stealth Bomber", "faction": "Minmatar", "role": "Covert Torpedo / Bomb Bomber", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Explosive bombs and torpedoes from cloak."},
    "Scalpel": {"class": "Logistics Frigate", "faction": "Minmatar", "role": "T2 Shield Logistics Frigate", "threat": THREAT_LOGI, "tank": "Shield", "speed": "Extreme", "optimal_range": "Remote Shield", "tactics": "T2 frigate remote shield transfer."},

    # --- Minmatar Destroyers & T3D ---
    "Thrasher": {"class": "Destroyer", "faction": "Minmatar", "role": "Autocannon / Artillery High Alpha", "threat": THREAT_COMBATANT, "tank": "Shield / Armor Buffer", "speed": "Fast (2.5 km/s)", "optimal_range": "0-15 km AC / 40-70 km Art", "tactics": "8 projectile turrets deliver huge instant alpha strike."},
    "Talwar": {"class": "Destroyer", "faction": "Minmatar", "role": "Light Missile Fleet Kiter", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "30-60 km", "tactics": "7 missile launchers with MWD signature radius reduction."},
    "Thrasher Fleet Issue": {"class": "Faction Destroyer", "faction": "Minmatar (Fleet)", "role": "Navy Projectile Destroyer", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "0-20 km", "tactics": "Enhanced projectile rate of fire and tracking."},
    "Sabre": {"class": "Interdictor", "faction": "Minmatar", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Fast (3.5+ km/s)", "optimal_range": "0-12 km (Autocannons)", "tactics": "Launches 20km warp disruption probes (bubbles). Primary tackle priority in fleets. Target and destroy immediately before bubble deployment."},
    "Bifrost": {"class": "Command Destroyer", "faction": "Minmatar", "role": "Micro Jump Field / Shield Boosts", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Micro Jump Field jumps ships 100km; provides shield warfare links."},
    "Svipul": {"class": "Tactical Destroyer", "faction": "Minmatar", "role": "Mode Switching Projectile", "threat": THREAT_T2_COMBAT, "tank": "Shield / Armor", "speed": "Extreme", "optimal_range": "10-30 km", "tactics": "Switches between Propulsion, Defense, and Sharpshooter modes."},

    # --- Minmatar Cruisers & T2 / T3C ---
    "Rupture": {"class": "Cruiser", "faction": "Minmatar", "role": "Projectile Brawler Cruiser", "threat": THREAT_COMBATANT, "tank": "Armor / Shield Buffer", "speed": "Moderate", "optimal_range": "0-25 km", "tactics": "Versatile projectile platform with strong armor/shield buffer."},
    "Stabber": {"class": "Cruiser", "faction": "Minmatar", "role": "High-Speed Autocannon Kiter", "threat": THREAT_COMBATANT, "tank": "Shield Buffer / Active", "speed": "Extreme (2.5+ km/s)", "optimal_range": "0-20 km", "tactics": "High speed projectile kiter. Outruns most other cruisers."},
    "Scythe": {"class": "Cruiser", "faction": "Minmatar", "role": "Shield Logistics Cruiser", "threat": THREAT_LOGI, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "Remote Shield (40-60 km)", "tactics": "Solo-cap sustained shield logistics cruiser."},
    "Bellicose": {"class": "Cruiser", "faction": "Minmatar", "role": "Target Painter / Missile Cruiser", "threat": THREAT_ECM, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "20-60 km", "tactics": "Target painters and rapid light / heavy missile firepower."},
    "Stabber Fleet Issue": {"class": "Faction Cruiser", "faction": "Minmatar (Fleet)", "role": "High DPS Projectile Cruiser", "threat": THREAT_COMBATANT, "tank": "Shield / Armor Buffer", "speed": "Fast (2.4 km/s)", "optimal_range": "0-25 km", "tactics": "Heavy projectile damage and tracking speed."},
    "Scythe Fleet Issue": {"class": "Faction Cruiser", "faction": "Minmatar (Fleet)", "role": "High-Speed Missile / AC Skirmisher", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Fast (2.5+ km/s)", "optimal_range": "20-60 km", "tactics": "Fast missile and autocannon skirmish cruiser."},
    "Vagabond": {"class": "Heavy Assault Cruiser", "faction": "Minmatar", "role": "Nano Autocannon Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual ASB) + ADC", "speed": "Extreme (3.0+ km/s)", "optimal_range": "0-25 km", "tactics": "High speed and fast falloff projectile brawler with ADC. Scram and web to neutralize speed tank."},
    "Muninn": {"class": "Heavy Assault Cruiser", "faction": "Minmatar", "role": "Missile / Skirmish Cruiser", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer + ADC", "speed": "Fast (2.2 km/s)", "optimal_range": "40-80 km", "tactics": "High-mobility missile HAC with strong kinetic/explosive damage and ADC."},
    "Broadsword": {"class": "Heavy Interdiction Cruiser", "faction": "Minmatar", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate (500MN HIC viable)", "optimal_range": "0-35 km", "tactics": "WDFG projects focused infinite point (scrams supercapitals) or 20km bubble."},
    "Scimitar": {"class": "Logistics Cruiser", "faction": "Minmatar", "role": "T2 Shield Logistics (Self-Cap)", "threat": THREAT_LOGI, "tank": "Shield Buffer", "speed": "Fast (2.2+ km/s)", "optimal_range": "Remote Shield 50-70 km", "tactics": "T2 fleet shield repairer that is self-sufficient without a cap chain."},
    "Rapier": {"class": "Force Recon", "faction": "Minmatar", "role": "Covert Cyno / Long Web", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Moderate", "optimal_range": "30-50 km Web", "tactics": "Cloaked long-range stasis webifier (40-60 km). Shuts down kite ships. Lights covert cynos."},
    "Huginn": {"class": "Combat Recon", "faction": "Minmatar", "role": "Long Web & Paint / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield", "speed": "Moderate", "optimal_range": "40-60 km Web", "tactics": "IMMUNE TO D-SCAN. Extreme range webifier and target painter."},
    "Loki": {"class": "Strategic Cruiser", "faction": "Minmatar", "role": "Web / Heavy Projectile / Cloaky", "threat": THREAT_CYNO, "tank": "Shield / Armor Buffer", "speed": "Fast (2.0-2.8 km/s)", "optimal_range": "15-40 km", "tactics": "Modular T3C. Extreme versatility: 40km 90% webs, covert cloak, nullification, or heavy autocannon/artillery/missile DPS."},

    # --- Minmatar Battlecruisers & Command Ships ---
    "Hurricane": {"class": "Battlecruiser", "faction": "Minmatar", "role": "Heavy Projectile Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Shield / Armor Buffer", "speed": "Fast for BC", "optimal_range": "15-40 km AC / 70+ km Art", "tactics": "Versatile projectile platform with high alpha strike."},
    "Cyclone": {"class": "Battlecruiser", "faction": "Minmatar", "role": "Active Shield Missile Brawler", "threat": THREAT_COMBATANT, "tank": "Active Shield (Dual XLASB)", "speed": "Moderate", "optimal_range": "0-30 km", "tactics": "Massive active shield boost bonus and heavy missile firepower."},
    "Tornado": {"class": "Attack Battlecruiser", "faction": "Minmatar", "role": "Battleship-Gun 1400mm Artillery Sniper", "threat": THREAT_COMBATANT, "tank": "Paper Thin Shield", "speed": "Fast for BC (2.0 km/s)", "optimal_range": "80-150 km", "tactics": "Fits Large 1400mm Artillery on Battlecruiser hull. Devastating alpha strike (10,000+ alpha)."},
    "Hurricane Fleet Issue": {"class": "Faction Battlecruiser", "faction": "Minmatar (Fleet)", "role": "Navy Projectile Battlecruiser", "threat": THREAT_COMBATANT, "tank": "Shield / Armor Buffer", "speed": "Fast for BC", "optimal_range": "15-50 km AC / 80+ km Art", "tactics": "Enhanced projectile rate of fire and tracking."},
    "Cyclone Fleet Issue": {"class": "Faction Battlecruiser", "faction": "Minmatar (Fleet)", "role": "Heavy Missile Navy BC", "threat": THREAT_COMBATANT, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "20-60 km", "tactics": "Enhanced missile rate of fire and velocity."},
    "Sleipnir": {"class": "Command Ship", "faction": "Minmatar", "role": "Shield Skirmish Booster / AC DPS", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual ASB)", "speed": "Fast", "optimal_range": "10-35 km", "tactics": "Monster active shield booster with heavy autocannon damage and fleet shield boosts."},
    "Claymore": {"class": "Command Ship", "faction": "Minmatar", "role": "Shield Command / Missile DPS", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "30-70 km", "tactics": "Fleet command ship providing shield warfare links."},

    # --- Minmatar Battleships & T2 ---
    "Tempest": {"class": "Battleship", "faction": "Minmatar", "role": "Artillery / AC Battleship", "threat": THREAT_COMBATANT, "tank": "Shield / Armor", "speed": "Fast for BS", "optimal_range": "20-40 km AC / 100+ km Art", "tactics": "High-speed projectile battleship with massive alpha."},
    "Typhoon": {"class": "Battleship", "faction": "Minmatar", "role": "Missile / Cruise Battleship", "threat": THREAT_COMBATANT, "tank": "Armor / Shield", "speed": "Fast for BS", "optimal_range": "30-90 km", "tactics": "Rapid heavy missile / torpedo platform with versatile slot layout."},
    "Maelstrom": {"class": "Battleship", "faction": "Minmatar", "role": "Active Shield Projectile Battleship", "threat": THREAT_COMBATANT, "tank": "Active Shield (X-Large Booster)", "speed": "Slow", "optimal_range": "20-40 km AC / 80+ km Art", "tactics": "Active shield booster bonus and heavy projectile firepower."},
    "Tempest Fleet Issue": {"class": "Faction Battleship", "faction": "Minmatar (Fleet)", "role": "Artillery / AC High Alpha Battleship", "threat": THREAT_COMBATANT, "tank": "Shield / Armor Buffer", "speed": "Fast for BS", "optimal_range": "25-50 km AC / 100+ km Art", "tactics": "Extreme projectile rate of fire and devastating alpha strike."},
    "Typhoon Fleet Issue": {"class": "Faction Battleship", "faction": "Minmatar (Fleet)", "role": "Missile / Cruise Fleet Battleship", "threat": THREAT_COMBATANT, "tank": "Armor / Shield Buffer", "speed": "Fast for BS", "optimal_range": "30-100 km", "tactics": "Versatile missile and projectile platform with high armor buffer."},
    "Panther": {"class": "Black Ops", "faction": "Minmatar", "role": "Covert Bridge / Projectile DPS", "threat": THREAT_CYNO, "tank": "Shield / Armor", "speed": "Jump Drive", "optimal_range": "20-50 km", "tactics": "High-mobility projectile Black Ops battleship."},
    "Vargur": {"class": "Marauder", "faction": "Minmatar", "role": "Bastion Autocannon/Artillery DPS", "threat": THREAT_MARAUDER, "tank": "Active Shield (2000+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "0-45 km Autocannon / 100+ km Art", "tactics": "BASTION MODE: 100% rep bonus, immune to EWAR (neuts still apply), 0 sub-warp speed for 60s. Heavy tracking bonus. Counter with neuts, extreme transversal, or fleet focus fire."},

    # --- Minmatar Capitals & Freighters ---
    "Naglfar": {"class": "Dreadnought", "faction": "Minmatar", "role": "Capital Projectile Siege", "threat": THREAT_CAPITAL, "tank": "Shield / Armor Active", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "High alpha projectile dreadnought with Siege module."},
    "Naglfar Navy Issue": {"class": "Faction Dreadnought", "faction": "Minmatar (Fleet)", "role": "Navy Projectile Dreadnought", "threat": THREAT_CAPITAL, "tank": "Shield / Armor Active", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Enhanced projectile rate of fire and dual tank options."},
    "Valravn": {"class": "Lancer Dreadnought", "faction": "Minmatar", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Shield", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Minmatar disruptive capital lance weapon."},
    "Nidhoggur": {"class": "Carrier", "faction": "Minmatar", "role": "Capital Fighter Platform", "threat": THREAT_CAPITAL, "tank": "Shield Buffer", "speed": "Capital", "optimal_range": "Fighter Operations", "tactics": "Minmatar fleet carrier with fighter velocity and damage bonuses."},
    "Lif": {"class": "Force Auxiliary", "faction": "Minmatar", "role": "Capital Shield Logistics", "threat": THREAT_CAPITAL, "tank": "Shield Active (Triage)", "speed": "Capital", "optimal_range": "Fleet Remote Shield", "tactics": "Capital shield repairer. In Triage mode reps massive shield EHP per second to fleet."},
    "Hel": {"class": "Supercarrier", "faction": "Minmatar", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Minmatar supercarrier deploying heavy fighter wings and burst projectors."},
    "Ragnarok": {"class": "Titan", "faction": "Minmatar", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Minmatar supercapital Titan with Gjallarhorn Doomsday device."},
    "Wreathe": {"class": "Industrial", "faction": "Minmatar", "role": "Fast Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Fast for Hauler", "optimal_range": "Hauler", "tactics": "Fast align Minmatar industrial hauler."},
    "Mammoth": {"class": "Industrial", "faction": "Minmatar", "role": "High Capacity Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Slow", "optimal_range": "Hauler", "tactics": "High-capacity Minmatar cargo hauler."},
    "Prowler": {"class": "Blockade Runner", "faction": "Minmatar", "role": "Covert Cloak Hauler", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Fast Align / Cloaked", "optimal_range": "Covert Cloak", "tactics": "Fastest blockade runner in EVE; covert cloaking; immune to cargo scanners."},
    "Mastodon": {"class": "Deep Space Transport", "faction": "Minmatar", "role": "Heavy Buffer Transport", "threat": THREAT_HAULER, "tank": "Massive Shield Buffer (+2 Warp Core)", "speed": "Slow (MWD-Cloak)", "optimal_range": "Hauler", "tactics": "Fleet hangar transport with +2 passive warp core strength and massive shield tank."},
    "Fenrir": {"class": "Freighter", "faction": "Minmatar", "role": "Sub-Capital Bulk Freighter", "threat": THREAT_HAULER, "tank": "Shield Buffer", "speed": "Fast for Freighter", "optimal_range": "Freighter", "tactics": "Fastest aligning sub-capital bulk cargo freighter."},
    "Nomad": {"class": "Jump Freighter", "faction": "Minmatar", "role": "Jump Drive Bulk Transport", "threat": THREAT_HAULER, "tank": "Shield Buffer", "speed": "Jump Drive", "optimal_range": "Cyno Jump", "tactics": "Jump drive freighter for logistics across cyno beacons."},

    # =========================================================================
    # 6. MINING & INDUSTRIAL SPECIALIST VESSELS
    # =========================================================================
    "Procurer": {"class": "Mining Barge", "faction": "ORE", "role": "Heavy Tank Mining Barge", "threat": THREAT_HAULER, "tank": "Shield Heavy Buffer", "speed": "Slow", "optimal_range": "Mining", "tactics": "Bait mining barge with massive shield hitpoints. Hard to gank."},
    "Retriever": {"class": "Mining Barge", "faction": "ORE", "role": "Large Ore Hold Barge", "threat": THREAT_HAULER, "tank": "Shield Paper", "speed": "Slow", "optimal_range": "Mining", "tactics": "High-capacity ore bay mining barge; vulnerable to ganks."},
    "Covetor": {"class": "Mining Barge", "faction": "ORE", "role": "Maximum Yield Mining Barge", "threat": THREAT_HAULER, "tank": "Paper Thin", "speed": "Slow", "optimal_range": "Mining", "tactics": "Maximum yield strip miner with paper thin tank."},
    "Skiff": {"class": "Exhumer", "faction": "ORE", "role": "T2 Heavy Tank Exhumer", "threat": THREAT_HAULER, "tank": "Massive Shield Buffer", "speed": "Slow", "optimal_range": "Mining", "tactics": "T2 exhumer with extreme shield buffer and defensive drones."},
    "Mackinaw": {"class": "Exhumer", "faction": "ORE", "role": "T2 High Capacity Exhumer", "threat": THREAT_HAULER, "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "Mining", "tactics": "T2 exhumer with huge ore hold."},
    "Hulk": {"class": "Exhumer", "faction": "ORE", "role": "T2 Max Yield Exhumer", "threat": THREAT_HAULER, "tank": "Shield Paper", "speed": "Slow", "optimal_range": "Mining", "tactics": "T2 exhumer with highest mining yield in game."},
    "Noctis": {"class": "Industrial", "faction": "ORE", "role": "Salvage & Tractor Platform", "threat": THREAT_HAULER, "tank": "Shield", "speed": "Slow", "optimal_range": "Salvaging", "tactics": "Dedicated wrecks salvaging and tractor beam platform."},
    "Porpoise": {"class": "Industrial Command", "faction": "ORE", "role": "Mining Fleet Booster", "threat": THREAT_HAULER, "tank": "Shield Active / Buffer", "speed": "Moderate", "optimal_range": "Mining Boosts", "tactics": "Agile sub-capital mining fleet command booster."},
    "Orca": {"class": "Industrial Command", "faction": "ORE", "role": "Heavy Mining Fleet Command", "threat": THREAT_HAULER, "tank": "Massive Shield Buffer", "speed": "Slow", "optimal_range": "Mining Boosts", "tactics": "Sub-capital industrial flagship with massive fleet hangar and mining links."},
    "Rorqual": {"class": "Capital Industrial", "faction": "ORE", "role": "Capital Industrial / PANIC", "threat": THREAT_CAPITAL, "tank": "Shield Active (PANIC 5-7 min invuln)", "speed": "Capital", "optimal_range": "Capital Mining", "tactics": "Capital industrial ship. PANIC module grants total invulnerability for up to 7 minutes while cyno/fleet responds."}
}

# Slang and Abbreviation Resolution Aliases
SHIP_ALIASES: Dict[str, str] = {
    "dram": "Dramiel",
    "cyna": "Cynabal",
    "mach": "Machariel",
    "rattler": "Rattlesnake",
    "cerb": "Cerberus",
    "mun": "Muninn",
    "vaga": "Vagabond",
    "deim": "Deimos",
    "zeal": "Zealot",
    "sac": "Sacrilege",
    "bhaal": "Bhaalgorn",
    "dictor": "Sabre",
    "interdictor": "Sabre",
    "hic": "Broadsword",
    "hictor": "Broadsword",
    "t3c": "Loki",
    "t3d": "Hecate",
    "bomber": "Hound",
    "sb": "Hound",
    "bo": "Redeemer",
    "blops": "Redeemer",
    "dread": "Naglfar",
    "lancer": "Valravn",
    "super": "Hel",
    "titan": "Ragnarok",
    "rni": "Raven Navy Issue",
    "ani": "Apocalypse Navy Issue",
    "tfi": "Tempest Fleet Issue",
    "mni": "Megathron Navy Issue",
    "vni": "Vexor Navy Issue",
    "cni": "Caracal Navy Issue",
    "sni": "Scorpion Navy Issue",
    "oni": "Omen Navy Issue",
    "sfi": "Stabber Fleet Issue",
    "hfi": "Hurricane Fleet Issue",
    "cfi": "Cyclone Fleet Issue",
    "pni": "Phoenix Navy Issue",
    "rni_dread": "Revelation Navy Issue",
    "kiki": "Kikimora",
    "hookbill": "Caldari Navy Hookbill",
    "slicer": "Imperial Navy Slicer",
    "comet": "Federation Navy Comet",
    "firetail": "Republic Fleet Firetail"
}

# Fast O(1) Lowercase Lookup Hash Map
_FAST_SHIP_LOOKUP: Dict[str, Dict[str, Any]] = {}
for name, data in SHIP_DATABASE.items():
    _FAST_SHIP_LOOKUP[name.lower()] = {**data, "canonical_name": name}

for alias, canonical in SHIP_ALIASES.items():
    if canonical in SHIP_DATABASE:
        _FAST_SHIP_LOOKUP[alias.lower()] = {**SHIP_DATABASE[canonical], "canonical_name": canonical}


def lookup_ship(name: str) -> Optional[Dict[str, Any]]:
    """Fast O(1) resolver for any ship name, slang, or alias."""
    clean = name.strip().lower()
    if not clean or clean in ["cyno", "cynos", "cynou", "bubble", "gate", "outgate", "ingate", "station", "undock", "local", "spike", "nv", "na", "clear", "hostiles", "reds"]:
        return None
    return _FAST_SHIP_LOOKUP.get(clean)


ROLE_DOCTRINES: Dict[str, str] = {
    "Solo PvP Roaming": (
        "[COMBAT ROLE DOCTRINE — SOLO PVP ROAMING]:\n"
        "• Strategic Mandate: Self-sufficient combat, independent tackle, capacitor resilience against neuts, and GTFO disengagement.\n"
        "• Fitting Rules: MUST fit independent tackle (Warp Disruptor for kiting or Warp Scrambler + Heavy Stasis Webifier for brawling). Fit Heavy Capacitor Booster 800/3200 or Large Cap Battery. Fit local active tank or self-sufficient buffer with nanite paste. Fit MWD or Micro Jump Drive (MJD) for fast escape.\n"
        "• Absolute Prohibitions: Do NOT fit fleet anchor bricks or remote repairs (no fleet logistics exist in solo roaming). Do NOT omit tackle."
    ),
    "Small Gang Brawling": (
        "[COMBAT ROLE DOCTRINE — SMALL GANG BRAWLING]:\n"
        "• Strategic Mandate: High close-range DPS, heavy tackle pinning, extreme capacitor pressure, and target suppression.\n"
        "• Fitting Rules: Fit Warp Scrambler (<=10km to shut off enemy MWD/MJD) and Heavy Stasis Webifier or Grappler. Fit close-range high DPS weapons (Autocannons, Blasters, Pulse Lasers, Torpedoes). Fit Heavy Energy Neutralizers and strong active or buffer armor/shield tank with cap boosters."
    ),
    "Nano Kiting": (
        "[COMBAT ROLE DOCTRINE — NANO KITING / SKIRMISH]:\n"
        "• Strategic Mandate: High speed skirmishing, manual piloting, isolating targets at range, and avoiding tackle traps.\n"
        "• Cruisers/Battlecruisers: Overheated 50MN/500MN Microwarpdrive, Warp Disruptor (long point 24-30km), long-range projection weapons (Artillery, Beam Lasers, Railguns, Heavy Missiles), Nanofiber Internal Structure, Polycarbon Engine rigs. Maintain distance >20km outside web range; avoid scrambler range at all costs.\n"
        "• Battleships (e.g. Raven Navy, Apocalypse Navy): Battleships have heavy mass and kite via Large Micro Jump Drive (MJD) 100km range resets + long-range weapons (Cruise Missiles, Beam Lasers, Artillery) + Target Painter, NOT cruiser nano agility. Stasis Webifiers are strictly defensive peeling inside 10km, not used for kiting at >40km."
    ),
    "Abyssal Deadspace": (
        "[COMBAT ROLE DOCTRINE — ABYSSAL DEADSPACE PVE]:\n"
        "• Strategic Mandate: Survive and clear 3 combat rooms within 20 minutes under environmental weather hazards.\n"
        "• Fitting Rules: Strict capacitor stability or Large Cap Battery (immune to Starving neuts), sustained active shield/armor repair (500-1200+ EHP/s), damage type matched to weather (Kinetic in Exotic, EM in Electrical, Thermal in Firestorm), MTU/Mobile Tractor Unit."
    ),
    "Fleet Anchor DPS": (
        "[COMBAT ROLE DOCTRINE — FLEET ANCHOR DPS / HEAVY LINE COMBAT]:\n"
        "• Strategic Mandate: Fleet line combat anchoring on the FC; maximize alpha/DPS projection and resist-buffer for fleet logistics reps.\n"
        "• Fitting Rules: Maximum buffer EHP (1600mm Steel Plates or Large Shield Extenders + resist modules), long-range projection guns (Artillery/Tachyon/Mega Pulse/Rails/Cruise Missiles), Tracking Computers / Target Painters. Do NOT fit solo tackle (Warp Disruptors/Scramblers) as fleet tackle wings handle points; leave low/mid slots for max DPS & Buffer."
    ),
    "Nullsec Combat Site Ratting": (
        "[COMBAT ROLE DOCTRINE — NULLSEC SITE RATTING & ESCALATIONS]:\n"
        "• Strategic Mandate: Maximum clear speed against pirate NPC anomalies (Havens/Sanctums) and DED 6/10-10/10 escalations.\n"
        "• Fitting Rules: Specialized NPC damage-type resists (e.g. EM/Therm for Blood/Sansha, Kin/Therm for Guristas, Exp/Kin for Angels), maximum sustained application/DPS (Missile Guidance / Tracking Computers / Drone Damage Amps), large capacitor pool, Mobile Tractor Unit (MTU)."
    ),
    "Wormhole": (
        "[COMBAT ROLE DOCTRINE — WORMHOLE SOLO & EXPLORATION]:\n"
        "• Strategic Mandate: Relic/Data hacking, Sleeper site clearing, and covert travel in J-space.\n"
        "• Fitting Rules: Core Probe Launcher with Sisters Probes, Relic & Data Analyzers, Covert Ops Cloaking Device, Omni-resist active tank (Sleepers deal all 4 damage types and apply heavy neuts/webs)."
    ),
    "Fast Tackle": (
        "[COMBAT ROLE DOCTRINE — HEAVY INTERCEPTION & FAST TACKLE]:\n"
        "• Strategic Mandate: Fast initial point on warping targets, holding tackle until fleet arrives.\n"
        "• Fitting Rules: Sub-2 second align time, 5MN/50MN MWD, Sensor Booster with Scan Resolution script (for insta-locking on gates), Warp Disruptor + Scrambler, Overdrive/Nanofiber modules."
    )
}

EVE_COMBAT_AXIOMS = """
[EVE ONLINE COMBAT DOCTRINE & TACTICAL DIRECTIVES]:
1. STRICT SINGLE RESPONSE (NO DUPLICATES): Output your tactical advice once in 2 to 4 concise bullet points total. NEVER repeat yourself, NEVER generate duplicate sections, and NEVER output headers like '[ENGAGEMENT RANGE / TRANSVERSAL / EVASION / WARP OUT]' or '[EVADE ROUTES]'.
2. NEVER ECHO SYSTEM HEADERS: Never repeat, quote, or output reference headers or tags (such as `[EVE TACTICAL INTELLIGENCE]`, `[TACTICAL DIRECTIVE]`, `[ENGAGEMENT RANGE]`).
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


def get_tactical_grounding(prompt: str, attachments: List[Dict[str, Any]] = None, piloted_ship: Optional[str] = None) -> str:
    """
    Extracts verified ship dossiers and tactical axioms for everything mentioned in the prompt.
    Correctly distinguishes Capsuleer's own piloted vessel from hostile contacts.
    """
    full_text = prompt + " "
    if attachments:
        for att in attachments:
            full_text += att.get("text", "") + " "

    lower_text = full_text.lower()
    words = re.findall(r"\b[A-Za-z0-9\-]+\b", full_text)
    
    grounding_blocks = []
    detected_hulls = set()
    
    # 0. Check if Capsuleer is stating their own piloted vessel (e.g. "I am in a Loki", "Flying a Cerberus")
    own_ship_match = re.search(
        r"\b(?:i am in a|i'm in a|flying a|piloting a|my ship is a?|in a)\s+([A-Za-z0-9\-\s]+?)(?:\s+and|\s+with|\s+need|\s+looking|\s+waiting|\s*\.|\s*,|\s*$)",
        prompt,
        re.IGNORECASE
    )
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

    # Check for direct multi-word ship names first (e.g. "Apocalypse Navy Issue")
    for ship_name, s_info in SHIP_DATABASE.items():
        if len(ship_name.split()) > 1 and ship_name.lower() in lower_text:
            if piloted_ship_name and ship_name.lower() == piloted_ship_name.lower():
                continue
            if ship_name.lower() not in detected_hulls:
                detected_hulls.add(ship_name.lower())
                dossier = (
                    f"• {ship_name} ({s_info.get('class', 'Vessel')} - {s_info.get('faction', 'General')}) | Tank: {s_info.get('tank', 'Shield/Armor')} | "
                    f"Optimal: {s_info.get('optimal_range', 'Standard')} | Threat: {s_info.get('threat', 'Combatant')}\n"
                    f"  Tactics: {s_info.get('tactics', 'Engage according to weapon tracking and range.')}"
                )
                grounding_blocks.append(dossier)

    for w in words:
        s_info = lookup_ship(w)
        if s_info:
            cname = s_info.get("canonical_name", w.capitalize())
            if piloted_ship_name and cname.lower() == piloted_ship_name.lower():
                continue
            if cname.lower() not in detected_hulls:
                detected_hulls.add(cname.lower())
                dossier = (
                    f"• {cname} ({s_info.get('class', 'Vessel')} - {s_info.get('faction', 'General')}) | Tank: {s_info.get('tank', 'Shield/Armor')} | "
                    f"Optimal: {s_info.get('optimal_range', 'Standard')} | Threat: {s_info.get('threat', 'Combatant')}\n"
                    f"  Tactics: {s_info.get('tactics', 'Engage according to weapon tracking and range.')}"
                )
                grounding_blocks.append(dossier)

    # Check for Role Doctrine Grounding
    for role_key, role_doctrine in ROLE_DOCTRINES.items():
        if role_key.lower() in lower_text:
            grounding_blocks.append(role_doctrine)

    # If Capsuleer stated their ship and is waiting/preparing to select a ping
    if piloted_ship_name and not detected_hulls and ("ping" in lower_text or "select" in lower_text or "waiting" in lower_text or "counter" in lower_text):
        grounding_blocks.append(
            f"[TACTICAL STAGING & PILOT READINESS — {piloted_ship_name.upper()}]:\n"
            f"• Capsuleer Status: Ready in {piloted_ship_name}; awaiting specific hostile target ping/vector.\n"
            f"• Tactical Directive: Acknowledge {piloted_ship_name} combat posture (pre-heat webifier/tackle racks, verify nanite paste and ammo loadout, align to safe perch / hold cloak). Prompt capsuleer to select or transmit the hostile contact to calculate range, transversal, and damage countermeasures."
        )

    # Check for explicit NO VISUAL (NV) with pilot name vs pure system clear
    has_nv_term = bool(re.search(r"\b(nv|na|no\s*visual)\b", lower_text))
    has_clear_term = bool(re.search(r"\b(clear|clr|clean|safe|nil|none)\b", lower_text))
    
    if has_nv_term and ("pilot" in lower_text or "unlocated" in lower_text or "target in system" in lower_text or "hostile" in lower_text):
        grounding_blocks.append(
            "[INTEL STATUS — HOSTILE IN LOCAL (NO VISUAL / NV)]:\n"
            "• Status: Hostile pilot is confirmed in local chat but has NO VISUAL (NV) on gates or D-Scan yet (possibly cloaked, at a safe spot, or docked).\n"
            "• Tactical Directive: Do NOT warp to open gates or sites blind. Align out, perform 360° 14.3 AU D-Scan across celestial clusters, watch for combat scanning probes, and prepare defensive tackle."
        )
    elif (has_clear_term or has_nv_term) and not detected_hulls and not piloted_ship_name and ("reported clear" in lower_text or "0 vessels" in lower_text or "zero" in lower_text):
        return (
            "[INTEL STATUS — NO VISUAL / SYSTEM CLEAR]:\n"
            "• Status: Solar system is reported NO VISUAL (NV) or CLEAR. Zero hostile combat vessels, bubbles, or cynos logged on grid.\n"
            "• Tactical Directive: Confirm local space is clear. Advise standard scouting vigilance (monitor local chat list and periodic 14.3 AU D-Scan for incoming hostiles).\n\n"
            f"{EVE_COMBAT_AXIOMS}"
        )

    # 1. Cynosural / Force Recon / Hotdrop Hazard Grounding
    if any(k in lower_text for k in ["cyno", "hotdrop", "arazu", "falcon", "pilgrim", "rapier", "black ops", "blops"]):
        grounding_blocks.append(
            "[TACTICAL INTEL AXIOM — COVERT CYNO & RECON AMBUSH]:\n"
            "• Hazard: A Force Recon (Arazu/Falcon/Rapier/Pilgrim) indicates an active Covert Cyno / Hot-Drop trap. Black Ops or Dreadnoughts may jump in immediately.\n"
            "• Falcon Threat: 100km+ ECM Jamming breaks locks completely. Counter: Drone auto-attack, rapid lock/destroy paper tank, or damp range.\n"
            "• Arazu Threat: 40km+ Long Point/Scram prevents warp. Counter: Overheat MWD away immediately; neut capacitor dry.\n"
            "• Tactical Directive: Do NOT warp to gate. Align out to celestial/citadel, burn away from cyno beacon, and warp immediately if unpointed."
        )

    # 2. Interdictor / Warp Bubble Gatecamp Grounding
    if any(k in lower_text for k in ["bubble", "bubbled", "sabre", "dictor", "hic", "hictor", "interdictor", "gate camp", "camp"]):
        grounding_blocks.append(
            "[TACTICAL INTEL AXIOM — WARP BUBBLE & GATE CAMP EVASION]:\n"
            "• Hazard: 20km Warp Disruption Bubble deployed on gate/grid. Warp drives disabled while inside bubble.\n"
            "• Gate Jump Evasion: Hold gate cloak (up to 60s). Identify safe celestial 180° away from campers, overheat MWD/cloak (MWD-Cloak trick), and burn out of bubble edge.\n"
            "• Fleet Engagement: Focus fire primary Interdictor (Sabre/Flycatcher) instantly to stop chain bubbling."
        )

    # 3. Marauder Bastion Grounding
    if any(k in lower_text for k in ["vargur", "paladin", "kronos", "golem", "marauder", "bastion"]):
        grounding_blocks.append(
            "[TACTICAL INTEL AXIOM — MARAUDER BASTION ENGAGEMENT]:\n"
            "• Bastion Mechanics: Marauder has 100% active rep bonus and EWAR immunity, but 0 sub-warp speed for 60s.\n"
            "• Tactical Counter: Drain capacitor with Heavy Neutralizers (active tank collapses instantly without cap). Maintain high transversal velocity outside turret tracking."
        )

    # 4. Capital Dreadnought Grounding
    if any(k in lower_text for k in ["naglfar", "moros", "revelation", "phoenix", "zirnitra", "dread", "dreadnought"]):
        grounding_blocks.append(
            "[TACTICAL INTEL AXIOM — CAPITAL DREADNOUGHT ENGAGEMENT]:\n"
            "• Hazard: Capital Dreadnought possesses massive alpha strike / DPS in Siege Mode (immobile at 0 m/s for 5 min, immune to ECM/remote repairs).\n"
            "• Sub-Capital Survival Counter: Orbit at high angular transversal velocity (capital turrets cannot track fast cruisers/frigates at orbiting ranges) and apply Tracking Disruptors (Tracking Speed script).\n"
            "• Tackle: Warp Scrambler (range <=10km, disables MWD/MJD) or Warp Disruptor (range <=30km). Never fly in a direct low-transversal line toward or away from a Dreadnought."
        )

    # 5. Abyssal Deadspace Grounding
    if re.search(r"\b(abyssal|abyss|filament|tier\s*[1-6]\s*(?:gamma|dark|electrical|exotic|firestorm))\b", lower_text):
        grounding_blocks.append(
            "[ABYSSAL DEADSPACE WEATHER PENALTIES]:\n"
            "- Dark: -Turret Range, +Ship Speed (use missiles/drones like Gila/Cerberus).\n"
            "- Gamma: +Shield HP, -Explosive Resist.\n"
            "- Electrical: +Cap Recharge, -EM Resist.\n"
            "- Exotic: +Kinetic Resist, -Scan Resolution.\n"
            "- Firestorm: +Armor HP, -Thermal Resist.\n"
            "- Priority Targets: Starving Damavik/Leshak (neut), Ephialtes (tracking disruption), Drifter/Karen (alpha)."
        )

    if grounding_blocks:
        joined_dossiers = "\n\n".join(grounding_blocks[:8])
        return f"[Tactical Grounding Matrix]:\n{joined_dossiers}\n\n{EVE_COMBAT_AXIOMS}"
    
    default_summary = (
        "[GENERAL FLEET SCOUTING & COMBAT READINESS]:\n"
        "• Hostile Composition: Unspecified / General hostile elements reported.\n"
        "• Tactical Action: Maintain directional scan (14.3 AU at 360°), hold bookmark / gate perches, align out if uncloaked, and prepare defensive tackle or warp-out vectors."
    )
    return f"{default_summary}\n\n{EVE_COMBAT_AXIOMS}"
