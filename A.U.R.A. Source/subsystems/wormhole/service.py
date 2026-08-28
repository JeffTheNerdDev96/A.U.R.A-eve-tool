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
A.U.R.A. Wormhole Mapping Subsystem Service Layer.
Placeholder architecture for the v0.3.x Wormhole Mapping System milestone.
"""

from typing import Any, override
import uuid
import time
from core.base_subsystem import BaseSubsystem
from core.events import (
    WormholeSystemAddedEvent,
    WormholeConnectionUpdatedEvent,
    CosmicSignatureUpdatedEvent,
)
from .models import (
    WormholeNode,
    WormholeConnection,
    WormholeChain,
    CosmicSignature,
    WormholeClass,
    MassState,
    LifetimeState,
)


class WormholeSubsystem(BaseSubsystem):
    """
    Subsystem Service Layer for Wormhole Chain Mapping & Signature Tracking.
    Encapsulates chain graph topology, state tracking, and cross-subsystem event dispatch.
    """

    def __init__(self):
        super().__init__(name="WormholeSubsystem")
        self.active_chain: WormholeChain | None = None

    @override
    def initialize(self) -> bool:
        """Initializes data structures and event subscriptions."""
        # Initial chain placeholder
        self.active_chain = WormholeChain(
            chain_id=str(uuid.uuid4()),
            home_system="",
        )
        return True

    @override
    def start(self) -> bool:
        """Starts active chain monitoring / timers."""
        super().start()
        return True

    @override
    def stop(self) -> bool:
        """Cleans up timers and memory buffers."""
        super().stop()
        return True

    def set_home_system(self, system_name: str, system_class: WormholeClass = WormholeClass.UNKNOWN) -> WormholeNode:
        """Sets the root/home solar system of the current wormhole chain."""
        if self.active_chain is None:
            self.initialize()

        node = WormholeNode(
            system_name=system_name,
            system_class=system_class,
            custom_name="Home",
            x=0.0,
            y=0.0,
        )
        self.active_chain.home_system = system_name
        self.active_chain.nodes[system_name] = node
        self.active_chain.updated_at = time.time()

        self.event_bus.publish(
            WormholeSystemAddedEvent(
                chain_id=self.active_chain.chain_id,
                system_name=system_name,
                system_class=system_class.value,
                is_home=True,
            )
        )
        return node

    def add_system(
        self,
        system_name: str,
        parent_system: str | None = None,
        wormhole_type: str = "",
        system_class: WormholeClass = WormholeClass.UNKNOWN,
        mass_state: MassState = MassState.FRESH,
        lifetime_state: LifetimeState = LifetimeState.STABLE,
        lifetime_duration_hours: float | None = 24.0,
    ) -> WormholeNode | None:
        """Adds a discovered wormhole system and optional connection link with expiration timer."""
        if self.active_chain is None:
            self.initialize()

        if system_name in self.active_chain.nodes:
            return self.active_chain.nodes[system_name]

        node = WormholeNode(
            system_name=system_name,
            system_class=system_class,
        )
        self.active_chain.nodes[system_name] = node

        if parent_system and parent_system in self.active_chain.nodes:
            now = time.time()
            expires_at = (now + lifetime_duration_hours * 3600.0) if lifetime_duration_hours and lifetime_duration_hours > 0 else None
            conn = WormholeConnection(
                connection_id=str(uuid.uuid4()),
                source_system=parent_system,
                target_system=system_name,
                wormhole_type=wormhole_type,
                mass_state=mass_state,
                lifetime_state=lifetime_state,
                created_at=now,
                expires_at=expires_at,
            )
            self.active_chain.connections.append(conn)

            self.event_bus.publish(
                WormholeConnectionUpdatedEvent(
                    chain_id=self.active_chain.chain_id,
                    connection_id=conn.connection_id,
                    source_system=parent_system,
                    target_system=system_name,
                    wormhole_type=wormhole_type,
                    mass_state=conn.mass_state.value,
                    lifetime_state=conn.lifetime_state.value,
                )
            )

        self.active_chain.updated_at = time.time()
        self.event_bus.publish(
            WormholeSystemAddedEvent(
                chain_id=self.active_chain.chain_id,
                system_name=system_name,
                system_class=system_class.value,
                parent_system=parent_system or "",
            )
        )
        return node

    def remove_connection(self, source_system: str, target_system: str) -> bool:
        """Removes an active connection link between two systems."""
        if not self.active_chain:
            return False
        before = len(self.active_chain.connections)
        self.active_chain.connections = [
            c for c in self.active_chain.connections
            if not (c.source_system == source_system and c.target_system == target_system)
        ]
        if len(self.active_chain.connections) < before:
            self.active_chain.updated_at = time.time()
            return True
        return False

    def remove_system(self, system_name: str) -> bool:
        """Removes a solar system and all its associated connections from the active chain."""
        if not self.active_chain or system_name not in self.active_chain.nodes:
            return False
        if system_name == self.active_chain.home_system:
            # Re-initialize chain if home system is removed
            self.initialize()
            return True

        del self.active_chain.nodes[system_name]
        self.active_chain.connections = [
            c for c in self.active_chain.connections
            if c.source_system != system_name and c.target_system != system_name
        ]
        self.active_chain.updated_at = time.time()
        return True

    def update_connection_timers(self) -> tuple[list[str], list[str]]:
        """
        Updates lifetime states based on expires_at countdown.
        Returns (eol_connection_ids, expired_connection_ids).
        """
        if not self.active_chain:
            return [], []
        now = time.time()
        eol_ids: list[str] = []
        expired_ids: list[str] = []

        for conn in self.active_chain.connections:
            if conn.expires_at is None:
                continue
            rem = conn.expires_at - now
            if rem <= 0:
                conn.lifetime_state = LifetimeState.CRITICAL
                expired_ids.append(conn.connection_id)
            elif rem <= 4 * 3600:
                conn.lifetime_state = LifetimeState.END_OF_LIFE
                eol_ids.append(conn.connection_id)
            else:
                conn.lifetime_state = LifetimeState.STABLE

        return eol_ids, expired_ids

    def clear_expired_connections(self) -> int:
        """Removes all connections that have exceeded their lifetime timer."""
        if not self.active_chain:
            return 0
        now = time.time()
        expired = [c for c in self.active_chain.connections if c.expires_at and c.expires_at <= now]
        if not expired:
            return 0
        expired_targets = {c.target_system for c in expired}
        self.active_chain.connections = [
            c for c in self.active_chain.connections
            if not (c.expires_at and c.expires_at <= now)
        ]
        # Remove orphaned child nodes that no longer have inbound links
        for target in expired_targets:
            has_inbound = any(c.target_system == target for c in self.active_chain.connections)
            if not has_inbound and target in self.active_chain.nodes and target != self.active_chain.home_system:
                del self.active_chain.nodes[target]
        self.active_chain.updated_at = now
        return len(expired)

    def add_or_update_signature(
        self,
        system_name: str,
        sig_id: str,
        signature: CosmicSignature,
    ) -> bool:
        """Adds or updates a cosmic signature in a specific solar system."""
        if not self.active_chain or system_name not in self.active_chain.nodes:
            return False

        node = self.active_chain.nodes[system_name]
        node.signatures[sig_id] = signature
        self.active_chain.updated_at = time.time()

        self.event_bus.publish(
            CosmicSignatureUpdatedEvent(
                chain_id=self.active_chain.chain_id,
                system_name=system_name,
                sig_id=sig_id,
                sig_group=signature.group.value,
                sig_name=signature.name,
                signal_strength=signature.signal_strength,
            )
        )
        return True

    def get_chain_summary(self) -> dict[str, Any]:
        """Returns diagnostic/state summary of the current chain."""
        if not self.active_chain:
            return {"status": "inactive", "nodes": 0, "connections": 0}

        return {
            "chain_id": self.active_chain.chain_id,
            "home_system": self.active_chain.home_system,
            "nodes_count": len(self.active_chain.nodes),
            "connections_count": len(self.active_chain.connections),
            "updated_at": self.active_chain.updated_at,
        }
