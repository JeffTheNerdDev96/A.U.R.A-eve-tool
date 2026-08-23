"""
In-game-style fitting window: slot paperdoll, HP / CPU / powergrid bars, per-module load.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QTextEdit, QFrame, QGridLayout,
    QMessageBox, QFileDialog, QSplitter, QScrollArea, QSizePolicy, QProgressBar,
    QApplication, QDialog, QDialogButtonBox,
)

from core.eve_data import SHIP_DATABASE, MODULE_DATABASE, lookup_ship, lookup_module
from subsystems.fitting.parser import FittingParser
from core.error_handler import AURAErrorCode, log_diagnostic_error
from subsystems.fitting.stats import compute_fit, module_load
from ui.theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_HEADER,
    BG_PANEL, BG_DEEP, BG_ELEVATED, BORDER, BORDER_MUTED, ACCENT, ACCENT_DIM, BORDER_FOCUS,
    BURNT_IRON_LIGHT, BTN_TEXT_ON_ACCENT,
    btn_secondary_css, radar_accent_btn_css,
)

COMBAT_ROLES = [
    "Solo PvP Roaming (Lowsec / FW / Null)",
    "Small Gang Brawling (Close Range Web & Scram)",
    "Nano Kiting / Skirmish (High Speed & Point)",
    "Abyssal Deadspace (Tier 3-5 Exotic / Electrical / Dark / Gamma / Firestorm)",
    "Fleet Anchor DPS / Heavy Line Combat",
    "Nullsec Combat Site Ratting & Escalations",
    "Wormhole C1-C3 Solo Combat & Exploration",
    "Heavy Interception & Fast Tackle Role",
]

SLOT_ACCENT = {
    "high": ACCENT,
    "mid": "#8a7a68",
    "low": "#c4b8a8",
    "rig": "#7cb87c",
    "sub": "#b08cd4",
}

_RE_EFT_HEADER = re.compile(r"^\[.+,.+\]")

SILHOUETTE_MIN_CENTER_W = 480
SILHOUETTE_SHOWN_MIN_W = 140
SILHOUETTE_SHOWN_MAX_W = 220


def _looks_like_eft(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    first = text.split("\n", 1)[0].strip()
    if _RE_EFT_HEADER.match(first):
        return True
    hull_part = first.replace("[", "").split(",")[0].strip()
    return lookup_ship(hull_part) is not None


class PasteEftDialog(QDialog):
    """Paste EFT block from clipboard or manual entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paste EFT Fit")
        self.setMinimumSize(480, 360)
        lay = QVBoxLayout(self)
        hint = QLabel("Paste an EFT / in-game fitting block below, then click Load.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{TEXT_SECONDARY};")
        lay.addWidget(hint)
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("[Hull Name, Fit Name]\nModule…")
        clip = QApplication.clipboard().text().strip()
        if clip:
            self.editor.setPlainText(clip)
        lay.addWidget(self.editor, stretch=1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Load")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def text(self) -> str:
        return self.editor.toPlainText()


class ResourceBar(QWidget):
    """CPU / PG / calibration bar in the EVE fitting attribute style."""

    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 2)
        lay.setSpacing(2)
        top = QHBoxLayout()
        self.title = QLabel(title)
        self.title.setStyleSheet(f"color:{TEXT_HEADER}; font-size: 11px; font-weight: bold;")
        self.value = QLabel("0 / 0")
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size: 11px; font-family: Consolas, monospace;"
        )
        top.addWidget(self.title)
        top.addWidget(self.value, stretch=1)
        lay.addLayout(top)
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self._color = color
        self.bar.setStyleSheet(self._sheet(color))
        lay.addWidget(self.bar)

    def _sheet(self, color: str) -> str:
        return (
            "QProgressBar { background:#1a1c1e; border:1px solid #3a3f44; border-radius:1px; }"
            f"QProgressBar::chunk {{ background:{color}; }}"
        )

    def set_values(self, used: float, output: float, ok: bool):
        output = max(output, 0.01)
        pct = int(min(100, max(0, (used / output) * 100)))
        self.bar.setValue(pct)
        overflow = used > output + 0.05
        color = "#c23b3b" if overflow else (self._color if ok else "#c9a227")
        self.bar.setStyleSheet(self._sheet(color))
        unit = ""
        if "CPU" in self.title.text():
            unit = " tf"
        elif "Power" in self.title.text():
            unit = " MW"
        self.value.setText(f"{used:.0f} / {output:.0f}{unit}")
        self.value.setStyleSheet(
            f"color: {'#f07178' if overflow else TEXT_PRIMARY}; "
            f"font-size: 11px; font-family: Consolas, monospace; font-weight: bold;"
        )


