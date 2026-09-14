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
Intel subsystem: parse chat lines, track reports, publish EventBus events.
"""

from typing import override
import time

from core.base_subsystem import BaseSubsystem, SubsystemStatus
from core.events import IntelReportEvent, ThreatAlertEvent, IntelStaleExpiredEvent
from .parser import IntelParser
from .expiration import StaleIntelManager
from .models import IntelReport


class IntelSubsystem(BaseSubsystem):
    """Parse intel lines, retain active reports, and dispatch radar/map events."""

    def __init__(self, expiration_seconds: float = 900.0):
        super().__init__(name="IntelSubsystem")
        self.stale_manager = StaleIntelManager(expiration_seconds=expiration_seconds)
        self._recent_intel_hashes: dict[str, float] = {}

    @property
    def active_reports(self) -> list[IntelReport]:
        reports: list[IntelReport] = []
        for status in self.stale_manager.get_all_active_threats().values():
            reports.extend(status.active_reports)
        return reports

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

    def process_intel_line(self, line: str, channel_name: str = "Intel") -> list[IntelReport]:
        rep = self.process_raw_line(line, channel_name)
        return [rep] if rep else []

    def process_raw_line(self, line: str, channel_name: str = "Intel") -> IntelReport | None:
        """Parse a raw chat log line once, store it, and publish intel events."""
        parsed = IntelParser.parse_single_line(line, channel_name=channel_name)
        if not parsed:
            return None

        time_key = parsed.get("time_str") or parsed.get("timestamp") or ""
        speaker_key = (parsed.get("speaker") or "").lower()
        clean_msg_key = (parsed.get("clean_msg") or "").lower()
        ch_key = (parsed.get("channel") or channel_name).lower()
        dedup_key = f"{ch_key}|{speaker_key}|{time_key}|{clean_msg_key}"
        now = time.time()
        if now - self._recent_intel_hashes.get(dedup_key, 0.0) < 25.0:
            return None
        self._recent_intel_hashes[dedup_key] = now
        if len(self._recent_intel_hashes) > 400:
            cutoff = now - 60.0
            self._recent_intel_hashes = {k: v for k, v in self._recent_intel_hashes.items() if v >= cutoff}

        report = IntelReport(
            system_name=parsed.get("system", ""),
            reporter=parsed.get("speaker", "Unknown"),
            channel=parsed.get("channel", channel_name),
            timestamp_str=parsed.get("time_str", ""),
            threat_level=parsed.get("threat_level", "CLEAR"),
            pilots=parsed.get("pilots", []),
            ship_classes=parsed.get("ships", []),
            raw_message=parsed.get("clean_msg", ""),
            pilot_count=int(parsed.get("est_count") or parsed.get("pilot_count") or 1),
            has_cyno=bool(parsed.get("has_cyno")),
            has_bubble=bool(parsed.get("has_bubble")),
            is_clear=bool(parsed.get("is_clear")),
        )
        self.stale_manager.add_report(report)

        evt = IntelReportEvent(
            system=report.system_name,
            pilots=list(report.pilots),
            ship_classes=list(report.ship_classes),
            threat_level=report.threat_level,
            raw_line=line,
            channel_name=report.channel,
            reporter=report.reporter,
            time_str=report.timestamp_str,
            clean_msg=report.raw_message,
            status_flags=list(parsed.get("status_flags") or []),
            has_cyno=report.has_cyno,
            has_bubble=report.has_bubble,
            is_clear=report.is_clear,
            is_critical=bool(parsed.get("is_critical")),
            pilot_count=report.pilot_count,
            payload=parsed,
        )
        self.event_bus.publish(evt)

        if parsed.get("is_critical") or report.threat_level in ("HOSTILE", "CRITICAL", "HIGH"):
            ships = report.ship_classes
            self.event_bus.publish(
                ThreatAlertEvent(
                    system=report.system_name,
                    threat_level=report.threat_level,
                    pilots=list(report.pilots),
                    ship_summary=", ".join(ships) if ships else f"{report.pilot_count} pilot(s)",
                    trigger_sound=True,
                    payload=parsed,
                )
            )

        return report

    def tick_expiration(self) -> None:
        """Periodic tick to prune expired reports and dispatch notifications."""
        expired_systems = self.stale_manager.prune_expired()
        if expired_systems:
            self.event_bus.publish(
                IntelStaleExpiredEvent(
                    system=expired_systems[0],
                    expired_report_ids=expired_systems,
                )
            )

    @override
    def get_status(self) -> SubsystemStatus:
        base_status = super().get_status()
        base_status.update({
            "tracked_systems": len(self.stale_manager.get_all_active_threats())
        })
        return base_status
