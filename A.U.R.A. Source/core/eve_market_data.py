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
Canonical EVE Online Market Price Baselines, Reprocessing Tables & Hauling Logistics.
Provides 100% offline valuation indices and mineral refining calculations.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# Baseline Mineral Prices (ISK per unit)
MINERAL_PRICES: Dict[str, float] = {
    "Tritanium": 4.25,
    "Pyerite": 14.50,
    "Mexallon": 105.00,
    "Isogen": 380.00,
    "Nocxium": 750.00,
    "Zydrine": 1850.00,
    "Megacyte": 4200.00,
    "Morphite": 11500.00,
}

# Standard Ore Reprocessing Batches (per 100 units of compressed/uncompressed ore)
# Mineral breakdown: {Tritanium, Pyerite, Mexallon, Isogen, Nocxium, Zydrine, Megacyte, Morphite}
ORE_REPROCESSING_TABLE: Dict[str, Dict[str, int]] = {
    "Veldspar": {"Tritanium": 415},
    "Concentrated Veldspar": {"Tritanium": 436},
    "Dense Veldspar": {"Tritanium": 457},
    "Scordite": {"Tritanium": 346, "Pyerite": 173},
    "Condensed Scordite": {"Tritanium": 363, "Pyerite": 182},
    "Glossy Scordite": {"Tritanium": 381, "Pyerite": 190},
    "Pyroxeres": {"Tritanium": 351, "Pyerite": 26, "Mexallon": 50, "Nocxium": 5},
    "Solid Pyroxeres": {"Tritanium": 369, "Pyerite": 27, "Mexallon": 53, "Nocxium": 5},
    "Viscous Pyroxeres": {"Tritanium": 386, "Pyerite": 29, "Mexallon": 55, "Nocxium": 6},
    "Plagioclase": {"Tritanium": 107, "Pyerite": 213, "Mexallon": 107},
    "Azure Plagioclase": {"Tritanium": 112, "Pyerite": 224, "Mexallon": 112},
    "Rich Plagioclase": {"Tritanium": 118, "Pyerite": 234, "Mexallon": 118},
    "Omber": {"Tritanium": 85, "Pyerite": 34, "Isogen": 85},
    "Silvery Omber": {"Tritanium": 89, "Pyerite": 36, "Isogen": 89},
    "Golden Omber": {"Tritanium": 94, "Pyerite": 37, "Isogen": 94},
    "Kernite": {"Tritanium": 134, "Mexallon": 267, "Isogen": 134},
    "Luminous Kernite": {"Tritanium": 141, "Mexallon": 280, "Isogen": 141},
    "Fiery Kernite": {"Tritanium": 147, "Mexallon": 294, "Isogen": 147},
    "Jaspet": {"Tritanium": 72, "Pyerite": 121, "Mexallon": 144, "Nocxium": 72, "Zydrine": 8},
    "Hemorphite": {"Tritanium": 190, "Isogen": 175, "Nocxium": 70, "Zydrine": 15},
    "Hedbergite": {"Pyerite": 270, "Isogen": 190, "Nocxium": 95, "Zydrine": 19},
    "Gneiss": {"Tritanium": 170, "Mexallon": 170, "Isogen": 340, "Zydrine": 34},
    "Dark Ochre": {"Tritanium": 250, "Isogen": 500, "Nocxium": 250},
    "Spodumain": {"Tritanium": 4800, "Pyerite": 960, "Mexallon": 160, "Isogen": 80},
    "Crokite": {"Tritanium": 380, "Nocxium": 380, "Zydrine": 190},
    "Bistot": {"Pyerite": 600, "Zydrine": 240, "Megacyte": 120},
    "Arkonor": {"Tritanium": 880, "Zydrine": 160, "Megacyte": 320},
    "Mercoxit": {"Morphite": 300},
}

