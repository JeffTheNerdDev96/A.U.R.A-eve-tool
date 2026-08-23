"""
A.U.R.A. Base Subsystem Contract.
Abstract base class for isolated domain services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .event_bus import get_event_bus, EventBus


class BaseSubsystem(ABC):
    """
    Abstract base class enforcing standard subsystem lifecycle boundaries.
    Subsystems do not directly mutate UI state; they publish/subscribe via EventBus.
    """

    def __init__(self, name: str):
        self.name = name
        self._is_running: bool = False
        self.event_bus: EventBus = get_event_bus()

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize resources, data structures, and registers event listeners."""
        pass

    @abstractmethod
    def start(self) -> bool:
        """Starts background workers or active monitoring."""
        self._is_running = True
        return True

    @abstractmethod
    def stop(self) -> bool:
        """Stops background workers and cleans up resources."""
        self._is_running = False
        return True

    def is_running(self) -> bool:
        """Returns active running state."""
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """Returns subsystem health status dictionary."""
        return {
            "name": self.name,
            "running": self._is_running
        }
