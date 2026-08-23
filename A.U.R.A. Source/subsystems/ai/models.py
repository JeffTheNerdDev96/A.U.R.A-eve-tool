"""
AI Subsystem Data Models & DTOs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class InferenceRequest:
    request_id: str
    prompt: str
    chat_history: List[Dict[str, str]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    piloted_ship: Optional[str] = None


@dataclass
class InferenceResult:
    request_id: str
    response_text: str
    tokens_per_second: float
    total_tokens: int
    duration_seconds: float
