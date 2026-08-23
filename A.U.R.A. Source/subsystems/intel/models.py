"""
Intel & Threat Data Models.
"""

from dataclasses import dataclass, field
import time
import uuid
from typing import List, Optional


class ThreatLevel:
    CLEAR = "CLEAR"
    SUSPICIOUS = "SUSPICIOUS"
    HOSTILE = "HOSTILE"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class IntelReport:
    """Immutable data record representing a single parsed intel message."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_name: str = ""
    reporter: str = ""
    channel: str = ""
    timestamp_str: str = ""
    created_at: float = field(default_factory=time.time)
    threat_level: str = "CLEAR"  # CLEAR, SUSPICIOUS, HOSTILE, CRITICAL
    pilots: List[str] = field(default_factory=list)
    ship_classes: List[str] = field(default_factory=list)
    raw_message: str = ""
    pilot_count: int = 1
    has_cyno: bool = False
    has_bubble: bool = False
    is_clear: bool = False

    @property
    def system(self) -> str:
        return self.system_name

    @property
    def ships(self) -> List[str]:
        return self.ship_classes


@dataclass
class ThreatStatus:
    """Active threat status summary for a solar system."""
    system_name: str
    threat_level: str = "CLEAR"
    active_reports: List[IntelReport] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    hostile_count: int = 0

    CLEAR = "CLEAR"
    SUSPICIOUS = "SUSPICIOUS"
    HOSTILE = "HOSTILE"
    CRITICAL = "CRITICAL"
