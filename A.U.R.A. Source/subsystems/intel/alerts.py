"""
Jump-range threat filter and Windows toast debounce for Live Intel Radar.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from subsystems.map import EveMapGraph, get_eve_map

_LEVEL_RANK = {
    "CLEAR": -1,
    "INFO": 0,
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}


class ThreatAlerter:
    def __init__(
        self,
        eve_map: Optional[EveMapGraph] = None,
        jump_range: int = 5,
        min_level: str = "MEDIUM",
        debounce_sec: float = 20.0,
    ):
        self.eve_map = eve_map or get_eve_map()
        self.jump_range = int(jump_range)
        self.min_level = min_level.upper()
        self.debounce_sec = debounce_sec
        self.current_system_id: Optional[int] = None
        self.current_system_name: Optional[str] = None
        self._neighborhood: Dict[int, int] = {}
        self._last_toast: Dict[str, float] = {}

    def set_jump_range(self, n: int) -> None:
        self.jump_range = max(0, int(n))
        self._refresh_neighborhood()

    def set_location(self, system_name: Optional[str], system_id: Optional[int]) -> None:
        self.current_system_name = system_name
        self.current_system_id = int(system_id) if system_id is not None else None
        self._refresh_neighborhood()

    def _refresh_neighborhood(self) -> None:
        if self.current_system_id is None:
            self._neighborhood = {}
            return
        self._neighborhood = self.eve_map.systems_within(self.current_system_id, self.jump_range)

    def annotate(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Attach map-resolved system, jump count, and in_range onto an intel event."""
        out = dict(parsed)
        raw_sys = parsed.get("system") or ""
        rec = None
        if raw_sys and raw_sys != "Unknown System":
            rec = self.eve_map.resolve_system_name(raw_sys)
        if rec is None:
            out["system_id"] = None
            out["jumps"] = None
            out["in_range"] = False
            out["location_known"] = self.current_system_id is not None
            return out

        out["system"] = rec["name"]
        out["system_id"] = rec["id"]
        out["location_known"] = self.current_system_id is not None
        if self.current_system_id is None:
            out["jumps"] = None
            out["in_range"] = False
            return out

        if rec["id"] in self._neighborhood:
            jumps = self._neighborhood[rec["id"]]
        else:
            jumps = self.eve_map.jump_distance(self.current_system_id, rec["id"], max_jumps=self.jump_range + 8)
        out["jumps"] = jumps
        out["in_range"] = jumps is not None and jumps <= self.jump_range
        return out

    def should_toast(self, annotated: Dict[str, Any]) -> bool:
        if not annotated.get("in_range"):
            return False
        if annotated.get("jumps") is None:
            return False
        level = str(annotated.get("threat_level") or "INFO").upper()
        if level == "CLEAR" or "SYSTEM CLEAR" in (annotated.get("status_flags") or []):
            return False
        min_rank = _LEVEL_RANK.get(self.min_level, 1)
        if _LEVEL_RANK.get(level, 0) < min_rank:
            return False

        sys_name = annotated.get("system") or ""
        msg = (annotated.get("clean_msg") or "")[:80]
        key = f"{sys_name}|{msg}"
        now = time.time()
        last = self._last_toast.get(key, 0.0)
        if now - last < self.debounce_sec:
            return False
        self._last_toast[key] = now
        if len(self._last_toast) > 200:
            cutoff = now - self.debounce_sec * 4
            self._last_toast = {k: v for k, v in self._last_toast.items() if v >= cutoff}
        return True

    @staticmethod
    def toast_title(annotated: Dict[str, Any]) -> str:
        jumps = annotated.get("jumps")
        if jumps == 0:
            hop = "LOCAL"
        else:
            hop = f"{jumps} jump{'s' if jumps != 1 else ''}"
        return f"A.U.R.A. threat — {hop}"

    @staticmethod
    def toast_body(annotated: Dict[str, Any]) -> str:
        sys_name = annotated.get("system") or "Unknown"
        level = annotated.get("threat_level") or "ALERT"
        ships = ", ".join(annotated.get("ships") or [])
        count = annotated.get("est_count") or 0
        flags = annotated.get("status_flags") or []
        bits = [sys_name, str(level)]
        if ships:
            bits.append(ships)
        elif count:
            bits.append(f"+{count}")
        if flags:
            bits.append(flags[0])
        return " · ".join(bits)
