#!/usr/bin/env python3
"""Décadi — French Revolutionary decimal time indicator for the GNOME system tray."""

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