# Baseline Commodity & Common Asset Prices (Sample representation of popular hulls/modules/materials)
BASELINE_ITEM_PRICES: Dict[str, float] = {
    # Popular Ships
    "Rifter": 450_000.0,
    "Merlin": 440_000.0,
    "Tristan": 460_000.0,
    "Incursus": 450_000.0,
    "Dramiel": 65_000_000.0,
    "Cynabal": 185_000_000.0,
    "Machariel": 490_000_000.0,
    "Sabre": 75_000_000.0,
    "Eris": 68_000_000.0,
    "Flycatcher": 70_000_000.0,
    "Heretic": 72_000_000.0,
    "Loki": 240_000_000.0,
    "Tengu": 235_000_000.0,
    "Legion": 230_000_000.0,
    "Proteus": 225_000_000.0,
    "Gila": 260_000_000.0,
    "Orthrus": 280_000_000.0,
    "Ishtar": 210_000_000.0,
    "Cerberus": 205_000_000.0,
    "Vagabond": 215_000_000.0,
    "Zealot": 220_000_000.0,
    "Hulk": 340_000_000.0,
    "Skiff": 320_000_000.0,
    "Mackinaw": 330_000_000.0,
    "Rorqual": 2_800_000_000.0,
    "Revelation": 4_200_000_000.0,
    "Naglfar": 4_400_000_000.0,
    "Moros": 4_100_000_000.0,
    "Phoenix": 4_300_000_000.0,
    
    # Common Modules
    "Damage Control II": 1_250_000.0,
    "Assault Damage Control II": 18_500_000.0,
    "1600mm Steel Plates II": 2_800_000.0,
    "Large Shield Extender II": 1_450_000.0,
    "Warp Disruptor II": 1_100_000.0,
    "Warp Scrambler II": 950_000.0,
    "Stasis Webifier II": 1_200_000.0,
    "500MN Microwarpdrive II": 14_500_000.0,
    "50MN Microwarpdrive II": 1_850_000.0,
    "5MN Microwarpdrive II": 420_000.0,
    "Heavy Missile Launcher II": 1_600_000.0,
    "425mm AutoCannon II": 1_350_000.0,
    "Mega Pulse Laser II": 2_400_000.0,
    "Heavy Neutron Blaster II": 2_100_000.0,

    # Raw Ores (Refining & Cargo Baselines)
    "Veldspar": 17.6,
    "Concentrated Veldspar": 18.5,
    "Dense Veldspar": 19.4,
    "Scordite": 39.8,
    "Condensed Scordite": 41.8,
    "Glossy Scordite": 43.8,
    "Pyroxeres": 108.7,
    "Solid Pyroxeres": 114.1,
    "Viscous Pyroxeres": 119.5,
    "Plagioclase": 147.8,
    "Azure Plagioclase": 155.2,
    "Rich Plagioclase": 162.6,
    "Omber": 331.5,
    "Silvery Omber": 348.1,
    "Golden Omber": 364.7,
    "Kernite": 795.2,
    "Luminous Kernite": 835.0,
    "Fiery Kernite": 874.8,
    "Jaspet": 859.8,
    "Hemorphite": 1475.5,
    "Hedbergite": 1825.1,
    "Gneiss": 2106.7,
    "Dark Ochre": 3785.6,
    "Spodumain": 815.2,
    "Crokite": 6381.5,
    "Bistot": 9567.0,
    "Arkonor": 16436.0,
    "Mercoxit": 34500.0,

    # Exploration & Probes
    "Core Scanner Probe I": 10_000.0,
    "Core Probe Launcher I": 50_000.0,
    "Expanded Probe Launcher I": 65_000.0,
    "Combat Scanner Probe I": 15_000.0,
    "Sisters Core Scanner Probe": 500_000.0,
    "Sisters Core Probe Launcher": 35_000_000.0,

    # Salvage & Exploration
    "Alloyed Tritanium Bar": 18_000.0,
    "Armor Plates": 35_000.0,
    "Burned Logic Circuit": 42_000.0,
    "Charred Micro Circuit": 38_000.0,
    "Contaminated Lore": 85_000.0,
    "Enhanced Ward Console": 180_000.0,
    "Intact Armor Plates": 4_200_000.0,
    "Logic Circuit": 12_000.0,
    "Micro Circuit": 14_000.0,
    "Power Circuit": 11_000.0,
    "Single-crystal Superalloy I-beam": 95_000.0,
    "Tripped Power Circuit": 28_000.0,
}

