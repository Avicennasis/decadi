# Décadi — French Decimal Time Indicator for GNOME

## Overview

A system tray indicator for Ubuntu/GNOME that displays the current time in the French Revolutionary decimal time system (10 hours/day, 100 minutes/hour, 100 seconds/minute). Built as a Python AppIndicator using AyatanaAppIndicator3 + GTK3.

## Target Environment

- Ubuntu with GNOME Shell 46+ on Wayland
- Python 3.12+
- AyatanaAppIndicator3 (already installed on standard Ubuntu)
- No external Python dependencies (stdlib + gi.repository only)

## Core: Decimal Time Conversion

Convert standard time to French Revolutionary decimal time:

1. Compute seconds since midnight (including microseconds for smooth ticking)
2. Scale to 100,000 decimal seconds per day: `decimal = seconds_since_midnight * 100000 / 86400`
3. Split into hours (0–9), minutes (0–99), seconds (0–99)

The GLib timer fires every ~864ms (one decimal second = 86400/100000 = 0.864 real seconds). The callback self-corrects by recalculating the next tick offset from the current wall clock to prevent drift over time.

## Tray Indicator

The indicator shows decimal time as a text label in the system tray:

- **Default (seconds on):** `⑩ 7:45:83`
- **Compact (seconds off):** `⑩ 7:45`

The `⑩` (circled 10) prefix distinguishes it from the regular clock and references the base-10 system.

No custom icon — AppIndicator requires an icon, so a transparent 1px PNG is bundled as a dummy. Category is `APPLICATION_STATUS`, status is `ACTIVE`.

## Click Menu

Clicking the indicator opens a GTK menu:

| Item | Type | Content |
|------|------|---------|
| Decimal time | Label | `Decimal: 7:45:83` |
| Standard time | Label | `Standard: 18:06:14` |
| Separator | — | — |
| Revolutionary date | Label | `14 Prairial CCXXXIV` |
| Separator | — | — |
| Show seconds | CheckMenuItem | Toggle, checked by default |
| Separator | — | — |
| Quit | MenuItem | Exits the app |

- Decimal and standard time labels update live while the menu is open.
- Revolutionary date is computed once per day and refreshed at midnight.

### Revolutionary Calendar Conversion

The calendar covers:

- 12 months of 30 days each (Vendémiaire through Fructidor)
- 5–6 complementary days (Sansculottides) at year end
- Year calculated from the Republican epoch (September 22, 1792)
- Year displayed in Roman numerals
- Leap year logic follows the original equinox rule (aligned with the Gregorian September equinox)

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
