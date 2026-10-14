# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
"""
Canonical Wormhole (J-Space) Static Connections and Environmental Weather Data.
Provides 100% offline lookup for wormhole types, system classes, static exits,
and Class 1-6 celestial phenomena effects (Wolf-Rayet, Pulsar, Magnetar, etc.).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# Canonical Wormhole Types (Static and Wandering connection specifications)
WORMHOLE_TYPES: Dict[str, Dict[str, Any]] = {
    # Highsec Exits
    "B274": {"dest": "Highsec", "source_class": "C1/C2", "max_mass_kg": 500_000_000, "jump_mass_kg": 20_000_000, "lifetime_hours": 24},
    "D845": {"dest": "Highsec", "source_class": "C2/C3", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "A641": {"dest": "Highsec", "source_class": "C4", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 16},
    "N110": {"dest": "Highsec", "source_class": "C1", "max_mass_kg": 500_000_000, "jump_mass_kg": 20_000_000, "lifetime_hours": 24},
    
    # Lowsec Exits
    "J244": {"dest": "Lowsec", "source_class": "C1/C2", "max_mass_kg": 500_000_000, "jump_mass_kg": 20_000_000, "lifetime_hours": 24},
    "U210": {"dest": "Lowsec", "source_class": "C3", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "C247": {"dest": "Lowsec", "source_class": "C4", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 16},
    "N968": {"dest": "Lowsec", "source_class": "C5", "max_mass_kg": 3_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},

    # Nullsec Exits
    "Z971": {"dest": "Nullsec", "source_class": "C1", "max_mass_kg": 500_000_000, "jump_mass_kg": 20_000_000, "lifetime_hours": 16},
    "K346": {"dest": "Nullsec", "source_class": "C3", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "E545": {"dest": "Nullsec", "source_class": "C4", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 16},
    "K329": {"dest": "Nullsec", "source_class": "C5", "max_mass_kg": 3_220_000_000, "jump_mass_kg": 375_000_000, "lifetime_hours": 24},

    # J-Space Inward Connections
    "H296": {"dest": "Class 5", "source_class": "C2/C3/C4", "max_mass_kg": 3_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "V928": {"dest": "Class 6", "source_class": "C5/C6", "max_mass_kg": 3_300_000_000, "jump_mass_kg": 375_000_000, "lifetime_hours": 24},
    "Z647": {"dest": "Class 1", "source_class": "C1/C2/C3", "max_mass_kg": 500_000_000, "jump_mass_kg": 20_000_000, "lifetime_hours": 16},
    "D382": {"dest": "Class 2", "source_class": "C2/C3/C4", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "M267": {"dest": "Class 3", "source_class": "C3/C4", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 24},
    "X873": {"dest": "Class 4", "source_class": "C4/C5", "max_mass_kg": 2_000_000_000, "jump_mass_kg": 300_000_000, "lifetime_hours": 16},
    "H900": {"dest": "Class 5", "source_class": "C5", "max_mass_kg": 3_220_000_000, "jump_mass_kg": 1_350_000_000, "lifetime_hours": 24},
}

# Environmental Weather Phenomena and Class 1 to Class 6 Stat Multipliers
# Stored as percentage modifiers where positive is a bonus and negative is a penalty.
WEATHER_PHENOMENA: Dict[str, Dict[str, Any]] = {
    "Wolf-Rayet": {
        "description": "Dense Wolf-Rayet star causing massive armor crystallization and weapon field expansion.",
        "effects": {
            1: {"armor_hp": 0.14, "small_energy_dmg": 0.28, "shield_resist": -0.14, "sig_radius": -0.14},
            2: {"armor_hp": 0.28, "small_energy_dmg": 0.56, "shield_resist": -0.21, "sig_radius": -0.21},
            3: {"armor_hp": 0.42, "small_energy_dmg": 0.84, "shield_resist": -0.28, "sig_radius": -0.28},
            4: {"armor_hp": 0.56, "small_energy_dmg": 1.12, "shield_resist": -0.35, "sig_radius": -0.35},
            5: {"armor_hp": 0.70, "small_energy_dmg": 1.40, "shield_resist": -0.42, "sig_radius": -0.42},
            6: {"armor_hp": 1.00, "small_energy_dmg": 2.00, "shield_resist": -0.50, "sig_radius": -0.50},
        }
    },
    "Pulsar": {
        "description": "Rapidly rotating neutron star producing strong electromagnetic shield charging and armor breakdown.",
        "effects": {
            1: {"shield_hp": 0.14, "cap_recharge": 0.14, "armor_resist": -0.14, "sig_radius": 0.14},
            2: {"shield_hp": 0.28, "cap_recharge": 0.28, "armor_resist": -0.21, "sig_radius": 0.28},
            3: {"shield_hp": 0.42, "cap_recharge": 0.42, "armor_resist": -0.28, "sig_radius": 0.42},
            4: {"shield_hp": 0.56, "cap_recharge": 0.56, "armor_resist": -0.35, "sig_radius": 0.56},
            5: {"shield_hp": 0.70, "cap_recharge": 0.70, "armor_resist": -0.42, "sig_radius": 0.70},
            6: {"shield_hp": 1.00, "cap_recharge": 1.00, "armor_resist": -0.50, "sig_radius": 1.00},
        }
    },
    "Magnetar": {
        "description": "Hyper-magnetic celestial body amplifying weapon damage at the cost of targeting tracking and missile velocity.",
        "effects": {
            1: {"damage": 0.14, "missile_explosion_radius": 0.14, "turret_tracking": -0.14, "target_painter_opt": -0.14},
            2: {"damage": 0.28, "missile_explosion_radius": 0.28, "turret_tracking": -0.21, "target_painter_opt": -0.21},
            3: {"damage": 0.42, "missile_explosion_radius": 0.42, "turret_tracking": -0.28, "target_painter_opt": -0.28},
            4: {"damage": 0.56, "missile_explosion_radius": 0.56, "turret_tracking": -0.35, "target_painter_opt": -0.35},
            5: {"damage": 0.70, "missile_explosion_radius": 0.70, "turret_tracking": -0.42, "target_painter_opt": -0.42},
            6: {"damage": 1.00, "missile_explosion_radius": 1.00, "turret_tracking": -0.50, "target_painter_opt": -0.50},
        }
    },
    "Cataclysmic Variable": {
        "description": "Unstable binary system amplifying local repair systems but severely penalizing remote logistics and capacitor drains.",
        "effects": {
            1: {"local_repair": 0.14, "repair_cap_cost": 0.14, "remote_repair": -0.14, "cap_capacity": 0.14},
            2: {"local_repair": 0.28, "repair_cap_cost": 0.28, "remote_repair": -0.21, "cap_capacity": 0.28},
            3: {"local_repair": 0.42, "repair_cap_cost": 0.42, "remote_repair": -0.28, "cap_capacity": 0.42},
            4: {"local_repair": 0.56, "repair_cap_cost": 0.56, "remote_repair": -0.35, "cap_capacity": 0.56},
            5: {"local_repair": 0.70, "repair_cap_cost": 0.70, "remote_repair": -0.42, "cap_capacity": 0.70},
            6: {"local_repair": 1.00, "repair_cap_cost": 1.00, "remote_repair": -0.50, "cap_capacity": 1.00},
        }
    },
    "Red Giant": {
        "description": "Swollen late-stage giant star emitting severe thermal radiation that enhances module overload and smartbombs.",
        "effects": {
            1: {"overheat_bonus": 0.14, "smartbomb_range": 0.14, "smartbomb_dmg": 0.14},
            2: {"overheat_bonus": 0.28, "smartbomb_range": 0.28, "smartbomb_dmg": 0.28},
            3: {"overheat_bonus": 0.42, "smartbomb_range": 0.42, "smartbomb_dmg": 0.42},
            4: {"overheat_bonus": 0.56, "smartbomb_range": 0.56, "smartbomb_dmg": 0.56},
            5: {"overheat_bonus": 0.70, "smartbomb_range": 0.70, "smartbomb_dmg": 0.70},
            6: {"overheat_bonus": 1.00, "smartbomb_range": 1.00, "smartbomb_dmg": 1.00},
        }
    },
    "Black Hole": {
        "description": "Gravitational singularity boosting sub-warp velocity and missile velocity with severe ship inertia and targeting range penalties.",
        "effects": {
            1: {"velocity": 0.14, "missile_velocity": 0.14, "inertia": 0.14, "lock_range": -0.14},
            2: {"velocity": 0.28, "missile_velocity": 0.28, "inertia": 0.21, "lock_range": -0.21},
            3: {"velocity": 0.42, "missile_velocity": 0.42, "inertia": 0.28, "lock_range": -0.28},
            4: {"velocity": 0.56, "missile_velocity": 0.56, "inertia": 0.35, "lock_range": -0.35},
            5: {"velocity": 0.70, "missile_velocity": 0.70, "inertia": 0.42, "lock_range": -0.42},
            6: {"velocity": 1.00, "missile_velocity": 1.00, "inertia": 0.50, "lock_range": -0.50},
        }
    },
}

# Static connection catalog for representative J-space systems
CANONICAL_WH_SYSTEMS: Dict[str, Dict[str, Any]] = {
    "J100000": {"class": 1, "statics": ["N110"], "weather": None},
    "J105432": {"class": 2, "statics": ["D845", "H296"], "weather": "Wolf-Rayet"},
    "J115405": {"class": 2, "statics": ["B274", "Z647"], "weather": "Pulsar"},
    "J120000": {"class": 3, "statics": ["D845"], "weather": "Magnetar"},
    "J135622": {"class": 4, "statics": ["X873", "C247"], "weather": "Cataclysmic Variable"},
    "J155502": {"class": 5, "statics": ["H296"], "weather": "Red Giant"},
    "J210000": {"class": 6, "statics": ["V928"], "weather": "Black Hole"},
    "Thera":   {"class": 12, "statics": ["Highsec", "Lowsec", "Nullsec"], "weather": None},
}


def lookup_wormhole_system(system_name_or_jnum: str) -> Optional[Dict[str, Any]]:
    """Lookup wormhole system static exits and weather effects."""
    clean = system_name_or_jnum.strip().upper()
    if clean in CANONICAL_WH_SYSTEMS:
        return CANONICAL_WH_SYSTEMS[clean]

    # Heuristic fallback based on standard J-Space numbering if not in canonical table
    if clean.startswith("J") and len(clean) == 7 and clean[1:].isdigit():
        num = int(clean[1:])
        # C1 to C6 classification ranges
        if num < 110000:
            wh_class = 1
        elif num < 130000:
            wh_class = 2
        elif num < 150000:
            wh_class = 3
        elif num < 180000:
            wh_class = 4
        elif num < 210000:
            wh_class = 5
        else:
            wh_class = 6
        return {"class": wh_class, "statics": [], "weather": None}

    return None


def get_weather_effects(weather_name: str, wh_class: int) -> Dict[str, float]:
    """Retrieve exact stat multiplier dict for a given phenomenon and system class (1-6)."""
    wh_class = max(1, min(6, int(wh_class)))
    phenom = WEATHER_PHENOMENA.get(weather_name)
    if not phenom:
        return {}
    return phenom["effects"].get(wh_class, {})
