"""
Real-Time EVE Online Live Chat Log Tailer & Intel Stream Monitor (RIFT-Style).
Monitors EVE Online chat logs in `%USERPROFILE%\\Documents\\EVE\\logs\\Chatlogs`,
detects live appends across intel/alliance/local channels, decodes UTF-16/UTF-8 lines,
and triggers real-time tactical alerts for A.U.R.A.
"""
import os
import glob
import time
from typing import Dict, List, Any, Optional, Set
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from intel_parser import IntelParser


def find_default_chatlog_dir() -> str:
    """Finds the active EVE Online Chatlogs folder on Windows or Linux (Steam Proton / Wine)."""
    home = os.path.expanduser("~")
    user_name = os.environ.get("USER", os.environ.get("USERNAME", "steamuser"))
    candidates = [
        # Windows Standard
        os.path.join(home, "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "OneDrive", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "Saved Games", "EVE", "logs", "Chatlogs"),
        # Linux Native / Home EVE
        os.path.join(home, "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".eve", "logs", "Chatlogs"),
        # Linux Steam Proton (EVE Online Steam App ID: 8500)
        os.path.join(home, ".local", "share", "Steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".steam", "steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, ".var", "app", "com.valvesoftware.Steam", ".local", "share", "Steam", "steamapps", "compatdata", "8500", "pfx", "drive_c", "users", "steamuser", "Documents", "EVE", "logs", "Chatlogs"),
        # Linux Wine / Lutris / Bottles prefixes
        os.path.join(home, ".wine", "drive_c", "users", user_name, "Documents", "EVE", "logs", "Chatlogs"),
        os.path.join(home, "Games", "eve-online", "drive_c", "users", user_name, "Documents", "EVE", "logs", "Chatlogs"),
        # App local fallback
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "Chatlogs"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
            
    # Default preferred path (even if not yet created by EVE)
    default_dir = os.path.join(home, "Documents", "EVE", "logs", "Chatlogs")
    return os.path.abspath(default_dir)


def decode_log_bytes(raw_bytes: bytes) -> str:
    """Safely decodes raw bytes from EVE Online chat logs."""
    for enc in ["utf-16-le", "utf-16", "utf-8-sig", "utf-8", "cp1252", "latin-1"]:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


def extract_channel_name_from_filename(filename: str) -> str:
    """Extracts the human-readable channel name from EVE log filename: e.g. Delve.Intel_20260818_193000_123.txt -> Delve.Intel"""
    base = os.path.basename(filename)
    parts = base.split("_")
    if len(parts) >= 2:
        return parts[0]
    return os.path.splitext(base)[0]


class LiveChatMonitor(QThread):
    """
    Background worker that watches EVE chat log files in real-time.
    Similar to RIFT Intel Fusion Tool core log tailing.
    """
    intel_received = pyqtSignal(dict)           # Emitted on every parsed intel message
    critical_threat_detected = pyqtSignal(dict) # Emitted on high/critical threat lines
    active_channels_updated = pyqtSignal(list)  # List of channel names currently monitored
    status_updated = pyqtSignal(str, bool)      # Status text, is_active

    def __init__(self, log_dir: Optional[str] = None, channel_filter: str = "all", poll_interval_ms: int = 400):
        super().__init__()
        self.log_dir = log_dir or find_default_chatlog_dir()
        self.channel_filter = channel_filter.lower()  # 'all', 'intel', 'alliance', 'corp', 'local'
        self.poll_interval = poll_interval_ms / 1000.0
        self.running = False
        
        # Track file positions: {filepath: last_byte_offset}
        self.file_positions: Dict[str, int] = {}
        self.known_files: Set[str] = set()
        self.cached_files: List[str] = []
        self.last_dir_scan_time: float = 0.0


    def set_log_dir(self, new_dir: str):
        """Updates monitored directory and resets file offsets."""
        self.log_dir = os.path.abspath(new_dir)
        self.file_positions.clear()
        self.known_files.clear()
        self.status_updated.emit(f"Log directory set to: {self.log_dir}", self.running)

    def set_channel_filter(self, channel_filter: str):
        self.channel_filter = channel_filter.lower()
        self.file_positions.clear()
        self.known_files.clear()

    def stop(self):
        self.running = False
        self.wait(1500)

    def run(self):
        self.running = True
        self.status_updated.emit(f"Monitoring active on {self.log_dir}", True)
        
        # Initial scan: find existing files and seek to end so we only read NEW lines
        self.cached_files: List[str] = []
        self.last_dir_scan_time = 0.0
        self._scan_and_seek_to_end()

        while self.running:
            try:
                self._check_for_new_data()
            except Exception:
                pass
            time.sleep(self.poll_interval)

        self.status_updated.emit("Monitoring paused", False)

    def _matches_filter(self, filepath: str) -> bool:
        fname = os.path.basename(filepath).lower()
        if self.channel_filter == "all":
            return True
        elif self.channel_filter == "intel":
            return "intel" in fname
        elif self.channel_filter == "alliance":
            return "alliance" in fname or "intel" in fname
        elif self.channel_filter == "corp":
            return "corp" in fname
        elif self.channel_filter == "local":
            return "local" in fname
        elif self.channel_filter in fname:
            return True
        return False

    def _get_active_log_files(self, force_rescan: bool = False) -> List[str]:
        now = time.time()
        # Rescan directory only once every 5 seconds to eliminate disk I/O churn
        if not force_rescan and self.cached_files and (now - self.last_dir_scan_time < 5.0):
            return self.cached_files

        if not os.path.exists(self.log_dir):
            self.cached_files = []
            return []

        pattern = os.path.join(self.log_dir, "*.txt")
        files = glob.glob(pattern)
        matched = [f for f in files if self._matches_filter(f)]
        # Sort by mtime descending
        matched.sort(key=os.path.getmtime, reverse=True)
        self.cached_files = matched[:20]  # Watch top 20 most recent channels
        self.last_dir_scan_time = now
        return self.cached_files

    def _scan_and_seek_to_end(self):
        """Initial baseline seek to the end of all active files."""
        files = self._get_active_log_files(force_rescan=True)
        active_names = []
        for f in files:
            ch_name = extract_channel_name_from_filename(f)
            if ch_name not in active_names:
                active_names.append(ch_name)
            try:
                sz = os.path.getsize(f)
                self.file_positions[f] = sz
                self.known_files.add(f)
            except Exception:
                pass
        self.active_channels_updated.emit(active_names)

    def _check_for_new_data(self):
        current_files = self._get_active_log_files(force_rescan=False)
        active_names = []

        for f in current_files:
            ch_name = extract_channel_name_from_filename(f)
            if ch_name not in active_names:
                active_names.append(ch_name)

            # If brand new file detected while running
            if f not in self.file_positions:
                try:
                    self.file_positions[f] = os.path.getsize(f)
                    self.known_files.add(f)
                except Exception:
                    pass
                continue

            # Check if file has grown using fast stat
            try:
                current_size = os.path.getsize(f)
                last_pos = self.file_positions.get(f, 0)
                
                if current_size > last_pos:
                    with open(f, "rb") as fp:
                        fp.seek(last_pos)
                        new_bytes = fp.read(current_size - last_pos)
                        self.file_positions[f] = current_size
                    
                    decoded_text = decode_log_bytes(new_bytes)
                    lines = decoded_text.splitlines()
                    
                    for raw_line in lines:

                        parsed = IntelParser.parse_single_line(raw_line, ch_name)
                        if parsed:
                            self.intel_received.emit(parsed)
                            if parsed["is_critical"]:
                                self.critical_threat_detected.emit(parsed)
                                
                elif current_size < last_pos:
                    # File was truncated/recreated
                    self.file_positions[f] = current_size
            except Exception:
                pass

        self.active_channels_updated.emit(active_names)

    def simulate_intel_line(self, line: str, channel: str = "Delve.Intel"):
        """Directly feeds a simulated chat line for test/dry-run purposes."""
        parsed = IntelParser.parse_single_line(line, channel)
        if parsed:
            self.intel_received.emit(parsed)
            if parsed["is_critical"]:
                self.critical_threat_detected.emit(parsed)
