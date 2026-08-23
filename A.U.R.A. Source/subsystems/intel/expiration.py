"""
Subsystem Stale Intel Expiration Manager.
Decays threat levels and purges expired intel reports gracefully over time.
"""

import time
from typing import Dict, List, Optional
from .models import IntelReport, ThreatStatus


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
            status.hostile_count += report.pilot_count
            # Re-evaluate maximum threat level among active reports
            threat_ranks = {"CLEAR": 0, "SUSPICIOUS": 1, "HOSTILE": 2, "CRITICAL": 3}
            highest_rank = max((threat_ranks.get(r.threat_level, 0) for r in status.active_reports), default=0)
            inv_ranks = {0: "CLEAR", 1: "SUSPICIOUS", 2: "HOSTILE", 3: "CRITICAL"}
            status.threat_level = inv_ranks[highest_rank]

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
                else:
                    threat_ranks = {"CLEAR": 0, "SUSPICIOUS": 1, "HOSTILE": 2, "CRITICAL": 3}
                    highest_rank = max((threat_ranks.get(r.threat_level, 0) for r in status.active_reports), default=0)
                    inv_ranks = {0: "CLEAR", 1: "SUSPICIOUS", 2: "HOSTILE", 3: "CRITICAL"}
                    status.threat_level = inv_ranks[highest_rank]
                    status.hostile_count = sum(r.pilot_count for r in status.active_reports)

        return modified_systems

    def get_status(self, system_name: str) -> Optional[ThreatStatus]:
        """Returns threat status for a system."""
        return self._system_statuses.get(system_name)

    def get_all_active_threats(self) -> Dict[str, ThreatStatus]:
        """Returns dict of system threat statuses."""
        return self._system_statuses
