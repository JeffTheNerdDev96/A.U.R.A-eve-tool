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
Map Router Engine.
Provides sub-millisecond BFS graph routing across EVE Online stargate network.
"""

from collections import deque
from typing import List, Optional, Set
from .eve_map import get_eve_map, EveMapGraph
from .models import SystemNode, RouteResult


class MapRouter:
    """BFS graph router with system avoidance and security analysis."""

    def __init__(self, map_graph: Optional[EveMapGraph] = None):
        self.map_graph = map_graph or get_eve_map()

    def get_system(self, name_or_id: str) -> Optional[SystemNode]:
        """Resolves system by name or integer ID."""
        rec = None
        if name_or_id.isdigit():
            rec = self.map_graph.get_system(int(name_or_id))
        else:
            rec = self.map_graph.resolve_system_name(name_or_id)

        if not rec:
            return None
        return SystemNode(
            system_id=rec["id"],
            name=rec["name"],
            region=rec["region"],
            security=rec["security"]
        )

    def calculate_route(self, origin: str, destination: str, avoid_systems: Optional[List[str]] = None) -> Optional[RouteResult]:
        """
        Calculates shortest stargate route between origin and destination.
        Returns RouteResult DTO or None if unreachable.
        """
        orig_node = self.get_system(origin)
        dest_node = self.get_system(destination)

        if not orig_node or not dest_node:
            return None

        avoid_ids: Set[int] = set()
        if avoid_systems:
            for sys_name in avoid_systems:
                node = self.get_system(sys_name)
                if node and node.system_id not in (orig_node.system_id, dest_node.system_id):
                    avoid_ids.add(node.system_id)

        # BFS for shortest path
        q = deque([[orig_node.system_id]])
        visited = {orig_node.system_id}

        found_path_ids: Optional[List[int]] = None
        while q:
            path = q.popleft()
            curr = path[-1]
            if curr == dest_node.system_id:
                found_path_ids = path
                break

            for neighbor in self.map_graph.neighbors(curr):
                if neighbor not in visited and neighbor not in avoid_ids:
                    visited.add(neighbor)
                    q.append(path + [neighbor])

        if not found_path_ids:
            return None

        # Build route result
        path_names: List[str] = []
        securities: List[float] = []
        for sid in found_path_ids:
            rec = self.map_graph.get_system(sid)
            if rec:
                path_names.append(rec["name"])
                securities.append(rec["security"])

        min_sec = min(securities) if securities else 0.0
        avg_sec = sum(securities) / len(securities) if securities else 0.0

        return RouteResult(
            origin=orig_node.name,
            destination=dest_node.name,
            path=path_names,
            total_jumps=len(path_names) - 1,
            security_min=min_sec,
            security_avg=avg_sec,
            avoided_systems=avoid_systems or []
        )

    find_route = calculate_route

