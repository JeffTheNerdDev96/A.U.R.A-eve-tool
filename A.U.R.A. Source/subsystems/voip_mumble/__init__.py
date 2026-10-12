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
A.U.R.A. VOIP (Mumble) Subsystem.
Alliance voice sessions, channel tree, channel text, and speaking telemetry.
"""

from .models import (
    VOIPAccountConfig,
    VOIPChannel,
    VOIPConnectionState,
    VOIPMessageType,
    VOIPTextMessage,
    VOIPUser,
)
from .runtime import ensure_opus_dll_path, get_voip_runtime_dir, is_opus_available
from .client import MumbleProtocolAdapter, build_mumble_ssl_context
from .service import VOIPMumbleSubsystem

__all__ = [
    "VOIPMumbleSubsystem",
    "VOIPConnectionState",
    "VOIPMessageType",
    "VOIPAccountConfig",
    "VOIPChannel",
    "VOIPTextMessage",
    "VOIPUser",
    "MumbleProtocolAdapter",
    "build_mumble_ssl_context",
    "ensure_opus_dll_path",
    "get_voip_runtime_dir",
    "is_opus_available",
]
