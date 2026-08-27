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
Input sanitization helpers for untrusted text (chat, EVE logs, attachments, paste).
"""
from __future__ import annotations

import html
import os
import re

# Default caps (overridden by config at runtime where applicable)
MAX_CHAT_CHARS = 16_000
MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024
MAX_LOG_READ_BYTES = 512 * 1024
MAX_LLM_CONTEXT_CHARS = 24_000
MAX_LINE_CHARS = 8_192
MAX_IMAGE_PIXELS = 25_000_000
MAX_PDF_PAGES = 200
MAX_DOCX_PARAGRAPHS = 2_000

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def escape_html(text: str) -> str:
    """Escape text for safe insertion into Qt rich-text HTML."""
    if not text:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return html.escape(normalized, quote=True)


def strip_control_chars(text: str) -> str:
    """Remove C0 control characters except newline and tab."""
    if not text:
        return ""
    return _CONTROL_RE.sub("", text)


def clamp_text(text: str, max_chars: int, suffix: str = "…") -> str:
    """Truncate text to max_chars, appending suffix when clipped."""
    if max_chars <= 0:
        return ""
    if not text or len(text) <= max_chars:
        return text
    if len(suffix) >= max_chars:
        return text[:max_chars]
    return text[: max_chars - len(suffix)] + suffix


def safe_display_text(text: str, max_chars: int = MAX_CHAT_CHARS) -> str:
    """Plain display string: strip controls and clamp length."""
    return clamp_text(strip_control_chars(text or ""), max_chars)


def is_path_under(base: str, path: str) -> bool:
    """True when path resolves to a location under base (symlink-safe)."""
    if not base or not path:
        return False
    try:
        base_real = os.path.realpath(os.path.abspath(base))
        path_real = os.path.realpath(os.path.abspath(path))
        common = os.path.commonpath([base_real, path_real])
        return common == base_real
    except (OSError, ValueError):
        return False


def is_safe_log_file(base_dir: str, filepath: str) -> bool:
    """Regular file under base_dir (not a symlink)."""
    if not is_path_under(base_dir, filepath):
        return False
    try:
        if not os.path.isfile(filepath):
            return False
        if os.path.islink(filepath):
            return False
        return True
    except OSError:
        return False


def wrap_untrusted(label: str, content: str, max_chars: int | None = None) -> str:
    """Delimit untrusted content for LLM prompts."""
    body = strip_control_chars(content or "")
    if max_chars is not None:
        body = clamp_text(body, max_chars)
    return f"[{label}]\n{body}\n[/{label}]"
