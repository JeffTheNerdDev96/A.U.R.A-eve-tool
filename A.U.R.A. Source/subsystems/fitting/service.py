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
from .stats import calculate_fit_stats, validate_module_fit
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

        ship_name = raw_fit.get("ship_name") or raw_fit.get("hull_name", "")
        fit_name = raw_fit.get("fit_name", "")

        # Validate modules against hardpoints and single-fit rules
        validation_warnings: list[str] = []
        rejected_modules: list[str] = []
        fitted_so_far: list[str] = []
        valid_highs: list[str] = []
        valid_mids: list[str] = []
        valid_lows: list[str] = []
        valid_rigs: list[str] = []
        valid_subs: list[str] = []

        slot_groups = [
            (raw_fit.get("high_slots", []), valid_highs),
            (raw_fit.get("mid_slots", []), valid_mids),
            (raw_fit.get("low_slots", []), valid_lows),
            (raw_fit.get("rig_slots", []), valid_rigs),
            (raw_fit.get("subsystems", []), valid_subs),
        ]

        for raw_group, valid_target in slot_groups:
            for mod in raw_group:
                if not mod:
                    continue
                ok, reason = validate_module_fit(ship_name, fitted_so_far, mod)
                if ok:
                    valid_target.append(mod)
                    fitted_so_far.append(mod)
                else:
                    rejected_modules.append(mod)
                    validation_warnings.append(f"{mod}: {reason}")

        stats = calculate_fit_stats({
            "ship_name": ship_name,
            "high_slots": valid_highs,
            "mid_slots": valid_mids,
            "low_slots": valid_lows,
            "rig_slots": valid_rigs,
            "subsystems": valid_subs,
        })

        layout = FittingSlotLayout(
            high_slots=valid_highs,
            mid_slots=valid_mids,
            low_slots=valid_lows,
            rig_slots=valid_rigs,
            subsystems=valid_subs,
            drones=raw_fit.get("drones", []),
            cargo=raw_fit.get("cargo", [])
        )

        parsed = ParsedFitting(
            ship_name=ship_name,
            fit_name=fit_name,
            slots=layout,
            raw_eft=eft_text,
            stats=stats,
            validation_warnings=validation_warnings,
            rejected_modules=rejected_modules,
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
