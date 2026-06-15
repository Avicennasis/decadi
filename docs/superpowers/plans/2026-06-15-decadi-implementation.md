# Décadi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GNOME system tray indicator that displays French Revolutionary decimal time, with a click menu showing standard time, Revolutionary calendar date, and a seconds toggle.

**Architecture:** Single Python script (`decadi.py`) using AyatanaAppIndicator3 for the tray label and GTK3 for the click menu. A one-shot GLib timer fires every ~864ms (one decimal second), self-correcting from wall-clock time. DBus session bus handles single-instance enforcement. All logic lives in one file — no modules, no packages.

**Tech Stack:** Python 3.12+, AyatanaAppIndicator3, GTK3 (via PyGObject/gi.repository), GLib, DBus (via Gio)

---

## File Map

| File | Responsibility |
|------|---------------|
| `decadi.py` | Main script — decimal time conversion, Revolutionary calendar, AppIndicator, menu, timer, DBus single-instance, signal handling |
| `assets/transparent.png` | 22×22 transparent dummy icon for AppIndicator |
| `decadi.desktop` | XDG autostart desktop entry |
| `tests/test_decimal_time.py` | Unit tests for decimal time conversion |
| `tests/test_republican_calendar.py` | Unit tests for Revolutionary calendar conversion |
| `tests/test_roman_numerals.py` | Unit tests for Roman numeral conversion |
| `LICENSE` | MIT license |
| `README.md` | Usage and install instructions |

---

### Task 1: Project scaffolding and transparent icon

**Files:**
- Create: `assets/transparent.png`
- Create: `LICENSE`
- Create: `decadi.py` (empty shebang + docstring)

- [ ] **Step 1: Create the transparent icon**

```bash
mkdir -p assets
python3 -c "
from PIL import Image
img = Image.new('RGBA', (22, 22), (0, 0, 0, 0))
img.save('assets/transparent.png')
"
```

If Pillow is not installed, use ImageMagick instead:

```bash
mkdir -p assets
convert -size 22x22 xc:transparent assets/transparent.png
```

Verify: `file assets/transparent.png` should show `PNG image data, 22 x 22`.

- [ ] **Step 2: Create the MIT license**

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Léon Simmons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

- [ ] **Step 3: Create the script stub**

```python
#!/usr/bin/env python3
"""Décadi — French Revolutionary decimal time indicator for the GNOME system tray."""
```

- [ ] **Step 4: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 5: Make the script executable**

```bash
chmod +x decadi.py
```

- [ ] **Step 6: Commit**

```bash
git add assets/transparent.png LICENSE decadi.py .gitignore
git commit -m "chore: scaffold project with transparent icon and license"
```

---

### Task 2: Decimal time conversion with tests (TDD)

**Files:**
- Create: `tests/test_decimal_time.py`
- Modify: `decadi.py`

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_decimal_time.py -v`
Expected: FAIL with `ImportError: cannot import name 'decimal_time'`

- [ ] **Step 3: Implement decimal_time and format_decimal_time**

Add to `decadi.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_decimal_time.py -v`
Expected: All 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add decadi.py tests/test_decimal_time.py
git commit -m "feat: decimal time conversion with tests"
```

---

### Task 3: Roman numeral conversion with tests (TDD)

**Files:**
- Create: `tests/test_roman_numerals.py`
- Modify: `decadi.py`

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_roman_numerals.py -v`
Expected: FAIL with `ImportError: cannot import name 'to_roman'`

- [ ] **Step 3: Implement to_roman**

Add to `decadi.py` after the existing functions:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_roman_numerals.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add decadi.py tests/test_roman_numerals.py
git commit -m "feat: Roman numeral conversion with tests"
```

---

### Task 4: Revolutionary calendar conversion with tests (TDD)

**Files:**
- Create: `tests/test_republican_calendar.py`
- Modify: `decadi.py`

- [ ] **Step 1: Write the failing tests**

