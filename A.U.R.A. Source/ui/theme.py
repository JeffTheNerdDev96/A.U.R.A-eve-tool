"""
Angel Cartel UI theme — blackened metal, burnt iron, bone ivory, oxide red accents.
Single source of truth for A.U.R.A. desktop styling.
"""
from __future__ import annotations

import os
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

# Semantic (intel / map — gameplay signals, not faction chrome)
THREAT_CRITICAL = "#f43f5e"
THREAT_HIGH = "#fb923c"
THREAT_MEDIUM = "#facc15"
THREAT_INFO = "#38bdf8"
THREAT_CLEAR = "#34d399"
STATUS_ONLINE = "#34d399"
STATUS_STANDBY_BG = BURNT_IRON
STATUS_STANDBY_BORDER = BURNT_IRON_BORDER

BTN_TEXT_ON_ACCENT = BONE_WHITE

FONT_DISPLAY = "'Orbitron', 'Segoe UI', sans-serif"
_DISPLAY_FONT_LOADED = False
_DISPLAY_FONT_FAMILY = "Orbitron"


def _fonts_dir() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(this_dir, "assets", "fonts"),
        os.path.join(this_dir, "..", "assets", "fonts"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)
    return os.path.abspath(candidates[1])


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


def threat_colors() -> Dict[str, str]:
    return {
        "CRITICAL": THREAT_CRITICAL,
        "HIGH": THREAT_HIGH,
        "MEDIUM": THREAT_MEDIUM,
        "INFO": THREAT_INFO,
        "LOW": THREAT_INFO,
        "CLEAR": THREAT_CLEAR,
    }


def btn_secondary_css() -> str:
    return (
        f"QPushButton {{ background:{BTN_SECONDARY_BG}; color:{TEXT_PRIMARY}; "
        f"border:1px solid {BTN_SECONDARY_BORDER}; border-radius:2px; "
        f"padding:5px 12px; font-size:12px; }}"
        f"QPushButton:hover {{ background:{BURNT_IRON_LIGHT}; border:1px solid {ACCENT}; }}"
    )


def chrome_action_btn_css() -> str:
    return (
        f"font-family: {FONT_DISPLAY}; color: {TEXT_PRIMARY}; "
        f"background: {BTN_SECONDARY_BG}; border: 1px solid {BTN_SECONDARY_BORDER}; "
        f"border-radius: 6px; padding: 6px 14px; font-size: 13px; font-weight: bold;"
        f"QPushButton:hover {{ background: {BURNT_IRON_LIGHT}; border: 1px solid {ACCENT}; }}"
    )


def tier_badge_font_css() -> str:
    return f"font-family: {FONT_DISPLAY};"


def dialog_stylesheet() -> str:
    return f"""
        QDialog {{
            background-color: {BG_CHROME};
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        QTextEdit, QTextBrowser {{
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {TEXT_PRIMARY};
            padding: 8px;
            font-size: 13px;
            selection-background-color: {ACCENT_DIM};
        }}
        QComboBox {{
            background-color: {BG_ELEVATED};
            border: 1px solid {BORDER};
            border-radius: 4px;
            color: {TEXT_PRIMARY};
            padding: 4px 8px;
        }}
        QPushButton {{
            background-color: {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
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
    return f"""
        QMainWindow {{
            background-color: {BG_DEEP};
        }}
        QWidget {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', -apple-system, 'SF Pro Display', 'Inter', system-ui, sans-serif;
            font-size: 14px;
        }}
        QFrame#AppShell {{
            background-color: {BG_DEEP};
            border: 1px solid {BORDER};
            border-radius: 0;
        }}
        QFrame#BrowserChrome {{
            background-color: {BG_TITLEBAR};
            border: none;
            padding: 6px 12px;
        }}
        QFrame#BrowserFooter {{
            background-color: {BG_TITLEBAR};
            border: none;
            border-top: 2px solid {ACCENT};
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
            border: 1px solid {BORDER};
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
            background-color: {BG_PANEL};
            border: none;
            border-radius: 0;
            padding: 12px;
        }}
        QFrame#TabCard {{
            background: {BG_PANEL};
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
            background: transparent;
            width: 7px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {BTN_SECONDARY_BORDER};
            min-height: 24px;
            border-radius: 3px;
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
            background-color: {ACCENT};
            color: {BTN_TEXT_ON_ACCENT};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13.5px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
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
        QTabWidget::pane {{
            border: 1px solid {BORDER};
            background: {BG_DEEP};
            top: -1px;
            border-radius: 0;
            padding: 8px;
        }}
        QTabBar::tab {{
            background: {BG_CHROME};
            color: {TEXT_HINT};
            border: 1px solid {BORDER};
            border-bottom: none;
            border-top: 2px solid {BORDER};
            padding: 10px 18px;
            margin-right: 8px;
            margin-top: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: 13px;
        }}
        QTabBar::tab:selected {{
            background: {BG_PANEL};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-top: 2px solid {ACCENT};
            border-bottom: 1px solid {BG_PANEL};
            margin-bottom: -1px;
        }}
        QTabBar::tab:hover:!selected {{
            color: {TEXT_SECONDARY};
            background: {BURNT_IRON};
        }}
        QSpinBox {{
            background: {BG_INPUT};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_MUTED};
            border-radius: 4px;
            padding: 2px 6px;
            min-width: 52px;
        }}
        QScrollBar:vertical {{
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
        }}
    """
