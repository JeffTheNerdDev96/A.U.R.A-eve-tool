"""
Subsystem Service Layer for Intel & Threat Assessment.
Extends BaseSubsystem, monitoring live chat logs and emitting EventBus events.
"""

from typing import override
from core.base_subsystem import BaseSubsystem, SubsystemStatus
from core.events import IntelReportEvent, ThreatAlertEvent, IntelStaleExpiredEvent
from .parser import IntelRegexParser
from .expiration import StaleIntelManager
from .models import IntelReport


class IntelSubsystem(BaseSubsystem):
    """
    Intel Subsystem managing chat log parsing, threat tracking, and event dispatches.
    """

    def __init__(self, expiration_seconds: float = 900.0):
        super().__init__(name="IntelSubsystem")
        self.parser = IntelRegexParser()
        self.stale_manager = StaleIntelManager(expiration_seconds=expiration_seconds)

    @override
    def initialize(self) -> bool:
        """Initialize resources and prepare subsystem state."""
        return True

    @override
    def start(self) -> bool:
        """Start monitoring."""
        super().start()
        return True

    @override
    def stop(self) -> bool:
        """Stop monitoring."""
        super().stop()
        return True

    def process_intel_line(self, line: str, channel_name: str = "Intel") -> list[IntelReport]:
        rep = self.process_raw_line(line, channel_name)
        return [rep] if rep else []

    def process_raw_line(self, line: str, channel_name: str = "Intel") -> IntelReport | None:
        """
        Processes a raw chat log line.
        On success, emits IntelReportEvent and ThreatAlertEvent over EventBus.
        """
        report = self.parser.parse_line(line, channel_name=channel_name)
        if not report:
            return None

        status = self.stale_manager.add_report(report)

        # Emit IntelReportEvent
        evt = IntelReportEvent(
            system=report.system_name,
            pilots=report.pilots,
            ship_classes=report.ship_classes,
            threat_level=report.threat_level,
            raw_line=report.raw_message,
            channel_name=report.channel,
            reporter=report.reporter
        )
        self.event_bus.publish(evt)

        # Emit ThreatAlertEvent if threat level is HOSTILE or CRITICAL
        if report.threat_level in ("HOSTILE", "CRITICAL"):
            alert_evt = ThreatAlertEvent(
                system=report.system_name,
                threat_level=report.threat_level,
                pilots=report.pilots,
                ship_summary=", ".join(report.ship_classes) if report.ship_classes else f"{report.pilot_count} pilot(s)",
                trigger_sound=True
            )
            self.event_bus.publish(alert_evt)

        return report

    def tick_expiration(self) -> None:
        """Periodic tick to prune expired reports and dispatch notifications."""
        expired_systems = self.stale_manager.prune_expired()
        if expired_systems:
            evt = IntelStaleExpiredEvent(
                system=expired_systems[0],
                expired_report_ids=expired_systems
            )
            self.event_bus.publish(evt)

    @override
    def get_status(self) -> SubsystemStatus:
        base_status = super().get_status()
        base_status.update({
            "tracked_systems": len(self.stale_manager.get_all_active_threats())
        })
        return base_status
