import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
# -*- coding: utf-8 -*-
"""
EVE Online Complete Module & Weapon Dataset Generator
Generates:
- training/t-data/eve_modules.json
- training/t-data/eve_modules.csv
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

from tools.build_all_eve_data import get_module_data

# Comprehensive dictionary of module family specifications with stats
# Missing / non-applicable stats are left None (blank in CSV)
MODULE_SPECS_DATABASE = {
    # --- Energy Turrets (Lasers) ---
    "Small Pulse Laser": {"slot": "High", "size": "Small", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 15, "pg": 8, "cap_cost": 4.5, "optimal": 4800, "falloff": 2400, "tracking": 0.350, "rof": 2.8, "damage_types": "EM / Thermal", "role": "Frigate close-range high tracking laser"},
    "Small Beam Laser": {"slot": "High", "size": "Small", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 22, "pg": 14, "cap_cost": 7.2, "optimal": 14500, "falloff": 3200, "tracking": 0.160, "rof": 4.2, "damage_types": "EM / Thermal", "role": "Frigate long-range sniper laser"},
    "Medium Pulse Laser": {"slot": "High", "size": "Medium", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 35, "pg": 125, "cap_cost": 18.0, "optimal": 12000, "falloff": 6500, "tracking": 0.125, "rof": 3.6, "damage_types": "EM / Thermal", "role": "Cruiser close-range heavy laser brawler"},
    "Medium Beam Laser": {"slot": "High", "size": "Medium", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 48, "pg": 195, "cap_cost": 28.5, "optimal": 34000, "falloff": 8500, "tracking": 0.055, "rof": 5.4, "damage_types": "EM / Thermal", "role": "Cruiser / Battlecruiser long-range beam sniper"},
    "Large Pulse Laser (Mega Pulse)": {"slot": "High", "size": "Large", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 65, "pg": 1850, "cap_cost": 95.0, "optimal": 24000, "falloff": 14000, "tracking": 0.038, "rof": 5.1, "damage_types": "EM / Thermal", "role": "Battleship heavy pulse brawler"},
    "Large Beam Laser (Tachyon / Mega Beam)": {"slot": "High", "size": "Large", "category": "Energy Turret", "meta": "Tech I / Tech II / Faction", "cpu": 88, "pg": 2950, "cap_cost": 155.0, "optimal": 78000, "falloff": 22000, "tracking": 0.016, "rof": 7.8, "damage_types": "EM / Thermal", "role": "Battleship extreme range sniper"},
    "Capital Energy Turret": {"slot": "High", "size": "Capital", "category": "Energy Turret", "meta": "Tech I / Faction", "cpu": 150, "pg": 185000, "cap_cost": 1450.0, "optimal": 65000, "falloff": 35000, "tracking": 0.0025, "rof": 12.0, "damage_types": "EM / Thermal", "role": "Dreadnought anti-capital energy siege weapon"},

    # --- Hybrid Turrets (Blasters & Railguns) ---
    "Small Blaster (Neutron / Electron / Ion)": {"slot": "High", "size": "Small", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 16, "pg": 9, "cap_cost": 1.8, "optimal": 2200, "falloff": 3800, "tracking": 0.420, "rof": 2.2, "damage_types": "Kinetic / Thermal", "role": "Frigate supreme close-range DPS"},
    "Small Railgun": {"slot": "High", "size": "Small", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 24, "pg": 12, "cap_cost": 2.8, "optimal": 16500, "falloff": 4800, "tracking": 0.145, "rof": 3.8, "damage_types": "Kinetic / Thermal", "role": "Frigate long-range rail sniper"},
    "Medium Blaster (Heavy Neutron / Electron)": {"slot": "High", "size": "Medium", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 36, "pg": 135, "cap_cost": 7.5, "optimal": 5500, "falloff": 9500, "tracking": 0.145, "rof": 3.0, "damage_types": "Kinetic / Thermal", "role": "Cruiser face-melting blaster DPS"},
    "Medium Railgun (250mm / 200mm)": {"slot": "High", "size": "Medium", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 46, "pg": 185, "cap_cost": 11.5, "optimal": 38000, "falloff": 12000, "tracking": 0.048, "rof": 4.8, "damage_types": "Kinetic / Thermal", "role": "Cruiser / Battlecruiser fleet rail sniper"},
    "Large Blaster (Neutron Blaster Cannon)": {"slot": "High", "size": "Large", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 68, "pg": 1950, "cap_cost": 38.0, "optimal": 11000, "falloff": 18000, "tracking": 0.042, "rof": 4.2, "damage_types": "Kinetic / Thermal", "role": "Battleship close-range thermal/kinetic brawler"},
    "Large Railgun (425mm / 350mm)": {"slot": "High", "size": "Large", "category": "Hybrid Turret", "meta": "Tech I / Tech II / Faction", "cpu": 82, "pg": 2750, "cap_cost": 55.0, "optimal": 85000, "falloff": 28000, "tracking": 0.014, "rof": 6.8, "damage_types": "Kinetic / Thermal", "role": "Battleship fleet railgun sniper"},
    "Capital Hybrid Turret": {"slot": "High", "size": "Capital", "category": "Hybrid Turret", "meta": "Tech I / Faction", "cpu": 140, "pg": 175000, "cap_cost": 480.0, "optimal": 45000, "falloff": 40000, "tracking": 0.0028, "rof": 10.5, "damage_types": "Kinetic / Thermal", "role": "Dreadnought capital hybrid blaster/rail siege gun"},

    # --- Projectile Turrets (Autocannons & Artillery) ---
    "Small Autocannon (200mm / 150mm)": {"slot": "High", "size": "Small", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 11, "pg": 5, "cap_cost": 0.0, "optimal": 1200, "falloff": 6500, "tracking": 0.480, "rof": 2.4, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless frigate brawling autocannon"},
    "Small Artillery (280mm Howitzer)": {"slot": "High", "size": "Small", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 25, "pg": 18, "cap_cost": 0.0, "optimal": 12500, "falloff": 9500, "tracking": 0.098, "rof": 6.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless frigate massive alpha volley"},
    "Medium Autocannon (425mm / 220mm)": {"slot": "High", "size": "Medium", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 28, "pg": 85, "cap_cost": 0.0, "optimal": 2800, "falloff": 16500, "tracking": 0.165, "rof": 3.2, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless cruiser nano skirmish autocannon"},
    "Medium Artillery (720mm Howitzer)": {"slot": "High", "size": "Medium", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 52, "pg": 245, "cap_cost": 0.0, "optimal": 28000, "falloff": 21000, "tracking": 0.035, "rof": 8.2, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless cruiser fleet alpha volley strike"},
    "Large Autocannon (800mm Repeating Cannon)": {"slot": "High", "size": "Large", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 55, "pg": 1450, "cap_cost": 0.0, "optimal": 5500, "falloff": 32000, "tracking": 0.052, "rof": 4.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless battleship mobile autocannon DPS"},
    "Large Artillery (1400mm Howitzer)": {"slot": "High", "size": "Large", "category": "Projectile Turret", "meta": "Tech I / Tech II / Faction", "cpu": 95, "pg": 3850, "cap_cost": 0.0, "optimal": 58000, "falloff": 42000, "tracking": 0.009, "rof": 12.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Capless battleship fleet instakill alpha strike"},
    "Capital Projectile Turret": {"slot": "High", "size": "Capital", "category": "Projectile Turret", "meta": "Tech I / Faction", "cpu": 130, "pg": 195000, "cap_cost": 0.0, "optimal": 38000, "falloff": 65000, "tracking": 0.0022, "rof": 14.0, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Dreadnought capital projectile siege cannon"},

    # --- Missile Launchers ---
    "Rocket Launcher": {"slot": "High", "size": "Small", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 22, "pg": 5, "cap_cost": 0.0, "optimal": 12000, "falloff": None, "tracking": None, "rof": 2.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Frigate close-range rocket brawler"},
    "Light Missile Launcher": {"slot": "High", "size": "Small", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 38, "pg": 8, "cap_cost": 0.0, "optimal": 45000, "falloff": None, "tracking": None, "rof": 6.8, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Frigate / Destroyer long range kiter"},
    "Heavy Assault Missile Launcher (HAM)": {"slot": "High", "size": "Medium", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 42, "pg": 85, "cap_cost": 0.0, "optimal": 25000, "falloff": None, "tracking": None, "rof": 4.2, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Cruiser close-range heavy missile DPS"},
    "Heavy Missile Launcher (HML)": {"slot": "High", "size": "Medium", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 55, "pg": 115, "cap_cost": 0.0, "optimal": 68000, "falloff": None, "tracking": None, "rof": 7.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Cruiser fleet long-range missile platform"},
    "Torpedo Launcher": {"slot": "High", "size": "Large", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 65, "pg": 1150, "cap_cost": 0.0, "optimal": 38000, "falloff": None, "tracking": None, "rof": 8.5, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Stealth Bomber / Battleship heavy anti-capital torpedo"},
    "Cruise Missile Launcher": {"slot": "High", "size": "Large", "category": "Missile Launcher", "meta": "Tech I / Tech II / Faction", "cpu": 85, "pg": 950, "cap_cost": 0.0, "optimal": 180000, "falloff": None, "tracking": None, "rof": 11.2, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Battleship extreme range cruise missile sniper"},
    "XL Torpedo / Cruise Launcher": {"slot": "High", "size": "Capital", "category": "Missile Launcher", "meta": "Tech I / Faction", "cpu": 160, "pg": 145000, "cap_cost": 0.0, "optimal": 85000, "falloff": None, "tracking": None, "rof": 15.0, "damage_types": "Selectable (EM/Therm/Kin/Exp)", "role": "Dreadnought capital missile siege bombardment"},

    # --- Electronic Warfare & Tackle ---
    "Warp Scrambler (Scram)": {"slot": "Mid", "size": "Small", "category": "Tackle", "meta": "Tech I / Tech II / Faction / Officer", "cpu": 28, "pg": 1, "cap_cost": 22.0, "optimal": 9000, "falloff": None, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Applies 2-3 points of warp disruption and disables target MWD/MJD"},
    "Warp Disruptor (Long Point)": {"slot": "Mid", "size": "Small", "category": "Tackle", "meta": "Tech I / Tech II / Faction / Officer", "cpu": 32, "pg": 1, "cap_cost": 30.0, "optimal": 24000, "falloff": None, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Applies 1 point of warp disruption (allows target MWD to function)"},
    "Stasis Webifier": {"slot": "Mid", "size": "Small", "category": "Tackle / EWAR", "meta": "Tech I / Tech II / Faction / Officer", "cpu": 25, "pg": 1, "cap_cost": 15.0, "optimal": 10000, "falloff": None, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Reduces target sub-warp velocity by 50-60% (up to 90% with bonuses)"},
    "Heavy Stasis Grappler": {"slot": "Mid", "size": "Battleship", "category": "Tackle", "meta": "Tech I / Tech II / Faction", "cpu": 45, "pg": 250, "cap_cost": 65.0, "optimal": 2500, "falloff": 9000, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Battleship extreme short-range velocity reduction (up to 85%)"},
    "Energy Neutralizer (Small / Medium / Large / Capital)": {"slot": "High", "size": "Universal", "category": "Capacitor Warfare", "meta": "Tech I / Tech II / Faction / Officer", "cpu": 45, "pg": 280, "cap_cost": 120.0, "optimal": 18000, "falloff": 12000, "tracking": None, "rof": 12.0, "damage_types": None, "role": "Destroys target capacitor directly, disabling active modules and weapons"},
    "Energy Nosferatu (Small / Medium / Large / Capital)": {"slot": "High", "size": "Universal", "category": "Capacitor Warfare", "meta": "Tech I / Tech II / Faction / Officer", "cpu": 35, "pg": 190, "cap_cost": 0.0, "optimal": 14000, "falloff": 8000, "tracking": None, "rof": 6.0, "damage_types": None, "role": "Leeches capacitor from target into own capacitor pool"},
    "Target Painter": {"slot": "Mid", "size": "Small", "category": "EWAR", "meta": "Tech I / Tech II / Faction", "cpu": 28, "pg": 1, "cap_cost": 18.0, "optimal": 36000, "falloff": 24000, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Blooms target signature radius by 25-35% to increase damage application"},
    "Sensor Dampener": {"slot": "Mid", "size": "Small", "category": "EWAR", "meta": "Tech I / Tech II / Faction", "cpu": 34, "pg": 1, "cap_cost": 22.0, "optimal": 48000, "falloff": 32000, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Reduces target targeting range or slows targeting lock speed"},
    "Tracking Disruptor": {"slot": "Mid", "size": "Small", "category": "EWAR", "meta": "Tech I / Tech II / Faction", "cpu": 30, "pg": 1, "cap_cost": 20.0, "optimal": 42000, "falloff": 28000, "tracking": None, "rof": 5.0, "damage_types": None, "role": "Reduces hostile turret tracking speed or optimal range / falloff"},
    "ECM Jammer": {"slot": "Mid", "size": "Small", "category": "EWAR", "meta": "Tech I / Tech II / Faction", "cpu": 45, "pg": 1, "cap_cost": 45.0, "optimal": 55000, "falloff": 25000, "tracking": None, "rof": 20.0, "damage_types": None, "role": "Forces target to lose all target locks except the jamming vessel"},

    # --- Propulsion Modules ---
    "1MN / 5MN Afterburner": {"slot": "Mid", "size": "Frigate", "category": "Propulsion", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 15, "pg": 15, "cap_cost": 12.0, "optimal": None, "falloff": None, "tracking": None, "rof": 10.0, "speed_bonus": "+135%", "sig_penalty": "None", "role": "Frigate afterburner (immune to scram shutoff)"},
    "10MN / 50MN Afterburner": {"slot": "Mid", "size": "Cruiser", "category": "Propulsion", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 28, "pg": 135, "cap_cost": 45.0, "optimal": None, "falloff": None, "tracking": None, "rof": 10.0, "speed_bonus": "+135%", "sig_penalty": "None", "role": "Cruiser / BC afterburner (immune to scram shutoff)"},
    "100MN / 500MN Afterburner": {"slot": "Mid", "size": "Battleship", "category": "Propulsion", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 45, "pg": 1850, "cap_cost": 165.0, "optimal": None, "falloff": None, "tracking": None, "rof": 10.0, "speed_bonus": "+135%", "sig_penalty": "None", "role": "Battleship heavy afterburner (immune to scram shutoff)"},
    "5MN / 50MN / 500MN Microwarpdrive (MWD)": {"slot": "Mid", "size": "Universal", "category": "Propulsion", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 32, "pg": 150, "cap_cost": 75.0, "optimal": None, "falloff": None, "tracking": None, "rof": 10.0, "speed_bonus": "+500%", "sig_penalty": "+500% Sig Radius", "role": "Extreme sub-warp speed (disabled by Warp Scrambler)"},
    "Micro Jump Drive (MJD)": {"slot": "Mid", "size": "Battleship / BC", "category": "Propulsion", "meta": "Tech I / Tech II", "cpu": 55, "pg": 850, "cap_cost": 300.0, "optimal": 100000, "falloff": None, "tracking": None, "rof": 180.0, "speed_bonus": "100km Instant Blink", "sig_penalty": None, "role": "Instantly teleports ship 100km forward after spool"},

    # --- Shield Defense Modules ---
    "Medium / Large Shield Extender (MSE / LSE)": {"slot": "Mid", "size": "Frigate / Cruiser / BS", "category": "Shield Buffer", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 45, "pg": 120, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "shield_hp_bonus": "+2800 HP", "role": "Passive shield buffer EHP with signature penalty"},
    "Medium / Large / X-Large Shield Booster": {"slot": "Mid", "size": "Universal", "category": "Shield Active", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 65, "pg": 185, "cap_cost": 180.0, "optimal": None, "falloff": None, "tracking": None, "rof": 4.0, "shield_boost_hp": "750 HP / cycle", "role": "Active local shield repairer"},
    "Ancillary Shield Booster (MASB / LASB / XL-ASB)": {"slot": "Mid", "size": "Universal", "category": "Shield Active", "meta": "Tech I / Tech II", "cpu": 75, "pg": 160, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": 4.0, "shield_boost_hp": "950 HP / cycle (Uses Cap Boosters)", "role": "Capless active burst shield repairer"},
    "Multi-Spectrum Shield Hardener": {"slot": "Mid", "size": "Universal", "category": "Shield Hardener", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 38, "pg": 1, "cap_cost": 18.0, "optimal": None, "falloff": None, "tracking": None, "rof": 20.0, "resist_bonus": "+30% All Shield Resists", "role": "Active omni-resistance booster for shields"},

    # --- Armor Defense Modules ---
    "200mm / 400mm / 800mm / 1600mm Steel Plates": {"slot": "Low", "size": "Frigate / Cruiser / BS", "category": "Armor Buffer", "meta": "Tech I / Tech II / Faction", "cpu": 25, "pg": 380, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "armor_hp_bonus": "+3500 HP", "role": "Passive armor buffer EHP with mass penalty"},
    "Small / Medium / Large Armor Repairer": {"slot": "Low", "size": "Universal", "category": "Armor Active", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 32, "pg": 195, "cap_cost": 140.0, "optimal": None, "falloff": None, "tracking": None, "rof": 9.0, "armor_rep_hp": "680 HP / cycle", "role": "Active local armor repairer"},
    "Ancillary Armor Repairer (SAAR / MAAR / LAAR)": {"slot": "Low", "size": "Universal", "category": "Armor Active", "meta": "Tech I / Tech II", "cpu": 38, "pg": 175, "cap_cost": 45.0, "optimal": None, "falloff": None, "tracking": None, "rof": 9.0, "armor_rep_hp": "1450 HP (with Nanite Paste)", "role": "High burst active armor repairer with nanite paste charges"},
    "Multi-Spectrum Energized Membrane II": {"slot": "Low", "size": "Universal", "category": "Armor Resistance", "meta": "Tech I / Tech II / Faction / Deadspace", "cpu": 28, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "resist_bonus": "+22.5% All Armor Resists", "role": "Passive capless omni-armor resistance membrane"},
    "Reactive Armor Hardener (RAH)": {"slot": "Low", "size": "Universal", "category": "Armor Resistance", "meta": "Tech I", "cpu": 30, "pg": 1, "cap_cost": 10.0, "optimal": None, "falloff": None, "tracking": None, "rof": 5.0, "resist_bonus": "Adaptive Armor Resists (Shifts toward incoming damage)", "role": "Dynamically shifts resistance profile to match incoming damage types"},
    "Damage Control II (DCU II)": {"slot": "Low", "size": "Universal", "category": "Hull / Defense", "meta": "Tech II", "cpu": 25, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "resist_bonus": "+12.5% Shield, +15% Armor, +60% Hull Resists", "role": "Passive omni-defense module fit on virtually every combat vessel"},
    "Assault Damage Control II (ADC II)": {"slot": "Low", "size": "Assault Only", "category": "Assault Defense", "meta": "Tech II", "cpu": 32, "pg": 1, "cap_cost": 15.0, "optimal": None, "falloff": None, "tracking": None, "rof": 150.0, "resist_bonus": "+95% All Resists for 15s Panic Window", "role": "Exclusive to Assault Frigates & HACs; 15s near-invulnerability panic button"},

    # --- Weapon Upgrades & Support ---
    "Gyrostabilizer II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 28, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+10% Projectile Damage, +10.5% RoF", "role": "Passive projectile turret DPS amplifier"},
    "Magnetic Field Stabilizer II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 28, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+10% Hybrid Damage, +10.5% RoF", "role": "Passive hybrid blaster/rail DPS amplifier"},
    "Heat Sink II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 28, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+10% Laser Damage, +10.5% RoF", "role": "Passive energy laser DPS amplifier"},
    "Ballistic Control System II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 32, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+10% Missile Damage, +10.5% RoF", "role": "Passive missile launcher DPS amplifier"},
    "Drone Damage Amplifier II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 24, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+23% Drone & Fighter Damage", "role": "Passive drone DPS amplifier"},
    "Entropic Radiation Sink II": {"slot": "Low", "size": "Universal", "category": "Weapon Upgrade", "meta": "Tech II / Faction / Officer", "cpu": 26, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "damage_bonus": "+10% Disintegrator Damage, +10.5% RoF", "role": "Passive Triglavian disintegrator DPS amplifier"},
    "Nanofiber Internal Structure II": {"slot": "Low", "size": "Universal", "category": "Mobility", "meta": "Tech II", "cpu": 15, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "speed_bonus": "+9.4% Velocity, -15.8% Inertia / Align", "role": "Increases sub-warp speed and reduces align time at cost of 20% structure HP"},
    "Overdrive Injector System II": {"slot": "Low", "size": "Universal", "category": "Mobility", "meta": "Tech II", "cpu": 12, "pg": 1, "cap_cost": 0.0, "optimal": None, "falloff": None, "tracking": None, "rof": None, "speed_bonus": "+12.5% Max Velocity", "role": "Increases maximum sub-warp velocity at cost of cargo capacity"}
}


def build_complete_module_dataset() -> List[Dict[str, Any]]:
    modules_list = []
    for name, spec in sorted(MODULE_SPECS_DATABASE.items()):
        rec = {
            "name": name,
            "slot_type": spec.get("slot"),
            "size_class": spec.get("size"),
            "category": spec.get("category"),
            "meta_tier": spec.get("meta"),
            "cpu_tf": spec.get("cpu"),
            "powergrid_mw": spec.get("pg"),
            "activation_cost_gj": spec.get("cap_cost"),
            "optimal_range_m": spec.get("optimal"),
            "falloff_range_m": spec.get("falloff"),
            "tracking_speed_rad_s": spec.get("tracking"),
            "rate_of_fire_s": spec.get("rof"),
            "damage_types": spec.get("damage_types"),
            "damage_bonus": spec.get("damage_bonus"),
            "shield_hp_bonus": spec.get("shield_hp_bonus"),
            "shield_boost_hp": spec.get("shield_boost_hp"),
            "armor_hp_bonus": spec.get("armor_hp_bonus"),
            "armor_rep_hp": spec.get("armor_rep_hp"),
            "resist_bonus": spec.get("resist_bonus"),
            "speed_bonus": spec.get("speed_bonus"),
            "role_and_tactics": spec.get("role")
        }
        modules_list.append(rec)
    return modules_list


def export_datasets():
    print("[A.U.R.A. Data Generator] Building full EVE Online Modules dataset...")
    mods = build_complete_module_dataset()

    json_path = os.path.join(OUTPUT_DIR, "eve_modules.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported JSON dataset: {json_path} ({len(mods)} module families)")

    csv_path = os.path.join(OUTPUT_DIR, "eve_modules.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "SlotType", "SizeClass", "Category", "MetaTier", "CPU_tf", "Powergrid_MW",
            "CapCost_GJ", "Optimal_m", "Falloff_m", "Tracking_rad_s", "ROF_s", "DamageTypes",
            "DamageBonus", "ShieldHPBonus", "ShieldBoostHP", "ArmorHPBonus", "ArmorRepHP", "ResistBonus", "SpeedBonus", "Role"
        ])
        for m in mods:
            writer.writerow([
                m["name"],
                m["slot_type"] or "",
                m["size_class"] or "",
                m["category"] or "",
                m["meta_tier"] or "",
                m["cpu_tf"] if m["cpu_tf"] is not None else "",
                m["powergrid_mw"] if m["powergrid_mw"] is not None else "",
                m["activation_cost_gj"] if m["activation_cost_gj"] is not None else "",
                m["optimal_range_m"] if m["optimal_range_m"] is not None else "",
                m["falloff_range_m"] if m["falloff_range_m"] is not None else "",
                m["tracking_speed_rad_s"] if m["tracking_speed_rad_s"] is not None else "",
                m["rate_of_fire_s"] if m["rate_of_fire_s"] is not None else "",
                m["damage_types"] or "",
                m["damage_bonus"] or "",
                m["shield_hp_bonus"] or "",
                m["shield_boost_hp"] or "",
                m["armor_hp_bonus"] or "",
                m["armor_rep_hp"] or "",
                m["resist_bonus"] or "",
                m["speed_bonus"] or "",
                m["role_and_tactics"] or ""
            ])
    print(f"  [OK] Exported CSV dataset:  {csv_path} ({len(mods)} rows)")


if __name__ == "__main__":
    export_datasets()