class HpBar(QWidget):
    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        name = QLabel(title)
        name.setFixedWidth(56)
        name.setStyleSheet(f"color:{TEXT_HEADER}; font-size: 11px;")
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(12)
        self.bar.setStyleSheet(
            "QProgressBar { background:#141618; border:1px solid #3a3f44; border-radius:1px; }"
            f"QProgressBar::chunk {{ background:{color}; }}"
        )
        self.value = QLabel("0")
        self.value.setFixedWidth(72)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size: 11px; font-family: Consolas, monospace;"
        )
        lay.addWidget(name)
        lay.addWidget(self.bar, stretch=1)
        lay.addWidget(self.value)

    def set_hp(self, hp: float):
        self.bar.setValue(100)
        self.value.setText(f"{hp:,.0f}")


class SlotButton(QPushButton):
    """Square in-game-style module cell."""

    def __init__(self, kind: str, index: int, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.index = index
        self.module_name: Optional[str] = None
        self.setFixedSize(54, 54)
        self.set_empty()

    def set_empty(self):
        self.module_name = None
        accent = SLOT_ACCENT.get(self.kind, "#6b7280")
        self.setText("")
        self.setToolTip(f"Empty {self.kind} slot — select a module and click")
        self.setStyleSheet(
            f"QPushButton {{ background:#2a2e32; border:1px solid #4b5563; border-bottom:3px solid {accent}; "
            f"border-radius:2px; }}"
            f"QPushButton:hover {{ background:#3a4046; border:2px solid {accent}; }}"
        )

    def set_module(self, name: str):
        self.module_name = name
        load = module_load(name)
        accent = SLOT_ACCENT.get(self.kind, "#9ca3af")
        short = name if len(name) <= 11 else name[:10] + "…"
        self.setText(short)
        self.setToolTip(
            f"{name}\nCPU {load['cpu']:.0f} tf   PG {load['powergrid']:.0f} MW"
            + (f"   Cal {load['calibration']:.0f}" if load["calibration"] else "")
        )
        self.setStyleSheet(
            f"QPushButton {{ background:#3d4450; color:{TEXT_PRIMARY}; border:1px solid {accent}; "
            f"border-bottom:3px solid {accent}; border-radius:2px; font-size:8px; font-weight:bold; }}"
            f"QPushButton:hover {{ background:#4b5563; border:2px solid {accent}; }}"
        )


class FittingLabWidget(QWidget):
    """In-game-inspired fitting window."""
    evaluate_requested = pyqtSignal(str, dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot_buttons: Dict[str, List[SlotButton]] = {
            "high": [], "mid": [], "low": [], "rig": [], "sub": [],
        }
        self.drones: List[str] = []
        self.cargo: List[str] = []
        self.fit_split: Optional[QSplitter] = None
        self.center_panel: Optional[QFrame] = None
        self.ship_silhouette: Optional[QFrame] = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"FittingLabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
            "QLineEdit, QComboBox, QTextEdit, QListWidget {"
            f"  background:#1a1d21; color:{TEXT_PRIMARY}; border:1px solid #3f4650; border-radius:2px; }}"
        )
        self._init_ui()
        hulls = sorted(SHIP_DATABASE.keys())
        if hulls:
            self.hull_combo.setCurrentText("Cynabal" if "Cynabal" in hulls else hulls[0])
            self._on_hull_changed(self.hull_combo.currentText())

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        chrome = QFrame()
        chrome.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        ch = QHBoxLayout(chrome)
        ch.setContentsMargins(10, 6, 10, 6)
        title = QLabel("FITTING")
        title.setStyleSheet(
            f"color:{ACCENT}; font-size:13px; font-weight:bold; letter-spacing:2px; border:none;"
        )
        ch.addWidget(title)
        self.ship_title = QLabel("No hull")
        self.ship_title.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size:14px; font-weight:bold; border:none;"
        )
        ch.addWidget(self.ship_title, stretch=1)
        self.fit_name_edit = QLineEdit("Custom Fit")
        self.fit_name_edit.setFixedWidth(220)
        self.fit_name_edit.setPlaceholderText("Fit name")
        self.fit_name_edit.textChanged.connect(self._sync_eft_text)
        ch.addWidget(self.fit_name_edit)
        root.addWidget(chrome)

        split = QSplitter(Qt.Orientation.Horizontal)

        # --- Market / module browser (left) ---
        left = QFrame()
        left.setMinimumWidth(240)
        left.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.addWidget(self._section("SHIP"))
        self.hull_combo = QComboBox()
        self.hull_combo.setEditable(True)
        self.hull_combo.addItems(sorted(SHIP_DATABASE.keys()))
        self.hull_combo.currentTextChanged.connect(self._on_hull_changed)
        ll.addWidget(self.hull_combo)
        self.hull_meta = QLabel("")
        self.hull_meta.setWordWrap(True)
        self.hull_meta.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px; border:none;")
        ll.addWidget(self.hull_meta)

        ll.addWidget(self._section("MARKET / MODULES"))
        self.mod_search = QLineEdit()
        self.mod_search.setPlaceholderText("Search modules…")
        self.mod_search.setFixedHeight(28)
        self.mod_search.textChanged.connect(self._refresh_module_list)
        ll.addWidget(self.mod_search)
        self.mod_slot_filter = QComboBox()
        self.mod_slot_filter.addItems(["All slots", "High", "Mid", "Low", "Rig"])
        self.mod_slot_filter.currentTextChanged.connect(self._refresh_module_list)
        ll.addWidget(self.mod_slot_filter)
        self.mod_list = QListWidget()
        self.mod_list.setSpacing(4)
        self.mod_list.setStyleSheet(
            f"QListWidget {{ background:{BG_DEEP}; border:1px solid {BORDER}; outline:none; }}"
            f"QListWidget::item {{"
            f"  border:1px solid {BORDER_MUTED}; border-radius:3px; padding:8px 10px;"
            f"  margin:4px 2px; background:{BG_ELEVATED}; color:{TEXT_PRIMARY}; }}"
            f"QListWidget::item:hover {{ border:1px solid {ACCENT}; background:{BURNT_IRON_LIGHT}; }}"
            f"QListWidget::item:selected {{ border:2px solid {BORDER_FOCUS}; background:{BURNT_IRON_LIGHT}; color:{TEXT_PRIMARY}; }}"
        )
        self.mod_list.itemDoubleClicked.connect(self._fit_selected_module)
        ll.addWidget(self.mod_list, stretch=1)
        fit_sel = QPushButton("Fit to next empty slot")
        fit_sel.setStyleSheet(self._btn_css())
        fit_sel.clicked.connect(lambda: self._fit_selected_module(self.mod_list.currentItem()))
        ll.addWidget(fit_sel)
        split.addWidget(left)

        # --- Center paperdoll ---
        center = QFrame()
        center.setStyleSheet(f"QFrame {{ background:{BG_DEEP}; border:none; }}")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(10, 10, 10, 10)

        body = QHBoxLayout()
        sil = QFrame()
        sil.setMinimumWidth(SILHOUETTE_SHOWN_MIN_W)
        sil.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sil.setStyleSheet(
            f"QFrame {{ background: qradialgradient(cx:0.5, cy:0.45, radius:0.8, fx:0.5, fy:0.4,"
            f" stop:0 {BG_ELEVATED}, stop:0.55 {BG_DEEP}, stop:1 {BG_DEEP});"
            f" border:1px solid {BORDER_MUTED}; }}"
        )
        sl = QVBoxLayout(sil)
        sl.addStretch()
        self.sil_name = QLabel("SHIP")
        self.sil_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sil_name.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size:16px; font-weight:bold; border:none; background:transparent;"
        )
        sl.addWidget(self.sil_name)
        self.sil_class = QLabel("")
        self.sil_class.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sil_class.setStyleSheet(
            f"color:{TEXT_HINT}; font-size:11px; border:none; background:transparent;"
        )
        sl.addWidget(self.sil_class)
        sl.addStretch()
        body.addWidget(sil)

        slots_wrap = QScrollArea()
        slots_wrap.setWidgetResizable(True)
        slots_wrap.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        slot_host = QWidget()
        self.slot_grid = QGridLayout(slot_host)
        self.slot_grid.setSpacing(10)
        self.slot_grid.setHorizontalSpacing(12)
        self.slot_grid.setContentsMargins(8, 4, 8, 4)
        slots_wrap.setWidget(slot_host)
        body.addWidget(slots_wrap, stretch=1)
        cl.addLayout(body, stretch=1)

        hp_box = QFrame()
        hp_box.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        hp_l = QVBoxLayout(hp_box)
        hp_l.setContentsMargins(8, 6, 8, 6)
        hp_hdr = QLabel("STRUCTURE")
        hp_hdr.setStyleSheet(
            f"color:{TEXT_HEADER}; font-size:10px; letter-spacing:1px; border:none;"
        )
        hp_l.addWidget(hp_hdr)
        self.hp_shield = HpBar("Shield", "#3b82f6")
        self.hp_armor = HpBar("Armor", "#d97706")
        self.hp_hull = HpBar("Hull", "#a8a29e")
        hp_l.addWidget(self.hp_shield)
        hp_l.addWidget(self.hp_armor)
        hp_l.addWidget(self.hp_hull)
        self.ehp_lbl = QLabel("EHP  0")
        self.ehp_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12px; font-weight:bold; border:none;"
        )
        hp_l.addWidget(self.ehp_lbl)
        cl.addWidget(hp_box)

        extra = QHBoxLayout()
        self.drone_edit = QLineEdit()
        self.drone_edit.setPlaceholderText("Drone bay (Warrior II x5)")
        extra.addWidget(self.drone_edit)
        add_d = QPushButton("Drones")
        add_d.setStyleSheet(self._btn_css())
        add_d.clicked.connect(self._add_drone)
        extra.addWidget(add_d)
        self.cargo_edit = QLineEdit()
        self.cargo_edit.setPlaceholderText("Cargo / ammo")
        extra.addWidget(self.cargo_edit)
        add_c = QPushButton("Cargo")
        add_c.setStyleSheet(self._btn_css())
        add_c.clicked.connect(self._add_cargo)
        extra.addWidget(add_c)
        cl.addLayout(extra)
        split.addWidget(center)

        # --- Right: attributes + cargo ---
        right = QFrame()
        right.setMinimumWidth(280)
        right.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 8, 8, 8)
        rl.addWidget(self._section("FITTING"))
        self.cpu_bar = ResourceBar("CPU", "#5b9bd5")
        self.pg_bar = ResourceBar("Powergrid", "#e8c872")
        self.cal_bar = ResourceBar("Calibration", "#7cb87c")
        rl.addWidget(self.cpu_bar)
        rl.addWidget(self.pg_bar)
        rl.addWidget(self.cal_bar)
        self.resource_caption = QLabel("CPU and powergrid used vs this hull (approximate).")
        self.resource_caption.setWordWrap(True)
        self.resource_caption.setStyleSheet(f"color:{TEXT_HINT}; font-size:10px; border:none;")
        rl.addWidget(self.resource_caption)
        self.fit_status = QLabel("")
        self.fit_status.setWordWrap(True)
        self.fit_status.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px; border:none;")
        rl.addWidget(self.fit_status)

        rl.addWidget(self._section("CARGO / AMMO"))
        self.cargo_list = QListWidget()
        self.cargo_list.setStyleSheet(
            f"QListWidget {{ font-size:11px; color:{TEXT_PRIMARY}; }}"
            "QListWidget::item { padding:4px 6px; }"
        )
        self.cargo_list.itemDoubleClicked.connect(self._remove_cargo_item)
        rl.addWidget(self.cargo_list, stretch=1)

        rl.addWidget(self._section("ROLE / EFT"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(COMBAT_ROLES)
        rl.addWidget(self.role_combo)
        self.eft_edit = QTextEdit()
        self.eft_edit.setPlaceholderText("[Hull, Fit Name]")
        self.eft_edit.setReadOnly(True)
        self.eft_edit.setMaximumHeight(80)
        rl.addWidget(self.eft_edit)
        btn_row = QHBoxLayout()
        imp = QPushButton("Import")
        imp.setStyleSheet(self._btn_css())
        imp.clicked.connect(self._import_eft)
        btn_row.addWidget(imp)
        exp = QPushButton("Export")
        exp.setStyleSheet(self._btn_css())
        exp.clicked.connect(self._export_eft_file)
        btn_row.addWidget(exp)
        rl.addLayout(btn_row)
        ev = QPushButton("⚡ ASK A.U.R.A.")
        ev.setFixedHeight(26)
        ev.setStyleSheet(radar_accent_btn_css())
        ev.clicked.connect(self._evaluate)
        rl.addWidget(ev)
        split.addWidget(right)

        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 5)
        split.setStretchFactor(2, 2)
        split.setSizes([320, 720, 300])
        self.fit_split = split
        self.center_panel = center
        self.ship_silhouette = sil
        split.splitterMoved.connect(self._update_ship_silhouette_visibility)
        root.addWidget(split, stretch=1)
        self._refresh_module_list()
        self._update_ship_silhouette_visibility()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_ship_silhouette_visibility()

    def _update_ship_silhouette_visibility(self) -> None:
        if not self.ship_silhouette or not self.center_panel:
            return
        show = self.center_panel.width() >= SILHOUETTE_MIN_CENTER_W
        self.ship_silhouette.setVisible(show)
        if show:
            self.ship_silhouette.setMinimumWidth(SILHOUETTE_SHOWN_MIN_W)
            self.ship_silhouette.setMaximumWidth(SILHOUETTE_SHOWN_MAX_W)
        else:
            self.ship_silhouette.setMinimumWidth(0)
            self.ship_silhouette.setMaximumWidth(0)

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{TEXT_HEADER}; font-size:10px; font-weight:bold; letter-spacing:1px; "
            f"border:none; padding-top:6px;"
        )
        return lbl

    def _btn_css(self) -> str:
        return btn_secondary_css()

    def _current_hull_info(self) -> Optional[Dict[str, Any]]:
        return lookup_ship(self.hull_combo.currentText().strip())

    def _on_hull_changed(self, name: str):
        info = lookup_ship(name)
        if not info:
            self.hull_meta.setText("Unknown hull — defaulting to 8/8/8/3 slots.")
            self.ship_title.setText(name or "Unknown")
            self.sil_name.setText(name or "SHIP")
            self.sil_class.setText("")
            self._rebuild_slots(8, 8, 8, 3, 0)
            self._sync_eft_text()
            self._refresh_stats()
            return
        highs = int(info.get("high_slots") or 8)
        mids = int(info.get("mid_slots") or 8)
        lows = int(info.get("low_slots") or 8)
        rigs = int(info.get("rig_slots") or 3)
        subs = 5 if "Strategic Cruiser" in str(info.get("class") or "") or "T3" in str(info.get("class") or "") else 0
        cname = info.get("canonical_name", name)
        self.ship_title.setText(f"{cname}")
        self.sil_name.setText(cname)
        self.sil_class.setText(f"{info.get('class', '')}  ·  {info.get('faction', '')}")
        self.hull_meta.setText(
            f"{info.get('class', '')}  ·  {info.get('role', '')}\n"
            f"Turrets {info.get('turret_hardpoints', '?')}  ·  Launchers {info.get('launcher_hardpoints', '?')}"
        )
        self._rebuild_slots(highs, mids, lows, rigs, subs)
        self._sync_eft_text()
        self._refresh_stats()

    def _rebuild_slots(self, highs: int, mids: int, lows: int, rigs: int, subs: int):
        while self.slot_grid.count():
            item = self.slot_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.slot_buttons = {"high": [], "mid": [], "low": [], "rig": [], "sub": []}
        specs = [
            ("high", "HIGH", highs),
            ("mid", "MED", mids),
            ("low", "LOW", lows),
            ("rig", "RIG", rigs),
        ]
        if subs:
            specs.append(("sub", "SUB", subs))

        col = 0
        max_rows = max((c for _, _, c in specs), default=0)
        for idx, (kind, label, count) in enumerate(specs):
            if idx > 0:
                spacer = QWidget()
                spacer.setFixedWidth(22)
                self.slot_grid.addWidget(spacer, 0, col, max_rows + 1, 1)
                col += 1
            hdr = QLabel(label)
            hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hdr.setStyleSheet(
                f"color:{SLOT_ACCENT.get(kind, TEXT_HINT)}; font-size:10px; font-weight:bold; "
                f"letter-spacing:1px; padding-bottom:4px;"
            )
            self.slot_grid.addWidget(hdr, 0, col)
            for i in range(count):
                btn = SlotButton(kind, i)
                btn.clicked.connect(lambda _, b=btn: self._on_slot_clicked(b))
                self.slot_buttons[kind].append(btn)
                self.slot_grid.addWidget(btn, i + 1, col)
            col += 1

    def _refresh_module_list(self):
        self.mod_list.clear()
        q = (self.mod_search.text() or "").strip().lower()
        slot_f = self.mod_slot_filter.currentText()
        for name, info in MODULE_DATABASE.items():
            slot = str(info.get("slot") or "")
            if slot_f != "All slots" and slot.lower() != slot_f.lower():
                continue
            blob = f"{name} {info.get('category', '')} {info.get('role', '')}".lower()
            if q and q not in blob:
                continue
            load = module_load(name)
            kind = self._module_slot_kind(name)
            accent = SLOT_ACCENT.get(kind, "#6b7280")
            item = QListWidgetItem(
                f"{name}\n  {slot}  ·  CPU {load['cpu']:.0f}  PG {load['powergrid']:.0f}"
            )
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setData(Qt.ItemDataRole.UserRole + 1, accent)
            item.setSizeHint(QSize(0, 52))
            font = QFont()
            font.setPointSize(10)
            item.setFont(font)
            self.mod_list.addItem(item)

    def _selected_module_name(self, item: Optional[QListWidgetItem] = None) -> Optional[str]:
        it = item or self.mod_list.currentItem()
        if not it:
            return None
        return it.data(Qt.ItemDataRole.UserRole)

    def _module_slot_kind(self, name: str) -> str:
        info = lookup_module(name) or MODULE_DATABASE.get(name) or {}
        slot = str(info.get("slot") or "High").lower()
        if slot.startswith("high"):
            return "high"
        if slot.startswith("mid"):
            return "mid"
        if slot.startswith("low"):
            return "low"
        if slot.startswith("rig"):
            return "rig"
        return "high"

    def _after_fit_change(self):
        self._sync_eft_text()
        self._refresh_stats()

    def _fit_selected_module(self, item: Optional[QListWidgetItem] = None):
        name = self._selected_module_name(item)
        if not name:
            return
        kind = self._module_slot_kind(name)
        for btn in self.slot_buttons.get(kind, []):
            if not btn.module_name:
                btn.set_module(name)
                self._after_fit_change()
                return
        QMessageBox.information(self, "Fitting", f"No empty {kind} slots remain on this hull.")

    def _on_slot_clicked(self, btn: SlotButton):
        if btn.module_name:
            btn.set_empty()
            self._after_fit_change()
            return
        name = self._selected_module_name()
        if not name:
            return
        kind = self._module_slot_kind(name)
        if kind != btn.kind:
            QMessageBox.information(self, "Fitting", f"{name} belongs in a {kind} slot.")
            return
        btn.set_module(name)
        self._after_fit_change()

    def _add_drone(self):
        t = self.drone_edit.text().strip()
        if t:
            self.drones.append(t)
            self.drone_edit.clear()
            self._refresh_cargo_list()
            self._after_fit_change()

    def _add_cargo(self):
        t = self.cargo_edit.text().strip()
        if t:
            self.cargo.append(t)
            self.cargo_edit.clear()
            self._refresh_cargo_list()
            self._after_fit_change()

    def _refresh_cargo_list(self):
        self.cargo_list.clear()
        for d in self.drones:
            self.cargo_list.addItem(QListWidgetItem(f"Drone: {d}"))
        for c in self.cargo:
            self.cargo_list.addItem(QListWidgetItem(f"Cargo: {c}"))

    def _remove_cargo_item(self, item: QListWidgetItem):
        text = item.text()
        if text.startswith("Drone: "):
            val = text[7:]
            if val in self.drones:
                self.drones.remove(val)
        elif text.startswith("Cargo: "):
            val = text[7:]
            if val in self.cargo:
                self.cargo.remove(val)
        self._refresh_cargo_list()
        self._after_fit_change()

    def _slot_names(self, kind: str) -> List[str]:
        return [b.module_name for b in self.slot_buttons.get(kind, []) if b.module_name]

    def _all_fitted(self) -> List[str]:
        names: List[str] = []
        for kind in ("high", "mid", "low", "rig", "sub"):
            names.extend(self._slot_names(kind))
        return names

    def current_eft(self) -> str:
        hull = self.hull_combo.currentText().strip() or "Unknown"
        fname = self.fit_name_edit.text().strip() or "Custom Fit"
        blocks = [
            f"[{hull}, {fname}]",
            "\n".join(self._slot_names("low")),
            "\n".join(self._slot_names("mid")),
            "\n".join(self._slot_names("high")),
            "\n".join(self._slot_names("rig")),
            "\n".join(self._slot_names("sub")),
            "\n".join(self.drones),
            "\n".join(self.cargo),
        ]
        return "\n\n".join([b for b in blocks if b]).strip() + "\n"

    def _sync_eft_text(self):
        self.eft_edit.blockSignals(True)
        self.eft_edit.setPlainText(self.current_eft())
        self.eft_edit.blockSignals(False)

    def _refresh_stats(self):
        hull = self.hull_combo.currentText().strip()
        stats = compute_fit(hull, self._all_fitted())
        self.cpu_bar.set_values(stats["cpu_used"], stats["cpu_output"], stats["cpu_ok"])
        self.pg_bar.set_values(stats["pg_used"], stats["pg_output"], stats["pg_ok"])
        self.cal_bar.set_values(stats["cal_used"], stats["cal_output"], stats["cal_ok"])
        self.hp_shield.set_hp(stats["shield"])
        self.hp_armor.set_hp(stats["armor"])
        self.hp_hull.set_hp(stats["hull"])
        self.ehp_lbl.setText(f"EHP  {stats['ehp']:,.0f}   (approx. hull + modules)")
        warns = []
        if not stats["cpu_ok"]:
            warns.append("CPU overloaded")
        if not stats["pg_ok"]:
            warns.append("Powergrid overloaded")
        if not stats["cal_ok"]:
            warns.append("Calibration exceeded")
        info = self._current_hull_info() or {}
        highs = self._slot_names("high")
        turret_kw = ("laser", "blaster", "rail", "autocannon", "artillery", "pulse", "beam", "disintegrator")
        launcher_kw = ("missile", "rocket", "torpedo", "launcher", "bomb")
        t_count = sum(1 for m in highs if any(k in m.lower() for k in turret_kw))
        l_count = sum(1 for m in highs if any(k in m.lower() for k in launcher_kw))
        tm = info.get("turret_hardpoints")
        lm = info.get("launcher_hardpoints")
        if tm is not None and t_count > int(tm):
            warns.append(f"Turret hardpoints {t_count}/{tm}")
        if lm is not None and l_count > int(lm):
            warns.append(f"Launcher hardpoints {l_count}/{lm}")
        if warns:
            self.fit_status.setText("  ·  ".join(warns))
            self.fit_status.setStyleSheet("color:#f07178; font-size:11px; font-weight:bold; border:none;")
        else:
            leftover_cpu = stats["cpu_output"] - stats["cpu_used"]
            leftover_pg = stats["pg_output"] - stats["pg_used"]
            self.fit_status.setText(
                f"Fit is legal (approx.)  ·  {leftover_cpu:.0f} tf / {leftover_pg:.0f} MW remaining"
            )
            self.fit_status.setStyleSheet("color:#86efac; font-size:11px; border:none;")
        self._refresh_cargo_list()

    def _fill_from_parsed(self, parsed: Dict[str, Any]):
        hull = parsed.get("hull_name") or ""
        overflow_notes: List[str] = []

        self.hull_combo.blockSignals(True)
        self.fit_name_edit.blockSignals(True)
        try:
            if hull:
                idx = self.hull_combo.findText(hull)
                if idx < 0:
                    self.hull_combo.setEditText(hull)
                else:
                    self.hull_combo.setCurrentIndex(idx)
                info = lookup_ship(hull)
                if info:
                    highs = int(info.get("high_slots") or 8)
                    mids = int(info.get("mid_slots") or 8)
                    lows = int(info.get("low_slots") or 8)
                    rigs = int(info.get("rig_slots") or 3)
                    subs = (
                        5
                        if "Strategic Cruiser" in str(info.get("class") or "")
                        or "T3" in str(info.get("class") or "")
                        else 0
                    )
                    cname = info.get("canonical_name", hull)
                    self.ship_title.setText(cname)
                    self.sil_name.setText(cname)
                    self.sil_class.setText(f"{info.get('class', '')}  ·  {info.get('faction', '')}")
                    self.hull_meta.setText(
                        f"{info.get('class', '')}  ·  {info.get('role', '')}\n"
                        f"Turrets {info.get('turret_hardpoints', '?')}  ·  "
                        f"Launchers {info.get('launcher_hardpoints', '?')}"
                    )
                    self._rebuild_slots(highs, mids, lows, rigs, subs)
                else:
                    self._rebuild_slots(8, 8, 8, 3, 0)

            self.fit_name_edit.setText(parsed.get("fit_name") or "Custom Fit")

            mapping = {
                "high": parsed.get("high_slots") or [],
                "mid": parsed.get("mid_slots") or [],
                "low": parsed.get("low_slots") or [],
                "rig": parsed.get("rig_slots") or [],
                "sub": parsed.get("subsystems") or [],
            }
            for kind, mods in mapping.items():
                buttons = self.slot_buttons.get(kind, [])
                for i, btn in enumerate(buttons):
                    if i < len(mods) and mods[i]:
                        btn.set_module(mods[i])
                    else:
                        btn.set_empty()
                if len(mods) > len(buttons):
                    overflow_notes.append(
                        f"{len(mods) - len(buttons)} extra {kind} module(s) dropped"
                    )

            self.drones = list(parsed.get("drones") or [])
            self.cargo = list(parsed.get("cargo_items") or [])
        finally:
            self.hull_combo.blockSignals(False)
            self.fit_name_edit.blockSignals(False)

        self._refresh_cargo_list()
        self._after_fit_change()
        if overflow_notes:
            QMessageBox.warning(
                self,
                "Fitting",
                "Imported with warnings:\n" + "\n".join(overflow_notes),
            )

    def _import_eft(self):
        text = ""
        clip = QApplication.clipboard().text().strip()
        if _looks_like_eft(clip):
            text = clip
        else:
            dlg = PasteEftDialog(self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                text = dlg.text().strip()
            if not text:
                path, _ = QFileDialog.getOpenFileName(
                    self, "Import EFT", "", "Text (*.txt);;All Files (*.*)"
                )
                if not path:
                    return
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as fh:
                        text = fh.read().strip()
                except OSError as exc:
                    log_diagnostic_error(
                        AURAErrorCode.ERR_4003_CACHE_IO_ERROR,
                        exc,
                        f"FittingLabWidget._import_eft({path})",
                    )
                    QMessageBox.warning(self, "Fitting", f"Could not read file:\n{exc}")
                    return
        if not text:
            return
        parsed = FittingParser.parse(text)
        if not parsed or parsed.get("error"):
            QMessageBox.warning(self, "Fitting", "Could not parse EFT text.")
            return
        self._fill_from_parsed(parsed)

    def _export_eft_file(self):
        text = self.current_eft()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export EFT", "fit.txt", "Text (*.txt);;All Files (*.*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as exc:
            log_diagnostic_error(
                AURAErrorCode.ERR_4003_CACHE_IO_ERROR,
                exc,
                f"FittingLabWidget._export_eft_file({path})",
            )
            QMessageBox.warning(self, "Fitting", f"Could not write file:\n{exc}")

    def _evaluate(self):
        text = self.current_eft()
        parsed = FittingParser.parse(text)
        if not parsed or parsed.get("error"):
            QMessageBox.warning(self, "Fitting", "Fit is empty or unrecognized.")
            return
        self.evaluate_requested.emit(text, parsed, self.role_combo.currentText())