```python
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
        # September 22, 1792 = 1 Vendémiaire I
        result = republican_date(date(1792, 9, 22))
        assert result == "1 Vendémiaire I"

    def test_known_date_2026(self):
        # June 15, 2026: Republican year starts Sept 22, 2025 = Year CCXXXIV
        # Days from Sept 22, 2025 to June 15, 2026 = 266 days
        # 266 / 30 = month 8 (0-indexed) = 9th month = Prairial, day 27
        result = republican_date(date(2026, 6, 15))
        assert result == "27 Prairial CCXXXIV"

    def test_pre_epoch(self):
        result = republican_date(date(1789, 7, 14))
        assert result == "(pre-epoch)"

    def test_new_year(self):
        # Sept 22, 2025 = 1 Vendémiaire CCXXXIV
        result = republican_date(date(2025, 9, 22))
        assert result == "1 Vendémiaire CCXXXIV"

    def test_last_day_of_year(self):
        # Sept 21, 2026 should be the last day of Year CCXXXIV
        # Either 30 Fructidor or a Sansculottide
        result = republican_date(date(2026, 9, 21))
        # Day 365 of year CCXXXIV (non-leap): 360 regular days + 5 sansculottides
        # Day 365 = 5th sansculottide = "Jour des Récompenses"
        assert result == "Jour des Récompenses CCXXXIV"

    def test_sansculottide_first(self):
        # The 361st day of a republican year is the 1st complementary day
        # Sept 17, 2026 = day 361 of Year CCXXXIV
        result = republican_date(date(2026, 9, 17))
        assert result == "Jour de la Vertu CCXXXIV"

    def test_leap_year_6th_sansculottide(self):
        # Republican Year IV is a leap year (4 % 4 == 0)
        # Sept 21, 1796 = day 365 of Year IV → 6th sansculottide
        result = republican_date(date(1796, 9, 21))
        assert result == "Jour de la Révolution IV"

    def test_month_names_order(self):
        # Oct 22, 2025 = 1 Brumaire CCXXXIV (2nd month)
        result = republican_date(date(2025, 10, 22))
        assert result == "1 Brumaire CCXXXIV"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_republican_calendar.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement is_republican_leap_year and republican_date**

Add to `decadi.py` (the `from datetime` import goes at the top of the file, below the existing imports):

```python
from datetime import date, datetime

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_republican_calendar.py -v`
Expected: All tests PASS

If any assertions fail, debug the implementation against an authoritative Republican calendar reference — do not adjust test expectations to match the implementation.

- [ ] **Step 5: Run the full test suite**

Run: `python3 -m pytest tests/ -v`
Expected: All tests across all 3 test files PASS

- [ ] **Step 6: Commit**

```bash
git add decadi.py tests/test_republican_calendar.py
git commit -m "feat: Republican calendar conversion with tests"
```

---

### Task 5: AppIndicator, menu, and timer (GUI integration)

**Files:**
- Modify: `decadi.py`

This task adds the GTK/AppIndicator GUI layer. These components require a running display server and cannot be unit-tested headlessly, so they are tested manually.

- [ ] **Step 1: Add dependency check and imports at top of decadi.py**

Add these imports to the top of `decadi.py`, **below** the existing `from datetime import date, datetime` line. The GUI imports are placed inside `main()` (see Step 3) so that headless test runs can still import the pure-Python functions without requiring GTK.

```python
import os
import signal
import sys
```

- [ ] **Step 2: Add the DecadiIndicator class**

Add after the `republican_date` function:

```python
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
```

- [ ] **Step 3: Add the main function with DBus single-instance and signal handling**

Add at the end of `decadi.py`:

```python
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
```

- [ ] **Step 4: Test manually**

Run: `python3 decadi.py`

Verify:
1. A tray indicator appears showing decimal time with the ⑩ prefix
2. Time updates every ~0.864 seconds
3. Clicking shows the menu with decimal time, standard time, Revolutionary date
4. "Show seconds" toggle works — unchecking removes seconds from both tray and menu
5. "Quit" exits the app
6. Running a second `python3 decadi.py` exits silently without creating a duplicate icon
7. `kill -TERM <pid>` cleanly removes the indicator

- [ ] **Step 5: Run the full test suite to verify nothing broke**

Run: `python3 -m pytest tests/ -v`
Expected: All existing tests still PASS (GUI imports are inside `main()`, so pure-Python functions remain importable without GTK)

- [ ] **Step 6: Commit**

```bash
git add decadi.py
git commit -m "feat: AppIndicator GUI with menu, timer, DBus single-instance"
```

---

### Task 6: Desktop entry and README

**Files:**
- Create: `decadi.desktop`
- Create: `README.md`

- [ ] **Step 1: Create the desktop entry**

```ini
[Desktop Entry]
Type=Application
Name=Décadi
Comment=French Revolutionary decimal time indicator
Exec=python3 /home/avicennasis/github/avic/decadi/decadi.py
Icon=/home/avicennasis/github/avic/decadi/assets/transparent.png
Terminal=false
Categories=Utility;Clock;
StartupNotify=false
X-GNOME-Autostart-enabled=true
```

Note: `Exec` and `Icon` use absolute paths. Users who clone to a different location must update these paths.

- [ ] **Step 2: Create the README**

```markdown
# Décadi

