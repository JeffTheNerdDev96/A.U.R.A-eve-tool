"""
Map Subsystem Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SystemNode:
    """Immutable record for a solar system in the map graph."""
    system_id: int
    name: str
    region: str
    security: float


@dataclass(frozen=True)
class RouteResult:
    """Immutable record for a calculated jump route."""
    origin: str
    destination: str
    path: List[str]
    total_jumps: int
    security_min: float
    security_avg: float
    avoided_systems: List[str] = field(default_factory=list)

    @property
    def start_system(self) -> str:
        return self.origin

    @property
    def destination_system(self) -> str:
        return self.destination
