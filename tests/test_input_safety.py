"""Unit tests for input_safety sanitization helpers."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "A.U.R.A. Source"))

from input_safety import (  # noqa: E402
    clamp_text,
    escape_html,
    is_path_under,
    safe_display_text,
    strip_control_chars,
    wrap_untrusted,
)


class TestEscapeHtml(unittest.TestCase):
    def test_escapes_tags_and_quotes(self):
        raw = '<div onclick="x">file://secret & "quote"</div>'
        out = escape_html(raw)
        self.assertNotIn("<div", out)
        self.assertIn("&lt;div", out)
        self.assertIn("&amp;", out)
        self.assertIn("&quot;", out)

    def test_normalizes_line_endings(self):
        self.assertEqual(escape_html("a\r\nb"), "a\nb")


class TestClampText(unittest.TestCase):
    def test_truncates_with_suffix(self):
        self.assertEqual(clamp_text("abcdef", 4), "abc…")

    def test_no_change_when_short(self):
        self.assertEqual(clamp_text("hi", 10), "hi")


class TestStripControlChars(unittest.TestCase):
    def test_keeps_newline_tab(self):
        self.assertEqual(strip_control_chars("a\n\tb\x07c"), "a\n\tbc")


class TestSafeDisplayText(unittest.TestCase):
    def test_strips_and_clamps(self):
        self.assertEqual(safe_display_text("  ok  ", 10), "  ok  ")


class TestWrapUntrusted(unittest.TestCase):
    def test_delimiters(self):
        block = wrap_untrusted("UNTRUSTED_USER_QUERY", "hello")
        self.assertIn("[UNTRUSTED_USER_QUERY]", block)
        self.assertIn("[/UNTRUSTED_USER_QUERY]", block)


class TestIsPathUnder(unittest.TestCase):
    def test_child_path(self):
        with tempfile.TemporaryDirectory() as base:
            child = os.path.join(base, "logs", "chat.txt")
            os.makedirs(os.path.dirname(child), exist_ok=True)
            with open(child, "w", encoding="utf-8") as fh:
                fh.write("test")
            self.assertTrue(is_path_under(base, child))

    def test_outside_path(self):
        with tempfile.TemporaryDirectory() as base:
            with tempfile.TemporaryDirectory() as other:
                self.assertFalse(is_path_under(base, other))


if __name__ == "__main__":
    unittest.main()
