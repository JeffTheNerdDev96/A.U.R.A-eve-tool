"""
A.U.R.A. XMPP Chat Subsystem.
Modular out-of-game tactical messaging and alliance broadcast stream receiver.
"""

from .models import (
    XMPPConnectionState,
    XMPPMessageType,
    XMPPBroadcastPriority,
    XMPPAccountConfig,
    XMPPBroadcastPing,
    XMPPMessage,
    XMPPMUCChannel,
    XMPPRosterContact,
)
from .client import XMPPProtocolAdapter, parse_broadcast_ping
from .service import XMPPChatSubsystem

__all__ = [
    "XMPPChatSubsystem",
    "XMPPConnectionState",
    "XMPPMessageType",
    "XMPPBroadcastPriority",
    "XMPPAccountConfig",
    "XMPPBroadcastPing",
    "XMPPMessage",
    "XMPPMUCChannel",
    "XMPPRosterContact",
    "XMPPProtocolAdapter",
    "parse_broadcast_ping",
]
