# Décadi — French Decimal Time Indicator for GNOME

## Overview

A system tray indicator for Ubuntu/GNOME that displays the current time in the French Revolutionary decimal time system (10 hours/day, 100 minutes/hour, 100 seconds/minute). Built as a Python AppIndicator using AyatanaAppIndicator3 + GTK3.

## Target Environment

- Ubuntu with GNOME Shell 46+ on Wayland
- GNOME Shell AppIndicator extension (`gnome-shell-extension-appindicator`) must be enabled for tray indicators to appear
- Python 3.12+
- AyatanaAppIndicator3 (already installed on standard Ubuntu)
- No pip-installable dependencies; requires system packages `python3-gi` and `gir1.2-ayatanaappindicator3-0.1` (pre-installed on standard Ubuntu desktop)

On startup, if AyatanaAppIndicator3 or GTK3 is not importable, the script prints a clear error message naming the missing package and exits with code 1.

## Core: Decimal Time Conversion

Convert standard time to French Revolutionary decimal time:

1. Compute seconds since midnight using wall-clock decomposition (`hour * 3600 + minute * 60 + second + microsecond / 1e6`), which naturally caps at 86400 regardless of DST day length
2. Scale to 100,000 decimal seconds per day: `decimal = seconds_since_midnight * 100000 / 86400`
3. Split into hours (0–9), minutes (0–99), seconds (0–99)

**Timezone and DST:** The conversion uses the local system timezone. During DST transitions, the wall clock may jump forward (spring) or repeat an hour (fall). The app does not attempt to compensate — it simply converts whatever `datetime.now()` returns, which means the decimal clock jumps or repeats in sync with the wall clock. This is the expected behavior for a display-only clock.

The GLib timer fires every ~864ms (one decimal second = 86400/100000 = 0.864 real seconds). The callback self-corrects by recalculating the next tick offset from the current wall clock to prevent drift over time. After system suspend/resume, the callback detects the gap and immediately resynchronizes from the wall clock.

## Tray Indicator

The indicator shows decimal time as a text label in the system tray:

- **Default (seconds on):** `⑩ 7:54:32` — hours unpadded, minutes and seconds zero-padded to two digits
- **Compact (seconds off):** `⑩ 7:54`

The `⑩` (U+2469, circled 10) prefix distinguishes it from the regular clock and references the base-10 system. Font coverage detection is unreliable in tray contexts, so this is hardcoded — if a user's environment can't render it, they can change the prefix in the script.

No custom icon — AppIndicator requires an icon, so a 22×22 transparent PNG is bundled as a dummy (standard indicator icon size, renders correctly on HiDPI). If the icon file is missing at runtime, the script falls back to the stock `image-missing` icon name. Category is `APPLICATION_STATUS`, status is `ACTIVE`.

The script resolves asset paths relative to `__file__` (via `os.path.realpath`) so symlinks and arbitrary working directories work correctly. A single-instance check via DBus well-known name (`systems.simmons.Decadi`) prevents duplicate tray icons. If the name is already owned, the second instance exits silently.

SIGTERM/SIGINT handlers call `Gtk.main_quit()` for clean shutdown during session logout.

## Click Menu

Clicking the indicator opens a GTK menu:

| Item | Type | Content |
|------|------|---------|
| Decimal time | Label | `Decimal: 7:54:32` |
| Standard time | Label | `Standard: 18:06:14` (hardcoded 24-hour format) |
| Separator | — | — |
| Revolutionary date | Label | `14 Prairial CCXXXIV` |
| Separator | — | — |
| Show seconds | CheckMenuItem | Toggle, checked by default. Affects both tray label and menu decimal time. |
| Separator | — | — |
| Quit | MenuItem | Exits the app |

- Decimal and standard time labels update live while the menu is open.
- Revolutionary date is cached and recomputed only when the tick callback detects a calendar-day change.

### Revolutionary Calendar Conversion

The calendar covers:

- 12 months of 30 days each (Vendémiaire through Fructidor)
- 5–6 complementary days (Sansculottides) at year end, named: Jour de la Vertu, du Génie, du Travail, de l'Opinion, des Récompenses, and (leap years only) de la Révolution. Displayed as e.g. `Jour du Travail CCXXXIV`
- Year calculated from the Republican epoch (September 22, 1792): count days from epoch to today, divide into years accounting for leap years, then derive month (1–12) and day (1–30) from day-of-year. Dates before the epoch display `(pre-epoch)` instead of a calendar date
- Year displayed in Roman numerals (standard algorithm, max year 3999 — sufficient through ~5791 CE)
- Leap year logic: apply the standard Gregorian leap year rule to the Republican year number directly (divisible by 4, except centuries unless divisible by 400). This is the Romme convention used by most modern implementations. It does not match the historical record for the first ~20 years (which used equinox observation), but is the standard approximation for a non-astronomical tool
- Month names are hardcoded in French (Vendémiaire, Brumaire, etc.) — this is intentional, as the calendar is a French historical artifact

## Project Structure

```
decadi/
├── decadi.py              # Main script (single file, all logic)
├── assets/
│   └── transparent.png    # 1px transparent dummy icon
├── decadi.desktop         # XDG autostart entry
├── LICENSE                # MIT
└── README.md              # Usage, install, screenshot
```

## Autostart

An XDG `.desktop` file copied to `~/.config/autostart/`. No systemd unit — this is a GUI app that starts with the desktop session, not the system.

## Install

Manual: clone the repo, symlink or copy the `.desktop` file to `~/.config/autostart/`. No pip/snap/flatpak packaging for now.

## Non-Goals

- No pip/snap/flatpak packaging (can add later if needed)
- No settings persistence beyond the session (show-seconds toggle resets on restart)
- No GNOME extension — AppIndicator only
- No alarm/notification features
