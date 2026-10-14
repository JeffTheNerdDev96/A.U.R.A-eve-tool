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
Canonical Planetary Industry (PI) Production Schematics & POCO Tax Calculator.
Provides 100% offline lookup for P0 through P4 commodity trees and customs export costs.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Commodity tier volume per unit in cubic meters (m3)
TIER_VOLUMES_M3: Dict[str, float] = {
    "P0": 0.01,
    "P1": 0.38,
    "P2": 1.50,
    "P3": 6.00,
    "P4": 100.00,
}

# Base planetary export tax base prices per unit defined by CCP
EXPORT_BASE_PRICES: Dict[str, float] = {
    "P0": 5.0,
    "P1": 500.0,
    "P2": 9_000.0,
    "P3": 70_000.0,
    "P4": 1_350_000.0,
}

# Raw Planets to P1 Refined Commodities
P0_TO_P1_MAP: Dict[str, str] = {
    "Aqueous Liquids": "Water",
    "Autotrophs": "Industrial Fibers",
    "Base Metals": "Reactive Metals",
    "Carbon Compounds": "Biofuels",
    "Complex Organisms": "Proteins",
    "Felsic Magma": "Silicon",
    "Heavy Metals": "Toxic Metals",
    "Ionic Solutions": "Electrolytes",
    "Microorganisms": "Bacteria",
    "Noble Gas": "Oxygen",
    "Noble Metals": "Precious Metals",
    "Non-CS Crystals": "Chiral Structures",
    "Planktic Colonies": "Biomass",
    "Reactive Gas": "Oxidizing Compound",
    "Suspended Plasma": "Plasmoids",
}

# P2 Specialized Commodities: {Name: [Input P1_1, Input P1_2]}
P2_RECIPES: Dict[str, List[str]] = {
    "Biocells": ["Biofuels", "Precious Metals"],
    "Construction Blocks": ["Reactive Metals", "Toxic Metals"],
    "Consumer Goods": ["Toxic Metals", "Water"],
    "Coolant": ["Electrolytes", "Water"],
    "Enriched Uranium": ["Precious Metals", "Toxic Metals"],
    "Fertilizer": ["Bacteria", "Proteins"],
    "Genetically Enhanced Livestock": ["Biomass", "Proteins"],
    "Livestock": ["Biofuels", "Proteins"],
    "Mechanical Parts": ["Precious Metals", "Reactive Metals"],
    "Microfiber Shielding": ["Industrial Fibers", "Silicon"],
    "Miniature Electronics": ["Chiral Structures", "Silicon"],
    "Nanites": ["Bacteria", "Reactive Metals"],
    "Oxides": ["Oxidizing Compound", "Oxygen"],
    "Polyaramids": ["Industrial Fibers", "Oxidizing Compound"],
    "Polytextiles": ["Biofuels", "Industrial Fibers"],
    "Rocket Fuel": ["Electrolytes", "Plasmoids"],
    "Silicate Glass": ["Oxidizing Compound", "Silicon"],
    "Superconductors": ["Plasmoids", "Water"],
    "Supertensile Plastics": ["Biomass", "Oxygen"],
    "Synthetic Oil": ["Electrolytes", "Oxygen"],
    "Test Cultures": ["Bacteria", "Water"],
    "Transmitters": ["Chiral Structures", "Plasmoids"],
    "Viral Agent": ["Bacteria", "Biomass"],
    "Water-Cooled CPU": ["Reactive Metals", "Water"],
}

