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
Subsystem Service Layer for Solar System Map & Navigation.
"""

from typing import override
from core.base_subsystem import BaseSubsystem
from core.events import SystemSelectedEvent, RouteCalculatedEvent
from .router import MapRouter
from .models import RouteResult, SystemNode


class MapSubsystem(BaseSubsystem):
    """Map subsystem managing solar system lookup, BFS route planning, and navigation events."""

    def __init__(self):
        super().__init__(name="MapSubsystem")
        self.router = MapRouter()

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

    def select_system(self, system_name: str) -> SystemNode | None:
        """Looks up system and emits SystemSelectedEvent over EventBus."""
        node = self.router.get_system(system_name)
        if not node:
            return None

        evt = SystemSelectedEvent(
            system_name=node.name,
            region_name=node.region,
            security_status=node.security
        )
        self.event_bus.publish(evt)
        return node

    def plan_route(self, origin: str, destination: str, avoid_systems: list[str] | None = None) -> RouteResult | None:
        """Calculates route and emits RouteCalculatedEvent over EventBus."""
        result = self.router.calculate_route(origin, destination, avoid_systems=avoid_systems)
        if not result:
            return None

        evt = RouteCalculatedEvent(
            origin_system=result.origin,
            destination_system=result.destination,
            route_path=result.path,
            total_jumps=result.total_jumps,
            avoid_systems=result.avoided_systems
        )
        self.event_bus.publish(evt)
        return result

    calculate_route = plan_route
    find_route = plan_route
