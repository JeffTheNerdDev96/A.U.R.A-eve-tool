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
A.U.R.A. VOIP (Mumble) Subsystem Service Layer, part 1.
Connection lifecycle, topology snapshots, text history, EventBus publishing.
"""

from __future__ import annotations

from typing import Any, override

from core.base_subsystem import BaseSubsystem
from core.config import config
from core.events import (
    VOIPChannelUpdatedEvent,
    VOIPConnectionStateChangedEvent,
    VOIPTextMessageEvent,
    VOIPUserSpeakingEvent,
)
from .client import MumbleProtocolAdapter
from .models import (
    VOIPAccountConfig,
    VOIPChannel,
    VOIPConnectionState,
    VOIPTextMessage,
    VOIPUser,
)


class VOIPMumbleSubsystem(BaseSubsystem):
    """Service layer for alliance Mumble voice and channel text."""

    MAX_HISTORY_MESSAGES = 500

    def __init__(self):
        super().__init__(name="VOIPMumbleSubsystem")
        self.client = MumbleProtocolAdapter(
            on_state_change=self._handle_client_state_change,
            on_text_received=self._handle_client_text,
            on_topology_changed=self._handle_topology_changed,
            on_speaking_changed=self._handle_speaking_changed,
        )
        self.active_config: VOIPAccountConfig | None = None
        self.messages: list[VOIPTextMessage] = []
        self.channels: dict[int, VOIPChannel] = {}
        self.users: dict[int, VOIPUser] = {}
        self.own_session_id: int = -1
        self.active_channel_id: int = 0

    @override
    def initialize(self) -> bool:
        """Clears in-memory voice state."""
        self.messages.clear()
        self.channels.clear()
        self.users.clear()
        self.own_session_id = -1
        self.active_channel_id = 0
        return True

    @override
    def start(self) -> bool:
        """Arms the subsystem for voice sessions."""
        super().start()
        return True

    @override
    def stop(self) -> bool:
        """Disconnects the voice session and purges ephemeral memory."""
        self.disconnect()
        self.messages.clear()
        self.channels.clear()
        self.users.clear()
        self.own_session_id = -1
        self.active_channel_id = 0
        self.active_config = None
        super().stop()
        return True

    def connect(self, cfg: VOIPAccountConfig) -> bool:
        """Initiates a voice session with ephemeral credentials."""
        self.active_config = cfg
        return self.client.connect(cfg)

    def disconnect(self) -> None:
        """Stops the voice session and zeroes in-memory credentials."""
        self.client.disconnect()
        if self.active_config:
            self.active_config.wipe_credentials()
        self.active_config = None

    def join_channel(self, channel_path: str) -> bool:
        """Moves the session into the named alliance channel."""
        return self.client.join_channel_path(channel_path)

    def send_channel_text(self, channel_id: int, body: str) -> bool:
        """Sends channel text and records the outbound echo."""
        ok = self.client.send_channel_text(channel_id, body)
        if ok:
            name = ""
            try:
                name = self.channels.get(int(channel_id), VOIPChannel()).name
            except Exception:
                name = ""
            echo = VOIPTextMessage(
                sender=self.active_config.username if self.active_config else "You",
                channel_name=name,
                body=body.strip()[:4000],
                is_self=True,
            )
            self.messages.append(echo)
            if len(self.messages) > self.MAX_HISTORY_MESSAGES:
                self.messages.pop(0)
        return ok

    def set_self_mute(self, muted: bool) -> bool:
        """Toggles the local microphone mute flag."""
        return self.client.set_self_mute(muted)

    def set_self_deafen(self, deafened: bool) -> bool:
        """Toggles the local deafen flag."""
        return self.client.set_self_deafen(deafened)

    def set_push_to_talk(self, active: bool) -> None:
        """Gates outbound microphone PCM on push-to-talk state."""
        self.client.set_push_to_talk(active)

    def push_outbound_pcm(self, pcm: bytes) -> bool:
        """Queues microphone PCM for transmission."""
        return self.client.push_outbound_pcm(pcm)

    def pop_inbound_pcm(self) -> list[tuple[int, bytes]]:
        """Drains inbound PCM chunks for the Qt playback layer."""
        return self.client.pop_inbound_pcm()

    def get_channels(self) -> list[VOIPChannel]:
        """Returns the voice channel tree snapshot."""
        return list(self.channels.values())

    def get_users(self, channel_id: int | None = None) -> list[VOIPUser]:
        """Returns connected peers, optionally filtered by channel."""
        if channel_id is None:
            return list(self.users.values())
        return [u for u in self.users.values() if u.channel_id == channel_id]

    def get_messages(self, limit: int = 200) -> list[VOIPTextMessage]:
        """Returns recent channel text history."""
        return list(self.messages[-max(1, limit):])

    def inject_simulated_message(
        self,
        sender: str = "FleetCommander",
        channel: str = "Fleet 1",
        body: str = "",
    ) -> VOIPTextMessage:
        """Injects a synthetic channel message for UI demonstration."""
        msg = VOIPTextMessage(
            sender=sender,
            channel_name=channel,
            body=body or "Form up in Fleet 1 comms. Align to the staging gate.",
        )
        self._handle_client_text(msg)
        return msg

    def _handle_client_state_change(self, state: VOIPConnectionState, error_msg: str) -> None:
        """Publishes voice session state transitions to the EventBus."""
        host = self.active_config.host if self.active_config else ""
        username = self.active_config.username if self.active_config else ""
        self.event_bus.publish(
            VOIPConnectionStateChangedEvent(
                state=state.value,
                host=host,
                username=username,
                error_message=error_msg,
            )
        )

    def _handle_client_text(self, message: VOIPTextMessage) -> None:
        """Buffers inbound channel text and notifies listeners."""
        max_messages = int(getattr(config, "voip_max_messages", self.MAX_HISTORY_MESSAGES) or self.MAX_HISTORY_MESSAGES)
        self.messages.append(message)
        while len(self.messages) > max_messages:
            self.messages.pop(0)
        self.event_bus.publish(
            VOIPTextMessageEvent(
                msg_id=message.msg_id,
                sender=message.sender,
                channel_name=message.channel_name,
                body=message.body,
                is_self=message.is_self,
                message=message,
            )
        )

    def _handle_topology_changed(self) -> None:
        """Refreshes channel/user caches and publishes the active channel."""
        try:
            channels, users, own_session = self.client.snapshot_topology()
        except Exception:
            return
        self.channels = {c.channel_id: c for c in channels}
        self.users = {u.session_id: u for u in users}
        self.own_session_id = own_session
        active_id = 0
        active_name = ""
        active_path = ""
        active_count = 0
        try:
            if own_session in self.users:
                active_id = int(self.users[own_session].channel_id or 0)
            if active_id in self.channels:
                active = self.channels[active_id]
                active_name = active.name
                active_path = active.path
                active_count = active.user_count
        except Exception:
            pass
        self.active_channel_id = active_id
        self.event_bus.publish(
            VOIPChannelUpdatedEvent(
                channel_id=active_id,
                channel_name=active_name,
                channel_path=active_path,
                user_count=active_count,
            )
        )

    def _handle_speaking_changed(self, session_id: int, username: str, channel_id: int, is_speaking: bool) -> None:
        """Marks peer transmit state and notifies listeners."""
        user = self.users.get(session_id)
        if user is not None:
            user.is_speaking = is_speaking
            username = username or user.name
            channel_id = user.channel_id
        self.event_bus.publish(
            VOIPUserSpeakingEvent(
                session_id=session_id,
                username=username,
                channel_id=channel_id,
                is_speaking=is_speaking,
            )
        )

    @override
    def get_status(self) -> dict[str, Any]:
        """Returns subsystem telemetry summary."""
        return {
            "name": self.name,
            "running": self._is_running,
            "connected": self.client.state == VOIPConnectionState.CONNECTED,
            "state": self.client.state.value,
            "channels_count": len(self.channels),
            "users_count": len(self.users),
            "active_channel_id": self.active_channel_id,
            "buffered_messages": len(self.messages),
        }
