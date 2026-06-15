# tests/test_republican_calendar.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from decadi import republican_date, is_republican_leap_year


class TestIsRepublicanLeapYear:
    def test_year_4_is_leap(self):
        assert is_republican_leap_year(4) is True

    def test_year_100_is_not_leap(self):
        assert is_republican_leap_year(100) is False

    def test_year_400_is_leap(self):
        assert is_republican_leap_year(400) is True

    def test_year_1_is_not_leap(self):
        assert is_republican_leap_year(1) is False

    def test_year_8_is_leap(self):
        assert is_republican_leap_year(8) is True


class TestRepublicanDate:
    def test_epoch_day(self):
        result = republican_date(date(1792, 9, 22))
        assert result == "1 Vendémiaire I"

    def test_known_date_2026(self):
        # June 15, 2026: Year CCXXXIV starts Sept 22, 2025
        # Days from Sept 22 to June 15 = 266 days (0-indexed)
        # 266 // 30 = month 8 (Prairial), 266 % 30 + 1 = day 27
        result = republican_date(date(2026, 6, 15))
        assert result == "27 Prairial CCXXXIV"

    def test_pre_epoch(self):
        result = republican_date(date(1789, 7, 14))
        assert result == "(pre-epoch)"

    def test_new_year(self):
        result = republican_date(date(2025, 9, 22))
        assert result == "1 Vendémiaire CCXXXIV"

    def test_last_day_of_year(self):
        # Day 364 (0-indexed) of non-leap Year CCXXXIV = 5th sansculottide
        result = republican_date(date(2026, 9, 21))
        assert result == "Jour des Récompenses CCXXXIV"

    def test_sansculottide_first(self):
        # Day 360 (0-indexed) = 1st complementary day
        result = republican_date(date(2026, 9, 17))
        assert result == "Jour de la Vertu CCXXXIV"

    def test_leap_year_6th_sansculottide(self):
        # Republican Year IV is a leap year (4 % 4 == 0)
        # Sept 21, 1796 = day 365 of Year IV → 6th sansculottide
        result = republican_date(date(1796, 9, 21))
        assert result == "Jour de la Révolution IV"

    def test_month_names_order(self):
        result = republican_date(date(2025, 10, 22))
        assert result == "1 Brumaire CCXXXIV"
