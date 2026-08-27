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
A.U.R.A. Central Thread-Safe Async Event Bus.
Decouples domain subsystems and PyQt6 UI using typed signals.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable
from typing import Callable, Any
import logging
import traceback
from collections import defaultdict

from .events import BaseEvent

logger = logging.getLogger("AURA.EventBus")


class EventBus(QObject):
    """
    Singleton Event Bus utilizing Qt signal/slot mechanism to bridge
    background worker threads and UI event consumers safely.
    """
    _qt_event_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._subscribers: dict[type[BaseEvent], list[Callable[[Any], None]]] = defaultdict(list)
        self._thread_pool = QThreadPool.globalInstance()
        self._qt_event_signal.connect(self._dispatch_to_subscribers)

    def publish(self, event: BaseEvent) -> None:
        """
        Publishes an event to all registered subscribers asynchronously via Qt signal.
        Thread-safe: Can be called safely from any thread.
        """
        self._qt_event_signal.emit(event)

    def subscribe[E: BaseEvent](self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """
        Registers a callback handler for a specific event type.
        """
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe[E: BaseEvent](self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """
        Unregisters a callback handler for a specific event type.
        """
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def _dispatch_to_subscribers(self, event: BaseEvent) -> None:
        """Internal Qt slot executing on the thread associated with the EventBus instance."""
        event_type = type(event)
        
        # Exact match handlers
        handlers = list(self._subscribers.get(event_type, []))
        
        # Parent match handlers (e.g. subscribing to BaseEvent catches all)
        for registered_type, subscriber_list in self._subscribers.items():
            if registered_type != event_type and isinstance(event, registered_type):
                handlers.extend(subscriber_list)

        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.error(f"Error handling event {event_type.__name__} in {handler}: {exc}")
                logger.debug(traceback.format_exc())

    def run_async(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Utility helper to execute a standard python function in QThreadPool."""
        class WorkerRunnable(QRunnable):
            def run(self):
                try:
                    fn(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing async task {fn}: {e}")
                    logger.debug(traceback.format_exc())

        runnable = WorkerRunnable()
        runnable.setAutoDelete(True)
        self._thread_pool.start(runnable)


# Global Singleton Instance
_EVENT_BUS_INSTANCE: EventBus | None = None


def get_event_bus() -> EventBus:
    """Returns global singleton EventBus instance."""
    global _EVENT_BUS_INSTANCE
    if _EVENT_BUS_INSTANCE is None:
        _EVENT_BUS_INSTANCE = EventBus()
    return _EVENT_BUS_INSTANCE
