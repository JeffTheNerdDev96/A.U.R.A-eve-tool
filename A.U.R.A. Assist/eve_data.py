"""
EVE Online Tactical Database, Comprehensive Combat Matrix & Domain Grounding Engine.
Customized for A.U.R.A. (Adaptive Underworld Recon Array) — ver.0.1.1phi & Core.
Contains encyclopedic vessel dossiers, weapon tracking mathematics, capacitor warfare,
abyssal deadspace environmental hazards, and electronic warfare matrices.
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

SHIP_DATABASE: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. PIRATE & FACTION VESSELS
    # =========================================================================
    # --- Angel Cartel (Fast Projectile / Warp Speed) ---
    "Dramiel": {"class": "Frigate", "faction": "Angel Cartel", "role": "Pirate Interceptor / Tackler", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme (4.5-5.5 km/s MWD)", "optimal_range": "0-12 km (Autocannons)", "tactics": "Extreme warp speed and agility. Fly with high transversal against larger guns. Vulnerable to dual webs and scramblers."},
    "Cynabal": {"class": "Cruiser", "faction": "Angel Cartel", "role": "Nano Skirmisher / Fleet Cruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme (2.2-3.0 km/s MWD)", "optimal_range": "15-28 km (425mm Autocannons / Barrage)", "tactics": "Premier nano kiter. Fast align and warp acceleration. Keep range 20-25 km, kite away from scrams/webs, apply tracking-disruptive transversal against heavy turrets."},
    "Machariel": {"class": "Battleship", "faction": "Angel Cartel", "role": "Fast Battleship / Fleet Anchor", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Armor", "speed": "Very Fast (1.5-2.0 km/s MWD)", "optimal_range": "15-40 km (800mm AC) or 70-130 km (1400mm Artillery)", "tactics": "Cruiser-like sub-warp agility. Immense alpha with Artillery or heavy mobile DPS with Autocannons. Retain transversal against dreads."},
    "Mekubal": {"class": "Destroyer", "faction": "Angel Cartel", "role": "Pirate Destroyer / Frigate Hunter", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Extreme (3.8-4.5 km/s)", "optimal_range": "8-20 km (Autocannons)", "tactics": "High-speed destroyer with extreme projectile alpha. Shreds frigates and light tackle before they close range."},
    "Khizriel": {"class": "Battlecruiser", "faction": "Angel Cartel", "role": "Heavy Skirmish Battlecruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast (1.8-2.4 km/s)", "optimal_range": "20-50 km", "tactics": "Heavy projectile alpha with high mobility. Fast align and warp speed allow repositioning across grid effortlessly."},
    "Azariel": {"class": "Titan", "faction": "Angel Cartel", "role": "Pirate Supercapital Titan", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Fast for Titan", "optimal_range": "Omni Capital Range", "tactics": "Angel Cartel supercapital with devastating projectile alpha strike and Titan doomsday weapon."},

    # --- Guristas (Shield / Drone / Kinetic-Thermal Missiles) ---
    "Worm": {"class": "Frigate", "faction": "Guristas", "role": "Heavy Drone / Missile Frigate", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Passive (300% Drone Bonus)", "speed": "Moderate", "optimal_range": "0-40 km", "tactics": "Extreme drone HP and damage (1 drone deals damage of 4). Kill drones or kite outside lock range."},
    "Gila": {"class": "Cruiser", "faction": "Guristas", "role": "Drone / Missile Combat Cruiser", "threat": THREAT_PIRATE, "tank": "Passive / Active Shield (500% Drone Bonus)", "speed": "Moderate (1.6-2.0 km/s)", "optimal_range": "0-60 km", "tactics": "Abyssal king. 2 Medium drones deliver damage and HP of 10. Heavy shield buffer. Counter by destroying drones or heavy cap neuts."},
    "Rattlesnake": {"class": "Battleship", "faction": "Guristas", "role": "Heavy Drone / Cruise Battleship", "threat": THREAT_PIRATE, "tank": "Passive / Active Shield", "speed": "Slow", "optimal_range": "20-80 km", "tactics": "Massive passive shield recharge and heavy drone DPS. Cap neuts have low impact on passive shield regen."},
    "Mamba": {"class": "Destroyer", "faction": "Guristas", "role": "Pirate Missile Destroyer", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "20-45 km", "tactics": "Fast missile and light drone destroyer with strong shield tank."},
    "Alligator": {"class": "Battlecruiser", "faction": "Guristas", "role": "Heavy Drone / Missile Battlecruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "30-70 km", "tactics": "Heavy drone and heavy assault missile platform with massive shield reserves."},
    "Komodo": {"class": "Titan", "faction": "Guristas", "role": "Guristas Supercapital Titan", "threat": THREAT_SUPER, "tank": "Shield Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Guristas pirate supercapital Titan with extreme missile burst and supercapital drones."},

    # --- Blood Raiders (Armor / Energy Neut / NOS / Web) ---
    "Cruor": {"class": "Frigate", "faction": "Blood Raiders", "role": "Web / NOS Frigate", "threat": THREAT_ECM, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Heavy webs and NOS that drains cap even when ship cap is full. Keep distance outside 15 km."},
    "Ashimmu": {"class": "Cruiser", "faction": "Blood Raiders", "role": "Heavy Web / NOS Cruiser", "threat": THREAT_ECM, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-25 km", "tactics": "90% webs and severe energy neut drain. Eliminates enemy capacitor in seconds."},
    "Bhaalgorn": {"class": "Battleship", "faction": "Blood Raiders", "role": "Fleet Cap Drain / Heavy Web", "threat": THREAT_ECM, "tank": "Armor", "speed": "Slow", "optimal_range": "0-40 km", "tactics": "Fleet flagship neut. Heavy energy neutralizers drain 3000+ GJ per cycle at up to 40 km."},
    "Molok": {"class": "Titan", "faction": "Blood Raiders", "role": "Blood Raider Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Blood Raider pirate supercapital Titan with massive neut drain."},

    # --- Serpentis (Armor / 90% Stasis Web / Blaster) ---
    "Daredevil": {"class": "Frigate", "faction": "Serpentis", "role": "90% Web Blaster Frigate", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "0-8 km", "tactics": "90% stasis web stops targets dead. Massive close-range blaster DPS. Do not let it close inside 10km."},
    "Vigilant": {"class": "Cruiser", "faction": "Serpentis", "role": "90% Web Blaster Cruiser", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "90% webifier with 1000+ DPS medium blasters. Overheat propulsion and stay outside 18 km."},
    "Vindicator": {"class": "Battleship", "faction": "Serpentis", "role": "90% Web Blaster Battleship", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-20 km", "tactics": "2000+ DPS close range. Webifier locks targets down for massive neutron blaster application."},
    "Vanquisher": {"class": "Titan", "faction": "Serpentis", "role": "Serpentis Supercapital", "threat": THREAT_SUPER, "tank": "Armor Buffer", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Serpentis pirate supercapital Titan with 90% web and blaster power."},

    # --- Sansha's Nation (Shield / Afterburner / Laser) ---
    "Succubus": {"class": "Frigate", "faction": "Sansha's Nation", "role": "AB Speed Laser Frigate", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme AB (2.5+ km/s)", "optimal_range": "0-15 km", "tactics": "Huge Afterburner speed bonus (immune to warp scrambler MWD shutoff). High transversal pulse lasers."},
    "Phantasm": {"class": "Cruiser", "faction": "Sansha's Nation", "role": "100MN AB Laser Cruiser", "threat": THREAT_PIRATE, "tank": "Shield Buffer / Active", "speed": "Extreme AB (2.0+ km/s)", "optimal_range": "15-35 km", "tactics": "Runs 100MN Afterburner with cruiser-grade agility. Unscrammable speed tank. Hit with tracking disruptors or heavy webs."},
    "Nightmare": {"class": "Battleship", "faction": "Sansha's Nation", "role": "Fast Laser Battleship", "threat": THREAT_PIRATE, "tank": "Shield Buffer", "speed": "Fast AB (1.5+ km/s)", "optimal_range": "30-80 km", "tactics": "High-mobility beam/pulse laser battleship. Applies instant EM/Thermal damage with large energy turrets."},

    # --- Sisters of EVE (Armor / Cloak / Drone / Exploration) ---
    "Astero": {"class": "Frigate", "faction": "Sisters of EVE", "role": "Covert Ops / Drone Scout", "threat": THREAT_PIRATE, "tank": "Armor Buffer / Dual Rep", "speed": "Fast", "optimal_range": "0-15 km", "tactics": "Covert cloaking exploration frigate with vicious light drone combat capability. Often dual-repaired."},
    "Stratios": {"class": "Cruiser", "faction": "Sisters of EVE", "role": "Covert Ops / Drone Brawler", "threat": THREAT_PIRATE, "tank": "Armor Buffer / Dual Rep", "speed": "Moderate", "optimal_range": "0-30 km", "tactics": "Covert cloaking cruiser. Can fit covert cyno, heavy neuts, and full flight of heavy/sentry drones."},
    "Nestor": {"class": "Battleship", "faction": "Sisters of EVE", "role": "Remote Rep / Wormhole Core", "threat": THREAT_PIRATE, "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-20 km", "tactics": "Sub-capital remote armor repair flagship. Very low mass allows mass-efficient wormhole transit."},

    # --- Mordu's Legion (Point / Web Range / Rapid Light Missiles) ---
    "Garmur": {"class": "Frigate", "faction": "Mordu's Legion", "role": "Long-Range Point Kiter", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme (5.0+ km/s)", "optimal_range": "30-40 km", "tactics": "Projects 35+ km warp disruptor point at extreme speed. Counter with sensor dampeners, rapid light missiles, or light combat drones."},
    "Orthrus": {"class": "Cruiser", "faction": "Mordu's Legion", "role": "Long-Range Point & Web Kiter", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Extreme (3.0+ km/s)", "optimal_range": "35-50 km", "tactics": "45+ km point and 25 km web range with rapid light missiles. Counter with heavy projection snipers or long-range dampeners."},
    "Barghest": {"class": "Battleship", "faction": "Mordu's Legion", "role": "Heavy Point / Cruise Battleship", "threat": THREAT_PIRATE, "tank": "Shield", "speed": "Fast", "optimal_range": "50-100 km", "tactics": "Extreme missile velocity and 60+ km point range. High alpha cruise missiles."},

    # --- Triglavian Collective (Spooling Disintegrator / Armor Remote Rep) ---
    "Damavik": {"class": "Frigate", "faction": "Triglavian", "role": "Spooling Disintegrator Frigate", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast", "optimal_range": "5-18 km", "tactics": "Entropic disintegrator damage ramps up continuously over time. Break lock or kill quickly before spool reaches maximum."},
    "Vedmak": {"class": "Cruiser", "faction": "Triglavian", "role": "Spooling Disintegrator Cruiser", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Fast (2.2-2.8 km/s)", "optimal_range": "10-35 km", "tactics": "High sub-warp speed with continuous spooling thermal/explosive damage. Disengage if fight extends past 60 seconds."},
    "Drekavac": {"class": "Battlecruiser", "faction": "Triglavian", "role": "Heavy Disintegrator / Armor Links", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "15-45 km", "tactics": "Heavy armor tank and massive max-spool disintegrator DPS."},
    "Leshak": {"class": "Battleship", "faction": "Triglavian", "role": "Capital / Structure Buster", "threat": THREAT_PIRATE, "tank": "Armor", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Spools to over 3500 DPS. Lethal to capitals, POS structures, and stationary targets."},
    "Ikitursa": {"class": "Heavy Assault Cruiser", "faction": "Triglavian", "role": "HAC Disintegrator Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor", "speed": "Fast", "optimal_range": "10-35 km", "tactics": "T2 assault damage controls and huge spooling DPS make it formidable in small gang engagements."},

    # =========================================================================
    # 2. T2 COMBAT SPECIALISTS & FLEET CORES
    # =========================================================================
    # --- Heavy Assault Cruisers (HAC) ---
    "Cerberus": {"class": "Heavy Assault Cruiser", "faction": "Caldari", "role": "Missile Fleet Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer", "speed": "Fast (2.0 km/s)", "optimal_range": "60-110 km", "tactics": "Heavy assault missile or heavy missile fleet platform with ADC. Counter with close brawling inside minimum range."},
    "Eagle": {"class": "Heavy Assault Cruiser", "faction": "Caldari", "role": "Railgun Fleet Sniper", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "50-120 km", "tactics": "Extreme railgun range and optimal bonuses. Shield buffer and ADC. Vulnerable to fast high-transversal tackle."},
    "Muninn": {"class": "Heavy Assault Cruiser", "faction": "Minmatar", "role": "Missile / Skirmish Cruiser", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer", "speed": "Fast (2.2 km/s)", "optimal_range": "40-80 km", "tactics": "High-mobility missile HAC with strong kinetic/explosive damage."},
    "Vagabond": {"class": "Heavy Assault Cruiser", "faction": "Minmatar", "role": "Nano Autocannon Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual ASB)", "speed": "Extreme (3.0+ km/s)", "optimal_range": "0-25 km", "tactics": "High speed and fast falloff projectile brawler. Scram and web to neutralize speed tank."},
    "Ishtar": {"class": "Heavy Assault Cruiser", "faction": "Gallente", "role": "Heavy Sentry / Drone Cruiser", "threat": THREAT_T2_COMBAT, "tank": "Shield Buffer / Armor", "speed": "Moderate", "optimal_range": "0-80 km", "tactics": "Heavy drone / sentry combat cruiser. Signature radius reduction makes it hard to hit with heavy guns."},
    "Deimos": {"class": "Heavy Assault Cruiser", "faction": "Gallente", "role": "Active Armor Blaster Brawler", "threat": THREAT_T2_COMBAT, "tank": "Active Armor (Dual Rep)", "speed": "Fast", "optimal_range": "0-10 km", "tactics": "Monster active armor rep with ADC. Extreme close-range blaster DPS. Counter with heavy neuts."},
    "Zealot": {"class": "Heavy Assault Cruiser", "faction": "Amarr", "role": "Beam / Pulse Laser Sniper", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "30-80 km", "tactics": "Armor fleet laser sniper with high EM/Thermal alpha."},
    "Sacrilege": {"class": "Heavy Assault Cruiser", "faction": "Amarr", "role": "Heavy Missile / Armor Brawler", "threat": THREAT_T2_COMBAT, "tank": "Armor Buffer / Active", "speed": "Moderate", "optimal_range": "15-40 km", "tactics": "Exceptional armor resistances and heavy assault missile firepower with neuts."},

    # --- Interdictors & Heavy Interdictors (Bubbles) ---
    "Sabre": {"class": "Interdictor", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Fast (3.5+ km/s)", "optimal_range": "0-12 km (Autocannons)", "tactics": "Launches 20km warp disruption probes (bubbles). Primary tackle priority in fleets. Target and destroy immediately before bubble deployment."},
    "Flycatcher": {"class": "Interdictor", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Rocket/Missile interdictor with strong shield buffer."},
    "Heretic": {"class": "Interdictor", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-15 km", "tactics": "Armor-buffered interdictor with rocket/missile DPS."},
    "Eris": {"class": "Interdictor", "role": "Warp Disruption Bubble", "threat": THREAT_BUBBLE, "tank": "Armor/Hull Buffer", "speed": "Fast", "optimal_range": "0-8 km", "tactics": "Blaster hull-tanked interdictor with high close-range DPS."},
    "Broadsword": {"class": "Heavy Interdiction Cruiser", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate (500MN HIC viable)", "optimal_range": "0-35 km", "tactics": "Warp Disruption Field Generator projects focused point (scrams supercapitals) or 20km bubble."},
    "Devoter": {"class": "Heavy Interdiction Cruiser", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "Heavy armor tanked HIC with infinite tackle point."},
    "Phobos": {"class": "Heavy Interdiction Cruiser", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "Blaster armor HIC with infinite tackle point."},
    "Onyx": {"class": "Heavy Interdiction Cruiser", "role": "Infinite Point / Bubble", "threat": THREAT_BUBBLE, "tank": "Shield Buffer", "speed": "Moderate", "optimal_range": "0-35 km", "tactics": "Heavy shield missile HIC."},

    # --- Recons (Covert Cyno & D-Scan Immunity) ---
    "Arazu": {"class": "Force Recon", "role": "Covert Cyno / Long Point", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Moderate", "optimal_range": "35-50 km point", "tactics": "Can cloak and light Covert Cynos for Black Ops hotdrops. Projects 40+ km point. High bait hazard."},
    "Falcon": {"class": "Force Recon", "role": "Covert Cyno / Jammer", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Moderate", "optimal_range": "50-80 km ECM", "tactics": "Cloaked ECM jammer. Breaks target locks completely. Primary EWAR threat; lock and destroy or neut out."},
    "Pilgrim": {"class": "Force Recon", "role": "Covert Cyno / Neut", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Moderate", "optimal_range": "0-25 km Neut", "tactics": "Cloaked heavy energy neutralizer and drone boat."},
    "Rapier": {"class": "Force Recon", "role": "Covert Cyno / Long Web", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Moderate", "optimal_range": "30-50 km Web", "tactics": "Cloaked long-range stasis webifier (40-60 km). Shuts down kite ships."},
    "Curse": {"class": "Combat Recon", "role": "Cap Drain / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield/Armor", "speed": "Moderate", "optimal_range": "40-60 km Neut", "tactics": "IMMUNE TO D-SCAN. Heavy energy neutralizer and tracking disruptor."},
    "Lachesis": {"class": "Combat Recon", "role": "Long Point / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield/Armor", "speed": "Moderate", "optimal_range": "50-70 km Point", "tactics": "IMMUNE TO D-SCAN. Extreme range warp disruptor point (60+ km)."},
    "Rook": {"class": "Combat Recon", "role": "ECM Jammer / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield", "speed": "Moderate", "optimal_range": "50-80 km Jam", "tactics": "IMMUNE TO D-SCAN. Heavy missile and ECM jammer."},
    "Huginn": {"class": "Combat Recon", "role": "Long Web & Paint / D-Scan Immune", "threat": THREAT_ECM, "tank": "Shield", "speed": "Moderate", "optimal_range": "40-60 km Web", "tactics": "IMMUNE TO D-SCAN. Extreme range webifier and target painter."},

    # --- Marauders (Bastion Mode) ---
    "Vargur": {"class": "Marauder", "role": "Bastion Autocannon/Artillery DPS", "threat": THREAT_MARAUDER, "tank": "Active Shield (2000+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "0-45 km Autocannon / 100+ km Art", "tactics": "BASTION MODE: 100% rep bonus, immune to EWAR (neuts still apply), 0 sub-warp speed for 60s. Heavy tracking bonus. Counter with neuts, extreme transversal, or fleet focus fire."},
    "Paladin": {"class": "Marauder", "role": "Bastion Pulse/Beam Laser DPS", "threat": THREAT_MARAUDER, "tank": "Active Armor (2500+ HP/s)", "speed": "Immobile in Bastion", "optimal_range": "30-100 km", "tactics": "Extreme laser projection. Neuts drain capacitor rapidly due to heavy laser cap use."},
    "Kronos": {"class": "Marauder", "role": "Bastion Blaster/Railgun DPS", "threat": THREAT_MARAUDER, "tank": "Active Armor", "speed": "Immobile in Bastion", "optimal_range": "0-15 km Blaster (2000+ DPS)", "tactics": "Deadly close-range blaster DPS. Stay outside 20km or neutralize capacitor."},
    "Golem": {"class": "Marauder", "role": "Bastion Torpedo/Cruise DPS", "threat": THREAT_MARAUDER, "tank": "Active Shield", "speed": "Immobile in Bastion", "optimal_range": "30-120 km", "tactics": "Target painter bonus applies massive torpedo damage. Fast small-sig ships mitigate missile damage."},

    # --- Strategic Cruisers (T3C) ---
    "Loki": {"class": "Strategic Cruiser", "role": "Web / Heavy Projectile / Cloaky", "threat": THREAT_CYNO, "tank": "Shield/Armor Buffer", "speed": "Fast (2.0-2.8 km/s)", "optimal_range": "15-40 km", "tactics": "Extreme versatility. Often fitted with 40km 90% webs, covert cloak, nullification, or heavy autocannon/artillery/missile DPS."},
    "Tengu": {"class": "Strategic Cruiser", "role": "Missile Sniper / ECM / Nullified", "threat": THREAT_CYNO, "tank": "Shield Buffer", "speed": "Fast", "optimal_range": "40-90 km", "tactics": "Heavy missile sniper or covert scout."},
    "Proteus": {"class": "Strategic Cruiser", "role": "Heavy Scram / Blaster DPS", "threat": THREAT_CYNO, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "0-10 km", "tactics": "Cloaky heavy blaster brawler with extended scram range."},
    "Legion": {"class": "Strategic Cruiser", "role": "Neut / Laser DPS / Heavy Tank", "threat": THREAT_CYNO, "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "15-50 km", "tactics": "Heavy armor buffer, pulse/beam lasers, or extreme energy neuts."},

    # --- Tactical Destroyers (T3D) ---
    "Hecate": {"class": "Tactical Destroyer", "role": "Mode Switching Blaster DPS", "threat": "FAST TACKLE/DPS", "tank": "Armor/Hull", "speed": "Extreme", "optimal_range": "0-8 km", "tactics": "1000+ DPS blaster destroyer. Switches between Propulsion, Defense, and Sharpshooter modes instantly."},
    "Jackdaw": {"class": "Tactical Destroyer", "role": "Mode Switching Missile Sniper", "threat": "FAST TACKLE/DPS", "tank": "Shield", "speed": "Extreme", "optimal_range": "30-70 km", "tactics": "Extreme range rocket/light missile platform with defense mode tank."},
    "Confessor": {"class": "Tactical Destroyer", "role": "Mode Switching Laser Sniper", "threat": "FAST TACKLE/DPS", "tank": "Armor", "speed": "Extreme", "optimal_range": "15-45 km", "tactics": "Mode-switching beam/pulse laser destroyer."},
    "Svipul": {"class": "Tactical Destroyer", "role": "Mode Switching Projectile", "threat": "FAST TACKLE/DPS", "tank": "Shield/Armor", "speed": "Extreme", "optimal_range": "10-30 km", "tactics": "High-mobility autocannon/artillery destroyer."},

    # --- Stealth Bombers & Covert Ops ---
    "Hound": {"class": "Stealth Bomber", "faction": "Minmatar", "role": "Covert Torpedo Bomber / Bomb Launcher", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Launches explosive bombs or high-alpha torpedoes from cloak. Align and warp out immediately after decloaking."},
    "Manticore": {"class": "Stealth Bomber", "faction": "Caldari", "role": "Covert Torpedo Bomber / Bomb Launcher", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Kinetic torpedoes and bombs from stealth."},
    "Nemesis": {"class": "Stealth Bomber", "faction": "Gallente", "role": "Covert Torpedo Bomber / Bomb Launcher", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "Thermal torpedoes and bombs from stealth."},
    "Purifier": {"class": "Stealth Bomber", "faction": "Amarr", "role": "Covert Torpedo Bomber / Bomb Launcher", "threat": "HIGH ALPHA / BOMBER", "tank": "Paper Thin", "speed": "Cloaked", "optimal_range": "30-60 km", "tactics": "EM torpedoes and bombs from stealth."},

    # --- Command Ships & Battlecruisers ---
    "Sleipnir": {"class": "Command Ship", "faction": "Minmatar", "role": "Shield Skirmish Booster / Autocannon DPS", "threat": THREAT_T2_COMBAT, "tank": "Active Shield (Dual ASB)", "speed": "Fast", "optimal_range": "10-35 km", "tactics": "Monster active shield booster with heavy autocannon damage and fleet shield boosts."},
    "Drake": {"class": "Battlecruiser", "faction": "Caldari", "role": "Heavy Missile Buffer", "threat": "COMBATANT", "tank": "Passive / Buffer Shield", "speed": "Slow", "optimal_range": "40-80 km", "tactics": "Iconic shield brick battlecruiser with kinetic heavy missile bonuses."},
    "Hurricane": {"class": "Battlecruiser", "faction": "Minmatar", "role": "Heavy Projectile Battlecruiser", "threat": "COMBATANT", "tank": "Shield / Armor Buffer", "speed": "Fast for BC", "optimal_range": "15-40 km AC / 70+ km Art", "tactics": "Versatile projectile platform with high alpha strike."},
    "Brutix": {"class": "Battlecruiser", "faction": "Gallente", "role": "Blaster Brawler", "threat": "COMBATANT", "tank": "Active / Buffer Armor", "speed": "Moderate", "optimal_range": "0-12 km", "tactics": "Devastating close-range blaster DPS with armor repair bonus."},
    "Harbinger": {"class": "Battlecruiser", "faction": "Amarr", "role": "Medium Laser Battlecruiser", "threat": "COMBATANT", "tank": "Armor Buffer", "speed": "Moderate", "optimal_range": "20-60 km", "tactics": "Heavy pulse/beam laser firepower with strong armor buffer."},

    # --- Empire Battleships ---
    "Raven": {"class": "Battleship", "faction": "Caldari", "role": "Cruise / Torpedo Battleship", "threat": "HEAVY COMBATANT", "tank": "Shield Buffer / Active", "speed": "Slow", "optimal_range": "40-120 km", "tactics": "Long-range cruise missile or torpedo battleship."},
    "Rokh": {"class": "Battleship", "faction": "Caldari", "role": "Railgun Fleet Sniper", "threat": "HEAVY COMBATANT", "tank": "Shield Buffer", "speed": "Very Slow", "optimal_range": "80-180 km", "tactics": "Massive railgun optimal range and shield resistances."},
    "Megathron": {"class": "Battleship", "faction": "Gallente", "role": "Blaster / Railgun Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-20 km Blaster / 60+ km Rail", "tactics": "Heavy hybrid turret tracking bonus."},
    "Dominix": {"class": "Battleship", "faction": "Gallente", "role": "Drone / Neut Battleship", "threat": "HEAVY COMBATANT", "tank": "Dual Armor Rep / Buffer", "speed": "Slow", "optimal_range": "0-70 km", "tactics": "Heavy drone projection and heavy energy neutralizers."},
    "Tempest": {"class": "Battleship", "faction": "Minmatar", "role": "Artillery / AC Battleship", "threat": "HEAVY COMBATANT", "tank": "Shield / Armor", "speed": "Fast for BS", "optimal_range": "20-40 km AC / 100+ km Art", "tactics": "High-speed projectile battleship with massive alpha."},
    "Typhoon": {"class": "Battleship", "faction": "Minmatar", "role": "Missile / Cruise Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor / Shield", "speed": "Fast for BS", "optimal_range": "30-90 km", "tactics": "Rapid heavy missile / torpedo platform with versatile slot layout."},
    "Abaddon": {"class": "Battleship", "faction": "Amarr", "role": "Heavy Laser Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Brick Buffer", "speed": "Slow", "optimal_range": "30-90 km", "tactics": "Extremely heavy armor resistance bonus; cap intensive lasers."},
    "Apocalypse": {"class": "Battleship", "faction": "Amarr", "role": "Laser Sniper Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "60-140 km", "tactics": "Optimal range bonus allows beam lasers to strike beyond 100km effortlessly."},
    "Apocalypse Navy Issue": {"class": "Faction Battleship", "faction": "Amarr (Navy)", "role": "Heavy Laser Line / Combat Battleship", "threat": "HEAVY COMBATANT", "tank": "Heavy Armor Buffer (1600mm Plates) / Dual Rep", "speed": "Slow (MWD/MJD)", "optimal_range": "30-100 km (Mega Pulse / Scorch)", "tactics": "Exceptional energy turret tracking speed bonus and optimal range. For Fleet Line Combat: anchor with remote armor logistics, max buffer, and long-range Scorch projection (no solo tackle). For Solo PvP Roaming: fit Heavy Cap Booster 800/3200, Warp Scrambler + Heavy Web or Warp Disruptor, and MJD."},
    "Armageddon Navy Issue": {"class": "Faction Battleship", "faction": "Amarr (Navy)", "role": "Laser / Heavy Drone Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "20-70 km", "tactics": "Heavy laser rate of fire and drone hitpoint bonus."},
    "Megathron Navy Issue": {"class": "Faction Battleship", "faction": "Gallente (Navy)", "role": "Heavy Blaster / Rail Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-30 km", "tactics": "Massive hybrid damage and tracking speed bonuses."},
    "Dominix Navy Issue": {"class": "Faction Battleship", "faction": "Gallente (Navy)", "role": "Hybrid / Drone Fleet Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor Buffer", "speed": "Slow", "optimal_range": "0-60 km", "tactics": "Heavy railgun/blaster damage alongside combat drones."},
    "Raven Navy Issue": {"class": "Faction Battleship", "faction": "Caldari (Navy)", "role": "Cruise / Torpedo Battleship", "threat": "HEAVY COMBATANT", "tank": "Shield Buffer", "speed": "Slow", "optimal_range": "40-140 km", "tactics": "8 launcher missile salvo with explosion radius and velocity bonuses."},
    "Tempest Fleet Issue": {"class": "Faction Battleship", "faction": "Minmatar (Fleet)", "role": "Artillery / AC High Alpha Battleship", "threat": "HEAVY COMBATANT", "tank": "Shield/Armor Buffer", "speed": "Fast for BS", "optimal_range": "25-50 km AC / 100+ km Art", "tactics": "Extreme projectile rate of fire and devastating alpha strike."},
    "Typhoon Fleet Issue": {"class": "Faction Battleship", "faction": "Minmatar (Fleet)", "role": "Missile / Cruise Fleet Battleship", "threat": "HEAVY COMBATANT", "tank": "Armor/Shield Buffer", "speed": "Fast for BS", "optimal_range": "30-100 km", "tactics": "Versatile missile and projectile platform with high armor buffer."},

    # --- Black Ops Battleships ---
    "Redeemer": {"class": "Black Ops", "role": "Covert Bridge / Laser DPS", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Jump Drive", "optimal_range": "20-60 km", "tactics": "Covert jump bridge conduit and heavy pulse laser DPS."},
    "Panther": {"class": "Black Ops", "role": "Covert Bridge / Projectile DPS", "threat": THREAT_CYNO, "tank": "Shield/Armor", "speed": "Jump Drive", "optimal_range": "20-50 km", "tactics": "High-mobility projectile Black Ops battleship."},
    "Sin": {"class": "Black Ops", "role": "Covert Bridge / Drone & Neut DPS", "threat": THREAT_CYNO, "tank": "Armor", "speed": "Jump Drive", "optimal_range": "0-30 km", "tactics": "Heavy energy neutralizer and heavy drone combatant."},
    "Widow": {"class": "Black Ops", "role": "Covert Bridge / ECM Jammer", "threat": THREAT_CYNO, "tank": "Shield", "speed": "Jump Drive", "optimal_range": "40-80 km", "tactics": "Long-range ECM jammer and rapid missile battleship."},

    # =========================================================================
    # 3. CAPITAL & SUPERCAPITAL SHIPS
    # =========================================================================
    "Naglfar": {"class": "Dreadnought", "role": "Capital Projectile Siege", "threat": THREAT_CAPITAL, "tank": "Shield/Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "High alpha projectile dreadnought with Siege module."},
    "Moros": {"class": "Dreadnought", "role": "Capital Blaster/Rail Siege", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "0-40 km", "tactics": "Extreme capital blaster DPS in Siege mode."},
    "Revelation": {"class": "Dreadnought", "role": "Capital Laser Siege", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "30-80 km", "tactics": "Heavy laser siege dreadnought."},
    "Phoenix": {"class": "Dreadnought", "role": "Capital Missile Siege", "threat": THREAT_CAPITAL, "tank": "Shield", "speed": "Capital", "optimal_range": "50-150 km", "tactics": "Capital torpedo/cruise missile dreadnought."},
    "Zirnitra": {"class": "Dreadnought", "role": "Triglavian Ramp-Up Siege", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Continuous spooling capital disintegrator."},
    "Bane": {"class": "Lancer Dreadnought", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Projects lance weapon disabling warp and jump drives."},
    "Karura": {"class": "Lancer Dreadnought", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Shield", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Caldari disruptive capital lance."},
    "Hubris": {"class": "Lancer Dreadnought", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Armor", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Gallente disruptive capital lance."},
    "Valravn": {"class": "Lancer Dreadnought", "role": "Capital Disruptive Lance", "threat": THREAT_CAPITAL, "tank": "Shield", "speed": "Capital", "optimal_range": "Capital Grid", "tactics": "Minmatar disruptive capital lance."},
    "Ragnarok": {"class": "Titan", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Shield", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Minmatar supercapital Titan with Gjallarhorn Doomsday device."},
    "Avatar": {"class": "Titan", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Armor", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Amarr supercapital Titan with Judgement Doomsday device."},
    "Erebus": {"class": "Titan", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Armor", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Gallente supercapital Titan with Aurora Omniphage Doomsday device."},
    "Leviathan": {"class": "Titan", "role": "Fleet Doomsday / Supercapital", "threat": THREAT_SUPER, "tank": "Shield", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Caldari supercapital Titan with Oblivion Doomsday device."},
    "Hel": {"class": "Supercarrier", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Shield", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Minmatar shield supercarrier with heavy fighter wings."},
    "Nyx": {"class": "Supercarrier", "role": "Heavy Fighter Strike", "threat": THREAT_SUPER, "tank": "Armor", "speed": "Supercapital", "optimal_range": "Omni Grid", "tactics": "Gallente armor supercarrier with heavy fighter wings."}
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
    "titan": "Ragnarok"
}

EVE_COMBAT_AXIOMS = """
[EVE ONLINE COMBAT DOCTRINE & TACTICAL DIRECTIVES]:
1. BREVITY & COMPLETION: Keep tactical responses to 2 to 4 actionable, punchy bullet points. Always conclude your sentences cleanly.
2. NEVER ECHO REFERENCE HEADERS: Never repeat, quote, or output headers or tags (such as `[EVE TACTICAL INTELLIGENCE]`, `[TACTICAL DIRECTIVE]`).
3. RIGOROUS TACKLE & EWAR DEFINITIONS:
   - Warp Scrambler (Scram): Range <=10km (short point). Disables Microwarpdrive (MWD) & Micro Jump Drives (MJD).
   - Warp Disruptor (Long Point): Range <=30km (up to 45km+ on Recons). Disables warp only (target retains full MWD speed).
   - Tracking Disruptor: Scripts for Tracking Speed / Optimal Range applied to hostile turrets to make large guns miss high-transversal targets.
   - Stasis Webifier: Slows target velocity by 50-60% (up to 90% on Serpentis/Huginn/Loki).
   - Heavy Energy Neutralizer: Drains raw capacitor per cycle, shutting down active reps.
