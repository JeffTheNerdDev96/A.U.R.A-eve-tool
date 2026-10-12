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
A.U.R.A. VOIP Qt Audio Engine, part 1: device capture and playback pumps.
48kHz mono s16 PCM between QtMultimedia devices and the Mumble adapter.
"""

from __future__ import annotations

import collections
from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

_SAMPLE_RATE = 48000
_CHANNELS = 1
_FRAME_MS = 20
_FRAME_BYTES = _SAMPLE_RATE * _CHANNELS * 2 * _FRAME_MS // 1000
_PLAYBACK_MAX_CHUNKS = 64


class QtAudioEngine(QObject):
    """QtMultimedia capture/playback bridge for alliance voice sessions."""

    inbound_level = pyqtSignal(float)
    outbound_level = pyqtSignal(float)
    audio_error = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._source = None
        self._source_device = None
        self._sink = None
        self._sink_device = None
        self._capture_buffer = bytearray()
        self._playback_queue: collections.deque = collections.deque(maxlen=_PLAYBACK_MAX_CHUNKS)
        self._pump_timer = QTimer(self)
        self._pump_timer.setInterval(_FRAME_MS)
        self._pump_timer.timeout.connect(self._on_pump)
        self._on_capture_frame: Optional[Callable[[bytes], None]] = None
        self._capture_enabled = False
        self._input_volume_pct = 80
        self._output_volume_pct = 80
        self._capture_device_id = ""
        self._playback_device_id = ""

    @staticmethod
    def _qt_multimedia():
        from PyQt6.QtMultimedia import (
            QAudioFormat,
            QAudioSink,
            QAudioSource,
            QMediaDevices,
        )
        return QAudioFormat, QAudioSink, QAudioSource, QMediaDevices

    @staticmethod
    def list_input_devices() -> list[tuple[str, str]]:
        """Returns (device_id, description) for capture devices."""
        try:
            from PyQt6.QtMultimedia import QMediaDevices
            out = []
            for dev in QMediaDevices.audioInputs():
                out.append((dev.id().toString() if hasattr(dev.id(), "toString") else str(dev.id()), dev.description()))
            return out
        except Exception:
            return []

    @staticmethod
    def list_output_devices() -> list[tuple[str, str]]:
        """Returns (device_id, description) for playback devices."""
        try:
            from PyQt6.QtMultimedia import QMediaDevices
            out = []
            for dev in QMediaDevices.audioOutputs():
                out.append((dev.id().toString() if hasattr(dev.id(), "toString") else str(dev.id()), dev.description()))
            return out
        except Exception:
            return []

    def set_volumes(self, input_pct: int, output_pct: int) -> None:
        """Applies capture/playback gain percentages (0-100)."""
        self._input_volume_pct = max(0, min(100, int(input_pct)))
        self._output_volume_pct = max(0, min(100, int(output_pct)))
        try:
            if self._source is not None:
                self._source.setVolume(self._input_volume_pct / 100.0)
        except Exception:
            pass
        try:
            if self._sink is not None:
                self._sink.setVolume(self._output_volume_pct / 100.0)
        except Exception:
            pass

    def set_devices(self, capture_device_id: str, playback_device_id: str) -> None:
        """Selects capture/playback devices by id (empty = system default)."""
        self._capture_device_id = capture_device_id or ""
        self._playback_device_id = playback_device_id or ""

    def start_capture(self, on_frame: Callable[[bytes], None]) -> bool:
        """Starts microphone capture; frames are 20ms 48kHz mono s16."""
        self.stop_capture()
        try:
            QAudioFormat, _sink_cls, QAudioSource, QMediaDevices = self._qt_multimedia()
            fmt = QAudioFormat()
            fmt.setSampleRate(_SAMPLE_RATE)
            fmt.setChannelCount(_CHANNELS)
            fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
            device = None
            if self._capture_device_id:
                for dev in QMediaDevices.audioInputs():
                    dev_id = dev.id().toString() if hasattr(dev.id(), "toString") else str(dev.id())
                    if dev_id == self._capture_device_id:
                        device = dev
                        break
                if device is not None and not device.isFormatSupported(fmt):
                    device = None
            if device is None:
                device = QMediaDevices.defaultAudioInput()
            self._source = QAudioSource(device, fmt, self)
            self._source.setBufferSize(_FRAME_BYTES * 8)
            self._source.setVolume(self._input_volume_pct / 100.0)
            self._source_device = self._source.start()
            if self._source_device is None:
                raise RuntimeError("microphone device refused to start")
            try:
                self._source_device.readyRead.connect(self._on_capture_ready)
            except Exception:
                pass
            self._on_capture_frame = on_frame
            self._capture_enabled = True
            if not self._pump_timer.isActive():
                self._pump_timer.start()
            return True
        except Exception as exc:
            self.audio_error.emit(f"Microphone failed: {exc}")
            self.stop_capture()
            return False

    def stop_capture(self) -> None:
        """Stops microphone capture and clears the frame buffer."""
        self._capture_enabled = False
        self._on_capture_frame = None
        self._capture_buffer = bytearray()
        try:
            if self._source_device is not None:
                try:
                    self._source_device.readyRead.disconnect(self._on_capture_ready)
                except Exception:
                    pass
        except Exception:
            pass
        self._source_device = None
        try:
            if self._source is not None:
                self._source.stop()
        except Exception:
            pass
        self._source = None
        self._maybe_stop_pump()

    def start_playback(self) -> bool:
        """Starts speaker playback of decoded alliance voice frames."""
        self.stop_playback()
        try:
            QAudioFormat, QAudioSink, _source_cls, QMediaDevices = self._qt_multimedia()
            fmt = QAudioFormat()
            fmt.setSampleRate(_SAMPLE_RATE)
            fmt.setChannelCount(_CHANNELS)
            fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
            device = None
            if self._playback_device_id:
                for dev in QMediaDevices.audioOutputs():
                    dev_id = dev.id().toString() if hasattr(dev.id(), "toString") else str(dev.id())
                    if dev_id == self._playback_device_id:
                        device = dev
                        break
                if device is not None and not device.isFormatSupported(fmt):
                    device = None
            if device is None:
                device = QMediaDevices.defaultAudioOutput()
            self._sink = QAudioSink(device, fmt, self)
            self._sink.setBufferSize(_FRAME_BYTES * 16)
            self._sink.setVolume(self._output_volume_pct / 100.0)
            self._sink_device = self._sink.start()
            if self._sink_device is None:
                raise RuntimeError("speaker device refused to start")
            if not self._pump_timer.isActive():
                self._pump_timer.start()
            return True
        except Exception as exc:
            self.audio_error.emit(f"Speaker failed: {exc}")
            self.stop_playback()
            return False

    def stop_playback(self) -> None:
        """Stops speaker playback and drops queued voice frames."""
        self._playback_queue.clear()
        self._sink_device = None
        try:
            if self._sink is not None:
                self._sink.stop()
        except Exception:
            pass
        self._sink = None
        self._maybe_stop_pump()

    def enqueue_playback(self, pcm: bytes) -> None:
        """Queues decoded PCM for the speaker pump (bounded, drops oldest)."""
        if pcm:
            self._playback_queue.append(bytes(pcm))

    def stop_all(self) -> None:
        """Stops capture and playback."""
        self.stop_capture()
        self.stop_playback()

    def _maybe_stop_pump(self) -> None:
        active = (
            self._capture_enabled
            or self._source is not None
            or self._sink is not None
        )
        if not active and self._pump_timer.isActive():
            self._pump_timer.stop()

    @staticmethod
    def _frame_peak_level(frame: bytes) -> float:
        """Peak amplitude of a 20ms s16 frame, normalized 0.0-1.0."""
        if not frame:
            return 0.0
        try:
            import array
            samples = array.array("h")
            samples.frombytes(frame[: (len(frame) // 2) * 2])
            if not samples:
                return 0.0
            peak = max(abs(s) for s in samples)
            return min(1.0, peak / 32768.0)
        except Exception:
            return 0.0

    def _on_capture_ready(self) -> None:
        """readyRead slot: slices device bytes into 20ms frames."""
        if not self._capture_enabled or self._source_device is None:
            return
        try:
            data = bytes(self._source_device.readAll())
        except Exception:
            return
        if not data:
            return
        self._capture_buffer.extend(data)
        while len(self._capture_buffer) >= _FRAME_BYTES and self._capture_enabled:
            frame = bytes(self._capture_buffer[:_FRAME_BYTES])
            del self._capture_buffer[:_FRAME_BYTES]
            try:
                self.outbound_level.emit(self._frame_peak_level(frame))
            except Exception:
                pass
            callback = self._on_capture_frame
            if callback is not None:
                try:
                    callback(frame)
                except Exception:
                    pass

    def _on_pump(self) -> None:
        """20ms tick: drains playback queue into the speaker device."""
        sink_device = self._sink_device
        sink = self._sink
        if sink_device is None or sink is None:
            return
        try:
            free = int(sink.bytesFree())
        except Exception:
            free = _FRAME_BYTES
        while self._playback_queue and free >= _FRAME_BYTES:
            frame = self._playback_queue.popleft()
            try:
                written = sink_device.write(frame[:_FRAME_BYTES])
            except Exception:
                break
            if written is None:
                break
            try:
                written = int(written)
            except Exception:
                break
            if written <= 0:
                self._playback_queue.appendleft(frame)
                break
            free -= written
            try:
                self.inbound_level.emit(self._frame_peak_level(frame))
            except Exception:
                pass