French Revolutionary decimal time indicator for the GNOME system tray.

Displays the current time in the [French decimal time](https://en.wikipedia.org/wiki/Decimal_time#France) system — 10 hours per day, 100 minutes per hour, 100 seconds per minute. Click the indicator to see standard time, the Revolutionary calendar date, and toggle the seconds display.

## Requirements

- Ubuntu with GNOME Shell (tested on 46+, Wayland)
- GNOME Shell AppIndicator extension enabled (`gnome-shell-extension-appindicator`)
- Python 3.12+
- System packages (pre-installed on Ubuntu desktop):
  - `python3-gi`
  - `gir1.2-ayatanaappindicator3-0.1`

## Install

Clone the repo and symlink the autostart entry:

    git clone https://github.com/Avicennasis/decadi.git ~/github/avic/decadi
    ln -s ~/github/avic/decadi/decadi.desktop ~/.config/autostart/decadi.desktop

The indicator starts automatically on your next login. To start it now:

    python3 ~/github/avic/decadi/decadi.py &

## Usage

The indicator shows decimal time in the system tray: `⑩ 7:54:32`

Click it to see:
- Decimal time (updates live)
- Standard 24-hour time (updates live)
- French Revolutionary calendar date
- Toggle seconds on/off
- Quit

## License

MIT
```

- [ ] **Step 3: Commit**

```bash
git add decadi.desktop README.md
git commit -m "docs: add desktop entry and README"
```

---

### Task 7: Install autostart and final verification

**Files:**
- No new files

- [ ] **Step 1: Symlink the desktop entry**

```bash
ln -sf /home/avicennasis/github/avic/decadi/decadi.desktop ~/.config/autostart/decadi.desktop
```

- [ ] **Step 2: Kill any running instance and restart**

```bash
pkill -f "python3.*decadi.py" 2>/dev/null; sleep 1
python3 /home/avicennasis/github/avic/decadi/decadi.py &
```

- [ ] **Step 3: Full verification checklist**

Verify all of the following:

1. ☐ Tray indicator shows `⑩ H:MM:SS` and ticks every ~0.864s
2. ☐ Click menu opens with decimal time, standard time, Revolutionary date
3. ☐ "Show seconds" toggle removes/restores seconds in tray AND menu
4. ☐ Revolutionary date looks correct (verify against an online converter)
5. ☐ Second instance exits silently (run `python3 decadi.py` again)
6. ☐ `kill -TERM` cleanly removes the indicator
7. ☐ Full test suite passes: `python3 -m pytest tests/ -v`

- [ ] **Step 4: Run the full test suite one final time**

Run: `python3 -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Final commit if any adjustments were made**

```bash
git add -A
git commit -m "chore: final adjustments from verification"
```

Only create this commit if there were changes. Skip if working tree is clean.
