"""
Composition tab: paste friendly fleet vs hostile D-scan, role breakdown, local assessment.
"""
# Responsibilities:
# - CompositionTabWidget UI: dual paste panes, role table, local assessment panel
# - Delegates parsing and matchup logic to composition.py (no LLM)
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
)

from composition import parse_fleet_paste, compare_fleets, assess_matchup
from error_handler import AURAErrorCode, log_diagnostic_error
from theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_HEADER,
    BG_PANEL, BG_DEEP, BG_ELEVATED, BORDER, BORDER_MUTED, ACCENT, ACCENT_DIM,
    STATUS_ONLINE, BTN_TEXT_ON_ACCENT,
)


class CompositionTabWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"CompositionTabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        header = QLabel("COMPOSITION")
        header.setStyleSheet(
            f"color:{ACCENT}; font-size:13px; font-weight:bold; letter-spacing:2px;"
        )
        root.addWidget(header)

        paste_row = QHBoxLayout()
        paste_row.setSpacing(8)

        left = QFrame()
        left.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.addWidget(self._section("Friendly fleet (Fleet window / chat)"))
        self.friendly_edit = QTextEdit()
        self.friendly_edit.setPlaceholderText(
            "Paste friendly hulls — fleet window, overview, intel, or a list.\n\n"
            "Examples:\n"
            "8 Muninn\n"
            "4 Cerberus, 4 Scimitar\n"
            "[ 19:15:23 ] Scout > +3 Muninn Cerberus holding gate\n"
            "PilotName\tMuninn\t12 km"
        )
        ll.addWidget(self.friendly_edit, stretch=1)
        self.friendly_hint = QLabel("0 hulls · 0 unmatched")
        self.friendly_hint.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        ll.addWidget(self.friendly_hint)
        paste_row.addWidget(left, stretch=1)

        right = QFrame()
        right.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:none; }}")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 8, 8, 8)
        rl.addWidget(self._section("Hostile D-scan / grid"))
        self.enemy_edit = QTextEdit()
        self.enemy_edit.setPlaceholderText(
            "Paste hostile D-scan, overview, or intel channel lines.\n\n"
            "Examples:\n"
            "Ishtar\tIshtar\t24 km\n"
            "15x Ishtar\n"
            "[ 19:16:01 ] Wingman > V-3YG7 +5 Loki Cerberus gate\n"
            "HostilePilot\tIshtar\t18 km"
        )
        rl.addWidget(self.enemy_edit, stretch=1)
        self.enemy_hint = QLabel("0 hulls · 0 unmatched")
        self.enemy_hint.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        rl.addWidget(self.enemy_hint)
        paste_row.addWidget(right, stretch=1)
        root.addLayout(paste_row, stretch=2)

        analyze = QPushButton("Auto-Analyze Matchup")
        analyze.setFixedHeight(36)
        analyze.setStyleSheet(
            f"QPushButton {{ background:{ACCENT_DIM}; color:{TEXT_PRIMARY}; border:1px solid {ACCENT}; "
            "font-weight:bold; border-radius:2px; }"
            f"QPushButton:hover {{ background:{ACCENT}; color:{BTN_TEXT_ON_ACCENT}; }}"
        )
        analyze.clicked.connect(self._analyze)
        root.addWidget(analyze)

        root.addWidget(self._section("Tactical breakdown"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Role / Category", "Friendly (Count)", "Enemy (Count)", "Delta"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; "
            f"gridline-color:{BORDER_MUTED}; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HEADER}; "
            f"border:1px solid {BORDER}; padding:6px; font-weight:bold; }}"
        )
        root.addWidget(self.table, stretch=2)

        root.addWidget(self._section("Engagement assessment"))
        self.assessment = QTextEdit()
        self.assessment.setReadOnly(True)
        self.assessment.setPlaceholderText("Run Auto-Analyze Matchup to generate a local tactical readout.")
        self.assessment.setMaximumHeight(140)
        self.assessment.setStyleSheet(
            f"QTextEdit {{ background:{BG_DEEP}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; }}"
        )
        root.addWidget(self.assessment)

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{TEXT_HEADER}; font-size:10px; font-weight:bold; letter-spacing:1px;"
        )
        return lbl

    def _analyze(self):
        """Parse both paste panes and refresh the role table and engagement assessment."""
        try:
            f_raw = self.friendly_edit.toPlainText()
            e_raw = self.enemy_edit.toPlainText()
            f_parsed = parse_fleet_paste(f_raw)
            e_parsed = parse_fleet_paste(e_raw)
        except Exception as exc:
            log_diagnostic_error(
                AURAErrorCode.ERR_3001_DSCAN_PARSE_FAILED,
                exc,
                "CompositionTabWidget._analyze",
            )
            self.assessment.setHtml(
                f"<p style='color:{TEXT_HINT};'>Analysis failed — check paste format and try again.</p>"
            )
            return
        self.friendly_hint.setText(
            f"{f_parsed['total_ships']} hulls · {f_parsed['unmatched']} unmatched"
        )
        self.enemy_hint.setText(
            f"{e_parsed['total_ships']} hulls · {e_parsed['unmatched']} unmatched"
        )

        rows = compare_fleets(f_parsed["ship_counts"], e_parsed["ship_counts"])
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            items = [
                QTableWidgetItem(row["label"]),
                QTableWidgetItem(row["friendly"]),
                QTableWidgetItem(row["enemy"]),
                QTableWidgetItem(row["delta"]),
            ]
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, col, item)
            kind = row["delta_kind"]
            if kind == "adv":
                items[3].setForeground(QBrush(QColor(STATUS_ONLINE)))
            elif kind == "disadv":
                items[3].setForeground(QBrush(QColor(ACCENT)))

        bullets = assess_matchup(rows, f_parsed["total_ships"], e_parsed["total_ships"])
        if not f_parsed["total_ships"] and not e_parsed["total_ships"]:
            self.assessment.setHtml(
                f"<p style='color:{TEXT_HINT};'>No recognized hulls on either side. "
                "Paste fleet window / D-scan lines that include ship names.</p>"
            )
            return
        lis = "".join(f"<li>{self._esc(b)}</li>" for b in bullets)
        self.assessment.setHtml(
            f"<div style='color:{TEXT_PRIMARY};'>"
            f"<b>A.U.R.A. tactical advisor</b> (local, not neural)"
            f"<ul>{lis}</ul></div>"
        )

    @staticmethod
    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
