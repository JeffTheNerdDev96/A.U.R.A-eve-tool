"""
Offline EVE Online stargate graph: name lookup, BFS jump distance, N-jump neighborhoods.
Loads bundled data/eve_map.json (regenerate with tools/build_eve_map.py).

Map source: Fuzzwork SDE dumps (https://www.fuzzwork.co.uk), derived from the
CCP hf Static Data Export. See CREDITS.md.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

_MAP_INSTANCE: Optional["EveMapGraph"] = None


def _default_map_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "eve_map.json")


class EveMapGraph:
    """Undirected stargate graph keyed by solarSystemID."""

    def __init__(self, map_path: Optional[str] = None):
        self.map_path = map_path or _default_map_path()
        self.systems: Dict[int, Dict[str, Any]] = {}
        self.name_to_id: Dict[str, int] = {}
        self.adj: Dict[int, Set[int]] = defaultdict(set)
        self.loaded = False
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.map_path):
            self.loaded = False
            return
        try:
            with open(self.map_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, json.JSONDecodeError):
            self.loaded = False
            return

        systems = raw.get("systems") or {}
        for sid_str, info in systems.items():
            try:
                sid = int(sid_str)
            except (TypeError, ValueError):
                continue
            name = str(info.get("name") or "").strip()
            if not name:
                continue
            rec = {
                "id": sid,
                "name": name,
                "region": str(info.get("region") or ""),
                "security": float(info.get("security") or 0.0),
            }
            self.systems[sid] = rec
            self.name_to_id[name.lower()] = sid

        for a, b in raw.get("jumps") or []:
            try:
                ia, ib = int(a), int(b)
            except (TypeError, ValueError):
                continue
            if ia == ib:
                continue
            self.adj[ia].add(ib)
            self.adj[ib].add(ia)

        self.loaded = bool(self.systems)

    def get_system(self, system_id: int) -> Optional[Dict[str, Any]]:
        return self.systems.get(int(system_id))

    def resolve_system_id(self, system_id: int) -> Optional[Dict[str, Any]]:
        return self.get_system(system_id)

    def resolve_system_name(self, token: str) -> Optional[Dict[str, Any]]:
        """Case-insensitive exact name match. Returns system record or None."""
        if not token:
            return None
        cleaned = token.strip().strip(".,;:!?\"'()[]{}<>`~*|\\/")
        if not cleaned:
            return None
        sid = self.name_to_id.get(cleaned.lower())
        if sid is None:
            return None
        return self.systems.get(sid)

    def neighbors(self, system_id: int) -> Set[int]:
        return set(self.adj.get(int(system_id), set()))

    def jump_distance(self, origin_id: Optional[int], dest_id: Optional[int], max_jumps: int = 50) -> Optional[int]:
        """Stargate hop count. 0 if same system. None if unreachable or unknown."""
        if origin_id is None or dest_id is None:
            return None
        try:
            a, b = int(origin_id), int(dest_id)
        except (TypeError, ValueError):
            return None
        if a not in self.systems or b not in self.systems:
            return None
        if a == b:
            return 0
        dist = self._bfs_to(a, b, max_jumps)
        return dist

    def systems_within(self, origin_id: Optional[int], n: int) -> Dict[int, int]:
        """Map of system_id -> jump distance for all systems within n hops (inclusive)."""
        if origin_id is None or origin_id not in self.systems:
            return {}
        n = max(0, int(n))
        origin = int(origin_id)
        found: Dict[int, int] = {origin: 0}
        if n == 0:
            return found
        q = deque([(origin, 0)])
        while q:
            node, d = q.popleft()
            if d >= n:
                continue
            for nb in self.adj.get(node, ()):
                if nb not in found:
                    found[nb] = d + 1
                    q.append((nb, d + 1))
        return found

    def systems_within_capped(
        self, origin_id: Optional[int], n: int, max_nodes: int = 250
    ) -> Tuple[Dict[int, int], int]:
        """BFS neighborhood capped at max_nodes (closest hops first). Returns (id->distance, total_in_range)."""
        full = self.systems_within(origin_id, n)
        if not full:
            return {}, 0
        total = len(full)
        if total <= max_nodes:
            return full, total
        ordered = sorted(full.items(), key=lambda kv: (kv[1], kv[0]))
        capped = dict(ordered[:max_nodes])
        return capped, total

    def subgraph_edges(self, node_ids: Set[int]) -> List[Tuple[int, int]]:
        """Stargate edges where both endpoints are in node_ids (deduplicated, a < b)."""
        visible = {int(x) for x in node_ids}
        edges: List[Tuple[int, int]] = []
        seen: Set[Tuple[int, int]] = set()
        for a in visible:
            for b in self.adj.get(a, ()):
                if b not in visible or a >= b:
                    continue
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(key)
        return edges

    def _bfs_to(self, origin: int, dest: int, max_jumps: int) -> Optional[int]:
        q = deque([(origin, 0)])
        seen = {origin}
        while q:
            node, d = q.popleft()
            if d >= max_jumps:
                continue
            for nb in self.adj.get(node, ()):
                if nb in seen:
                    continue
                if nb == dest:
                    return d + 1
                seen.add(nb)
                q.append((nb, d + 1))
        return None


def get_eve_map() -> EveMapGraph:
    global _MAP_INSTANCE
    if _MAP_INSTANCE is None:
        _MAP_INSTANCE = EveMapGraph()
    return _MAP_INSTANCE
