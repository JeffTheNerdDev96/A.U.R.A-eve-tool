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
Planetary Industry (PI) Production Schematics & POCO Tax Calculator for A.U.R.A. v0.7.1-alpha.2.
Recursively resolves complex P4/P3/P2 factory schematics down to base P0 planets,
calculates daily extraction demands, volume requirements, and Customs Office export fees.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.eve_pi_data import (
    TIER_VOLUMES_M3,
    calculate_poco_export_tax,
    get_commodity_tier,
    get_recipe_inputs,
)


@dataclass(slots=True)
class PIIngredientDemand:
    name: str
    tier: str
    units_per_product: int
    daily_units_needed: int
    daily_volume_m3: float


@dataclass(slots=True)
class PIProductionSummary:
    product_name: str
    tier: str
    daily_output: int
    daily_export_tax_isk: float
    daily_output_volume_m3: float
    raw_p0_demands: List[PIIngredientDemand] = field(default_factory=list)
    intermediate_demands: List[PIIngredientDemand] = field(default_factory=list)
    recipe_tree: Dict[str, Any] = field(default_factory=dict)


class PICalculator:
    """Solves planetary production schematics and daily supply chains."""

    @classmethod
    def get_recipe_tree(cls, product_name: str) -> Dict[str, Any]:
        """Recursively builds the ingredient tree for a commodity."""
        tier = get_commodity_tier(product_name)
        inputs = get_recipe_inputs(product_name)

        children = [cls.get_recipe_tree(ing) for ing in inputs]

        return {
            "name": product_name,
            "tier": tier,
            "inputs": children,
        }

    @classmethod
    def solve_production_tree(cls, product_name: str, quantity: int = 1) -> Dict[str, Any]:
        tree = cls.get_recipe_tree(product_name)
        tree["quantity"] = quantity
        return tree

    @classmethod
    def calculate_production(
        cls,
        product_name: str,
        daily_units: int = 10,
        tax_rate_pct: float = 0.10,
    ) -> PIProductionSummary:
        tier = get_commodity_tier(product_name)
        tax_isk = calculate_poco_export_tax(product_name, daily_units, tax_rate_pct)
        unit_vol = TIER_VOLUMES_M3.get(tier, 1.5)
        out_vol = round(unit_vol * daily_units, 2)

        # Count total requirements
        p0_counts: Dict[str, int] = {}
        inter_counts: Dict[str, int] = {}

        def traverse(name: str, multiplier: int):
            t = get_commodity_tier(name)
            inputs = get_recipe_inputs(name)

            if not inputs:
                # Base P0
                p0_counts[name] = p0_counts.get(name, 0) + multiplier
                return

            if name != product_name:
                inter_counts[name] = inter_counts.get(name, 0) + multiplier

            # Standard factory conversion ratios:
            # 1 P4 needs approx 3 P3
            # 1 P3 needs approx 2 P2
            # 1 P2 needs approx 2 P1
            # 1 P1 needs approx 3000 P0
            child_mult = multiplier
            if t == "P1":
                child_mult = multiplier * 3000
            elif t in ("P2", "P3", "P4"):
                child_mult = multiplier * 2

            for child in inputs:
                traverse(child, child_mult)

        traverse(product_name, daily_units)

        p0_list: List[PIIngredientDemand] = []
        for p0_name, units in p0_counts.items():
            vol = round(units * TIER_VOLUMES_M3.get("P0", 0.01), 2)
            p0_list.append(PIIngredientDemand(p0_name, "P0", units // max(1, daily_units), units, vol))

        inter_list: List[PIIngredientDemand] = []
        for int_name, units in inter_counts.items():
            i_tier = get_commodity_tier(int_name)
            vol = round(units * TIER_VOLUMES_M3.get(i_tier, 0.38), 2)
            inter_list.append(PIIngredientDemand(int_name, i_tier, units // max(1, daily_units), units, vol))

        return PIProductionSummary(
            product_name=product_name,
            tier=tier,
            daily_output=daily_units,
            daily_export_tax_isk=round(tax_isk, 2),
            daily_output_volume_m3=out_vol,
            raw_p0_demands=p0_list,
            intermediate_demands=inter_list,
            recipe_tree=cls.get_recipe_tree(product_name),
        )