4. TACTICAL ENGAGEMENT: State Primary Threat/Target -> Engagement Range / Transversal -> Evasion / Warp Out vectors.
"""


def lookup_ship(name: str) -> Optional[Dict[str, Any]]:
    """Resolves any ship name or alias into a verified tactical ship dossier."""
    clean = name.strip()
    clean_lower = clean.lower()

    # Exclude common non-ship terms
    if clean_lower in ["cyno", "cynos", "cynou", "bubble", "gate", "outgate", "ingate", "station", "undock", "local", "spike"]:
        return None

    # Direct match
    for k, v in SHIP_DATABASE.items():
        if k.lower() == clean_lower:
            res = dict(v)
            res["canonical_name"] = k
            return res

    # Alias match
    if clean_lower in SHIP_ALIASES:
        canonical = SHIP_ALIASES[clean_lower]
        if canonical in SHIP_DATABASE:
            res = dict(SHIP_DATABASE[canonical])
            res["canonical_name"] = canonical
            return res

    return None


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
        "• Fitting Rules: Overheated 50MN/500MN Microwarpdrive, Warp Disruptor (long point 24-30km), long-range projection weapons (Artillery, Beam Lasers, Railguns, Heavy Missiles), Nanofiber Internal Structure, Polycarbon Engine rigs. Maintain distance >20km outside web range; avoid scrambler range at all costs."
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


def get_tactical_grounding(prompt: str, attachments: List[Dict[str, Any]] = None) -> str:
    """
    Extracts verified ship dossiers and tactical axioms for everything mentioned in the prompt.
    """
    full_text = prompt + " "
    if attachments:
        for att in attachments:
            full_text += att.get("text", "") + " "

    words = re.findall(r"\b[A-Za-z0-9\-]+\b", full_text)
    
    grounding_blocks = []
    detected_hulls = set()
    
    # Check for direct multi-word ship names first (e.g. "Apocalypse Navy Issue")
    for ship_name, s_info in SHIP_DATABASE.items():
        if ship_name.lower() in full_text.lower() and ship_name.lower() not in detected_hulls:
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
            if cname.lower() not in detected_hulls:
                detected_hulls.add(cname.lower())
                dossier = (
                    f"• {cname} ({s_info.get('class', 'Vessel')} - {s_info.get('faction', 'General')}) | Tank: {s_info.get('tank', 'Shield/Armor')} | "
                    f"Optimal: {s_info.get('optimal_range', 'Standard')} | Threat: {s_info.get('threat', 'Combatant')}\n"
                    f"  Tactics: {s_info.get('tactics', 'Engage according to weapon tracking and range.')}"
                )
                grounding_blocks.append(dossier)

    lower_text = full_text.lower()
    
    # Check for Role Doctrine Grounding
    for role_key, role_doctrine in ROLE_DOCTRINES.items():
        if role_key.lower() in lower_text:
            grounding_blocks.append(role_doctrine)

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

    # 5. Abyssal Deadspace Grounding (Strictly require explicit filament/abyssal keyword match)
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
    
    # If no specific hulls were recognized, inject the default Core Fleet Tactical Matrix
    default_summary = (
        "[EVE CORE COMBAT ROLES & SHIP COUNTERS]:\n"
        "• Interdictors (Sabre/Flycatcher): 20km warp disruption bubbles; primary fleet tackle threat.\n"
        "• Heavy Assault Cruisers (Cerberus/Muninn/Eagle/Ishtar/Vagabond): Assault Damage Control (ADC), high-resists and fleet projection.\n"
        "• Force Recons (Arazu/Falcon/Rapier/Pilgrim): Covert cloaking, 45km points/webs, ECM jammers, covert cyno hotdrops.\n"
        "• Marauders (Vargur/Paladin/Kronos/Golem): Bastion mode (100% rep bonus, EWAR immune, immobile for 60s); neut capacitor to kill.\n"
        "• Strategic Cruisers (Loki/Tengu/Proteus/Legion): T3C versatility, 40km 90% webs, covert cloak, or heavy neuts."
    )
    return f"{default_summary}\n\n{EVE_COMBAT_AXIOMS}"


