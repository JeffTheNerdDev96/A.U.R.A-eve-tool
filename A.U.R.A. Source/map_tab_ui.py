"""
Tactical stargate map tab: neighborhood bubble with intel overlays.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QWheelEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QApplication,
    QSizePolicy,
)

from eve_map import EveMapGraph
from theme import (
    BG_DEEP, BG_PANEL, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    ACCENT, ACCENT_HOVER, BORDER_FOCUS, btn_secondary_css,
)

INTEL_TTL_SEC = 30 * 60
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
    if security >= 0.45:
        return QColor("#3b82f6")
    if security > 0.0:
        return QColor("#d97706")
    return QColor("#dc2626")


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
            self._label.setPos(self.rect().center().x() + r + 2, self.rect().center().y() - 6)


class MapTabWidget(QWidget):
    """Tactical jump-range stargate map with intel overlays."""

    def __init__(self, eve_map: EveMapGraph, parent=None):
        super().__init__(parent)
        self.eve_map = eve_map
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

        rail = QFrame()
        rail.setFixedWidth(240)
        rail.setStyleSheet(f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER}; }}")
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(10, 10, 10, 10)
        hdr = QLabel("SYSTEM")
        hdr.setStyleSheet(f"color:{TEXT_HINT}; font-size:10px; font-weight:bold; letter-spacing:1px;")
        rl.addWidget(hdr)
        self.info_title = QLabel("—")
        self.info_title.setWordWrap(True)
        self.info_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:14px; font-weight:bold;")
        rl.addWidget(self.info_title)
        self.info_body = QLabel("Select a system or wait for location.")
        self.info_body.setWordWrap(True)
        self.info_body.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px;")
        rl.addWidget(self.info_body)
        rl.addStretch()
        leg = QLabel(
            "Legend\n"
            "● Highsec  ● Lowsec  ● Nullsec\n"
            "Ring: intel threat level\n"
            "Gold ring: you are here"
        )
        leg.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        rl.addWidget(leg)
        body.addWidget(rail)
        root.addLayout(body, stretch=1)

        self.caption_lbl = QLabel("")
        self.caption_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        root.addWidget(self.caption_lbl)

        self.placeholder = QLabel(
            "Location unknown — join Local or jump so A.U.R.A. can center the map on you."
        )
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet(f"color:{TEXT_HINT}; font-size:13px; padding:40px;")
        self.placeholder.setParent(self.view.viewport())

    def _btn_css(self) -> str:
        return btn_secondary_css()

    def _show_placeholder(self) -> None:
        self.placeholder.show()
        self.placeholder.raise_()
        self._resize_placeholder()

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
        self._hide_placeholder()
        self._rebuild_graph()

    def set_jump_range(self, n: int) -> None:
        self._jump_range = max(0, int(n))
        self.range_lbl.setText(f"Alert range: {self._jump_range} jumps")
        if self._origin_id is not None:
            self._rebuild_graph()

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
            self._rebuild_graph(full_layout=False)

    def _prune_intel(self) -> None:
        cutoff = time.time() - INTEL_TTL_SEC
        stale = [k for k, v in self._intel_by_system.items() if v.get("ts", 0) < cutoff]
        for k in stale:
            del self._intel_by_system[k]

    def _intel_for_id(self, system_id: int) -> Optional[Dict[str, Any]]:
        rec = self.eve_map.get_system(system_id)
        if not rec:
            return None
        return self._intel_by_system.get(rec["name"].lower())

    def _collect_visible_ids(self) -> Set[int]:
        if self._origin_id is None:
            return set()
        bubble, total = self.eve_map.systems_within_capped(
            self._origin_id, self._jump_range, MAX_NODES
        )
        self._bubble_total = total
        visible = set(bubble.keys())
        self._extra_ids = set()
        for intel in self._intel_by_system.values():
            rec = self.eve_map.resolve_system_name(intel.get("name", ""))
            if rec:
                sid = int(rec["id"])
                if sid not in visible:
                    visible.add(sid)
                    self._extra_ids.add(sid)
        return visible

    def _rebuild_graph(self, full_layout: bool = True) -> None:
        self._prune_intel()
        if self._origin_id is None:
            self._show_placeholder()
            return

        visible = self._collect_visible_ids()
        self._visible_ids = visible
        edges = self.eve_map.subgraph_edges(visible)

        cache_key = (self._origin_id, self._jump_range, frozenset(visible))
        if cache_key != self._layout_cache_key or full_layout:
            self._layout_cache = _force_layout(visible, edges, self._origin_id)
            self._layout_cache_key = cache_key

        positions = self._layout_cache
        self.scene.clear()
        self._node_items.clear()
        self._edge_items.clear()
        self._label_items.clear()

        for a, b in edges:
            pa = positions.get(a)
            pb = positions.get(b)
            if not pa or not pb:
                continue
            line = QGraphicsLineItem(pa[0], pa[1], pb[0], pb[1])
            line.setPen(QPen(QColor("#4b5563"), 1.0))
            line.setZValue(0)
            self.scene.addItem(line)
            self._edge_items.append(line)

        for sid in visible:
            rec = self.eve_map.get_system(sid)
            if not rec:
                continue
            pos = positions.get(sid)
            if not pos:
                continue
            is_current = sid == self._origin_id
            is_extra = sid in self._extra_ids
            intel = self._intel_for_id(sid)
            radius = 7.0 if is_current else 5.5
            node = SystemNodeItem(sid, rec["name"], radius)
            node.setPos(pos[0], pos[1])
            node.setZValue(2 if is_current else 1)

            sec = float(rec.get("security") or 0.0)
            fill = _sec_color(sec)
            ring = None
            ring_w = 2.0
            if intel:
                ring = QColor(_THREAT_RING.get(intel["level"], "#38bdf8"))
                ring_w = 2.5
            opacity = 0.55 if is_extra else 1.0

            lbl = QGraphicsTextItem(rec["name"])
            lbl.setDefaultTextColor(QColor(TEXT_SECONDARY))
            lbl.setFont(QFont("Segoe UI", 8))
            lbl.setZValue(3)
            self.scene.addItem(lbl)
            node.set_label(lbl)

            node.set_visual(fill, ring, ring_w, opacity, is_current)
            self.scene.addItem(node)
            self._node_items[sid] = node

        if self._bubble_total > MAX_NODES:
            self.caption_lbl.setText(
                f"Showing {min(len(self._visible_ids), MAX_NODES)} of {self._bubble_total} systems in range."
            )
        else:
            extra = len(self._extra_ids)
            txt = f"{len(self._visible_ids)} systems in view."
            if extra:
                txt += f" ({extra} intel-only outside bubble)"
            self.caption_lbl.setText(txt)

        self._fit_view()
        if self._selected_id and self._selected_id in self._node_items:
            self._node_items[self._selected_id].setSelected(True)

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
            self.info_body.setText(f"No system named “{token}”.")
            return
        sid = int(rec["id"])
        if sid not in self._node_items:
            if self._origin_id is None:
                self.info_body.setText("Set location first (Local / jump).")
                return
            self._extra_ids.add(sid)
            self._rebuild_graph(full_layout=True)
        node = self._node_items.get(sid)
        if node:
            node.setSelected(True)
            self.view.centerOn(node)
            self._update_info_panel(sid)
