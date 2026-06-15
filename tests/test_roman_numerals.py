# tests/test_roman_numerals.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decadi import to_roman


class TestToRoman:
    def test_one(self):
        assert to_roman(1) == "I"

    def test_four(self):
        assert to_roman(4) == "IV"

    def test_nine(self):
        assert to_roman(9) == "IX"

    def test_forty_two(self):
        assert to_roman(42) == "XLII"

    def test_current_republican_year(self):
        # 2026 - 1792 = 234
        assert to_roman(234) == "CCXXXIV"

    def test_max_3999(self):
        assert to_roman(3999) == "MMMCMXCIX"

    def test_zero_returns_empty(self):
        assert to_roman(0) == ""

    def test_negative_returns_empty(self):
        assert to_roman(-5) == ""