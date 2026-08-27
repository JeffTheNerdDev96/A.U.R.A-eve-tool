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
