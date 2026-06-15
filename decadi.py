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