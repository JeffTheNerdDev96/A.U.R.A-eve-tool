"""
Real-Time EVE Online Live Chat Log Tailer & Intel Stream Monitor (RIFT-Style).
Monitors EVE Online chat logs in `%USERPROFILE%\\Documents\\EVE\\logs\\Chatlogs`,
always tails Local + Gamelogs for location, and intel channels for threat pings.
"""
import os
import glob
import time
from typing import Dict, List, Any, Optional, Set
from PyQt6.QtCore import QThread, pyqtSignal

from intel_parser import IntelParser
from location_tracker import LocationTracker
from config import config

DEFAULT_INTEL_PATTERNS = [
    "intel", "imperium", "horde", "frt", "winter", "init", "brave", "snuff",
    "dock", "standing", "recon", "defense", "scout", "pvp"
]


def find_default_chatlog_dir() -> str:
    """Finds the active EVE Online Chatlogs folder on Windows or Linux (Steam Proton / Wine)."""
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
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(os.path.join(home, "Documents", "EVE", "logs", "Chatlogs"))


def find_default_gamelog_dir(chatlog_dir: Optional[str] = None) -> str:
    """Gamelogs sit beside Chatlogs: .../EVE/logs/Gamelogs."""
    if chatlog_dir:
        sibling = os.path.join(os.path.dirname(chatlog_dir), "Gamelogs")
        if os.path.exists(sibling) or os.path.isdir(os.path.dirname(chatlog_dir)):
            return os.path.abspath(sibling)
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Documents", "EVE", "logs", "Gamelogs"),
        os.path.join(home, "OneDrive", "Documents", "EVE", "logs", "Gamelogs"),
        os.path.join(home, "Saved Games", "EVE", "logs", "Gamelogs"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(os.path.join(home, "Documents", "EVE", "logs", "Gamelogs"))


def decode_log_bytes(raw_bytes: bytes) -> str:
    """Safely decodes raw bytes from EVE Online chat logs."""
    for enc in ["utf-16-le", "utf-16", "utf-8-sig", "utf-8", "cp1252", "latin-1"]:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


def extract_channel_name_from_filename(filename: str) -> str:
    """Extracts the human-readable channel name from EVE log filename."""
    base = os.path.basename(filename)
    parts = base.split("_")
    if len(parts) >= 2:
        return parts[0]
    return os.path.splitext(base)[0]


def _is_local_file(filepath: str) -> bool:
    return "local" in os.path.basename(filepath).lower()


def _is_gamelog_file(filepath: str) -> bool:
    return "gamelogs" in os.path.normpath(filepath).lower()


class LiveChatMonitor(QThread):
    """
    Background worker that watches EVE chat log files in real-time.
    Always tails Local and Gamelogs for location even when intel filters are active.
    """
    intel_received = pyqtSignal(dict)
    critical_threat_detected = pyqtSignal(dict)
    active_channels_updated = pyqtSignal(list)
    status_updated = pyqtSignal(str, bool)
    location_changed = pyqtSignal(str, int)

    def __init__(self, log_dir: Optional[str] = None, channel_filter: str = "intel", custom_patterns: Optional[str] = None, poll_interval_ms: int = 400):
        super().__init__()
        self.log_dir = log_dir or find_default_chatlog_dir()
        self.gamelog_dir = find_default_gamelog_dir(self.log_dir)
        self.channel_filter = channel_filter.lower()
        self.custom_patterns: List[str] = [p.strip().lower() for p in (custom_patterns or config.custom_intel_channels).split(",") if p.strip()]
        self.poll_interval = poll_interval_ms / 1000.0
        self.running = False
        self.file_positions: Dict[str, int] = {}
        self.known_files: Set[str] = set()
        self.cached_files: List[str] = []
        self.last_dir_scan_time: float = 0.0
        self.location = LocationTracker()

    def set_log_dir(self, new_dir: str):
        self.log_dir = os.path.abspath(new_dir)
        self.gamelog_dir = find_default_gamelog_dir(self.log_dir)
        self.file_positions.clear()
        self.known_files.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0
        self.status_updated.emit(f"Log directory set to: {self.log_dir}", self.running)

    def set_custom_patterns(self, pattern_str: str):
        self.custom_patterns = [p.strip().lower() for p in pattern_str.split(",") if p.strip()]
        config.custom_intel_channels = pattern_str
        self.file_positions.clear()
        self.known_files.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0

    def set_channel_filter(self, channel_filter: str):
        self.channel_filter = channel_filter.lower()
        self.file_positions.clear()
        self.known_files.clear()
        self.cached_files = []
        self.last_dir_scan_time = 0.0

    def stop(self):
        self.running = False
        self.wait(1500)

    def run(self):
        self.running = True
        self.status_updated.emit(f"Monitoring active on {self.log_dir}", True)
        self.cached_files = []
        self.last_dir_scan_time = 0.0
        self._scan_and_seek_to_end()

        while self.running:
            try:
                self._check_for_new_data()
            except Exception:
                pass
            time.sleep(self.poll_interval)

        self.status_updated.emit("Monitoring paused", False)

    def _matches_intel_filter(self, filepath: str) -> bool:
        fname = os.path.basename(filepath).lower()
        if self.channel_filter == "all":
            return True
        elif self.channel_filter == "intel":
            if any(pat in fname for pat in DEFAULT_INTEL_PATTERNS):
                return True
            if any(pat in fname for pat in self.custom_patterns):
                return True
            return False
        elif self.channel_filter == "custom":
            if not self.custom_patterns:
                return True
            return any(pat in fname for pat in self.custom_patterns)
        elif self.channel_filter == "alliance":
            return "alliance" in fname or any(pat in fname for pat in DEFAULT_INTEL_PATTERNS)
        elif self.channel_filter == "corp":
            return "corp" in fname
        elif self.channel_filter == "local":
            return "local" in fname
        elif any(pat in fname for pat in self.custom_patterns):
            return True
        elif self.channel_filter in fname:
            return True
        return False

    def _list_recent(self, directory: str, limit: int) -> List[str]:
        if not directory or not os.path.exists(directory):
            return []
        files = glob.glob(os.path.join(directory, "*.txt"))
        files.sort(key=os.path.getmtime, reverse=True)
        return files[:limit]

    def _get_active_log_files(self, force_rescan: bool = False) -> List[str]:
        now = time.time()
        if not force_rescan and self.cached_files and (now - self.last_dir_scan_time < 5.0):
            return self.cached_files

        intel_files = []
        if os.path.exists(self.log_dir):
            pattern = os.path.join(self.log_dir, "*.txt")
            intel_files = [f for f in glob.glob(pattern) if self._matches_intel_filter(f)]
            intel_files.sort(key=os.path.getmtime, reverse=True)
            intel_files = intel_files[:20]

        local_files = [f for f in self._list_recent(self.log_dir, 8) if _is_local_file(f)]
        game_files = self._list_recent(self.gamelog_dir, 4)

        merged: List[str] = []
        seen = set()
        for f in intel_files + local_files + game_files:
            if f not in seen:
                seen.add(f)
                merged.append(f)

        self.cached_files = merged
        self.last_dir_scan_time = now
        return self.cached_files

    def _emit_location(self, hit: Optional[Dict[str, Any]]):
        if not hit:
            return
        self.location_changed.emit(hit["system"], int(hit["system_id"]))

    def _read_prefix(self, filepath: str, nbytes: int = 8192) -> str:
        try:
            with open(filepath, "rb") as fp:
                return decode_log_bytes(fp.read(nbytes))
        except Exception:
            return ""

    def _ingest_location_prefix(self, filepath: str):
        blob = self._read_prefix(filepath)
        if not blob:
            return
        hit = self.location.parse_header_blob(blob)
        if not hit:
            for line in blob.splitlines():
                hit = self.location.parse_line(line)
                if hit:
                    break
        self._emit_location(hit)

    def _scan_and_seek_to_end(self):
        files = self._get_active_log_files(force_rescan=True)
        active_names = []
        bootstrapped_local = False
        bootstrapped_game = False
        for f in files:
            ch_name = extract_channel_name_from_filename(f)
            if ch_name not in active_names and not _is_gamelog_file(f):
                active_names.append(ch_name)
            try:
                sz = os.path.getsize(f)
                self.file_positions[f] = sz
                self.known_files.add(f)
            except Exception:
                continue
            if not bootstrapped_local and _is_local_file(f):
                self._ingest_location_prefix(f)
                bootstrapped_local = True
            elif not bootstrapped_game and _is_gamelog_file(f):
                self._ingest_location_prefix(f)
                bootstrapped_game = True
        self.active_channels_updated.emit(active_names)

    def _process_text(self, filepath: str, text: str, channel_name: str):
        is_local = _is_local_file(filepath)
        is_game = _is_gamelog_file(filepath)
        emit_intel = (not is_game) and (not is_local or self.channel_filter in ("local", "all"))

        for raw_line in text.splitlines():
            if is_local or is_game:
                hit = self.location.parse_line(raw_line)
                self._emit_location(hit)
            if not emit_intel:
                continue
            parsed = IntelParser.parse_single_line(raw_line, channel_name)
            if parsed:
                self.intel_received.emit(parsed)
                if parsed["is_critical"]:
                    self.critical_threat_detected.emit(parsed)

    def _check_for_new_data(self):
        current_files = self._get_active_log_files(force_rescan=False)
        active_names = []

        for f in current_files:
            ch_name = extract_channel_name_from_filename(f)
            if ch_name not in active_names and not _is_gamelog_file(f):
                active_names.append(ch_name)

            if f not in self.file_positions:
                try:
                    sz = os.path.getsize(f)
                    self.file_positions[f] = sz
                    self.known_files.add(f)
                    if _is_local_file(f) or _is_gamelog_file(f):
                        self._ingest_location_prefix(f)
                except Exception:
                    pass
                continue

            try:
                current_size = os.path.getsize(f)
                last_pos = self.file_positions.get(f, 0)

                if current_size > last_pos:
                    with open(f, "rb") as fp:
                        fp.seek(last_pos)
                        new_bytes = fp.read(current_size - last_pos)
                        self.file_positions[f] = current_size
                    decoded_text = decode_log_bytes(new_bytes)
                    self._process_text(f, decoded_text, ch_name)
                elif current_size < last_pos:
                    self.file_positions[f] = current_size
            except Exception:
                pass

        self.active_channels_updated.emit(active_names)

    def simulate_intel_line(self, line: str, channel: str = "Delve.Intel"):
        parsed = IntelParser.parse_single_line(line, channel)
        if parsed:
            self.intel_received.emit(parsed)
            if parsed["is_critical"]:
                self.critical_threat_detected.emit(parsed)
