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
