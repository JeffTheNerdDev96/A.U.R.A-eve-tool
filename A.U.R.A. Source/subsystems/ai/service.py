"""
Subsystem Service Layer for Local Neural Core & GGUF Inference.
"""

from typing import override
from core.base_subsystem import BaseSubsystem
from core.events import InferenceStreamTokenEvent, InferenceCompletedEvent
from .engine import UnifiedInferenceEngine
from .ingestion import DocumentParser, ImagePreprocessor
from .models import InferenceRequest, InferenceResult


class AISubsystem(BaseSubsystem):
    """AI Neural Inference subsystem managing model lifecycle, token streaming, and OCR."""

    def __init__(self):
        super().__init__(name="AISubsystem")
        self.engine = UnifiedInferenceEngine()
        self.doc_parser = DocumentParser()
        self.image_preprocessor = ImagePreprocessor()

    @override
    def initialize(self) -> bool:
        return True

    @override
    def start(self) -> bool:
        super().start()
        return True

    @override
    def stop(self) -> bool:
        self.engine.unload_model()
        super().stop()
        return True

    def generate_response(self, request: InferenceRequest) -> InferenceResult:
        """Runs inference generation, emitting token events and completion event."""
        tokens: List[str] = []
        tokens_per_sec = 0.0
        total_tokens = 0
        duration = 0.0

        for chunk in self.engine.generate_stream(
            request.prompt,
            request.chat_history,
            request.attachments,
            piloted_ship=request.piloted_ship
        ):
            chunk_type = chunk.get("type")
            if chunk_type == "token":
                tok = chunk.get("text", chunk.get("token", ""))
                tokens.append(tok)
                self.event_bus.publish(InferenceStreamTokenEvent(
                    request_id=request.request_id,
                    token=tok
                ))
            elif chunk_type == "done":
                tokens_per_sec = float(chunk.get("tokens_per_sec", chunk.get("tok_sec", 0.0)))
                total_tokens = int(chunk.get("tokens_generated", chunk.get("total_tokens", len(tokens))))
                duration = float(chunk.get("time_elapsed", chunk.get("duration", 0.0)))

        full_text = "".join(tokens)
        result = InferenceResult(
            request_id=request.request_id,
            response_text=full_text,
            tokens_per_second=tokens_per_sec,
            total_tokens=total_tokens,
            duration_seconds=duration
        )

        self.event_bus.publish(InferenceCompletedEvent(
            request_id=request.request_id,
            full_response=full_text,
            tokens_per_second=tokens_per_sec,
            total_tokens=total_tokens
        ))

        return result
