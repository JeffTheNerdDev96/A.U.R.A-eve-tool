"""
Fleet Composition Models & DTOs.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FleetCompAnalysis:
    """Immutable DTO holding parsed fleet role breakdown and counter recommendations."""
    total_ships: int
    role_counts: dict[str, int]  # Logistics, Tacklers, Strategic Cruisers, Mainline DPS, T2 Recons / EAS, Covert Ops
    ship_counts: dict[str, int]
    primary_threats: list[str]
    counter_recommendations: list[str]
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
    def t3c_count(self) -> int:
        return self.role_counts.get("Strategic Cruisers", 0)

    @property
    def recon_count(self) -> int:
        return self.role_counts.get("T2 Recons / EAS", 0)

    @property
    def ewar_count(self) -> int:
        return self.role_counts.get("T2 Recons / EAS", 0) or self.role_counts.get("EWAR", 0)

    @property
    def covert_ops_count(self) -> int:
        return self.role_counts.get("Covert Ops", 0)

    @property
    def counter_recommendation(self) -> str:
        return " ".join(self.counter_recommendations)
