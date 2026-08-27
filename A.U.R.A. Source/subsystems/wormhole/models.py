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
A.U.R.A. Wormhole Subsystem Models & Data Contracts.
Placeholder architecture for v0.3.x Wormhole Mapping System milestone.
"""

from dataclasses import dataclass, field
from enum import StrEnum
import time


class WormholeClass(StrEnum):
    """EVE Online Solar System / Wormhole Classifications."""
    C1 = "Class 1"
    C2 = "Class 2"
    C3 = "Class 3"
    C4 = "Class 4"
    C5 = "Class 5"
    C6 = "Class 6"
    THERA = "Thera"
    POCHVEN = "Pochven"
    HIGHSEC = "High-Security"
    LOWSEC = "Low-Security"
    NULLSEC = "Null-Security"
    UNKNOWN = "Unknown"


class WormholeEffect(StrEnum):
    """System-wide environmental effects in J-space."""
    NONE = "No Effect"
    PULSAR = "Pulsar"
    WOLF_RAYET = "Wolf-Rayet"
    CATACLYSMIC = "Cataclysmic Variable"
    MAGNETAR = "Magnetar"
    RED_GIANT = "Red Giant"
    BLACK_HOLE = "Black Hole"


class MassState(StrEnum):
    """Connection mass stages."""
    FRESH = "Stage 1 (>50%)"
    DESTAB = "Stage 2 (10%-50%)"
    CRITICAL = "Critical (<10%)"
    VERGE = "Verge of Collapse"


class LifetimeState(StrEnum):
    """Connection lifetime decay stages."""
    STABLE = "Stable (>24h or >4h depending on type)"
    END_OF_LIFE = "End of Life (<4h remaining)"
    CRITICAL = "Critical / Imminent Collapse"


class SignatureGroup(StrEnum):
    """Cosmic signature categories."""
    UNKNOWN = "Unscanned"
    WORMHOLE = "Wormhole"
    RELIC = "Relic Site"
    DATA = "Data Site"
    GAS = "Gas Site"
    COMBAT = "Combat Site"


@dataclass(slots=True)
class CosmicSignature:
    """Represents a scanned or unscanned cosmic signature in a system."""
    sig_id: str                          # e.g. "ABC-123"
    group: SignatureGroup = SignatureGroup.UNKNOWN
    name: str = ""                       # e.g. "Core Probe Scanner Relic Site"
    signal_strength: float = 0.0         # 0.0 - 100.0%
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    comment: str = ""


@dataclass(slots=True)
class WormholeConnection:
    """Represents an active wormhole link connecting two solar systems."""
    connection_id: str
    source_system: str
    target_system: str
    wormhole_type: str = ""              # e.g. "K162", "D845", "H296"
    mass_state: MassState = MassState.FRESH
    lifetime_state: LifetimeState = LifetimeState.STABLE
    source_sig_id: str | None = None
    target_sig_id: str | None = None
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    is_locked: bool = False
    notes: str = ""


@dataclass(slots=True)
class WormholeNode:
    """Represents a solar system in an active wormhole chain topology."""
    system_name: str                     # e.g. "J123456" or "Jita"
    system_class: WormholeClass = WormholeClass.UNKNOWN
    effect: WormholeEffect = WormholeEffect.NONE
    region: str = ""
    constellation: str = ""
    security_status: float = -0.99
    statics: list[str] = field(default_factory=list)      # e.g. ["D845", "N432"]
    signatures: dict[str, CosmicSignature] = field(default_factory=dict)
    custom_name: str = ""                # e.g. "Home", "Farm", "C3 Static"
    x: float = 0.0                       # Canvas coordinate
    y: float = 0.0                       # Canvas coordinate


@dataclass(slots=True)
class WormholeChain:
    """Represents a full mapped chain topology."""
    chain_id: str
    home_system: str
    nodes: dict[str, WormholeNode] = field(default_factory=dict)
    connections: list[WormholeConnection] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
