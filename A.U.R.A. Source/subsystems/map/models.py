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
Map Subsystem Models & DTOs.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SystemNode:
    """Immutable record for a solar system in the map graph."""
    system_id: int
    name: str
    region: str
    security: float


@dataclass(frozen=True, slots=True)
class RouteResult:
    """Immutable record for a calculated jump route."""
    origin: str
    destination: str
    path: list[str]
    total_jumps: int
    security_min: float
    security_avg: float
    avoided_systems: list[str] = field(default_factory=list)

    @property
    def start_system(self) -> str:
        return self.origin

    @property
    def destination_system(self) -> str:
        return self.destination
