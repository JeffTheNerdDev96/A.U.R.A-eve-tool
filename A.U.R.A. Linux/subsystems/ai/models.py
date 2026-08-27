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
AI Subsystem Data Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InferenceRequest:
    request_id: str
    prompt: str
    chat_history: list[dict[str, str]] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    piloted_ship: str | None = None


@dataclass(slots=True)
class InferenceResult:
    request_id: str
    response_text: str
    tokens_per_second: float
    total_tokens: int
    duration_seconds: float
