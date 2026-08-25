"""
A.U.R.A. Event Definitions.
Defines strongly-typed dataclasses for cross-subsystem asynchronous messaging.
"""

from dataclasses import dataclass, field
import time
import uuid


@dataclass(slots=True)
class BaseEvent:
    """Base class for all system events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


# --- Intel & Threat Events ---

@dataclass(slots=True)
class IntelReportEvent(BaseEvent):
    """Fired when an intel line is ingested and parsed."""
    system: str = ""
    pilots: list[str] = field(default_factory=list)
    ship_classes: list[str] = field(default_factory=list)
    threat_level: str = "CLEAR"  # CLEAR, SUSPICIOUS, HOSTILE, CRITICAL
    raw_line: str = ""
    channel_name: str = ""
    reporter: str = ""


@dataclass(slots=True)
class ThreatAlertEvent(BaseEvent):
    """Fired when a hostile threat threshold is breached."""
    system: str = ""
    threat_level: str = "HOSTILE"
    pilots: list[str] = field(default_factory=list)
    ship_summary: str = ""
    distance_jumps: int | None = None
    trigger_sound: bool = True


@dataclass(slots=True)
class IntelStaleExpiredEvent(BaseEvent):
    """Fired when an intel report decays past its validity window."""
    system: str = ""
    expired_report_ids: list[str] = field(default_factory=list)


# --- Map & Navigation Events ---

@dataclass(slots=True)
class SystemSelectedEvent(BaseEvent):
    """Fired when user or subsystem selects a solar system."""
    system_name: str = ""
    region_name: str = ""
    constellation_name: str = ""
    security_status: float = 0.0


@dataclass(slots=True)
class RouteCalculatedEvent(BaseEvent):
    """Fired when a solar system graph route calculation finishes."""
    origin_system: str = ""
    destination_system: str = ""
    route_path: list[str] = field(default_factory=list)
    total_jumps: int = 0
    avoid_systems: list[str] = field(default_factory=list)


# --- Fleet Composition Events ---

@dataclass(slots=True)
class FleetCompUpdatedEvent(BaseEvent):
    """Fired when fleet composition parser or manual D-scan is evaluated."""
    total_ships: int = 0
    role_counts: dict[str, int] = field(default_factory=dict)  # Logistics, Tacklers, Mainline DPS, EWAR, Covert Ops
    ship_counts: dict[str, int] = field(default_factory=dict)
    primary_threats: list[str] = field(default_factory=list)
    counter_recommendations: list[str] = field(default_factory=list)


# --- Fitting Events ---

@dataclass(slots=True)
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

@dataclass(slots=True)
class InferenceStreamTokenEvent(BaseEvent):
    """Fired when llama.cpp yields a token during async generation."""
    request_id: str = ""
    token: str = ""


@dataclass(slots=True)
class InferenceCompletedEvent(BaseEvent):
    """Fired when local GGUF inference completes generation."""
    request_id: str = ""
    full_response: str = ""
    tokens_per_second: float = 0.0
    total_tokens: int = 0


# --- Wormhole Mapping Events ---

@dataclass(slots=True)
class WormholeChainUpdatedEvent(BaseEvent):
    """Fired when an active wormhole chain structure or topology changes."""
    chain_id: str = ""
    home_system: str = ""
    total_nodes: int = 0
    total_connections: int = 0


@dataclass(slots=True)
class WormholeSystemAddedEvent(BaseEvent):
    """Fired when a new system is mapped into the chain."""
    chain_id: str = ""
    system_name: str = ""
    system_class: str = "Unknown"
    parent_system: str = ""
    is_home: bool = False


@dataclass(slots=True)
class WormholeConnectionUpdatedEvent(BaseEvent):
    """Fired when a wormhole connection state (mass/time/lock) changes."""
    chain_id: str = ""
    connection_id: str = ""
    source_system: str = ""
    target_system: str = ""
    wormhole_type: str = ""
    mass_state: str = "Stage 1 (>50%)"
    lifetime_state: str = "Stable"


@dataclass(slots=True)
class CosmicSignatureUpdatedEvent(BaseEvent):
    """Fired when a signature is added, scanned, or deleted in a system."""
    chain_id: str = ""
    system_name: str = ""
    sig_id: str = ""
    sig_group: str = "Unscanned"
    sig_name: str = ""
    signal_strength: float = 0.0


# --- XMPP Tactical Communications Events ---

@dataclass(slots=True)
class XMPPConnectionStateChangedEvent(BaseEvent):
    """Fired when XMPP client connection state transitions."""
    state: str = "DISCONNECTED"
    jid: str = ""
    server: str = ""
    error_message: str = ""


@dataclass(slots=True)
class XMPPMessageReceivedEvent(BaseEvent):
    """Fired when a new XMPP direct or groupchat message arrives."""
    msg_id: str = ""
    sender_jid: str = ""
    sender_nick: str = ""
    room_jid: str = ""
    body: str = ""
    is_broadcast: bool = False
    priority: str = "INFO"


@dataclass(slots=True)
class XMPPBroadcastAlertEvent(BaseEvent):
    """Fired when an alliance fleet broadcast ping is detected and parsed."""
    msg_id: str = ""
    sender_nick: str = ""
    target_system: str = ""
    doctrine_ships: list[str] = field(default_factory=list)
    fc_name: str = ""
    formup_timer: str = ""
    priority: str = "STRATOP"
    raw_text: str = ""


@dataclass(slots=True)
class XMPPRoomJoinedEvent(BaseEvent):
    """Fired when XMPP client successfully joins a MUC room or broadcast channel."""
    room_jid: str = ""
    nickname: str = ""
    subject: str = ""


@dataclass(slots=True)
class XMPPRosterUpdatedEvent(BaseEvent):
    """Fired when XMPP roster contacts or presence statuses change."""
    contacts_count: int = 0

