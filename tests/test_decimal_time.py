# tests/test_decimal_time.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decadi import decimal_time, format_decimal_time


class TestDecimalTime:
    def test_midnight(self):
        h, m, s = decimal_time(0, 0, 0, 0)
        assert (h, m, s) == (0, 0, 0)

    def test_noon(self):
        h, m, s = decimal_time(12, 0, 0, 0)
        assert (h, m, s) == (5, 0, 0)

    def test_end_of_day(self):
        # 86399 * 100000 / 86400 = 99998.84 → (9, 99, 98)
        h, m, s = decimal_time(23, 59, 59, 0)
        assert (h, m, s) == (9, 99, 98)

    def test_last_microsecond(self):
        h, m, s = decimal_time(23, 59, 59, 999999)
        assert (h, m, s) == (9, 99, 99)

    def test_known_conversion(self):
        # 18:06:14 = 65174 seconds → 65174 * 100000 / 86400 = 75432.87
        h, m, s = decimal_time(18, 6, 14, 0)
        assert (h, m, s) == (7, 54, 32)

    def test_morning(self):
        # 06:00:00 = 21600 seconds → 21600 * 100000 / 86400 = 25000
        h, m, s = decimal_time(6, 0, 0, 0)
        assert (h, m, s) == (2, 50, 0)


class TestFormatDecimalTime:
    def test_with_seconds(self):
        result = format_decimal_time(7, 54, 32, show_seconds=True)
        assert result == "⑩ 7:54:32"

    def test_without_seconds(self):
        result = format_decimal_time(7, 54, 32, show_seconds=False)
        assert result == "⑩ 7:54"

    def test_zero_padding(self):
        result = format_decimal_time(0, 0, 0, show_seconds=True)
        assert result == "⑩ 0:00:00"

    def test_zero_padding_minutes_only(self):
        result = format_decimal_time(0, 5, 3, show_seconds=True)
        assert result == "⑩ 0:05:03"