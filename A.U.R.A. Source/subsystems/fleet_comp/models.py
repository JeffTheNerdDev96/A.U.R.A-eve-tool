"""
Fleet Composition Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass(frozen=True)
class FleetCompAnalysis:
    """Immutable DTO holding parsed fleet role breakdown and counter recommendations."""
    total_ships: int
    role_counts: Dict[str, int]  # Logistics, Tacklers, Mainline DPS, EWAR, Covert Ops
    ship_counts: Dict[str, int]
    primary_threats: List[str]
    counter_recommendations: List[str]
    engagement_safety_score: str  # FAVORABLE, CAUTION, DISENGAGE

    @property
    def logistics_count(self) -> int:
        return self.role_counts.get("Logistics", 0)

    @property
    def tacklers_count(self) -> int:
        return self.role_counts.get("Tacklers", 0)

    @property
    def mainline_dps_count(self) -> int:
        return self.role_counts.get("Mainline DPS", 0)

    @property
    def ewar_count(self) -> int:
        return self.role_counts.get("EWAR", 0)

    @property
    def covert_ops_count(self) -> int:
        return self.role_counts.get("Covert Ops", 0)

    @property
    def counter_recommendation(self) -> str:
        return " ".join(self.counter_recommendations)
