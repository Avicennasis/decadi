#!/usr/bin/env python3
"""Décadi — French Revolutionary decimal time indicator for the GNOME system tray."""

from datetime import date, datetime
import os
import signal
import sys

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


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ICON_PATH = os.path.join(SCRIPT_DIR, "assets", "transparent.png")
DBUS_NAME = "systems.simmons.Decadi"
MAX_TICK_DELAY_MS = 5000


class DecadiIndicator:
    def __init__(self, AyatanaAppIndicator3, GLib, Gtk):
        self.show_seconds = True
        self._cached_date_str = ""
        self._cached_date_key = None
        self._GLib = GLib
        self._Gtk = Gtk

        icon = ICON_PATH if os.path.isfile(ICON_PATH) else "image-missing"
        self.indicator = AyatanaAppIndicator3.Indicator.new(
            "decadi",
            icon,
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)

        self._build_menu()
        self._tick()

    def _build_menu(self):
        Gtk = self._Gtk
        menu = Gtk.Menu()

        self.menu_decimal = Gtk.MenuItem(label="")
        self.menu_decimal.set_sensitive(False)
        menu.append(self.menu_decimal)

        self.menu_standard = Gtk.MenuItem(label="")
        self.menu_standard.set_sensitive(False)
        menu.append(self.menu_standard)

        menu.append(Gtk.SeparatorMenuItem())

        self.menu_revdate = Gtk.MenuItem(label="")
        self.menu_revdate.set_sensitive(False)
        menu.append(self.menu_revdate)

        menu.append(Gtk.SeparatorMenuItem())

        seconds_item = Gtk.CheckMenuItem(label="Show seconds")
        seconds_item.set_active(True)
        seconds_item.connect("toggled", self._on_toggle_seconds)
        menu.append(seconds_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: Gtk.main_quit())
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

    def _on_toggle_seconds(self, item):
        self.show_seconds = item.get_active()
        self._update_display(datetime.now())

    def _tick(self):
        now = datetime.now()
        try:
            self._update_display(now)
        except Exception:
            import traceback; traceback.print_exc()
        total_sec = now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1_000_000
        current_dec_sec = total_sec * 100_000 / 86_400
        next_dec_sec = int(current_dec_sec) + 1
        next_real_sec = next_dec_sec * 86_400 / 100_000
        delay_ms = max(50, min(MAX_TICK_DELAY_MS, int((next_real_sec - total_sec) * 1000)))
        self._GLib.timeout_add(delay_ms, self._tick)
        return False  # one-shot

    def _update_display(self, now):
        dec_h, dec_m, dec_s = decimal_time(now.hour, now.minute, now.second, now.microsecond)

        self.indicator.set_label(
            format_decimal_time(dec_h, dec_m, dec_s, self.show_seconds), ""
        )

        if self.show_seconds:
            self.menu_decimal.set_label(f"Decimal: {dec_h}:{dec_m:02d}:{dec_s:02d}")
        else:
            self.menu_decimal.set_label(f"Decimal: {dec_h}:{dec_m:02d}")

        self.menu_standard.set_label(f"Standard: {now.strftime('%H:%M:%S')}")

        today = now.date()
        if today != self._cached_date_key:
            self._cached_date_key = today
            self._cached_date_str = republican_date(today)
        self.menu_revdate.set_label(self._cached_date_str)


def main():
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import AyatanaAppIndicator3, GLib, Gtk, Gio
    except (ImportError, ValueError) as e:
        print(f"Error: missing system package: {e}", file=sys.stderr)
        print("Install: sudo apt install python3-gi gir1.2-ayatanaappindicator3-0.1", file=sys.stderr)
        sys.exit(1)

    bus = Gio.bus_get_sync(Gio.BusType.SESSION)
    flags = Gio.BusNameOwnerFlags.DO_NOT_QUEUE
    owner_id = Gio.bus_own_name_on_connection(
        bus, DBUS_NAME, flags, None, None,
    )

    # Flush to ensure the name request is processed, then check ownership
    bus.flush_sync()
    try:
        variant = bus.call_sync(
            "org.freedesktop.DBus", "/org/freedesktop/DBus",
            "org.freedesktop.DBus", "GetNameOwner",
            GLib.Variant("(s)", (DBUS_NAME,)),
            GLib.VariantType("(s)"),
            Gio.DBusCallFlags.NONE, -1, None,
        )
        owner = variant.get_child_value(0).get_string()
        if owner != bus.get_unique_name():
            sys.exit(0)
    except Exception:
        pass  # If DBus check fails, proceed (single-instance is best-effort)

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)

    indicator = DecadiIndicator(AyatanaAppIndicator3, GLib, Gtk)
    Gtk.main()


if __name__ == "__main__":
    main()