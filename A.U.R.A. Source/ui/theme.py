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
Angel Cartel UI theme — blackened metal, burnt iron, bone ivory, oxide red accents.
Single source of truth for A.U.R.A. desktop styling.
"""
from __future__ import annotations

import os
import sys
from typing import Dict

# --- Canonical Angel Cartel faction colors ---
BLACKENED_METAL = "#0c0a09"
BURNT_IRON = "#2a2522"
BURNT_IRON_LIGHT = "#3a3430"
BURNT_IRON_BORDER = "#524840"
BONE_WHITE = "#ece8e0"
BONE_IVORY = "#d4cec4"
BONE_MUTED = "#9a9288"
OXIDE_RED = "#b91c1c"
OXIDE_RED_HOVER = "#dc2626"
OXIDE_RED_DIM = "#6b1414"

# --- UI role aliases (keep names for imports across the app) ---
BG_DEEP = BLACKENED_METAL
BG_PANEL = BURNT_IRON
BG_ELEVATED = "#32302c"
BG_CHROME = "#141210"
BG_TITLEBAR = "#1a1614"
BG_INPUT = "#1a1816"

BORDER = BURNT_IRON_BORDER
BORDER_MUTED = BURNT_IRON_LIGHT
BORDER_FOCUS = OXIDE_RED

ACCENT = OXIDE_RED
ACCENT_HOVER = OXIDE_RED_HOVER
ACCENT_DIM = OXIDE_RED_DIM
ACCENT_PRESSED = "#991b1b"

TEXT_PRIMARY = BONE_WHITE
TEXT_SECONDARY = BONE_IVORY
TEXT_HINT = BONE_MUTED
TEXT_HEADER = BONE_IVORY
TEXT_BRAND = BONE_WHITE

BTN_SECONDARY_BG = BURNT_IRON
BTN_SECONDARY_BORDER = BURNT_IRON_BORDER

STATUS_ONLINE = "#34d399"
STATUS_STANDBY_BG = BURNT_IRON
STATUS_STANDBY_BORDER = BURNT_IRON_BORDER

BTN_TEXT_ON_ACCENT = BONE_WHITE

GUNMETAL_HIGH = "#1a1c20"
GUNMETAL = "#121418"
GUNMETAL_DEEP = "#0a0b0d"

GRAD_SHELL = (
    f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    f"stop:0 {GUNMETAL_HIGH}, stop:0.18 {GUNMETAL}, stop:1 {GUNMETAL_DEEP})"
)
GRAD_CHROME = (
    f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    f"stop:0 {BG_TITLEBAR}, stop:1 {BG_CHROME})"
)
GRAD_PANE = BG_PANEL
GRAD_TAB_IDLE = (
    f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    f"stop:0 {BG_TITLEBAR}, stop:1 {BG_PANEL})"
)
GRAD_TAB_HOVER = (
    f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    f"stop:0 {BG_PANEL}, stop:1 {BG_CHROME})"
)
GRAD_TAB_SELECTED = GRAD_PANE
GRAD_BTN = (
    f"qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    f"stop:0 {ACCENT_DIM}, stop:0.45 {ACCENT}, stop:1 {ACCENT_HOVER})"
)
GRAD_BTN_HOVER = (
    f"qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    f"stop:0 {ACCENT}, stop:1 {ACCENT_HOVER})"
)
GRAD_SIDEBAR = (
    f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
    f"stop:0 {BG_TITLEBAR}, stop:1 {BG_CHROME})"
)

FONT_DISPLAY = "'Orbitron', 'Segoe UI', sans-serif"
_DISPLAY_FONT_LOADED = False
_DISPLAY_FONT_FAMILY = "Orbitron"


def tier_badge_font_css() -> str:
    return f"font-family: {FONT_DISPLAY};"


def _fonts_dir() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(this_dir, "assets", "fonts"),
        os.path.join(this_dir, "..", "assets", "fonts"),
    ]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.insert(0, os.path.join(meipass, "assets", "fonts"))
        candidates.insert(1, meipass)
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "Orbitron-wght.ttf")):
            return os.path.abspath(c)
        if os.path.isfile(os.path.join(c, "Orbitron-wght.ttf")):
            return os.path.abspath(c)
    return os.path.abspath(candidates[-1] if candidates else this_dir)


def _shell_background_css() -> str:
    """Shaded gunmetal well — cool grey, no texture."""
    return f"background: {GRAD_SHELL};"


def _font_file_paths() -> list[str]:
    return [os.path.join(_fonts_dir(), "Orbitron-wght.ttf")]


def _font_file_exists() -> bool:
    return any(os.path.isfile(p) for p in _font_file_paths())


def load_display_font() -> str:
    """Load bundled Orbitron if present; return primary display family name."""
    global _DISPLAY_FONT_LOADED
    if _DISPLAY_FONT_LOADED:
        return _DISPLAY_FONT_FAMILY if _font_file_exists() else "Segoe UI"
    _DISPLAY_FONT_LOADED = True
    if _font_file_exists():
        from PyQt6.QtGui import QFontDatabase

        for path in _font_file_paths():
            if os.path.isfile(path):
                QFontDatabase.addApplicationFont(path)
        return _DISPLAY_FONT_FAMILY
    return "Segoe UI"


def input_field_css() -> str:
    return f"""
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
            background-color: {BG_INPUT};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_MUTED};
            border-radius: 6px;
            padding: 6px 10px;
            selection-background-color: {ACCENT_DIM};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid {ACCENT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {BG_CHROME};
            color: {TEXT_PRIMARY};
            selection-background-color: {ACCENT_DIM};
            selection-color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_MUTED};
        }}
    """


def btn_secondary_css() -> str:
    return (
        f"QPushButton {{ background:{BTN_SECONDARY_BG}; color:{TEXT_PRIMARY}; "
        f"border:1px solid {BTN_SECONDARY_BORDER}; border-radius:2px; "
        f"padding:5px 12px; font-size:12px; }}"
        f"QPushButton:hover {{ background:{BURNT_IRON_LIGHT}; border:1px solid {ACCENT}; }}"
    )


def dialog_stylesheet() -> str:
    fields = input_field_css()
    return f"""
        QDialog {{
            background-color: {BG_CHROME};
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        QLabel {{
            background: transparent;
            border: none;
        }}
        QFrame#OptionCard {{
            background-color: {BG_PANEL};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 10px;
        }}
        {fields}
        QCheckBox {{
            color: {TEXT_SECONDARY};
            font-size: 12.5px;
            font-weight: 500;
            spacing: 6px;
            background: transparent;
            border: none;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid {BONE_MUTED};
            background-color: {BG_DEEP};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {ACCENT_HOVER};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1px solid {ACCENT_HOVER};
        }}
        QPushButton {{
            background-color: {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {ACCENT_PRESSED};
        }}
        QPushButton#CancelBtn {{
            background-color: {BTN_SECONDARY_BG};
            color: {TEXT_HINT};
            border: 1px solid {BTN_SECONDARY_BORDER};
        }}
        QPushButton#CancelBtn:hover {{
            background-color: {BG_ELEVATED};
            color: {TEXT_PRIMARY};
        }}
    """


def dialog_header_css(size_px: int = 15) -> str:
    return f"color: {TEXT_BRAND}; font-size: {size_px}px; font-weight: bold;"


def dialog_sub_css() -> str:
    return f"color: {TEXT_HINT}; font-size: 12px;"


def credits_html_palette() -> Dict[str, str]:
    return {
        "link": f"color:{ACCENT_HOVER}; text-decoration:none;",
        "muted": f"color:{TEXT_HINT};",
        "h": f"color:{TEXT_BRAND}; margin:18px 0 8px 0;",
    }


def progress_bar_stylesheet() -> str:
    return f"""
        QProgressBar {{
            background-color: {BG_ELEVATED};
            border-radius: 3px;
            border: none;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_DIM}, stop:0.5 {ACCENT}, stop:1 {ACCENT_DIM});
            border-radius: 3px;
        }}
    """


def tier_badge_online_css() -> str:
    return (
        f"{tier_badge_font_css()} color: {STATUS_ONLINE}; font-weight: bold; background: #064e3b; "
        f"padding: 4px 12px; border-radius: 6px; border: 1px solid {STATUS_ONLINE};"
    )


def tier_badge_standby_css() -> str:
    return (
        f"{tier_badge_font_css()} color: {TEXT_SECONDARY}; font-weight: bold; background: {STATUS_STANDBY_BG}; "
        f"padding: 4px 12px; border-radius: 6px; border: 1px solid {STATUS_STANDBY_BORDER};"
    )


def radar_control_btn_css() -> str:
    return (
        f"font-size: 12px; padding: 2px 10px; background: {BTN_SECONDARY_BG}; "
        f"border: 1px solid {BTN_SECONDARY_BORDER}; color: {TEXT_PRIMARY}; font-weight: bold;"
    )


def radar_accent_btn_css() -> str:
    return (
        f"font-size: 12px; padding: 2px 10px; background: {ACCENT_DIM}; "
        f"border: 1px solid {ACCENT}; color: {TEXT_PRIMARY}; font-weight: bold;"
    )


def tier_badge_busy_css() -> str:
    return (
        f"{tier_badge_font_css()} color: {TEXT_PRIMARY}; font-weight: bold; background: {ACCENT_DIM}; "
        f"padding: 4px 12px; border-radius: 6px; border: 1px solid {ACCENT};"
    )


def main_stylesheet() -> str:
    fields = input_field_css()
    shell_bg = _shell_background_css()
    return f"""
        QMainWindow {{
            {shell_bg}
        }}
        QWidget {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', -apple-system, 'SF Pro Display', 'Inter', system-ui, sans-serif;
            font-size: 14px;
        }}
        {fields}
        QFrame#AppShell {{
            {shell_bg}
            border: 1px solid {BORDER};
            border-radius: 0;
        }}
        QFrame#BrowserChrome {{
            background: {GRAD_CHROME};
            border: 1px solid {BORDER};
            border-bottom: 2px solid {ACCENT};
            border-radius: 8px;
            padding: 6px 12px;
        }}
        QFrame#BrowserFooter {{
            background: {GRAD_CHROME};
            border: 1px solid {BORDER};
            border-top: 2px solid {ACCENT};
            border-radius: 8px;
            padding: 6px 12px;
        }}
        QFrame#ChromeStripe {{
            background-color: {ACCENT};
            border: none;
            border-radius: 2px;
            margin: 2px 0;
        }}
        QLabel#ChromeMark {{
            border: none;
            background: transparent;
            padding: 0;
        }}
        QLabel#ChromeBrand {{
            color: {BONE_WHITE};
            font-family: {FONT_DISPLAY};
            font-size: 17px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 0 8px 0 4px;
            border: none;
            background: transparent;
        }}
        QLabel#ChromeFooterMeta {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            padding: 0 4px;
            border: none;
            background: transparent;
        }}
        QLabel#ChromeFooterLink {{
            color: {TEXT_HINT};
            font-size: 12px;
            padding: 0 6px;
            border: none;
            background: transparent;
        }}
        QPushButton#ChromeAction {{
            font-family: {FONT_DISPLAY};
            background-color: {BTN_SECONDARY_BG};
            color: {TEXT_PRIMARY};
            border: 1px solid {BTN_SECONDARY_BORDER};
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton#ChromeAction:hover {{
            background-color: {BURNT_IRON_LIGHT};
            border: 1px solid {ACCENT};
        }}
        QLabel#TierBadge {{
            font-family: {FONT_DISPLAY};
        }}
        QLabel#AddressBar {{
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER_MUTED};
            border-radius: 14px;
            padding: 6px 14px;
            color: {TEXT_SECONDARY};
            font-size: 12px;
        }}
        QFrame#HardwarePanel {{
            background-color: {BG_CHROME};
            border-radius: 8px;
            border: 1px solid {BORDER};
            padding: 8px 14px;
        }}
        QComboBox#ModelSelectorCombo {{
            background-color: {BG_ELEVATED};
            color: {TEXT_SECONDARY};
            border: 1px solid {ACCENT};
            border-radius: 6px;
            padding: 5px 12px;
            font-weight: bold;
            font-size: 13px;
            min-width: 220px;
        }}
        QComboBox#ModelSelectorCombo:hover {{
            border-color: {ACCENT_HOVER};
            background-color: {BG_PANEL};
        }}
        QComboBox#ModelSelectorCombo::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox#ModelSelectorCombo QAbstractItemView {{
            background-color: {BG_CHROME};
            color: {TEXT_PRIMARY};
            selection-background-color: {ACCENT_DIM};
            selection-color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            padding: 6px;
            font-size: 13px;
        }}

        QFrame#LiveIntelPanel {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 12px;
        }}
        QFrame#TabCard {{
            background: transparent;
            border: none;
            border-radius: 0;
        }}
        QListWidget#LiveIntelList {{
            background-color: {BG_DEEP};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
            padding: 4px;
        }}
        QListWidget#LiveIntelList::item {{
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 3px 2px;
        }}
        QListWidget#LiveIntelList::item:hover {{
            background-color: transparent;
        }}
        QListWidget#LiveIntelList::item:selected {{
            background-color: transparent;
        }}
        QTextEdit#ChatDisplay {{
            background-color: {BG_DEEP};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 16px;
            color: {TEXT_PRIMARY};
            font-size: 14.5px;
            line-height: 1.6;
        }}
        QTextEdit#InputEdit {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_MUTED};
            border-radius: 8px;
            padding: 12px 14px;
            color: {TEXT_PRIMARY};
            font-size: 14px;
        }}
        QTextEdit#InputEdit:focus {{
            border: 1px solid {BORDER_FOCUS};
            background-color: {BG_ELEVATED};
        }}
        QScrollBar:vertical {{
            border: none;
            background: {BG_DEEP};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {BTN_SECONDARY_BORDER};
            min-height: 24px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ACCENT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
            background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QScrollBar:horizontal {{
            height: 0px;
            background: none;
        }}
        QPushButton {{
            background: {GRAD_BTN};
            color: {BTN_TEXT_ON_ACCENT};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13.5px;
        }}
        QPushButton:hover {{
            background: {GRAD_BTN_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {ACCENT_PRESSED};
        }}
        QPushButton#ResetBtn {{
            background-color: {BTN_SECONDARY_BG};
            color: {TEXT_PRIMARY};
            border: 1px solid {BTN_SECONDARY_BORDER};
        }}
        QPushButton#ResetBtn:hover {{
            background-color: {ACCENT_DIM};
            color: {TEXT_PRIMARY};
            border: 1px solid {ACCENT};
        }}
        QPushButton#ToolBtnDScan {{
            background-color: {BG_ELEVATED};
            border: 1px solid {ACCENT};
            color: {TEXT_SECONDARY};
            font-weight: bold;
        }}
        QPushButton#ToolBtnDScan:hover {{
            background-color: {ACCENT_DIM};
            color: {TEXT_PRIMARY};
        }}
        QPushButton#ToolBtnFit {{
            background-color: {ACCENT_DIM};
            border: 1px solid {ACCENT};
            color: {TEXT_PRIMARY};
            font-weight: bold;
        }}
        QPushButton#ToolBtnFit:hover {{
            background-color: {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
        }}
        QPushButton#ToolBtnIntel {{
            background-color: {BTN_SECONDARY_BG};
            border: 1px solid {BORDER};
            color: {TEXT_SECONDARY};
            font-weight: bold;
        }}
        QPushButton#ToolBtnIntel:hover {{
            background-color: {BG_ELEVATED};
            border: 1px solid {ACCENT};
            color: {TEXT_PRIMARY};
        }}
        QPushButton#AttachBtn {{
            background-color: {BTN_SECONDARY_BG};
            border: 1px solid {BTN_SECONDARY_BORDER};
            color: {TEXT_PRIMARY};
        }}
        QPushButton#AttachBtn:hover {{
            background-color: {BG_ELEVATED};
            border: 1px solid {ACCENT};
        }}
        QCheckBox {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 500;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid {BONE_MUTED};
            background-color: {BG_DEEP};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {ACCENT_HOVER};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1px solid {ACCENT_HOVER};
        }}
        QPushButton:disabled {{
            background-color: {BG_ELEVATED};
            color: {TEXT_HINT};
        }}
        QTabBar {{
            background: transparent;
        }}
        QTabWidget#MainTabs {{
            background: transparent;
            border: none;
        }}
        QTabWidget#MainTabs::pane {{
            border: 1px solid {BORDER};
            background: {GRAD_PANE};
            top: -1px;
            padding: 8px;
            border-top-left-radius: 0;
            border-top-right-radius: 8px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        QTabWidget#MainTabs QTabBar::tab {{
            background: {GRAD_TAB_IDLE};
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER};
            border-bottom: none;
            padding: 11px 20px;
            margin-right: 6px;
            margin-top: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: 13px;
        }}
        QTabWidget#MainTabs QTabBar::tab:selected {{
            background: {GRAD_TAB_SELECTED};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-top: 2px solid {ACCENT};
            border-bottom: 1px solid {BG_PANEL};
            margin-bottom: -1px;
        }}
        QTabWidget#MainTabs QTabBar::tab:hover:!selected {{
            color: {TEXT_PRIMARY};
            background: {GRAD_TAB_HOVER};
            border: 1px solid {BORDER};
            border-bottom: none;
            border-top: 2px solid {ACCENT_DIM};
        }}
    """


def installer_stylesheet() -> str:
    fields = input_field_css()
    return f"""
        QMainWindow, QDialog {{
            color: {TEXT_PRIMARY};
            background: {GRAD_SHELL};
        }}
        QWidget {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', -apple-system, 'SF Pro Display', 'Inter', system-ui, sans-serif;
            font-size: 13.5px;
        }}
        QLabel {{
            color: {TEXT_PRIMARY};
            background: transparent;
        }}
        QFrame#Sidebar, QFrame#InstallerSidebar {{
            background: {GRAD_SIDEBAR};
            border: none;
            border-right: 1px solid {BORDER};
        }}
        QFrame#InstallerContent {{
            background: {GRAD_SHELL};
            border: none;
        }}
        QFrame#InstallerContent QStackedWidget {{
            background: transparent;
        }}
        QFrame#Card {{
            background: {GRAD_PANE};
            border: 1px solid {BORDER_MUTED};
            border-radius: 8px;
        }}
        {fields}
        QTextEdit {{
            font-family: Consolas, monospace;
            font-size: 12px;
        }}
        QPushButton {{
            background-color: {BTN_SECONDARY_BG};
            color: {TEXT_PRIMARY};
            border: 1px solid {BTN_SECONDARY_BORDER};
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 600;
            min-width: 0;
        }}
        QPushButton:hover {{
            background-color: {BURNT_IRON_LIGHT};
            border: 1px solid {ACCENT};
            color: {TEXT_PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER_MUTED};
            color: {TEXT_HINT};
        }}
        QPushButton#PrimaryBtn {{
            background: {GRAD_BTN};
            border: 1px solid {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
            font-weight: bold;
        }}
        QPushButton#PrimaryBtn:hover, QPushButton#LaunchBtn:hover {{
            background: {GRAD_BTN_HOVER};
            border: 1px solid {ACCENT_HOVER};
        }}
        QPushButton#LaunchBtn {{
            background: {GRAD_BTN};
            border: 1px solid {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
            font-weight: bold;
            padding: 14px 20px;
            text-align: left;
            border-radius: 8px;
        }}
        QPushButton#ReinstallBtn {{
            background-color: {BG_PANEL};
            border: 1px solid {BORDER};
            color: {TEXT_PRIMARY};
            font-weight: bold;
        }}
        QPushButton#ReinstallBtn:hover {{
            background-color: {BG_ELEVATED};
            border: 1px solid {ACCENT};
        }}
        QProgressBar {{
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER};
            border-radius: 6px;
            text-align: center;
            color: {TEXT_PRIMARY};
            height: 22px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_DIM}, stop:0.5 {ACCENT}, stop:1 {ACCENT_HOVER});
            border-radius: 5px;
        }}
        QCheckBox {{
            color: {TEXT_SECONDARY};
            spacing: 8px;
            font-size: 13px;
            background: transparent;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {BONE_MUTED};
            background-color: {BG_DEEP};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {ACCENT_HOVER};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1px solid {ACCENT_HOVER};
        }}
        QMessageBox {{
            background: {BG_CHROME};
            color: {TEXT_PRIMARY};
        }}
        QMessageBox QLabel {{
            color: {TEXT_PRIMARY};
        }}
    """
