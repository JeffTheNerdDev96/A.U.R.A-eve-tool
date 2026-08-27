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
Subsystem Service Layer for Fleet Composition & Doctrine Counters.
"""

from typing import Any, override
from core.base_subsystem import BaseSubsystem
from core.events import FleetCompUpdatedEvent
from .analyzer import FleetCompAnalyzer
from .models import FleetCompAnalysis


class FleetCompSubsystem(BaseSubsystem):
    """Fleet comp subsystem evaluating fleet lists and emitting EventBus events."""

    def __init__(self):
        super().__init__(name="FleetCompSubsystem")
        self.analyzer = FleetCompAnalyzer()

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

    def evaluate_fleet(self, fleet_data: Any) -> FleetCompAnalysis:
        """Evaluates fleet from either dict of counts or raw text and emits FleetCompUpdatedEvent."""
        if isinstance(fleet_data, str):
            from .analyzer import parse_fleet_paste
            ship_counts = parse_fleet_paste(fleet_data)["ship_counts"]
        elif isinstance(fleet_data, dict):
            ship_counts = fleet_data
        else:
            ship_counts = {}

        analysis = self.analyzer.analyze_fleet(ship_counts)

        evt = FleetCompUpdatedEvent(
            total_ships=analysis.total_ships,
            role_counts=analysis.role_counts,
            ship_counts=analysis.ship_counts,
            primary_threats=analysis.primary_threats,
            counter_recommendations=analysis.counter_recommendations
        )
        self.event_bus.publish(evt)
        return analysis
