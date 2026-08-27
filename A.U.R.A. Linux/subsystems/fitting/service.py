# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
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
Subsystem Service Layer for Ship Fitting & EFT Calculations.
"""

from typing import override
from core.base_subsystem import BaseSubsystem
from core.events import FittingCalculatedEvent
from .parser import FittingParser
from .stats import calculate_fit_stats
from .models import ParsedFitting, FittingSlotLayout


class FittingSubsystem(BaseSubsystem):
    """Ship fitting subsystem managing EFT parsing, Dogma stats, and validation."""

    def __init__(self):
        super().__init__(name="FittingSubsystem")
        self.parser = FittingParser()

    @override
    def initialize(self) -> bool:
        return True

    @override
    def start(self) -> bool:
        super().start()
        return True

    @override
    def stop(self) -> bool:
        super().stop()
        return True

    def parse_eft(self, eft_text: str) -> ParsedFitting | None:
        """Parses raw EFT text and calculates defense, DPS, and capacitor stats."""
        raw_fit = self.parser.parse_eft_block(eft_text)
        if not raw_fit:
            return None

        stats = calculate_fit_stats(raw_fit)
        
        layout = FittingSlotLayout(
            high_slots=raw_fit.get("high_slots", []),
            mid_slots=raw_fit.get("mid_slots", []),
            low_slots=raw_fit.get("low_slots", []),
            rig_slots=raw_fit.get("rig_slots", []),
            subsystems=raw_fit.get("subsystems", []),
            drones=raw_fit.get("drones", []),
            cargo=raw_fit.get("cargo", [])
        )

        ship_name = raw_fit.get("ship_name") or raw_fit.get("hull_name", "")
        fit_name = raw_fit.get("fit_name", "")
        parsed = ParsedFitting(
            ship_name=ship_name,
            fit_name=fit_name,
            slots=layout,
            raw_eft=eft_text,
            stats=stats
        )

        # Emit event
        evt = FittingCalculatedEvent(
            ship_name=parsed.ship_name,
            fit_name=parsed.fit_name,
            effective_hp=float(stats.get("ehp", 0.0)),
            total_dps=float(stats.get("total_dps", 0.0)),
            cap_stable=bool(stats.get("cap_stable", False)),
            cap_time_seconds=float(stats.get("cap_time_sec", 0.0)),
            cpu_usage_pct=float(stats.get("cpu_pct", 0.0)),
            powergrid_usage_pct=float(stats.get("pg_pct", 0.0))
        )
        self.event_bus.publish(evt)

        return parsed
