"""
Subsystem Service Layer for Fleet Composition & Doctrine Counters.
"""

from typing import Dict, Any
from core.base_subsystem import BaseSubsystem
from core.events import FleetCompUpdatedEvent
from .analyzer import FleetCompAnalyzer
from .models import FleetCompAnalysis


class FleetCompSubsystem(BaseSubsystem):
    """Fleet comp subsystem evaluating fleet lists and emitting EventBus events."""

    def __init__(self):
        super().__init__(name="FleetCompSubsystem")
        self.analyzer = FleetCompAnalyzer()

    def initialize(self) -> bool:
        return True

    def start(self) -> bool:
        super().start()
        return True

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
