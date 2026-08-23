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
