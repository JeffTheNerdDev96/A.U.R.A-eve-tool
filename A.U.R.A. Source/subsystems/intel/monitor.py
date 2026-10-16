# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
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
Real-time EVE Online chat-log tailer for the Live Intel Radar.
Watches Chatlogs for intel pings and Local + Gamelogs for current system.
"""
from __future__ import annotations

import glob
import heapq
import os
import re
import time
from typing import Any, Dict, List, Optional, Set

from PyQt6.QtCore import QThread, pyqtSignal

from core.config import config
from core.error_handler import AURAErrorCode, log_diagnostic_error
from core.input_safety import is_safe_log_file
from .location import LocationTracker
from .parser import IntelParser

DEFAULT_INTEL_PATTERNS = [
    "intel", "imperium", "horde", "frt", "winter", "init", "brave", "snuff",
    "dock", "standing", "recon", "defense", "scout", "pvp",
]


def find_default_chatlog_dir() -> str:
    """Locate EVE Chatlogs on Windows, OneDrive, or Proton/Wine."""
    home = os.path.expanduser("~")
    user_name = os.environ.get("USER", os.environ.get("USERNAME", "steamuser"))
    candidates = [
        os.path.join(home, "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "OneDrive", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "Saved Games", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".eve", "logs", "Chatlogs"),
        os.path.join(home, ".local", "share", "Steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".steam", "steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".var", "app", "com.valvesoftware.Steam", ".local", "share", "Steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".wine", "drive_c", "users", user_name, "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "Games", "eve-online", "drive_c", "users", user_name, "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "Chatlogs"),
    ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(home, "Documents", "EVE", "logs", "Chatlogs"))


def find_default_gamelog_dir(chatlog_dir: Optional[str] = None) -> str:
    """Gamelogs sit beside Chatlogs under .../EVE/logs/Gamelogs."""
    if chatlog_dir:
        sibling = os.path.join(os.path.dirname(chatlog_dir), "Gamelogs")
        if os.path.isdir(sibling) or os.path.isdir(os.path.dirname(chatlog_dir)):
            return os.path.abspath(sibling)
    home = os.path.expanduser("~")
    for candidate in (
        os.path.join(home, "Documents", "EVE", "logs", "Gamelogs"),
        os.path.join(home, "OneDrive", "Documents", "EVE", "logs", "Gamelogs"),
        os.path.join(home, "Saved Games", "EVE", "logs", "Gamelogs"),
    ):
        if os.path.isdir(candidate):
            return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(home, "Documents", "EVE", "logs", "Gamelogs"))


_RE_LOG_DATESTAMP = re.compile(r"_\d{8}(?:_\d{4,6})?(?:_\d+)?")


def decode_log_bytes(raw: bytes, encoding: Optional[str] = None) -> str:
    if not raw:
        return ""
    if encoding:
        if "utf-16" in encoding.lower():
            even_len = len(raw) - (len(raw) % 2)
            decoded = raw[:even_len].decode(encoding, errors="replace")
            return decoded.replace("\x00", "").replace("\ufeff", "")
        decoded = raw.decode(encoding, errors="replace")
        return decoded.replace("\x00", "").replace("\ufeff", "")

    if raw.startswith(b"\xff\xfe"):
        even_len = len(raw[2:]) - (len(raw[2:]) % 2)
        return raw[2:2 + even_len].decode("utf-16-le", errors="replace").replace("\x00", "").replace("\ufeff", "")
    if raw.startswith(b"\xfe\xff"):
        even_len = len(raw[2:]) - (len(raw[2:]) % 2)
        return raw[2:2 + even_len].decode("utf-16-be", errors="replace").replace("\x00", "").replace("\ufeff", "")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="replace").replace("\x00", "").replace("\ufeff", "")

    # If NUL bytes are detected in raw, decode as UTF-16-LE
    if b"\x00" in raw:
        even_len = len(raw) - (len(raw) % 2)
        try:
            return raw[:even_len].decode("utf-16-le", errors="replace").replace("\x00", "").replace("\ufeff", "")
        except (UnicodeDecodeError, LookupError):
            pass

    try:
        return raw.decode("utf-8").replace("\x00", "").replace("\ufeff", "")
    except UnicodeDecodeError:
        pass

    for enc in ("utf-16-le", "cp1252", "latin-1"):
        try:
            if enc == "utf-16-le":
                even_len = len(raw) - (len(raw) % 2)
                return raw[:even_len].decode(enc, errors="replace").replace("\x00", "").replace("\ufeff", "")
            return raw.decode(enc).replace("\x00", "").replace("\ufeff", "")
        except (UnicodeDecodeError, LookupError):
            continue

    return raw.decode("utf-8", errors="ignore").replace("\x00", "").replace("\ufeff", "")


def detect_log_encoding(filepath: str) -> str:
    """Detects primary character encoding of an EVE log file."""
    try:
        with open(filepath, "rb") as fp:
            prefix = fp.read(1024)
            if prefix.startswith(b"\xff\xfe"):
                return "utf-16-le"
            if prefix.startswith(b"\xfe\xff"):
                return "utf-16-be"
            if prefix.startswith(b"\xef\xbb\xbf"):
                return "utf-8-sig"
            if len(prefix) >= 4 and prefix.count(b"\x00") > (len(prefix) // 4):
                return "utf-16-le"
    except Exception:
        pass
    return "utf-8"


def extract_channel_name(filepath: str) -> str:
    base = os.path.basename(filepath)
    stem, _ = os.path.splitext(base)
    m = _RE_LOG_DATESTAMP.search(stem)
    if m:
        return stem[:m.start()]
    return stem


def _is_local_file(filepath: str) -> bool:
    return "local" in os.path.basename(filepath).lower()


def _is_gamelog_file(filepath: str) -> bool:
    return "gamelogs" in os.path.normpath(filepath).lower()


class LiveChatMonitor(QThread):
    """Polls EVE chat/gamelog files and emits intel plus location signals."""

    intel_line_received = pyqtSignal(str, str)
    active_channels_updated = pyqtSignal(list)
    characters_updated = pyqtSignal(list)
    status_updated = pyqtSignal(str, bool)
    location_changed = pyqtSignal(str, int)

    def __init__(
        self,
        log_dir: Optional[str] = None,
        channel_filter: str = "intel",
        custom_patterns: Optional[str] = None,
        poll_interval_ms: int = 400,
    ):
        super().__init__()
        self.log_dir = log_dir or find_default_chatlog_dir()
        self.gamelog_dir = find_default_gamelog_dir(self.log_dir)
        self.channel_filter = (channel_filter or "intel").lower()
        pattern_src = custom_patterns if custom_patterns is not None else config.custom_intel_channels
        self.custom_patterns: List[str] = [p.strip().lower() for p in pattern_src.split(",") if p.strip()]
        self.poll_interval = poll_interval_ms / 1000.0
        self.running = False
        self.file_positions: Dict[str, int] = {}
        self.known_files: Set[str] = set()
        self.cached_files: List[str] = []
        self.last_dir_scan_time: float = 0.0
        self.location = LocationTracker()
        # Change detection must be per character: multiboxed pilots often enter the same system in turn.
        self._location_trackers: Dict[str, LocationTracker] = {}
        self._file_characters: Dict[str, str] = {}
        self._character_locations: Dict[str, Dict[str, Any]] = {}
        self._known_characters: Set[str] = set()
        self.selected_character: Optional[str] = None
        self._need_bootstrap = True
        self._last_active_channels: List[str] = []
        self._partial_buffers: Dict[str, str] = {}
        self._line_buffers: Dict[str, str] = self._partial_buffers
        self._file_encodings: Dict[str, str] = {}

    def set_selected_character(self, character_name: Optional[str]) -> None:
        if not character_name or character_name.strip() in ("Auto", "All", "None", ""):
            self.selected_character = None
            return
        self.selected_character = character_name.strip()
        loc = self._character_locations.get(self.selected_character)
        if loc:
            self.location_changed.emit(loc["system"], int(loc["system_id"]))

    def set_log_dir(self, new_dir: str) -> None:
        self.log_dir = os.path.abspath(new_dir)
        self.gamelog_dir = find_default_gamelog_dir(self.log_dir)
        self.file_positions.clear()
        self.known_files.clear()
        self._partial_buffers.clear()
        self._file_encodings.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0
        self._need_bootstrap = True
        dir_ok = os.path.isdir(self.log_dir)
        self.status_updated.emit(f"Log directory set to: {self.log_dir}", self.running and dir_ok)

    def set_custom_patterns(self, pattern_str: str) -> None:
        self.custom_patterns = [p.strip().lower() for p in pattern_str.split(",") if p.strip()]
        config.custom_intel_channels = pattern_str
        self.file_positions.clear()
        self.known_files.clear()
        self._partial_buffers.clear()
        self._file_encodings.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0

    def set_channel_filter(self, channel_filter: str) -> None:
        self.channel_filter = (channel_filter or "intel").lower()
        self.file_positions.clear()
        self.known_files.clear()
        self._partial_buffers.clear()
        self._file_encodings.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0

    def stop(self) -> None:
        self.running = False
        from core.lifecycle import CHAT_MONITOR_JOIN_MS
        self.wait(CHAT_MONITOR_JOIN_MS)

    def run(self) -> None:
        self.running = True
        self._need_bootstrap = True
        missing_logged_for: Optional[str] = None

        while self.running:
            if not os.path.isdir(self.log_dir):
                if missing_logged_for != self.log_dir:
                    log_diagnostic_error(
                        AURAErrorCode.ERR_4001_CHATLOG_DIR_MISSING,
                        FileNotFoundError(self.log_dir),
                        f"LiveChatMonitor.log_dir missing: {self.log_dir}",
                    )
                    missing_logged_for = self.log_dir
                self.status_updated.emit(f"Chat log directory not found: {self.log_dir}", False)
                self._need_bootstrap = True
                time.sleep(max(self.poll_interval, 1.0))
                continue

            missing_logged_for = None
            if self._need_bootstrap:
                self._need_bootstrap = False
                self.status_updated.emit(f"Monitoring active on {self.log_dir}", True)
                self.cached_files = []
                self.last_dir_scan_time = 0.0
                self._scan_and_seek_to_end()

            try:
                self._check_for_new_data()
            except PermissionError as exc:
                log_diagnostic_error(AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED, exc, "LiveChatMonitor.run")
            except OSError as exc:
                log_diagnostic_error(AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED, exc, "LiveChatMonitor.run")
            except Exception as exc:
                log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, "LiveChatMonitor.run")
            time.sleep(self.poll_interval)

        self.status_updated.emit("Monitoring paused", False)

    def _matches_intel_filter(self, filepath: str) -> bool:
        fname = os.path.basename(filepath).lower()
        if self.channel_filter == "all":
            return True
        if self.channel_filter == "intel":
            return any(pat in fname for pat in DEFAULT_INTEL_PATTERNS) or any(
                pat in fname for pat in self.custom_patterns
            )
        if self.channel_filter == "custom":
            if not self.custom_patterns:
                return True
            return any(pat in fname for pat in self.custom_patterns)
        if self.channel_filter == "alliance":
            return "alliance" in fname or any(pat in fname for pat in DEFAULT_INTEL_PATTERNS)
        if self.channel_filter == "corp":
            return "corp" in fname
        if self.channel_filter == "local":
            return "local" in fname
        if any(pat in fname for pat in self.custom_patterns):
            return True
        return self.channel_filter in fname

    def _allowed_log_roots(self) -> List[str]:
        return [self.log_dir, self.gamelog_dir]

    def _is_allowed_log_path(self, filepath: str) -> bool:
        return any(is_safe_log_file(root, filepath) for root in self._allowed_log_roots())

    def _list_recent(self, directory: str, limit: int, predicate: Optional[Any] = None) -> List[str]:
        if not directory or not os.path.isdir(directory) or limit <= 0:
            return []
        try:
            with os.scandir(directory) as it:
                entries = [
                    entry for entry in it
                    if entry.name.endswith(".txt") and entry.is_file() and self._is_allowed_log_path(entry.path)
                    and (predicate is None or predicate(entry.path))
                ]
                top_entries = heapq.nlargest(limit, entries, key=lambda e: e.stat().st_mtime)
                return [e.path for e in top_entries]
        except (OSError, PermissionError):
            return []

    def _get_active_log_files(self, force_rescan: bool = False) -> List[str]:
        now = time.time()
        if not force_rescan and self.cached_files and (now - self.last_dir_scan_time < 5.0):
            return self.cached_files

        intel_files: List[str] = []
        local_files: List[str] = []
        if os.path.isdir(self.log_dir):
            intel_files = self._list_recent(
                self.log_dir, 20,
                predicate=lambda p: self._matches_intel_filter(p)
            )
            # Prevent local chat monitoring starvation (BUG-PARSER-04): filter local files before slicing
            local_files = self._list_recent(
                self.log_dir, 8,
                predicate=lambda p: _is_local_file(p)
            )

        game_files = self._list_recent(self.gamelog_dir, getattr(config, "max_multibox_clients", 4))

        merged: List[str] = []
        seen = set()
        for path in intel_files + local_files + game_files:
            if path not in seen:
                seen.add(path)
                merged.append(path)

        self.cached_files = merged
        self.last_dir_scan_time = now
        return self.cached_files

    def _prune_inactive_log_maps(self, active_paths: List[str]) -> None:
        """Drop seek offsets and per-file character maps for logs no longer in the active set."""
        active = set(active_paths)
        for path in list(self.file_positions.keys()):
            if path not in active:
                self.file_positions.pop(path, None)
                self.known_files.discard(path)
                self._file_characters.pop(path, None)
                self._partial_buffers.pop(path, None)
                self._file_encodings.pop(path, None)
        still_known = set(self._file_characters.values())
        if still_known != self._known_characters:
            self._known_characters = still_known
            self.characters_updated.emit(sorted(self._known_characters))
        for name in list(self._character_locations.keys()):
            if name not in self._known_characters:
                self._character_locations.pop(name, None)
        for key in list(self._location_trackers.keys()):
            if key not in active and key not in self._known_characters:
                self._location_trackers.pop(key, None)

    def _tracker_for(self, filepath: str) -> LocationTracker:
        key = self._file_characters.get(filepath) or filepath
        tracker = self._location_trackers.get(key)
        if tracker is None:
            tracker = LocationTracker(self.location.eve_map)
            self._location_trackers[key] = tracker
        return tracker

    def _emit_location(self, hit: Optional[Dict[str, Any]], filepath: Optional[str] = None) -> None:
        if not hit:
            return
        char_name = self._file_characters.get(filepath) if filepath else None
        if char_name:
            self._character_locations[char_name] = {
                "system": hit["system"],
                "system_id": int(hit["system_id"]),
                "ts": time.time(),
            }
        if self.selected_character is None or self.selected_character == char_name:
            self.location_changed.emit(hit["system"], int(hit["system_id"]))

    def _read_prefix(self, filepath: str, nbytes: int = 8192) -> str:
        if not self._is_allowed_log_path(filepath):
            return ""
        nbytes = min(nbytes, int(getattr(config, "max_log_read_bytes", 512 * 1024)))
        try:
            if filepath not in self._file_encodings:
                self._file_encodings[filepath] = detect_log_encoding(filepath)
            enc = self._file_encodings[filepath]
            with open(filepath, "rb") as fp:
                return decode_log_bytes(fp.read(nbytes), encoding=enc)
        except PermissionError as exc:
            log_diagnostic_error(AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED, exc, f"LiveChatMonitor._read_prefix({filepath})")
            return ""
        except OSError as exc:
            log_diagnostic_error(AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED, exc, f"LiveChatMonitor._read_prefix({filepath})")
            return ""

    def _note_listener(self, filepath: str, blob: str) -> None:
        pilot = LocationTracker.extract_listener(blob)
        if not pilot:
            return
        self._file_characters[filepath] = pilot
        if pilot not in self._known_characters:
            self._known_characters.add(pilot)
            self.characters_updated.emit(sorted(self._known_characters))

    def _ingest_location_prefix(self, filepath: str) -> None:
        blob = self._read_prefix(filepath)
        if not blob:
            return
        self._note_listener(filepath, blob)
        tracker = self._tracker_for(filepath)
        hit = tracker.parse_header_blob(blob)
        if not hit:
            for line in blob.splitlines():
                hit = tracker.parse_line(line)
                if hit:
                    break
        self._emit_location(hit, filepath)

    def _scan_and_seek_to_end(self) -> None:
        files = self._get_active_log_files(force_rescan=True)
        active_names: List[str] = []
        bootstrapped_local = False
        bootstrapped_game = False
        for path in files:
            if not self._is_allowed_log_path(path):
                continue
            channel = extract_channel_name(path)
            if channel not in active_names and not _is_gamelog_file(path):
                active_names.append(channel)
            try:
                sz = os.path.getsize(path)
                if path not in self._file_encodings:
                    self._file_encodings[path] = detect_log_encoding(path)
                enc = self._file_encodings[path]
                if "utf-16" in enc.lower():
                    sz = sz - (sz % 2)
                self.file_positions[path] = sz
                self.known_files.add(path)
                if not _is_local_file(path) and not _is_gamelog_file(path) and sz > 0:
                    tail_len = min(sz, 8192)
                    if "utf-16" in enc.lower():
                        tail_len = tail_len - (tail_len % 2)
                    seek_pos = max(0, sz - tail_len)
                    if "utf-16" in enc.lower() and (seek_pos % 2) != 0:
                        seek_pos -= 1
                    with open(path, "rb") as fp:
                        fp.seek(seek_pos)
                        tail_bytes = fp.read(tail_len)
                    tail_text = decode_log_bytes(tail_bytes, encoding=enc)
                    if tail_text:
                        lines = tail_text.splitlines()[-25:]
                        trailing_nl = "\n" if tail_text.endswith(("\n", "\r")) else ""
                        self._process_text(path, "\n".join(lines) + trailing_nl, channel)
            except OSError:
                continue
            if path not in self._file_characters:
                self._note_listener(path, self._read_prefix(path, 4096))
            if not bootstrapped_local and _is_local_file(path):
                self._ingest_location_prefix(path)
                bootstrapped_local = True
            elif not bootstrapped_game and _is_gamelog_file(path):
                self._ingest_location_prefix(path)
                bootstrapped_game = True
        self._emit_active_channels(active_names)
        self._prune_inactive_log_maps(files)

    def _emit_active_channels(self, names: List[str]) -> None:
        if names == self._last_active_channels:
            return
        self._last_active_channels = list(names)
        self.active_channels_updated.emit(names)

    def _process_text(self, filepath: str, text: str, channel_name: str) -> None:
        if not text:
            return
        is_local = _is_local_file(filepath)
        is_game = _is_gamelog_file(filepath)
        emit_intel = (not is_game) and (not is_local or self.channel_filter in ("local", "all"))

        buffered = self._partial_buffers.get(filepath, "") + text
        if not text.endswith(("\n", "\r")):
            lines = buffered.splitlines()
            if lines:
                self._partial_buffers[filepath] = lines[-1]
                lines_to_process = lines[:-1]
            else:
                self._partial_buffers[filepath] = buffered
                lines_to_process = []
        else:
            self._partial_buffers[filepath] = ""
            lines_to_process = buffered.splitlines()

        for raw_line in lines_to_process:
            if is_local or is_game:
                self._emit_location(self._tracker_for(filepath).parse_line(raw_line), filepath)
            if not emit_intel:
                continue
            try:
                parsed = IntelParser.parse_single_line(raw_line, channel_name)
            except Exception as exc:
                log_diagnostic_error(
                    AURAErrorCode.ERR_5001_WORKER_CRASH,
                    exc,
                    "LiveChatMonitor._process_text.parse_single_line",
                )
                continue
            if not parsed:
                continue
            self.intel_line_received.emit(raw_line, channel_name)

    def _check_for_new_data(self) -> None:
        current_files = self._get_active_log_files(force_rescan=False)
        self._prune_inactive_log_maps(current_files)
        active_names: List[str] = []

        for path in current_files:
            if not self._is_allowed_log_path(path):
                continue
            channel = extract_channel_name(path)
            if channel not in active_names and not _is_gamelog_file(path):
                active_names.append(channel)

            if path not in self._file_characters:
                self._note_listener(path, self._read_prefix(path, 4096))

            if path not in self.file_positions:
                try:
                    sz = os.path.getsize(path)
                    if path not in self._file_encodings:
                        self._file_encodings[path] = detect_log_encoding(path)
                    enc = self._file_encodings[path]
                    if "utf-16" in enc.lower():
                        sz = sz - (sz % 2)
                    self.file_positions[path] = sz
                    self.known_files.add(path)
                    if _is_local_file(path) or _is_gamelog_file(path):
                        self._ingest_location_prefix(path)
                except OSError:
                    pass
                continue

            try:
                current_size = os.path.getsize(path)
                last_pos = self.file_positions.get(path, 0)
                if current_size < last_pos:
                    # File was truncated or rotated in place; reset position to start
                    last_pos = 0
                    self.file_positions[path] = 0
                    self._partial_buffers.pop(path, None)
                    self._file_encodings.pop(path, None)
                    if _is_local_file(path) or _is_gamelog_file(path):
                        self._note_listener(path, self._read_prefix(path, 4096))
                        self._ingest_location_prefix(path)

                if current_size > last_pos:
                    if path not in self._file_encodings or (self._file_encodings[path] == "utf-8" and current_size > 0):
                        old_enc = self._file_encodings.get(path)
                        new_enc = detect_log_encoding(path)
                        self._file_encodings[path] = new_enc
                        if old_enc != new_enc and "utf-16" in new_enc.lower():
                            if (last_pos % 2) != 0:
                                last_pos = last_pos - (last_pos % 2)
                                self.file_positions[path] = last_pos
                            if old_enc == "utf-8" and last_pos <= 2:
                                last_pos = 0
                                self.file_positions[path] = 0
                            self._partial_buffers.pop(path, None)

                    enc = self._file_encodings[path]

                    # For any UTF-16 file, enforce that last_pos is strictly aligned to even boundaries before seeking
                    if "utf-16" in enc.lower() and (last_pos % 2) != 0:
                        last_pos = last_pos - (last_pos % 2)
                        self.file_positions[path] = last_pos

                    read_len = min(current_size - last_pos, int(getattr(config, "max_log_read_bytes", 512 * 1024)))
                    # For UTF-16 encodings, enforce 2-byte alignment to prevent byte-shift stream desync (BUG-PARSER-02)
                    if "utf-16" in enc.lower() and (read_len % 2) != 0:
                        read_len -= 1

                    if read_len <= 0:
                        continue

                    with open(path, "rb") as fp:
                        fp.seek(last_pos)
                        new_bytes = fp.read(read_len)

                    # Ensure byte alignment if partial read ended on odd boundary
                    if "utf-16" in enc.lower() and (len(new_bytes) % 2) != 0:
                        new_bytes = new_bytes[:-1]

                    consumed = len(new_bytes)
                    self.file_positions[path] = last_pos + consumed
                    if new_bytes:
                        self._process_text(path, decode_log_bytes(new_bytes, encoding=enc), channel)
            except PermissionError as exc:
                log_diagnostic_error(
                    AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED,
                    exc,
                    f"LiveChatMonitor._check_for_new_data({path})",
                )
            except OSError as exc:
                log_diagnostic_error(
                    AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED,
                    exc,
                    f"LiveChatMonitor._check_for_new_data({path})",
                )

        self._emit_active_channels(active_names)

    def simulate_intel_line(self, line: str, channel: str = "Delve.Intel") -> None:
        try:
            parsed = IntelParser.parse_single_line(line, channel)
        except Exception as exc:
            log_diagnostic_error(
                AURAErrorCode.ERR_5001_WORKER_CRASH,
                exc,
                "LiveChatMonitor.simulate_intel_line",
            )
            return
        if not parsed:
            return
        self.intel_line_received.emit(line, channel)
