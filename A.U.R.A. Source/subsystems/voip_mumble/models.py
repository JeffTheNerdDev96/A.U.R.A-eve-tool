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
A.U.R.A. VOIP (Mumble) Subsystem Data Models & Session Contracts.
Ephemeral alliance voice configuration, channel tree, and peer state.
OPERATIONAL SECURITY: credentials exist strictly in volatile memory and are
wiped on disconnect, purge, or application exit. Never persisted to disk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class VOIPConnectionState(StrEnum):
    """Lifecycle states of the Mumble voice client session."""
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    AUTHENTICATING = "Authenticating"
    CONNECTED = "Connected"
    DISCONNECTING = "Disconnecting"
    ERROR = "Error"


class VOIPMessageType(StrEnum):
    """Categorization of VOIP text traffic."""
    CHANNEL = "Channel Message"
    DIRECT = "Direct Message"
    SYSTEM = "System Notice"


@dataclass(slots=True)
class VOIPAccountConfig:
    """
    In-memory account parameters for a Mumble session.
    OPERATIONAL SECURITY: This object is NEVER persisted to disk, registry,
    or config files. Wiped on disconnect via wipe_credentials().
    """
    host: str = ""                       # e.g. "mumble.alliance.net"
    port: int = 64738                    # Default Mumble TCP/TLS port
    username: str = ""                   # Pilot display name
    password: str = ""                   # Server password, wiped on session end
    channel_path: str = ""               # e.g. "Fleet 1" (auto-join target)
    tokens: list[str] = field(default_factory=list)  # Channel access tokens
    allow_self_signed_tls: bool = False  # Explicit opt-in for internal CAs
    auto_reconnect: bool = False         # pymumble reconnect flag (default off)

    def wipe_credentials(self) -> None:
        """Zero secret fields so reconnect cannot reuse them."""
        self.password = ""
        self.tokens = []


@dataclass(slots=True)
class VOIPChannel:
    """Represents a Mumble voice channel node."""
    channel_id: int = 0
    name: str = ""
    path: str = ""
    parent_id: int = -1
    description: str = ""
    user_count: int = 0
    is_temporary: bool = False


@dataclass(slots=True)
class VOIPUser:
    """Represents a connected Mumble peer."""
    session_id: int = 0
    name: str = ""
    channel_id: int = 0
    is_muted: bool = False
    is_deafened: bool = False
    is_self_muted: bool = False
    is_self_deafened: bool = False
    is_speaking: bool = False
    is_self: bool = False


@dataclass(slots=True)
class VOIPTextMessage:
    """Represents a Mumble channel or direct text message."""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    channel_name: str = ""
    body: str = ""
    msg_type: VOIPMessageType = VOIPMessageType.CHANNEL
    is_self: bool = False
    timestamp: float = field(default_factory=time.time)
