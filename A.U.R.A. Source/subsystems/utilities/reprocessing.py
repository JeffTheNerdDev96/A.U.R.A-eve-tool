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
Reprocessing & Refining Calculator for A.U.R.A. v0.7.1-alpha.4.
Calculates exact mineral yields, gross mineral value, ore raw value,
and net profit/loss with station/citadel tax adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.eve_market_data import (
    MINERAL_PRICES,
    calculate_reprocessing_yield,
    lookup_market_price,
)


@dataclass(slots=True)
class MineralYieldItem:
    mineral: str
    units: int
    unit_price: float
    total_isk: float


@dataclass(slots=True)
class ReprocessingReport:
    ore_name: str
    ore_units: int
    efficiency_pct: float
    station_tax_pct: float
    minerals: List[MineralYieldItem] = field(default_factory=list)
    raw_ore_value_isk: float = 0.0
    mineral_value_isk: float = 0.0
    net_gain_isk: float = 0.0
    profit_margin_pct: float = 0.0


class ReprocessingCalculator:
    """Calculates refining yields and economic margins."""

    @classmethod
    def calculate(
        cls,
        ore_name: str,
        units: int,
        efficiency_pct: float = 0.55,
        tax_pct: float = 0.05,
    ) -> ReprocessingReport:
        yields = calculate_reprocessing_yield(ore_name, units, efficiency_pct, tax_pct)

        items: List[MineralYieldItem] = []
        total_mineral_isk = 0.0

        for mineral, qty in yields.items():
            price = MINERAL_PRICES.get(mineral, 4.0)
            subtotal = price * qty
            items.append(MineralYieldItem(mineral, qty, price, round(subtotal, 2)))
            total_mineral_isk += subtotal

        # Calculate raw ore valuation based on baseline mineral price or ore proxy
        ore_unit_price = lookup_market_price(ore_name)
        raw_ore_isk = ore_unit_price * units

        net_gain = total_mineral_isk - raw_ore_isk
        margin = (net_gain / raw_ore_isk * 100.0) if raw_ore_isk > 0 else 0.0

        return ReprocessingReport(
            ore_name=ore_name,
            ore_units=units,
            efficiency_pct=round(efficiency_pct * 100.0, 1),
            station_tax_pct=round(tax_pct * 100.0, 1),
            minerals=items,
            raw_ore_value_isk=round(raw_ore_isk, 2),
            mineral_value_isk=round(total_mineral_isk, 2),
            net_gain_isk=round(net_gain, 2),
            profit_margin_pct=round(margin, 1),
        )