# Hauling Ship Classes & Effective Cargo Capacities (m3)
HAULER_CAPACITIES = [
    ("Blockade Runner (Prorator, Crane)", 12_000),
    ("Deep Space Transport (Occator, Bustard)", 62_500),
    ("Standard Industrial (Tayra, Mammoth)", 35_000),
    ("Orca (Ore Hold + Fleet Hangar)", 250_000),
    ("Jump Freighter (Anshar, Nomad)", 380_000),
    ("Standard Freighter (Fenrir, Charon)", 880_000),
    ("Bowhead (Ship Maintenance Array)", 1_300_000),
]


def lookup_market_price(item_name: str) -> float:
    """Return estimated baseline price in ISK for a given item name."""
    clean = item_name.strip()
    if clean in MINERAL_PRICES:
        return MINERAL_PRICES[clean]
    if clean in BASELINE_ITEM_PRICES:
        return BASELINE_ITEM_PRICES[clean]
    
    # Check lowercase/prefix matches
    for k, v in BASELINE_ITEM_PRICES.items():
        if k.lower() == clean.lower():
            return v
    for k, v in MINERAL_PRICES.items():
        if k.lower() == clean.lower():
            return v

    # Fallback heuristic based on module tiers
    lower = clean.lower()
    if "officer" in lower or "estamel" in lower or "cormack" in lower or "brynn" in lower:
        return 2_500_000_000.0
    if (
        "deadspace" in lower
        or any(t in lower for t in ("-type", "pith", "gist", "centus", "centum", "corpus", "corpum", "coreli", "corelum"))
    ):
        return 180_000_000.0
    if "faction" in lower or any(f in lower for f in ("federation navy", "caldari navy", "imperial navy", "republic fleet", "dark blood", "shadow serpentis", "dread guristas", "true sansha")):
        return 45_000_000.0
    if " ii" in lower:
        return 2_500_000.0
    
    return 100_000.0  # Conservative default


def calculate_reprocessing_yield(
    ore_name: str,
    units: int,
    efficiency_pct: float = 0.55,
    tax_pct: float = 0.05,
) -> Dict[str, int]:
    """
    Compute mineral yield for a batch of ore.
    Formula: output = floor(base_minerals * batches * (efficiency * (1 - tax)))
    """
    clean_ore = ore_name.strip()
    base_yield = ORE_REPROCESSING_TABLE.get(clean_ore)
    if not base_yield:
        # Check matching base ore if enhanced variant
        for k in ORE_REPROCESSING_TABLE:
            if k in clean_ore:
                base_yield = ORE_REPROCESSING_TABLE[k]
                break
    if not base_yield:
        return {}

    batches = units / 100.0
    effective_mult = max(0.0, min(1.0, efficiency_pct * (1.0 - tax_pct)))

    yields: Dict[str, int] = {}
    for mineral, base_amount in base_yield.items():
        min_yield = math.floor(base_amount * batches * effective_mult)
        if min_yield > 0:
            yields[mineral] = min_yield

    return yields


def recommend_hauler(total_volume_m3: float) -> Tuple[str, int]:
    """Recommend the most agile hauler class that fits the required volume."""
    for name, cap in HAULER_CAPACITIES:
        if total_volume_m3 <= cap:
            return name, cap
    # If larger than any single hauler, calculate freighter trips
    freighter_name, freighter_cap = HAULER_CAPACITIES[-2]
    trips = math.ceil(total_volume_m3 / freighter_cap)
    return f"{freighter_name} ({trips} trips needed)", freighter_cap
