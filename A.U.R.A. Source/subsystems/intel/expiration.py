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
Subsystem Stale Intel Expiration Manager.
Decays threat levels and purges expired intel reports gracefully over time.
"""

import time
from typing import Dict, List, Optional
from .models import IntelReport, ThreatStatus

# Module-level: these were rebuilt as dict literals inside add_report() and
# prune_expired() on every call (twice per prune pass per system).
_THREAT_RANKS = {"CLEAR": 0, "INFO": 1, "LOW": 1, "SUSPICIOUS": 1,
                 "MEDIUM": 2, "HIGH": 3, "HOSTILE": 3, "CRITICAL": 4}
_INV_RANKS = {0: "CLEAR", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}


def _recompute_status(status: "ThreatStatus") -> None:
    """Recompute threat level and hostile count from the active report set."""
    status.threat_level = _INV_RANKS[max(
        (_THREAT_RANKS.get(r.threat_level, 0) for r in status.active_reports), default=0)]
    status.hostile_count = sum(r.pilot_count for r in status.active_reports)


class StaleIntelManager:
    """
    Manages solar system threat statuses, tracking report lifetimes and demoting
    system threat levels as intel reports age out.
    """

    def __init__(self, expiration_seconds: float = 900.0):  # Default 15 minutes
        self.expiration_seconds = expiration_seconds
        self._system_statuses: Dict[str, ThreatStatus] = {}

    def add_report(self, report: IntelReport) -> ThreatStatus:
        """Incorporates a new IntelReport and updates the system's ThreatStatus."""
        sys_name = report.system_name
        if sys_name not in self._system_statuses:
            self._system_statuses[sys_name] = ThreatStatus(system_name=sys_name)

        status = self._system_statuses[sys_name]

        if report.is_clear:
            status.active_reports.clear()
            status.threat_level = "CLEAR"
            status.hostile_count = 0
        else:
            status.active_reports.append(report)
            _recompute_status(status)

        status.last_updated = time.time()
        return status

    def prune_expired(self, current_time: Optional[float] = None) -> List[str]:
        """
        Purges reports older than expiration_seconds.
        Returns list of solar system names whose threat status changed.
        """
        now = current_time or time.time()
        modified_systems: List[str] = []

        for sys_name, status in list(self._system_statuses.items()):
            initial_count = len(status.active_reports)
            status.active_reports = [
                r for r in status.active_reports
                if (now - r.created_at) < self.expiration_seconds
            ]
            if len(status.active_reports) != initial_count:
                modified_systems.append(sys_name)
                if not status.active_reports:
                    status.threat_level = "CLEAR"
                    status.hostile_count = 0
                    self._system_statuses.pop(sys_name, None)
                else:
                    _recompute_status(status)

        return modified_systems

    def get_status(self, system_name: str) -> Optional[ThreatStatus]:
        """Returns threat status for a system."""
        return self._system_statuses.get(system_name)

    def get_all_active_threats(self) -> Dict[str, ThreatStatus]:
        """Returns dict of system threat statuses."""
        return self._system_statuses
