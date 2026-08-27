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
A.U.R.A. XMPP Chat Subsystem Service Layer.
Encapsulates connection lifecycle, MUC rooms, message history buffering,
and EventBus cross-subsystem event publishing.
"""

from __future__ import annotations

from typing import Any, override
import time

from core.base_subsystem import BaseSubsystem
from core.events import (
    XMPPConnectionStateChangedEvent,
    XMPPMessageReceivedEvent,
    XMPPBroadcastAlertEvent,
    XMPPRoomJoinedEvent,
    XMPPRosterUpdatedEvent,
)
from .models import (
    XMPPAccountConfig,
    XMPPConnectionState,
    XMPPMessage,
    XMPPMessageType,
    XMPPBroadcastPing,
    XMPPBroadcastPriority,
    XMPPMUCChannel,
    XMPPRosterContact,
)
from .client import XMPPProtocolAdapter, parse_broadcast_ping


class XMPPChatSubsystem(BaseSubsystem):
    """
    Subsystem Service Layer for Alliance XMPP Chat & Fleet Broadcast Ingestion.
    Maintains ephemeral in-memory communication state, strictly non-persistent credentials,
    and event publishing to the main application bus.
    """

    MAX_HISTORY_MESSAGES = 500

    def __init__(self):
        super().__init__(name="XMPPChatSubsystem")
        self.client = XMPPProtocolAdapter(
            on_state_change=self._handle_client_state_change,
            on_message_received=self._handle_client_message,
            on_room_joined=self._handle_client_room_joined,
            on_roster_updated=self._handle_client_roster_updated,
        )
        self.active_config: XMPPAccountConfig | None = None
        self.messages: list[XMPPMessage] = []
        self.channels: dict[str, XMPPMUCChannel] = {}
        self.roster: dict[str, XMPPRosterContact] = {}

    @override
    def initialize(self) -> bool:
        """Initializes internal collections and default alliance rooms."""
        self.messages.clear()
        self.channels.clear()
        self.roster.clear()

        # Seed standard alliance broadcast channel placeholder
        default_bcast = XMPPMUCChannel(
            room_jid="broadcasts@conference.alliance.net",
            name="Alliance Broadcasts",
            topic="Official Alliance Strategic Fleet Notifications",
            auto_join=True,
            is_broadcast_channel=True,
            unread_count=0,
        )
        self.channels[default_bcast.room_jid] = default_bcast
        return True

    @override
    def start(self) -> bool:
        """Arms the subsystem for active connection sessions."""
        super().start()
        return True

    @override
    def stop(self) -> bool:
        """Disconnects active socket session and purges ephemeral memory."""
        self.disconnect()
        self.messages.clear()
        self.active_config = None
        super().stop()
        return True

    def connect(self, config: XMPPAccountConfig) -> bool:
        """
        Initiates connection with provided ephemeral account configuration.
        Credentials exist strictly in volatile memory.
        """
        self.active_config = config
        return self.client.connect(config)

    def disconnect(self) -> None:
        """Terminates active XMPP connection and purges sensitive credentials."""
        self.client.disconnect()
        if self.active_config:
            self.active_config.password = ""
        self.active_config = None

    def send_message(self, target_jid: str, body: str, is_groupchat: bool = True) -> bool:
        """Sends an outgoing message."""
        return self.client.send_message(target_jid, body, is_groupchat=is_groupchat)

    def join_room(self, room_jid: str, nickname: str = "") -> bool:
        """Subscribes to an XMPP MUC room."""
        success = self.client.join_room(room_jid, nickname)
        if success and room_jid not in self.channels:
            name = room_jid.split("@", 1)[0].replace(".", " ").title()
            self.channels[room_jid] = XMPPMUCChannel(
                room_jid=room_jid,
                name=name,
                auto_join=True,
                is_broadcast_channel="broadcast" in room_jid.lower(),
            )
        return success

    def leave_room(self, room_jid: str) -> bool:
        """Leaves a joined room."""
        return self.client.leave_room(room_jid)

    def get_messages(self, room_jid: str | None = None) -> list[XMPPMessage]:
        """Returns buffered message history (optionally filtered by room)."""
        if room_jid:
            return [m for m in self.messages if m.room_jid.lower() == room_jid.lower()]
        return list(self.messages)

    def get_channels(self) -> list[XMPPMUCChannel]:
        """Returns list of all known MUC channels."""
        return list(self.channels.values())

    def get_roster(self) -> list[XMPPRosterContact]:
        """Returns active roster contacts."""
        return list(self.roster.values())

    def inject_simulated_ping(
        self,
        target_system: str = "1DQ1-A",
        doctrine: str = "Tengu / Cerberus",
        fc: str = "ScoutCommander",
        body: str = "",
    ) -> XMPPMessage:
        """
        Helper method to inject a synthetic alliance broadcast ping for testing or UI demonstration.
        """
        raw = body or (
            f"*** ALLIANCE BROADCAST ***\n"
            f"STRATOP: Hostile Fortizar Timer in {target_system}\n"
            f"FC: {fc}\n"
            f"DOCTRINE: {doctrine}\n"
            f"LOCATION: {target_system}\n"
            f"COMMS: Fleet 1 (Mumble)\n"
            f"PAP: https://auth.alliance.net/pap/12345\n"
            f"All pilots in standing form up immediately!"
        )

        ping = parse_broadcast_ping(raw)
        msg = XMPPMessage(
            sender_jid=f"{fc.lower()}@alliance.net",
            sender_nick=fc,
            room_jid="broadcasts@conference.alliance.net",
            body=raw,
            msg_type=XMPPMessageType.BROADCAST,
            is_broadcast=True,
            priority=ping.priority if ping else XMPPBroadcastPriority.STRATOP,
            broadcast_ping=ping,
            timestamp=time.time(),
        )
        self._handle_client_message(msg)
        return msg

    def _handle_client_state_change(self, state: XMPPConnectionState, error_msg: str) -> None:
        """Handles client connection state updates and publishes to EventBus."""
        jid = self.active_config.jid if self.active_config else ""
        server = self.active_config.domain if self.active_config else ""

        self.event_bus.publish(
            XMPPConnectionStateChangedEvent(
                state=state.value,
                jid=jid,
                server=server,
                error_message=error_msg,
            )
        )

    def _handle_client_message(self, message: XMPPMessage) -> None:
        """Appends incoming message to in-memory buffer and publishes to EventBus."""
        self.messages.append(message)
        if len(self.messages) > self.MAX_HISTORY_MESSAGES:
            self.messages.pop(0)

        # Update room unread count
        if message.room_jid and message.room_jid in self.channels:
            self.channels[message.room_jid].unread_count += 1

        self.event_bus.publish(
            XMPPMessageReceivedEvent(
                msg_id=message.msg_id,
                sender_jid=message.sender_jid,
                sender_nick=message.sender_nick,
                room_jid=message.room_jid,
                body=message.body,
                is_broadcast=message.is_broadcast,
                priority=message.priority.value,
            )
        )

        # If this is a tactical broadcast ping, fire a specialized alert event
        if message.is_broadcast and message.broadcast_ping:
            p = message.broadcast_ping
            self.event_bus.publish(
                XMPPBroadcastAlertEvent(
                    msg_id=message.msg_id,
                    sender_nick=message.sender_nick,
                    target_system=p.target_system,
                    doctrine_ships=list(p.doctrine_ships),
                    fc_name=p.fc_name,
                    formup_timer=p.formup_timer,
                    priority=p.priority.value,
                    raw_text=message.body,
                )
            )

    def _handle_client_room_joined(self, room_jid: str, nickname: str, subject: str) -> None:
        """Handles MUC room join event."""
        if room_jid not in self.channels:
            name = room_jid.split("@", 1)[0].replace(".", " ").title()
            self.channels[room_jid] = XMPPMUCChannel(
                room_jid=room_jid,
                name=name,
                topic=subject,
                auto_join=True,
                is_broadcast_channel="broadcast" in room_jid.lower(),
            )

        self.event_bus.publish(
            XMPPRoomJoinedEvent(
                room_jid=room_jid,
                nickname=nickname,
                subject=subject,
            )
        )

    def _handle_client_roster_updated(self, contacts: list[XMPPRosterContact]) -> None:
        """Handles roster updates."""
        for c in contacts:
            self.roster[c.jid] = c

        self.event_bus.publish(
            XMPPRosterUpdatedEvent(
                contacts_count=len(self.roster)
            )
        )

    @override
    def get_status(self) -> dict[str, Any]:
        """Returns subsystem telemetry summary."""
        return {
            "name": self.name,
            "running": self._is_running,
            "connected": self.client.state == XMPPConnectionState.CONNECTED,
            "state": self.client.state.value,
            "channels_count": len(self.channels),
            "buffered_messages": len(self.messages),
        }
