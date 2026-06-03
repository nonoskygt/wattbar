"""Tests de los helpers de formato (puros)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wattbar.ui.theme import fmt_watts, fmt_pct, is_high


def test_fmt_watts_none():
    assert fmt_watts(None) == "--"


def test_fmt_watts_small_has_decimal():
    assert fmt_watts(2.82) == "2.8W"


def test_fmt_watts_large_is_integer():
    assert fmt_watts(60.394) == "60W"
    assert fmt_watts(75.097) == "75W"


def test_fmt_watts_negative_clamped():
    assert fmt_watts(-5) == "0.0W"


def test_fmt_pct():
    assert fmt_pct(None) == "--"
    assert fmt_pct(46.0) == "46%"
    assert fmt_pct(99.6) == "100%"


def test_is_high():
    assert is_high(90) is True
    assert is_high(85) is True
    assert is_high(84.9) is False
    assert is_high(None) is False
