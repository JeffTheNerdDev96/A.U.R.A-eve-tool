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

    MAX_HISTORY_MESSAGES = 1000

    def __init__(self):
        super().__init__(name="XMPPChatSubsystem")
        self.client = XMPPProtocolAdapter(
            on_state_change=self._handle_client_state_change,
            on_message_received=self._handle_client_message,
            on_room_joined=self._handle_client_room_joined,
            on_roster_updated=self._handle_client_roster_updated,
            on_channel_discovered=self._handle_client_channel_discovered,
            on_directory_discovered=self._handle_client_directory_discovered,
        )
        self.active_config: XMPPAccountConfig | None = None
        self.messages: list[XMPPMessage] = []
        self.channels: dict[str, XMPPMUCChannel] = {}
        self.directory_rooms: dict[str, XMPPMUCChannel] = {}
        self.roster: dict[str, XMPPRosterContact] = {}

        # Multicast UI listener callbacks (preserves service layer handling)
        self._message_listeners: list[Callable[[XMPPMessage], None]] = []
        self._state_listeners: list[Callable[[XMPPConnectionState, str], None]] = []
        self._room_joined_listeners: list[Callable[[str, str, str], None]] = []
        self._roster_listeners: list[Callable[[list[XMPPRosterContact]], None]] = []
        self._channel_discovered_listeners: list[Callable[[XMPPMUCChannel], None]] = []
        self._directory_discovered_listeners: list[Callable[[list[XMPPMUCChannel]], None]] = []

    def add_message_listener(self, listener: Callable[[XMPPMessage], None]) -> None:
        if listener not in self._message_listeners:
            self._message_listeners.append(listener)

    def add_state_listener(self, listener: Callable[[XMPPConnectionState, str], None]) -> None:
        if listener not in self._state_listeners:
            self._state_listeners.append(listener)

    def add_room_joined_listener(self, listener: Callable[[str, str, str], None]) -> None:
        if listener not in self._room_joined_listeners:
            self._room_joined_listeners.append(listener)

    def add_roster_listener(self, listener: Callable[[list[XMPPRosterContact]], None]) -> None:
        if listener not in self._roster_listeners:
            self._roster_listeners.append(listener)

    def add_channel_discovered_listener(self, listener: Callable[[XMPPMUCChannel], None]) -> None:
        if listener not in self._channel_discovered_listeners:
            self._channel_discovered_listeners.append(listener)

    def add_directory_discovered_listener(self, listener: Callable[[list[XMPPMUCChannel]], None]) -> None:
        if listener not in self._directory_discovered_listeners:
            self._directory_discovered_listeners.append(listener)

    @override
    def initialize(self) -> bool:
        """Initializes internal collections and default alliance rooms."""
        self.messages.clear()
        self.channels.clear()
        self.directory_rooms.clear()
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
        self.directory_rooms.clear()
        self.active_config = None
        super().stop()
        return True

    def connect(self, config: XMPPAccountConfig) -> bool:
        """
        Initiates connection with provided ephemeral account configuration.
        Credentials exist strictly in volatile memory.
        """
        self.active_config = config
        # Dynamic seeding for active domain
        if config.domain:
            muc_host = f"conference.{config.domain}"
            bcast_jid = f"broadcasts@{muc_host}"
            if bcast_jid not in self.channels:
                self.channels[bcast_jid] = XMPPMUCChannel(
                    room_jid=bcast_jid,
                    name=f"{config.domain.split('.', 1)[0].title()} Broadcasts",
                    topic="Alliance Strategic Broadcasts",
                    auto_join=True,
                    is_broadcast_channel=True,
                )
        return self.client.connect(config)

    def disconnect(self) -> None:
        """Terminates active XMPP connection and purges sensitive credentials."""
        self.client.disconnect()
        if self.active_config:
            self.active_config.password = ""
        self.active_config = None

    def send_message(self, target_jid: str, body: str, is_groupchat: bool = True) -> bool:
        """Sends an outgoing direct or MUC message and registers DM targets."""
        if not is_groupchat and target_jid:
            bare_target = target_jid.split("/", 1)[0]
            if bare_target not in self.roster:
                self.roster[bare_target] = XMPPRosterContact(
                    jid=bare_target,
                    name=bare_target.split("@", 1)[0],
                    group="Direct Messages",
                    is_direct_chat=True,
                )
                self._notify_roster_listeners()

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

    def get_messages(self, target_jid: str | None = None) -> list[XMPPMessage]:
        """Returns buffered message history filtered by room JID or direct contact JID."""
        if not target_jid:
            return list(self.messages)

        t_clean = target_jid.lower().strip()
        t_bare = t_clean.split("/", 1)[0]
        matched: list[XMPPMessage] = []

        for m in self.messages:
            if m.room_jid and m.room_jid.lower() == t_clean:
                matched.append(m)
            elif not m.room_jid:
                # Direct message matching: match incoming from contact or outgoing to contact
                sender_bare = m.sender_jid.split("/", 1)[0].lower()
                recip_bare = m.recipient_jid.split("/", 1)[0].lower() if m.recipient_jid else ""
                if sender_bare == t_bare or recip_bare == t_bare or t_bare in sender_bare or (recip_bare and t_bare in recip_bare):
                    matched.append(m)

        return matched

    def get_channels(self) -> list[XMPPMUCChannel]:
        """Returns list of all known MUC channels."""
        return list(self.channels.values())

    def get_directory_rooms(self) -> list[XMPPMUCChannel]:
        """Returns list of public directory rooms discovered on server."""
        return list(self.directory_rooms.values())

    def get_direct_chats(self) -> list[XMPPRosterContact]:
        """Returns active direct chat contacts."""
        return [c for c in self.roster.values() if c.is_direct_chat or c.group == "Direct Messages"]

    def get_roster(self) -> list[XMPPRosterContact]:
        """Returns active roster contacts."""
        return list(self.roster.values())

    def inject_simulated_ping(
        self,
        staging_system: str = "1DQ1-A",
        doctrine: str = "Tengu / Cerberus",
        fc: str = "ScoutCommander",
        body: str = "",
        target_system: str = "",
    ) -> XMPPMessage:
        """
        Helper method to inject a synthetic alliance broadcast ping for testing or UI demonstration.
        """
        effective_sys = staging_system or target_system or "1DQ1-A"
        raw = body or (
            f"*** ALLIANCE BROADCAST ***\n"
            f"STRATOP: Hostile Fortizar Timer in {effective_sys}\n"
            f"FC Name: {fc}\n"
            f"Formup Location: {effective_sys}\n"
            f"DOCTRINE: {doctrine}\n"
            f"COMMS: Fleet 1 (Mumble)\n"
            f"PAP: https://auth.alliance.net/pap/12345\n"
            f"All pilots in standing form up immediately!"
        )

        ping = parse_broadcast_ping(raw)
        bcast_room = "broadcasts@conference.alliance.net"
        if self.active_config and self.active_config.domain:
            bcast_room = f"broadcasts@conference.{self.active_config.domain}"

        msg = XMPPMessage(
            sender_jid=f"{fc.lower()}@alliance.net",
            sender_nick=fc,
            room_jid=bcast_room,
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

        for listener in list(self._state_listeners):
            try:
                listener(state, error_msg)
            except Exception:
                pass

    def _handle_client_message(self, message: XMPPMessage) -> None:
        """Appends incoming message to in-memory buffer, registers DMs, and notifies listeners."""
        self.messages.append(message)
        if len(self.messages) > self.MAX_HISTORY_MESSAGES:
            self.messages.pop(0)

        # Update room unread count or direct contact entry
        if message.room_jid and message.room_jid in self.channels:
            self.channels[message.room_jid].unread_count += 1
        elif not message.room_jid and message.sender_jid:
            bare_sender = message.sender_jid.split("/", 1)[0]
            if bare_sender in self.roster:
                self.roster[bare_sender].unread_count += 1
                self.roster[bare_sender].is_direct_chat = True
            else:
                self.roster[bare_sender] = XMPPRosterContact(
                    jid=bare_sender,
                    name=message.sender_nick or bare_sender.split("@", 1)[0],
                    group="Direct Messages",
                    is_direct_chat=True,
                    unread_count=1,
                )
                self._notify_roster_listeners()

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

        for listener in list(self._message_listeners):
            try:
                listener(message)
            except Exception:
                pass

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

        for listener in list(self._room_joined_listeners):
            try:
                listener(room_jid, nickname, subject)
            except Exception:
                pass

    def _handle_client_channel_discovered(self, channel: XMPPMUCChannel) -> None:
        """Handles newly discovered channel (e.g. from bookmarks)."""
        self.channels[channel.room_jid] = channel
        for listener in list(self._channel_discovered_listeners):
            try:
                listener(channel)
            except Exception:
                pass

    def _handle_client_directory_discovered(self, rooms: list[XMPPMUCChannel]) -> None:
        """Handles public MUC directory discovery."""
        for r in rooms:
            self.directory_rooms[r.room_jid] = r
        for listener in list(self._directory_discovered_listeners):
            try:
                listener(rooms)
            except Exception:
                pass

    def _handle_client_roster_updated(self, contacts: list[XMPPRosterContact]) -> None:
        """Handles roster updates."""
        for c in contacts:
            self.roster[c.jid] = c

        self.event_bus.publish(
            XMPPRosterUpdatedEvent(
                contacts_count=len(self.roster)
            )
        )

        self._notify_roster_listeners()

    def _notify_roster_listeners(self) -> None:
        contacts_list = list(self.roster.values())
        for listener in list(self._roster_listeners):
            try:
                listener(contacts_list)
            except Exception:
                pass

    @override
    def get_status(self) -> dict[str, Any]:
        """Returns subsystem telemetry summary."""
        return {
            "name": self.name,
            "running": self._is_running,
            "connected": self.client.state == XMPPConnectionState.CONNECTED,
            "state": self.client.state.value,
            "channels_count": len(self.channels),
            "directory_count": len(self.directory_rooms),
            "roster_count": len(self.roster),
            "buffered_messages": len(self.messages),
        }

