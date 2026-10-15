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
EVE Online Inventory, Cargo & Loot Valuation Parser for A.U.R.A. v0.7.1-alpha.2.
Parses clipboard text copied directly from EVE inventory, loot, asset safety,
or contracts. Computes offline baseline ISK appraisal, volume (m3), and hauler sizing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from core.eve_market_data import lookup_market_price, recommend_hauler


@dataclass(slots=True)
class ItemValuation:
    name: str
    quantity: int
    unit_price: float
    total_price: float
    volume_m3: float
    category: str = "General"


@dataclass(slots=True)
class ValuationReport:
    items: List[ItemValuation] = field(default_factory=list)
    total_isk: float = 0.0
    total_volume_m3: float = 0.0
    total_units: int = 0
    recommended_hauler: str = "Standard Industrial"
    hauler_capacity_m3: int = 35000


# Unit volume heuristics (m3 per unit) for items not explicitly tagged
_VOLUME_HEURISTICS = {
    "mineral": 0.01,
    "pi": 0.38,
    "ammo": 0.05,
    "missile": 0.1,
    "drone": 5.0,
    "frigate": 2500.0,
    "destroyer": 5000.0,
    "cruiser": 10000.0,
    "battlecruiser": 15000.0,
    "battleship": 50000.0,
    "module": 5.0,
    "salvage": 0.01,
}


class CargoValuationParser:
    """Parses raw text pasted from EVE inventory / loot / assets."""

    @classmethod
    def parse_clipboard(cls, text: str) -> ValuationReport:
        if not text or not text.strip():
            return ValuationReport()

        items: List[ItemValuation] = []
        lines = text.strip().splitlines()

        for line in lines:
            parsed = cls._parse_line(line)
            if parsed:
                items.append(parsed)

        total_isk = sum(it.total_price for it in items)
        total_vol = sum(it.volume_m3 for it in items)
        total_qty = sum(it.quantity for it in items)

        hauler_name, hauler_cap = recommend_hauler(total_vol)

        return ValuationReport(
            items=items,
            total_isk=round(total_isk, 2),
            total_volume_m3=round(total_vol, 2),
            total_units=total_qty,
            recommended_hauler=hauler_name,
            hauler_capacity_m3=hauler_cap,
        )

    @classmethod
    def _parse_line(cls, line: str) -> Optional[ItemValuation]:
        clean = line.strip()
        if not clean or clean.startswith("#"):
            return None

        # Check for tab-separated format from EVE inventory (e.g. Name \t Quantity \t Group \t Volume)
        if "\t" in clean:
            parts = [p.strip() for p in clean.split("\t") if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                if name.lower() in ("name", "item", "item name", "type", "total", "subtotal"):
                    return None
                if parts[1].lower() in ("quantity", "qty", "count"):
                    return None

                qty_str = parts[1].replace(",", "").replace(".", "").replace(" ", "")
                qty = int(qty_str) if qty_str.isdigit() else 1
                group = parts[2] if len(parts) >= 3 else "General"
                
                vol = 0.0
                vol_found = False
                for p in parts[2:]:
                    if "m3" in p.lower():
                        vol_m = re.search(r"([\d,.]+)", p)
                        if vol_m:
                            try:
                                vol = float(vol_m.group(1).replace(",", ""))
                                vol_found = True
                                break
                            except ValueError:
                                pass
                if not vol_found:
                    vol = cls._estimate_volume(name, qty, group)

                unit_price = lookup_market_price(name)
                total_price = unit_price * qty
                return ItemValuation(name, qty, unit_price, total_price, vol, group)

        # Check explicit multiplier prefix like "100x Scourge Heavy Missile" or "100 * Scourge Heavy Missile"
        m_x_prefix = re.match(r"^([\d,]+)\s*[xX*]\s+(.+)$", clean)
        if m_x_prefix:
            qty_str = m_x_prefix.group(1).replace(",", "")
            qty = int(qty_str) if qty_str.isdigit() else 1
            name = m_x_prefix.group(2).strip()
            if name.lower() in ("name", "item", "item name", "type", "total", "subtotal"):
                return None
            unit_price = lookup_market_price(name)
            vol = cls._estimate_volume(name, qty, "General")
            return ItemValuation(name, qty, unit_price, unit_price * qty, vol, "General")

        # Check space-separated quantity prefix like "100 Scourge Heavy Missile"
        # Must not match items starting with caliber/dimensions (e.g. "100 mm AutoCannon", "10 MN Afterburner")
        m_num_prefix = re.match(r"^([\d,]+)\s+(.+)$", clean)
        if m_num_prefix:
            rest = m_num_prefix.group(2).strip()
            if not re.match(r"^(?:mm|mn|gj|km|m3|w|kw|mw)\b", rest, re.IGNORECASE):
                qty_str = m_num_prefix.group(1).replace(",", "")
                qty = int(qty_str) if qty_str.isdigit() else 1
                name = rest
                if name.lower() in ("name", "item", "item name", "type", "total", "subtotal"):
                    return None
                unit_price = lookup_market_price(name)
                vol = cls._estimate_volume(name, qty, "General")
                return ItemValuation(name, qty, unit_price, unit_price * qty, vol, "General")

        m_x_suffix = re.match(r"^(.+?)\s+x?\s*([\d,]+)$", clean, re.IGNORECASE)
        if m_x_suffix:
            name = m_x_suffix.group(1).strip()
            if name.lower() in ("name", "item", "item name", "type", "total", "subtotal"):
                return None
            qty_str = m_x_suffix.group(2).replace(",", "")
            qty = int(qty_str) if qty_str.isdigit() else 1
            unit_price = lookup_market_price(name)
            vol = cls._estimate_volume(name, qty, "General")
            return ItemValuation(name, qty, unit_price, unit_price * qty, vol, "General")

        # Single item line
        name = clean
        if name.lower() in ("name", "item", "item name", "type", "total", "subtotal"):
            return None
        unit_price = lookup_market_price(name)
        vol = cls._estimate_volume(name, 1, "General")
        return ItemValuation(name, 1, unit_price, unit_price, vol, "General")

    @staticmethod
    def _estimate_volume(name: str, qty: int, group: str) -> float:
        lower_name = name.lower()
        lower_grp = group.lower()

        unit_vol = 5.0  # default 5 m3
        for kw, v in _VOLUME_HEURISTICS.items():
            if kw in lower_name or kw in lower_grp:
                unit_vol = v
                break

        return round(unit_vol * qty, 2)
