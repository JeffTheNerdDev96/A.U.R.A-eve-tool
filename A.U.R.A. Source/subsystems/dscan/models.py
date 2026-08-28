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
A.U.R.A. Directional Scan (D-Scan) Subsystem Models & Data Contracts.
"""

from dataclasses import dataclass, field
import time


@dataclass(slots=True)
class DScanEntry:
    """Represents an individual item or ship detected on Directional Scan."""
    name: str
    item_type: str
    ship_class: str = "Unknown"
    distance_str: str = "D-Scan Sphere (< 14.3 AU)"
    distance_km: float | None = None
    count: int = 1
    threat_level: str = "COMBATANT"
    is_ship: bool = True
    role: str = ""
    tactics: str = ""


@dataclass(slots=True)
class DScanClassSummary:
    """
    Represents an aggregated group of ships under a single ship class.
    Example: Heavy Assault Cruiser : 3 : Muninn, Cerberus x2
    """
    ship_class: str
    total_count: int
    ship_counts: dict[str, int] = field(default_factory=dict)
    breakdown_str: str = ""
    primary_threat: str = "COMBATANT"
    sample_distances: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DScanAnalysis:
    """Represents the full aggregated analysis of a Directional Scan paste."""
    total_ships: int = 0
    class_summaries: list[DScanClassSummary] = field(default_factory=list)
    ship_counts: dict[str, int] = field(default_factory=dict)
    class_counts: dict[str, int] = field(default_factory=dict)
    threat_level: str = "CLEAR"
    threat_color: str = "#34d399"
    range_brackets: dict[str, int] = field(default_factory=dict)
    raw_entries: list[DScanEntry] = field(default_factory=list)
    summary_text: str = ""
    created_at: float = field(default_factory=time.time)
