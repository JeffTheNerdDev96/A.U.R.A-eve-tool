"""
A.U.R.A. XMPP Chat Subsystem Models & Data Contracts.
Provides strongly-typed data structures for New Eden alliance XMPP communication.
"""

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class XMPPConnectionState(StrEnum):
    """Lifecycle states of the XMPP client session."""
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    AUTHENTICATING = "Authenticating"
    CONNECTED = "Connected"
    DISCONNECTING = "Disconnecting"
    ERROR = "Error"


class XMPPMessageType(StrEnum):
    """Categorization of received XMPP messages."""
    DIRECT = "Direct Message"
    GROUPCHAT = "Groupchat (MUC)"
    BROADCAST = "Alliance Broadcast"
    SYSTEM = "System Notice"


class XMPPBroadcastPriority(StrEnum):
    """Urgency level of alliance tactical pings."""
    INFO = "Info"
    FLEET_FORMUP = "Fleet Formup"
    STRATOP = "Strategic Operation (StratOp)"
    CTA = "Call to Arms (CTA)"
    STAND_DOWN = "Stand Down"


@dataclass(slots=True)
class XMPPAccountConfig:
    """
    In-memory account parameters for XMPP session authentication.
    OPERATIONAL SECURITY: This object is NEVER persisted to disk, registry, or config files.
    """
    jid: str = ""                         # e.g. "pilot@goonfleet.com" or "user@xmpp.pandemic-horde.org"
    password: str = ""                     # In-memory plain string, wiped on session termination
    host_override: str = ""                # Explicit server IP/hostname if SRV lookup is unavailable
    port: int = 5222                       # Default 5222 (STARTTLS) or 5223 (Direct TLS)
    use_tls: bool = True                   # Enforce TLS encryption
    allow_self_signed_tls: bool = False    # Allow internal alliance / self-signed certificates
    nickname: str = ""                     # Custom MUC nickname or fallback to JID node
    resource: str = "AURA-Client"          # XMPP resource identifier
    auto_reconnect: bool = True            # Silently re-establish connection on transient drop
    auto_join_rooms: list[str] = field(default_factory=list)  # Default MUC rooms (e.g. broadcasts)

    @property
    def domain(self) -> str:
        if "@" in self.jid:
            return self.jid.split("@", 1)[1].split("/", 1)[0]
        return ""

    @property
    def username(self) -> str:
        if "@" in self.jid:
            return self.jid.split("@", 1)[0]
        return self.jid


@dataclass(slots=True)
class XMPPBroadcastPing:
    """Parsed New Eden fleet ping extracted from broadcast bot messages."""
    target_system: str = ""
    doctrine_ships: list[str] = field(default_factory=list)
    fc_name: str = ""
    formup_timer: str = ""
    pap_link: str = ""
    mumble_channel: str = ""
    priority: XMPPBroadcastPriority = XMPPBroadcastPriority.INFO
    raw_body: str = ""


@dataclass(slots=True)
class XMPPMessage:
    """Represents an incoming or outgoing XMPP message."""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_jid: str = ""
    sender_nick: str = ""
    room_jid: str = ""                    # Blank for direct 1-on-1 messages
    body: str = ""
    msg_type: XMPPMessageType = XMPPMessageType.DIRECT
    is_broadcast: bool = False
    priority: XMPPBroadcastPriority = XMPPBroadcastPriority.INFO
    broadcast_ping: XMPPBroadcastPing | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class XMPPMUCChannel:
    """Represents a Multi-User Chat room or broadcast channel."""
    room_jid: str = ""                    # e.g. "broadcasts@conference.goonfleet.com"
    name: str = ""                        # Friendly display name
    topic: str = ""
    auto_join: bool = True
    is_broadcast_channel: bool = False
    unread_count: int = 0
    members: list[str] = field(default_factory=list)


@dataclass(slots=True)
class XMPPRosterContact:
    """Represents a contact pilot on the XMPP roster."""
    jid: str = ""
    name: str = ""
    subscription: str = "both"
    presence_show: str = "available"      # available, chat, away, dnd, xa, offline
    presence_status: str = ""