# P3 Advanced Commodities: {Name: [Input P2_1, Input P2_2, optional Input P1/P2]}
P3_RECIPES: Dict[str, List[str]] = {
    "Biotech Research Reports": ["Construction Blocks", "Livestock", "Nanites"],
    "Camera Drones": ["Rocket Fuel", "Silicate Glass"],
    "Condensates": ["Coolant", "Oxides"],
    "Cryoprotectant Solution": ["Fertilizer", "Synthetic Oil", "Test Cultures"],
    "Data Chips": ["Microfiber Shielding", "Supertensile Plastics"],
    "Gel-Matrix Biopaste": ["Biocells", "Oxides", "Superconductors"],
    "Guidance Systems": ["Transmitters", "Water-Cooled CPU"],
    "Hazmat Detection Systems": ["Polytextiles", "Transmitters", "Viral Agent"],
    "Hermetic Membranes": ["Genetically Enhanced Livestock", "Polyaramids"],
    "High-Tech Transmitters": ["Polyaramids", "Transmitters"],
    "Industrial Explosives": ["Fertilizer", "Polytextiles"],
    "Neocoms": ["Biocells", "Silicate Glass"],
    "Nuclear Reactors": ["Enriched Uranium", "Microfiber Shielding"],
    "Planetary Vehicles": ["Mechanical Parts", "Miniature Electronics", "Supertensile Plastics"],
    "Robotics": ["Consumer Goods", "Mechanical Parts"],
    "Smartfab Units": ["Construction Blocks", "Miniature Electronics"],
    "Supercomputers": ["Consumer Goods", "Coolant", "Water-Cooled CPU"],
    "Synthetic Synapses": ["Supertensile Plastics", "Test Cultures"],
    "Transcranial Microcontrollers": ["Biocells", "Nanites"],
    "Ukomi Super Conductors": ["Synthetic Oil", "Superconductors"],
    "Vaccines": ["Livestock", "Viral Agent"],
}

# P4 High-Tech Commodities: {Name: [Input P3_1, Input P3_2, ...]}
P4_RECIPES: Dict[str, List[str]] = {
    "Broadcast Node": ["Data Chips", "High-Tech Transmitters", "Neocoms"],
    "Integrity Response Drones": ["Gel-Matrix Biopaste", "Hazmat Detection Systems", "Planetary Vehicles"],
    "Nano-Factory": ["Industrial Explosives", "Reactive Metals", "Ukomi Super Conductors"],
    "Organic Mortar Applicators": ["Condensates", "Guidance Systems", "Hermetic Membranes"],
    "Recursive Computing Module": ["Guidance Systems", "Synthetic Synapses", "Transcranial Microcontrollers"],
    "Self-Harmonizing Power Core": ["Camera Drones", "Hermetic Membranes", "Nuclear Reactors"],
    "Sterile Conduits": ["Smartfab Units", "Vaccines", "Water"],
    "Wetware Mainframe": ["Biotech Research Reports", "Cryoprotectant Solution", "Supercomputers"],
}


def get_commodity_tier(name: str) -> str:
    """Return the tier code (P0, P1, P2, P3, P4) for a given PI commodity name."""
    clean = name.strip()
    if clean in P4_RECIPES:
        return "P4"
    if clean in P3_RECIPES:
        return "P3"
    if clean in P2_RECIPES:
        return "P2"
    if clean in P0_TO_P1_MAP.values():
        return "P1"
    if clean in P0_TO_P1_MAP:
        return "P0"
    return "P1"  # Default


def calculate_poco_export_tax(commodity_name: str, units: int, tax_rate_pct: float = 0.10) -> float:
    """Calculate Customs Office export tax in ISK for a given commodity and quantity."""
    tier = get_commodity_tier(commodity_name)
    base_price = EXPORT_BASE_PRICES.get(tier, 500.0)
    tax_rate = max(0.0, min(1.0, tax_rate_pct))
    return float(units * base_price * tax_rate)


def get_recipe_inputs(commodity_name: str) -> List[str]:
    """Retrieve required ingredient commodity names to produce the given commodity."""
    clean = commodity_name.strip()
    if clean in P4_RECIPES:
        return P4_RECIPES[clean]
    if clean in P3_RECIPES:
        return P3_RECIPES[clean]
    if clean in P2_RECIPES:
        return P2_RECIPES[clean]
    for p0, p1 in P0_TO_P1_MAP.items():
        if p1 == clean:
            return [p0]
    return []
