"""
Parse EVE Local chat headers and Gamelogs to detect the capsuleer's current solar system.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from subsystems.map import EveMapGraph, get_eve_map

_RE_CHANNEL_ID = re.compile(r"Channel ID:\s*(-?\d+)", re.IGNORECASE)
_RE_LOCAL_CHANGED = re.compile(
    r"(?:Channel changed to Local|local changed to)\s*[:\-]?\s*[\"']?([^\n\"']+)",
    re.IGNORECASE,
)
_RE_CONNECTING = re.compile(r"Connecting to\s*[\"']?([^\n\"']+)", re.IGNORECASE)
_RE_JUMPING = re.compile(r"Jumping from\s+(.+?)\s+to\s+(.+)", re.IGNORECASE)
_RE_LISTENER = re.compile(r"(?:Gamelog\s+)?Listener\s*:\s*([^\r\n]+)", re.IGNORECASE)

_SESSION_NOISE = frozenset({
    "tranquility", "singularity", "thunderdome", "serenity",
    "duality", "chaos", "eve", "tq", "character", "server",
})


def _strip_token(raw: str) -> str:
    return (raw or "").strip().strip(".,;:!?\"'()[]{}<>`~*|\\/")


class LocationTracker:
    """Resolves location events into (system_name, system_id)."""

    def __init__(self, eve_map: Optional[EveMapGraph] = None):
        self.eve_map = eve_map or get_eve_map()
        self.current_name: Optional[str] = None
        self.current_id: Optional[int] = None

    @property
    def current(self) -> Tuple[Optional[str], Optional[int]]:
        return self.current_name, self.current_id

    def apply(self, name: Optional[str], system_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Commit a resolved location. Returns payload if it changed."""
        rec = None
        if system_id is not None:
            rec = self.eve_map.resolve_system_id(int(system_id))
        if rec is None and name:
            rec = self.eve_map.resolve_system_name(name)
        if rec is None:
            return None
        sid = int(rec["id"])
        sname = rec["name"]
        if sid == self.current_id and sname == self.current_name:
            return None
        self.current_id = sid
        self.current_name = sname
        return {"system": sname, "system_id": sid, "region": rec.get("region", ""), "security": rec.get("security", 0.0)}

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single chat or gamelog line for a location change."""
        if not line:
            return None
        clean = line.strip()
        if not clean:
            return None

        m_id = _RE_CHANNEL_ID.search(clean)
        if m_id:
            try:
                sid = int(m_id.group(1))
            except ValueError:
                sid = None
            if sid and sid > 30000000:
                return self.apply(None, sid)

        m_jump = _RE_JUMPING.search(clean)
        if m_jump:
            dest = _strip_token(m_jump.group(2))
            return self.apply(dest, None)

        m_local = _RE_LOCAL_CHANGED.search(clean)
        if m_local:
            dest = _strip_token(m_local.group(1))
            dest = re.sub(r"^Local\s*[:\-]\s*", "", dest, flags=re.IGNORECASE).strip()
            return self.apply(dest, None)

        m_conn = _RE_CONNECTING.search(clean)
        if m_conn:
            dest = _strip_token(m_conn.group(1))
            if dest.lower() in _SESSION_NOISE:
                return None
            return self.apply(dest, None)

        return None

    def parse_header_blob(self, text: str) -> Optional[Dict[str, Any]]:
        """Scan the start of a Local log file for Channel ID (solarSystemID)."""
        if not text:
            return None
        for line in text.splitlines()[:40]:
            hit = self.parse_line(line)
            if hit:
                return hit
        return None

    @staticmethod
    def extract_listener(text: str) -> Optional[str]:
        """Extract pilot / character name from a chatlog or gamelog header."""
        if not text:
            return None
        for line in text.splitlines()[:30]:
            m = _RE_LISTENER.search(line)
            if m:
                pilot = _strip_token(m.group(1))
                if pilot and pilot.lower() not in _SESSION_NOISE:
                    return pilot
        return None
