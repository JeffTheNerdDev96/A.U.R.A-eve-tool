"""
Fitting Subsystem Data Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class FittingSlotLayout:
    high_slots: List[str] = field(default_factory=list)
    mid_slots: List[str] = field(default_factory=list)
    low_slots: List[str] = field(default_factory=list)
    rig_slots: List[str] = field(default_factory=list)
    subsystems: List[str] = field(default_factory=list)
    drones: List[str] = field(default_factory=list)
    cargo: List[str] = field(default_factory=list)


@dataclass
class ParsedFitting:
    ship_name: str = ""
    fit_name: str = ""
    slots: FittingSlotLayout = field(default_factory=FittingSlotLayout)
    raw_eft: str = ""
    stats: Dict[str, Any] = field(default_factory=dict)
