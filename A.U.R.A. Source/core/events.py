"""
A.U.R.A. Event Definitions.
Defines strongly-typed dataclasses for cross-subsystem asynchronous messaging.
"""

from dataclasses import dataclass, field
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class BaseEvent:
    """Base class for all system events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


# --- Intel & Threat Events ---

@dataclass
class IntelReportEvent(BaseEvent):
    """Fired when an intel line is ingested and parsed."""
    system: str = ""
    pilots: List[str] = field(default_factory=list)
    ship_classes: List[str] = field(default_factory=list)
    threat_level: str = "CLEAR"  # CLEAR, SUSPICIOUS, HOSTILE, CRITICAL
    raw_line: str = ""
    channel_name: str = ""
    reporter: str = ""


@dataclass
class ThreatAlertEvent(BaseEvent):
    """Fired when a hostile threat threshold is breached."""
    system: str = ""
    threat_level: str = "HOSTILE"
    pilots: List[str] = field(default_factory=list)
    ship_summary: str = ""
    distance_jumps: Optional[int] = None
    trigger_sound: bool = True


@dataclass
class IntelStaleExpiredEvent(BaseEvent):
    """Fired when an intel report decays past its validity window."""
    system: str = ""
    expired_report_ids: List[str] = field(default_factory=list)


# --- Map & Navigation Events ---

@dataclass
class SystemSelectedEvent(BaseEvent):
    """Fired when user or subsystem selects a solar system."""
    system_name: str = ""
    region_name: str = ""
    constellation_name: str = ""
    security_status: float = 0.0


@dataclass
class RouteCalculatedEvent(BaseEvent):
    """Fired when a solar system graph route calculation finishes."""
    origin_system: str = ""
    destination_system: str = ""
    route_path: List[str] = field(default_factory=list)
    total_jumps: int = 0
    avoid_systems: List[str] = field(default_factory=list)


# --- Fleet Composition Events ---

@dataclass
class FleetCompUpdatedEvent(BaseEvent):
    """Fired when fleet composition parser or manual D-scan is evaluated."""
    total_ships: int = 0
    role_counts: Dict[str, int] = field(default_factory=dict)  # Logistics, Tacklers, Mainline DPS, EWAR, Covert Ops
    ship_counts: Dict[str, int] = field(default_factory=dict)
    primary_threats: List[str] = field(default_factory=list)
    counter_recommendations: List[str] = field(default_factory=list)


# --- Fitting Events ---

@dataclass
class FittingCalculatedEvent(BaseEvent):
    """Fired when a fitting configuration math calculation is completed."""
    ship_name: str = ""
    fit_name: str = ""
    effective_hp: float = 0.0
    total_dps: float = 0.0
    cap_stable: bool = False
    cap_time_seconds: float = 0.0
    cpu_usage_pct: float = 0.0
    powergrid_usage_pct: float = 0.0


# --- AI / Neural Inference Events ---

@dataclass
class InferenceStreamTokenEvent(BaseEvent):
    """Fired when llama.cpp yields a token during async generation."""
    request_id: str = ""
    token: str = ""


@dataclass
class InferenceCompletedEvent(BaseEvent):
    """Fired when local GGUF inference completes generation."""
    request_id: str = ""
    full_response: str = ""
    tokens_per_second: float = 0.0
    total_tokens: int = 0
