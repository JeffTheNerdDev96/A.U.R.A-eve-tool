"""
Fitting Subsystem Data Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FittingSlotLayout:
    high_slots: list[str] = field(default_factory=list)
    mid_slots: list[str] = field(default_factory=list)
    low_slots: list[str] = field(default_factory=list)
    rig_slots: list[str] = field(default_factory=list)
    subsystems: list[str] = field(default_factory=list)
    drones: list[str] = field(default_factory=list)
    cargo: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParsedFitting:
    ship_name: str = ""
    fit_name: str = ""
    slots: FittingSlotLayout = field(default_factory=FittingSlotLayout)
    raw_eft: str = ""
    stats: dict[str, Any] = field(default_factory=dict)
