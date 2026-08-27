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
Intel & Threat Data Models.
"""

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class ThreatLevel(StrEnum):
    CLEAR = "CLEAR"
    SUSPICIOUS = "SUSPICIOUS"
    HOSTILE = "HOSTILE"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class IntelReport:
    """Immutable data record representing a single parsed intel message."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_name: str = ""
    reporter: str = ""
    channel: str = ""
    timestamp_str: str = ""
    created_at: float = field(default_factory=time.time)
    threat_level: str = "CLEAR"  # CLEAR, SUSPICIOUS, HOSTILE, CRITICAL
    pilots: list[str] = field(default_factory=list)
    ship_classes: list[str] = field(default_factory=list)
    raw_message: str = ""
    pilot_count: int = 1
    has_cyno: bool = False
    has_bubble: bool = False
    is_clear: bool = False

    @property
    def system(self) -> str:
        return self.system_name

    @property
    def ships(self) -> list[str]:
        return self.ship_classes


@dataclass(slots=True)
class ThreatStatus:
    """Active threat status summary for a solar system."""
    system_name: str
    threat_level: str = "CLEAR"
    active_reports: list[IntelReport] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    hostile_count: int = 0

    CLEAR = "CLEAR"
    SUSPICIOUS = "SUSPICIOUS"
    HOSTILE = "HOSTILE"
    CRITICAL = "CRITICAL"
