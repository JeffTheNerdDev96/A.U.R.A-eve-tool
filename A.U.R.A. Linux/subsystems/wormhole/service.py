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
    WormholeChainUpdatedEvent,
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
    WormholeEffect,
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
    ) -> WormholeNode | None:
        """Adds a discovered wormhole system and optional connection link."""
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
            conn = WormholeConnection(
                connection_id=str(uuid.uuid4()),
                source_system=parent_system,
                target_system=system_name,
                wormhole_type=wormhole_type,
                mass_state=mass_state,
                lifetime_state=lifetime_state,
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
