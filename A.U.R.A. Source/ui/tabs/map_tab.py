"""
Tactical stargate map tab: neighborhood bubble with intel overlays.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QWheelEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QScrollArea,
    QSizePolicy,
)

from subsystems.map import EveMapGraph, MapSubsystem
from subsystems.map.models import RouteResult
from core.input_safety import safe_display_text
from ui.theme import (
    BG_DEEP, BG_PANEL, BG_ELEVATED, BORDER, BORDER_MUTED, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    TEXT_BRAND, ACCENT, ACCENT_HOVER, BORDER_FOCUS, STATUS_ONLINE,
    btn_secondary_css, radar_accent_btn_css,
)

INTEL_TTL_SEC = 10 * 60
MAX_NODES = 250

_LEVEL_RANK = {
    "CLEAR": -1,
    "INFO": 0,
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}

_THREAT_RING = {
    "CRITICAL": "#f43f5e",
    "HIGH": "#fb923c",
    "MEDIUM": "#facc15",
    "INFO": "#38bdf8",
    "LOW": "#38bdf8",
    "CLEAR": "#34d399",
}


def _sec_color(security: float) -> QColor:
    """High-contrast security status color palette for dark tactical backgrounds."""
    if security >= 0.45:
        return QColor("#38bdf8")  # High-sec: crisp electric cyan
    if security > 0.0:
        return QColor("#fbbf24")  # Low-sec: crisp warm amber
    return QColor("#f87171")      # Null-sec: vibrant coral red


def _force_layout(
    node_ids: Set[int],
    edges: List[Tuple[int, int]],
    origin_id: Optional[int],
    iterations: int = 80,
) -> Dict[int, Tuple[float, float]]:
    """Fruchterman-Reingold layout; origin pinned at (0, 0)."""
    if not node_ids:
        return {}
    ids = list(node_ids)
    n = len(ids)
    area = max(40000.0, n * 800.0)
    k = math.sqrt(area / max(n, 1))
    pos: Dict[int, Tuple[float, float]] = {}
    for i, sid in enumerate(ids):
        if sid == origin_id:
            pos[sid] = (0.0, 0.0)
        else:
            angle = (2 * math.pi * i) / max(n, 1)
            r = k * 2.5
            pos[sid] = (math.cos(angle) * r, math.sin(angle) * r)

    adj: Dict[int, Set[int]] = {sid: set() for sid in ids}
    for a, b in edges:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)

    def disp(sid: int) -> Tuple[float, float]:
        return pos[sid]

    def set_disp(sid: int, x: float, y: float) -> None:
        if sid == origin_id:
            pos[sid] = (0.0, 0.0)
        else:
            pos[sid] = (x, y)

    for _ in range(iterations):
        disp_vec = {sid: [0.0, 0.0] for sid in ids}
        for v in ids:
            for u in ids:
                if u == v:
                    continue
                dx = disp(v)[0] - disp(u)[0]
                dy = disp(v)[1] - disp(u)[1]
                dist = math.hypot(dx, dy)
                if dist < 0.01:
                    dist = 0.01
                    dx, dy = 0.01, 0.0
                repulse = (k * k) / dist
                disp_vec[v][0] += (dx / dist) * repulse
                disp_vec[v][1] += (dy / dist) * repulse

        for a, b in edges:
            if a not in pos or b not in pos:
                continue
            dx = disp(b)[0] - disp(a)[0]
            dy = disp(b)[1] - disp(a)[1]
            dist = math.hypot(dx, dy)
            if dist < 0.01:
                dist = 0.01
            attract = (dist * dist) / k
            fx = (dx / dist) * attract
            fy = (dy / dist) * attract
            disp_vec[a][0] += fx
            disp_vec[a][1] += fy
            disp_vec[b][0] -= fx
            disp_vec[b][1] -= fy

        for v in ids:
            if v == origin_id:
                continue
            dlen = math.hypot(disp_vec[v][0], disp_vec[v][1])
            if dlen > 0:
                limit = min(dlen, 20.0)
                disp_vec[v][0] = disp_vec[v][0] / dlen * limit
                disp_vec[v][1] = disp_vec[v][1] / dlen * limit
            set_disp(v, disp(v)[0] + disp_vec[v][0], disp(v)[1] + disp_vec[v][1])

    return pos


class MapGraphicsView(QGraphicsView):
    """Pan/zoom view for the stargate graph."""

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        from PyQt6.QtGui import QPainter
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor(BG_DEEP)))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._zoom = 1.0

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta == 0:
            return
        factor = 1.15 if delta > 0 else 1 / 1.15
        self._zoom = max(0.2, min(4.0, self._zoom * factor))
        self.setTransform(self.transform().scale(factor, factor))


class SystemNodeItem(QGraphicsEllipseItem):
    """Clickable system node."""

    def __init__(self, system_id: int, name: str, radius: float, parent=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2, parent)
        self.system_id = system_id
        self.system_name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self._base_radius = radius
        self._label: Optional[QGraphicsTextItem] = None

    def set_label(self, text_item: QGraphicsTextItem) -> None:
        self._label = text_item

    def set_visual(
        self,
        fill: QColor,
        ring: Optional[QColor] = None,
        ring_width: float = 2.0,
        opacity: float = 1.0,
        is_current: bool = False,
    ) -> None:
        r = self._base_radius * (1.35 if is_current else 1.0)
        self.setRect(-r, -r, r * 2, r * 2)
        self.setBrush(QBrush(fill))
        if ring:
            pen = QPen(ring, ring_width)
        elif is_current:
            pen = QPen(QColor(ACCENT), 3.0)
        else:
            pen = QPen(QColor("#4b5563"), 1.0)
        self.setPen(pen)
        self.setOpacity(opacity)
        if self._label:
            r = self.rect().width() / 2.0
            self._label.setPos(r + 2, -6)


class MapTabWidget(QWidget):
    """Tactical jump-range stargate map with intel overlays and BFS Route Planner."""

    def __init__(self, eve_map: Optional[EveMapGraph] = None, parent=None):
        super().__init__(parent)
        from subsystems.map import get_eve_map
        self.eve_map = eve_map or get_eve_map()
        self.map_subsystem = MapSubsystem()
        self._origin_id: Optional[int] = None
        self._origin_name: Optional[str] = None
        self._jump_range = 5
        self._intel_by_system: Dict[str, Dict[str, Any]] = {}
        self._layout_cache_key: Optional[Tuple[Any, ...]] = None
        self._layout_cache: Dict[int, Tuple[float, float]] = {}
        self._node_items: Dict[int, SystemNodeItem] = {}
        self._edge_items: List[QGraphicsLineItem] = []
        self._label_items: List[QGraphicsTextItem] = []
        self._visible_ids: Set[int] = set()
        self._bubble_total = 0
        self._selected_id: Optional[int] = None
        self._extra_ids: Set[int] = set()

        # BFS Route Planning state
        self._current_route: Optional[RouteResult] = None
        self._route_node_ids: List[int] = []
        self._route_edges: Set[Tuple[int, int]] = set()

        self._prune_timer = QTimer(self)
        self._prune_timer.setInterval(15000)  # Prune expired 10-min intel every 15s
        self._prune_timer.timeout.connect(self._on_prune_timer)
        self._prune_timer.start()

        self.setStyleSheet(f"MapTabWidget {{ background:{BG_DEEP}; color:{TEXT_PRIMARY}; }}")
        self._init_ui()
        self._show_placeholder()

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        top = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search system name…")
        self.search_edit.returnPressed.connect(self._on_search)
        top.addWidget(self.search_edit, stretch=1)
        search_btn = QPushButton("Go")
        search_btn.setStyleSheet(self._btn_css())
        search_btn.clicked.connect(self._on_search)
        top.addWidget(search_btn)
        fit_btn = QPushButton("Fit view")
        fit_btn.setStyleSheet(self._btn_css())
        fit_btn.clicked.connect(self._fit_view)
        top.addWidget(fit_btn)
        self.range_lbl = QLabel("Alert range: 5 jumps")
        self.range_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:12px;")
        top.addWidget(self.range_lbl)
        root.addLayout(top)

        body = QHBoxLayout()
        self.scene = QGraphicsScene(self)
        self.view = MapGraphicsView(self.scene)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scene.selectionChanged.connect(self._on_selection_changed)
        body.addWidget(self.view, stretch=1)

        # Tactical Right Rail / Control Panel
        rail = QFrame()
        rail.setFixedWidth(280)
        rail.setStyleSheet(f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER}; }}")
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(10, 10, 10, 10)
        rl.setSpacing(8)

        # 1. System Info Section
        hdr = QLabel("SYSTEM INTEL")
        hdr.setStyleSheet(f"color:{TEXT_HINT}; font-size:10px; font-weight:bold; letter-spacing:1px;")
        rl.addWidget(hdr)
        self.info_title = QLabel("—")
        self.info_title.setWordWrap(True)
        self.info_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:14px; font-weight:bold;")
        rl.addWidget(self.info_title)
        self.info_body = QLabel("Select a system or wait for location.")
        self.info_body.setTextFormat(Qt.TextFormat.PlainText)
        self.info_body.setWordWrap(True)
        self.info_body.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px;")
        rl.addWidget(self.info_body)

        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.Shape.HLine)
        div1.setStyleSheet(f"color: {BORDER}; background-color: {BORDER}; max-height: 1px;")
        rl.addWidget(div1)

        # 2. BFS Tactical Route Planner Section
        route_hdr = QLabel("TACTICAL ROUTE PLANNER (BFS)")
        route_hdr.setStyleSheet(f"color:{TEXT_BRAND}; font-size:10.5px; font-weight:bold; letter-spacing:1px;")
        rl.addWidget(route_hdr)

        self.route_origin_edit = QLineEdit()
        self.route_origin_edit.setFixedHeight(26)
        self.route_origin_edit.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.route_origin_edit.setPlaceholderText("Origin (e.g. Jita)")
        rl.addWidget(self.route_origin_edit)

        self.route_dest_edit = QLineEdit()
        self.route_dest_edit.setFixedHeight(26)
        self.route_dest_edit.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.route_dest_edit.setPlaceholderText("Destination (e.g. Amarr)")
        self.route_dest_edit.returnPressed.connect(self._on_calculate_route)
        rl.addWidget(self.route_dest_edit)

        self.route_avoid_edit = QLineEdit()
        self.route_avoid_edit.setFixedHeight(26)
        self.route_avoid_edit.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.route_avoid_edit.setPlaceholderText("Avoid (e.g. Tama, Rancer)")
        self.route_avoid_edit.returnPressed.connect(self._on_calculate_route)
        rl.addWidget(self.route_avoid_edit)

        route_btn_row = QHBoxLayout()
        self.route_calc_btn = QPushButton("⚡ Plot Route")
        self.route_calc_btn.setFixedHeight(28)
        self.route_calc_btn.setStyleSheet(radar_accent_btn_css())
        self.route_calc_btn.clicked.connect(self._on_calculate_route)
        route_btn_row.addWidget(self.route_calc_btn, stretch=2)

        self.route_clear_btn = QPushButton("Clear")
        self.route_clear_btn.setFixedHeight(28)
        self.route_clear_btn.setStyleSheet(self._btn_css())
        self.route_clear_btn.clicked.connect(self._on_clear_route)
        route_btn_row.addWidget(self.route_clear_btn, stretch=1)
        rl.addLayout(route_btn_row)

        self.route_summary_lbl = QLabel("")
        self.route_summary_lbl.setWordWrap(True)
        self.route_summary_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11.5px;")
        rl.addWidget(self.route_summary_lbl)

        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet(f"color: {BORDER}; background-color: {BORDER}; max-height: 1px;")
        rl.addWidget(div2)

        rl.addStretch()

        # Legend
        leg = QLabel(
            "Map Legend\n"
            "● Highsec  ● Lowsec  ● Nullsec\n"
            "Ring: intel threat level\n"
            "Gold ring: origin / current location\n"
            "Cyan ring: destination\n"
            "Gold path: plotted stargate route"
        )
        leg.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        rl.addWidget(leg)
        body.addWidget(rail)
        root.addLayout(body, stretch=1)

        self.caption_lbl = QLabel("")
        self.caption_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        root.addWidget(self.caption_lbl)

        self.placeholder = QLabel(
            "Location unknown — join Local or jump so A.U.R.A. can center the map on you.\nOr plot a route using the Route Planner."
        )
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet(f"color:{TEXT_HINT}; font-size:13px; padding:40px;")
        self.placeholder.setParent(self.view.viewport())

    def _btn_css(self) -> str:
        return btn_secondary_css()

    def _show_placeholder(self) -> None:
        if self._origin_id is None and not self._route_node_ids:
            self.placeholder.show()
            self.placeholder.raise_()
            self._resize_placeholder()
        else:
            self._hide_placeholder()

    def _hide_placeholder(self) -> None:
        self.placeholder.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_placeholder()

    def _resize_placeholder(self) -> None:
        if self.placeholder.isVisible():
            self.placeholder.setGeometry(self.view.viewport().rect())

    def set_location(self, system_name: str, system_id: int) -> None:
        self._origin_id = int(system_id)
        self._origin_name = system_name
        if not self.route_origin_edit.text().strip():
            self.route_origin_edit.setText(system_name)
        self._hide_placeholder()
        self._rebuild_graph(fit_view=True)

    def set_jump_range(self, n: int) -> None:
        self._jump_range = max(0, int(n))
        self.range_lbl.setText(f"Alert range: {self._jump_range} jumps")
        if self._origin_id is not None:
            self._rebuild_graph(fit_view=True)

    def note_intel(self, parsed: dict) -> None:
        sys_name = (parsed.get("system") or "").strip()
        if not sys_name:
            return
        level = (parsed.get("threat_level") or "INFO").upper()
        msg = (parsed.get("clean_msg") or "").strip()
        ts = time.time()
        key = sys_name.lower()
        prev = self._intel_by_system.get(key)
        if prev and _LEVEL_RANK.get(level, 0) < _LEVEL_RANK.get(prev.get("level", "INFO"), 0):
            if ts - prev.get("ts", 0) < 120:
                return
        self._intel_by_system[key] = {"level": level, "msg": msg, "ts": ts, "name": sys_name}
        self._prune_intel()
        if self._origin_id is not None:
            self._rebuild_graph(full_layout=False, fit_view=False)

    def _prune_intel(self) -> None:
        cutoff = time.time() - INTEL_TTL_SEC
        stale = [k for k, v in self._intel_by_system.items() if v.get("ts", 0) < cutoff]
        for k in stale:
            del self._intel_by_system[k]

    def _on_prune_timer(self) -> None:
        if not self._intel_by_system:
            return
        prev_count = len(self._intel_by_system)
        self._prune_intel()
        if len(self._intel_by_system) != prev_count and self._origin_id is not None:
            self._rebuild_graph(full_layout=False, fit_view=False)

    def _intel_for_id(self, system_id: int) -> Optional[Dict[str, Any]]:
        rec = self.eve_map.get_system(system_id)
        if not rec:
            return None
        return self._intel_by_system.get(rec["name"].lower())

    def _collect_visible_ids(self) -> Set[int]:
        if self._origin_id is None and not self._route_node_ids:
            return set()
        res: Set[int] = set()
        if self._origin_id is not None:
            bubble, total = self.eve_map.systems_within_capped(
                self._origin_id, self._jump_range, MAX_NODES
            )
            self._bubble_total = total
            res.update(bubble.keys())
        res.update(self._extra_ids)
        res.update(self._route_node_ids)
        return res

    def _rebuild_graph(self, full_layout: bool = True, fit_view: bool = True) -> None:
        self._prune_intel()
        if self._origin_id is None and not self._route_node_ids:
            self._show_placeholder()
            return

        self._hide_placeholder()
        visible = self._collect_visible_ids()
        self._visible_ids = visible
        edges = self.eve_map.subgraph_edges(visible)

        # Include route edges explicitly in subgraph
        for r_edge in self._route_edges:
            edges.append(r_edge)

        anchor_id = self._origin_id if self._origin_id in visible else (self._route_node_ids[0] if self._route_node_ids else None)
        cache_key = (anchor_id, self._jump_range, frozenset(visible), frozenset(self._route_edges))
        if cache_key != self._layout_cache_key or full_layout:
            self._layout_cache = _force_layout(visible, edges, anchor_id)
            self._layout_cache_key = cache_key

        positions = self._layout_cache
        saved_transform = self.view.transform()
        if not fit_view:
            center_scene = self.view.mapToScene(self.view.viewport().rect().center())

        self.scene.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._label_items.clear()

        # Render edges with route path highlighting
        for a, b in edges:
            pa = positions.get(a)
            pb = positions.get(b)
            if not pa or not pb:
                continue
            line = QGraphicsLineItem(pa[0], pa[1], pb[0], pb[1])
            edge_key = (min(a, b), max(a, b))
            if edge_key in self._route_edges:
                line.setPen(QPen(QColor("#facc15"), 3.2))  # Glowing Gold route line
                line.setZValue(5)
            else:
                line.setPen(QPen(QColor("#475569"), 1.2))
                line.setZValue(0)
            self.scene.addItem(line)
            self._edge_items.append(line)

        # Render system nodes
        for sid in visible:
            rec = self.eve_map.get_system(sid)
            if not rec:
                continue
            pos = positions.get(sid)
            if not pos:
                continue
            is_current = (sid == self._origin_id)
            is_route_origin = bool(self._route_node_ids and sid == self._route_node_ids[0])
            is_route_dest = bool(self._route_node_ids and sid == self._route_node_ids[-1])
            is_route_waypoint = bool(sid in self._route_node_ids and not is_route_origin and not is_route_dest)

            intel = self._intel_for_id(sid)
            if is_current or is_route_origin or is_route_dest:
                radius = 7.5
                z_val = 6
            elif is_route_waypoint:
                radius = 6.2
                z_val = 4
            else:
                radius = 5.5
                z_val = 1

            node = SystemNodeItem(sid, rec["name"], radius)
            node.setPos(pos[0], pos[1])
            node.setZValue(z_val)

            sec = float(rec.get("security") or 0.0)
            fill = _sec_color(sec)
            ring = None
            ring_w = 2.0
            has_threat = False

            if is_route_origin:
                ring = QColor("#facc15")  # Gold origin ring
                ring_w = 3.5
            elif is_route_dest:
                ring = QColor("#38bdf8")  # Electric cyan destination ring
                ring_w = 3.5
            elif is_route_waypoint:
                ring = QColor("#fb923c")  # Orange transit waypoint
                ring_w = 2.4
            elif intel:
                level = intel.get("level", "INFO")
                ring = QColor(_THREAT_RING.get(level, "#38bdf8"))
                ring_w = 2.8
                has_threat = (level != "CLEAR")

            lbl = QGraphicsTextItem(rec["name"], node)
            if is_current or is_route_origin or is_route_dest:
                lbl.setDefaultTextColor(QColor("#ffffff"))
                lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            elif is_route_waypoint:
                lbl.setDefaultTextColor(QColor("#facc15"))
                lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            elif has_threat and intel:
                threat_col = _THREAT_RING.get(intel["level"], "#facc15")
                lbl.setDefaultTextColor(QColor(threat_col))
                lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            else:
                lbl.setDefaultTextColor(_sec_color(sec))
                lbl.setFont(QFont("Segoe UI", 8))
            lbl.setZValue(z_val + 1)
            node.set_label(lbl)
            self._label_items.append(lbl)

            node.set_visual(fill, ring, ring_w, 1.0, is_current or is_route_origin)
            self.scene.addItem(node)
            self._node_items[sid] = node

        if self._current_route:
            self.caption_lbl.setText(
                f"⚡ BFS Route: {self._current_route.origin} ➔ {self._current_route.destination} ({self._current_route.total_jumps} jumps) | Security: Min {self._current_route.security_min:.1f}, Avg {self._current_route.security_avg:.1f}"
            )
        elif self._bubble_total > MAX_NODES:
            self.caption_lbl.setText(
                f"Showing {min(len(self._visible_ids), MAX_NODES)} of {self._bubble_total} systems within {self._jump_range} jumps."
            )
        else:
            self.caption_lbl.setText(f"{len(self._visible_ids)} systems within {self._jump_range} jumps.")

        if fit_view:
            self._fit_view()
        else:
            self.view.setTransform(saved_transform)
            self.view.centerOn(center_scene)

        if self._selected_id and self._selected_id in self._node_items:
            self._node_items[self._selected_id].setSelected(True)

    def _on_calculate_route(self) -> None:
        """Executes sub-millisecond BFS graph routing between origin and destination."""
        orig_str = self.route_origin_edit.text().strip() or (self._origin_name or "")
        dest_str = self.route_dest_edit.text().strip()
        avoid_raw = self.route_avoid_edit.text().strip()

        if not orig_str or not dest_str:
            self.route_summary_lbl.setText("<span style='color:#f87171;'>Please enter both Origin and Destination.</span>")
            return

        avoid_list = [s.strip() for s in avoid_raw.split(",") if s.strip()] if avoid_raw else None

        route = self.map_subsystem.find_route(orig_str, dest_str, avoid_systems=avoid_list)
        if not route:
            self.route_summary_lbl.setText(f"<span style='color:#f87171;'>No route found between '{orig_str}' and '{dest_str}'.</span>")
            return

        self._current_route = route

        # Map route system names to system IDs
        node_ids: List[int] = []
        for name in route.path:
            rec = self.eve_map.resolve_system_name(name)
            if rec:
                node_ids.append(int(rec["id"]))

        self._route_node_ids = node_ids
        self._route_edges = {
            (min(node_ids[i], node_ids[i + 1]), max(node_ids[i], node_ids[i + 1]))
            for i in range(len(node_ids) - 1)
        }

        # Format route summary HTML
        sec_color = "#38bdf8" if route.security_min >= 0.45 else ("#fbbf24" if route.security_min > 0.0 else "#f87171")
        avoid_html = f"<br><b>Avoided:</b> {', '.join(route.avoided_systems)}" if route.avoided_systems else ""
        path_str = " ➔ ".join(route.path)

        self.route_summary_lbl.setText(
            f"<b>Jumps:</b> <span style='color:#facc15; font-weight:bold;'>{route.total_jumps}</span> | "
            f"<b>Min Sec:</b> <span style='color:{sec_color};'>{route.security_min:.1f}</span> | "
            f"<b>Avg:</b> {route.security_avg:.1f}{avoid_html}<br>"
            f"<span style='font-size:11px; color:#cbd5e1;'><b>Path:</b> {safe_display_text(path_str, 200)}</span>"
        )

        self._rebuild_graph(full_layout=True, fit_view=True)

    def _on_clear_route(self) -> None:
        """Clears active route highlights and resets map view."""
        self._current_route = None
        self._route_node_ids = []
        self._route_edges = set()
        self._extra_ids = set()
        self.route_summary_lbl.setText("")
        self._rebuild_graph(full_layout=True, fit_view=True)

    def _fit_view(self) -> None:
        rect = self.scene.itemsBoundingRect()
        if rect.isNull() or rect.width() < 1:
            return
        margin = 40
        self.view.fitInView(
            rect.adjusted(-margin, -margin, margin, margin),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def _on_selection_changed(self) -> None:
        selected = self.scene.selectedItems()
        if not selected:
            return
        for item in selected:
            if isinstance(item, SystemNodeItem):
                self._selected_id = item.system_id
                self._update_info_panel(item.system_id)
                break

    def _update_info_panel(self, system_id: int) -> None:
        rec = self.eve_map.get_system(system_id)
        if not rec:
            return
        name = rec["name"]
        sec = float(rec.get("security") or 0.0)
        region = rec.get("region") or "Unknown"
        jumps = None
        if self._origin_id is not None:
            jumps = self.eve_map.jump_distance(self._origin_id, system_id, max_jumps=50)
        hop = "—"
        if jumps is not None:
            hop = "LOCAL" if jumps == 0 else f"{jumps} jumps"
        self.info_title.setText(name)
        lines = [
            f"Region: {region}",
            f"Security: {sec:.1f}",
            f"Distance: {hop}",
        ]
        intel = self._intel_for_id(system_id)
        if intel:
            lines.append(f"Intel ({intel['level']}): {intel.get('msg', '')[:120]}")
        self.info_body.setText("\n".join(lines))

    def _on_search(self) -> None:
        token = self.search_edit.text().strip()
        if not token:
            return
        rec = self.eve_map.resolve_system_name(token)
        if not rec:
            self.info_body.setText(f'No system named "{safe_display_text(token, 128)}".')
            return
        sid = int(rec["id"])
        if sid not in self._node_items:
            if self._origin_id is None:
                self.info_body.setText("Set location first (Local / jump).")
                return
            self._extra_ids.add(sid)
            self._rebuild_graph(full_layout=True, fit_view=True)
        node = self._node_items.get(sid)
        if node:
            node.setSelected(True)
            self.view.centerOn(node)
            self._update_info_panel(sid)
