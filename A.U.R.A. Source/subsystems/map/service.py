"""
Subsystem Service Layer for Solar System Map & Navigation.
"""

from typing import Optional, List, Dict, Any
from core.base_subsystem import BaseSubsystem
from core.events import SystemSelectedEvent, RouteCalculatedEvent
from .router import MapRouter
from .models import RouteResult, SystemNode


class MapSubsystem(BaseSubsystem):
    """Map subsystem managing solar system lookup, BFS route planning, and navigation events."""

    def __init__(self):
        super().__init__(name="MapSubsystem")
        self.router = MapRouter()

    def initialize(self) -> bool:
        return True

    def start(self) -> bool:
        super().start()
        return True

    def stop(self) -> bool:
        super().stop()
        return True

    def select_system(self, system_name: str) -> Optional[SystemNode]:
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

    def plan_route(self, origin: str, destination: str, avoid_systems: Optional[List[str]] = None) -> Optional[RouteResult]:
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
