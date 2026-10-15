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
Unified Utilities Subsystem for A.U.R.A. v0.7.1-alpha.2.
Coordinates Cargo & Loot Appraisals, Mineral Reprocessing, Survey Scanner planning,
live Mining Session Ledgers, Killmail EFT generation, and Planetary Industry supply chains.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from core.base_subsystem import BaseSubsystem
from core.events import MiningYieldEvent
from .valuation_parser import CargoValuationParser, ValuationReport
from .reprocessing import ReprocessingCalculator, ReprocessingReport
from .mining_parser import SurveyScannerParser, SurveyScannerRock, MiningYieldPlanner, MiningCyclePlan, MiningLedger
from .killmail_parser import KillmailParser, ParsedKillmail
from .pi_calculator import PICalculator, PIProductionSummary


class UtilitiesSubsystem(BaseSubsystem):
    """Unified service for offline industrial, valuation, and tactical utilities."""

    def __init__(self):
        super().__init__(name="UtilitiesSubsystem")
        self._mining_ledger = MiningLedger()
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        """Register listeners on the EventBus for passive gamelog events."""
        self.event_bus.subscribe(MiningYieldEvent, self._on_mining_yield)
        return True

    def start(self) -> bool:
        super().start()
        return True

    def stop(self) -> bool:
        self.event_bus.unsubscribe(MiningYieldEvent, self._on_mining_yield)
        super().stop()
        return True

    def _on_mining_yield(self, event: MiningYieldEvent) -> None:
        with self._lock:
            self._mining_ledger.record_cycle(event.ore_name, event.units, event.volume_m3)

    # --- Public API methods ---

    def appraise_cargo(self, text: str) -> ValuationReport:
        return CargoValuationParser.parse_clipboard(text)

    parse_cargo = appraise_cargo

    def calculate_reprocessing(
        self,
        ore_name: str,
        units: int,
        efficiency_pct: float = 0.55,
        tax_pct: float = 0.05,
    ) -> ReprocessingReport:
        return ReprocessingCalculator.calculate(ore_name, units, efficiency_pct, tax_pct)

    def parse_survey_scan(self, text: str) -> List[SurveyScannerRock]:
        return SurveyScannerParser.parse(text)

    def plan_mining_cycle(
        self,
        rock_name: str,
        rock_volume_m3: float,
        laser_m3: float = 1200.0,
        cycle_sec: float = 180.0,
        lasers_count: int = 2,
    ) -> MiningCyclePlan:
        return MiningYieldPlanner.plan_depletion(rock_name, rock_volume_m3, laser_m3, cycle_sec, lasers_count)

    def get_mining_ledger(self) -> Dict[str, Any]:
        with self._lock:
            return self._mining_ledger.get_summary()

    def clear_mining_ledger(self) -> None:
        with self._lock:
            self._mining_ledger.clear()

    def parse_killmail(self, text: str) -> Optional[ParsedKillmail]:
        return KillmailParser.parse_clipboard(text)

    def calculate_pi_production(
        self,
        product_name: str,
        daily_units: int = 10,
        tax_rate_pct: float = 0.10,
    ) -> PIProductionSummary:
        return PICalculator.calculate_production(product_name, daily_units, tax_rate_pct)
