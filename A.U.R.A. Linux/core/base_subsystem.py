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
A.U.R.A. Base Subsystem Contract.
Abstract base class for isolated domain services.
"""

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .event_bus import EventBus

type SubsystemStatus = dict[str, Any]


class BaseSubsystem(ABC):
    """
    Abstract base class enforcing standard subsystem lifecycle boundaries.
    Subsystems do not directly mutate UI state; they publish/subscribe via EventBus.
    """

    def __init__(self, name: str):
        self.name = name
        self._is_running: bool = False
        from .event_bus import get_event_bus
        self.event_bus = get_event_bus()

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

    def get_status(self) -> SubsystemStatus:
        """Returns subsystem health status dictionary."""
        return {
            "name": self.name,
            "running": self._is_running
        }
