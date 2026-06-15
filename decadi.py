#!/usr/bin/env python3
"""Décadi — French Revolutionary decimal time indicator for the GNOME system tray."""

from datetime import date, datetime

PREFIX = "⑩"


def decimal_time(hour, minute, second, microsecond):
    """Convert wall-clock time components to French decimal time (h, m, s)."""
    total_seconds = hour * 3600 + minute * 60 + second + microsecond / 1_000_000
    decimal_total = total_seconds * 100_000 / 86_400
    dec_h = int(decimal_total // 10_000)
    dec_m = int((decimal_total % 10_000) // 100)
    dec_s = int(decimal_total % 100)
    return dec_h, dec_m, dec_s


def format_decimal_time(dec_h, dec_m, dec_s, show_seconds=True):
    """Format decimal time for tray display."""
    if show_seconds:
        return f"{PREFIX} {dec_h}:{dec_m:02d}:{dec_s:02d}"
    return f"{PREFIX} {dec_h}:{dec_m:02d}"


def to_roman(num):
    """Convert integer to Roman numeral string. Returns '' for values <= 0."""
    if num <= 0:
        return ""
    result = []
    for value, numeral in (
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ):
        while num >= value:
            result.append(numeral)
            num -= value
    return "".join(result)


REPUBLICAN_EPOCH = date(1792, 9, 22)

REPUBLICAN_MONTHS = [
    "Vendémiaire", "Brumaire", "Frimaire",
    "Nivôse", "Pluviôse", "Ventôse",
    "Germinal", "Floréal", "Prairial",
    "Messidor", "Thermidor", "Fructidor",
]

SANSCULOTTIDES = [
    "Jour de la Vertu",
    "Jour du Génie",
    "Jour du Travail",
    "Jour de l'Opinion",
    "Jour des Récompenses",
    "Jour de la Révolution",
]


def is_republican_leap_year(year):
    """Check if a Republican year is a leap year using the Romme convention."""
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def republican_date(today):
    """Convert a Gregorian date to a Republican calendar date string."""
    if today < REPUBLICAN_EPOCH:
        return "(pre-epoch)"

    delta_days = (today - REPUBLICAN_EPOCH).days

    year = 1
    while True:
        days_in_year = 366 if is_republican_leap_year(year) else 365
        if delta_days < days_in_year:
            break
        delta_days -= days_in_year
        year += 1

    day_of_year = delta_days  # 0-indexed

    if day_of_year < 360:
        month_index = day_of_year // 30
        day_of_month = (day_of_year % 30) + 1
        return f"{day_of_month} {REPUBLICAN_MONTHS[month_index]} {to_roman(year)}"

    sansculottide_index = day_of_year - 360
    return f"{SANSCULOTTIDES[sansculottide_index]} {to_roman(year)}"