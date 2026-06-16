# Décadi

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Avicennasis/decadi/badge)](https://scorecard.dev/viewer/?uri=github.com/Avicennasis/decadi)
[![Release](https://img.shields.io/github/v/release/Avicennasis/decadi?display_name=tag)](https://github.com/Avicennasis/decadi/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A system tray indicator for Ubuntu/GNOME that displays the current time in the [French Revolutionary decimal time](https://en.wikipedia.org/wiki/Decimal_time#France) system. During the French Revolution, the Convention introduced a decimal time system: 10 hours per day, 100 minutes per hour, 100 seconds per minute. Décadi brings it to your desktop.

## What It Does

The indicator sits in your GNOME system tray and shows the current decimal time, updating every ~0.864 seconds (one decimal second):

    ⑩ 7:54:32

Click the indicator to see:

- **Decimal time** — updates live while the menu is open
- **Standard time** — 24-hour format, also live
- **Revolutionary calendar date** — e.g. `27 Prairial CCXXXIV` (the full 12-month + Sansculottides calendar)
- **Show seconds** — toggle to compact `⑩ 7:54` mode
- **Quit** — cleanly exits

### The Decimal Time System

| Standard | Decimal | Notes |
|----------|---------|-------|
| 24 hours | 10 hours | Each decimal hour = 2.4 standard hours |
| 60 minutes | 100 minutes | Each decimal minute = 1.44 standard minutes |
| 60 seconds | 100 seconds | Each decimal second = 0.864 standard seconds |
| Midnight | 0:00:00 | Same |
| Noon | 5:00:00 | Halfway through the day |
| 6:00 PM | 7:50:00 | |

### The Revolutionary Calendar

The click menu also shows the current date in the [French Republican Calendar](https://en.wikipedia.org/wiki/French_Republican_calendar):

- 12 months of 30 days each (Vendémiaire through Fructidor)
- 5-6 complementary days (Sansculottides) at year end
- Year numbering from the Republican epoch (September 22, 1792)
- Years displayed in Roman numerals (e.g. CCXXXIV = 234)
- Leap years follow the Romme convention

## Requirements

- **Ubuntu** with GNOME Shell (tested on 46+, Wayland and X11)
- **GNOME Shell AppIndicator extension** — required for tray indicators to appear:
  ```
  sudo apt install gnome-shell-extension-appindicator
  ```
  Then enable it in GNOME Extensions or GNOME Tweaks. Log out and back in after enabling.
- **Python 3.12+**
- **System packages** (pre-installed on standard Ubuntu desktop):
  ```
  sudo apt install python3-gi gir1.2-ayatanaappindicator3-0.1
  ```

## Install

Clone the repo:

```bash
git clone https://github.com/Avicennasis/decadi.git
cd decadi
```

Symlink the autostart entry so it launches on login:

```bash
# Edit decadi.desktop first — update the Exec and Icon paths to match your clone location
ln -s "$(pwd)/decadi.desktop" ~/.config/autostart/decadi.desktop
```

Start it now without waiting for a login:

```bash
python3 decadi.py &
```

### Desktop Entry Paths

The included `decadi.desktop` file has hardcoded absolute paths. If you cloned to a different location than the default, edit the `Exec` and `Icon` lines to match:

```ini
Exec=python3 /your/clone/path/decadi.py
Icon=/your/clone/path/assets/transparent.png
```

## Usage

Once running, look for the `⑩` indicator in your system tray. It ticks every decimal second (~0.864 real seconds), so you'll see the seconds counter go past 59 into the 80s and 90s.

**Single instance:** If you accidentally launch it twice, the second instance detects the first via DBus and exits silently.

**Clean shutdown:** The indicator handles SIGTERM/SIGINT, so `kill` and session logout both work cleanly. Or just click Quit in the menu.

**Autostart:** The symlinked `.desktop` file ensures Décadi launches automatically on every login. To disable autostart, remove the symlink:

```bash
rm ~/.config/autostart/decadi.desktop
```

## Running Tests

The project includes unit tests for all conversion logic:

```bash
python3 -m pytest tests/ -v
```

Tests cover decimal time conversion, Roman numeral conversion, and Revolutionary calendar date computation (including leap years and Sansculottides). The test suite runs headlessly — no display server required.

## How It Works

Décadi is a single Python file (`decadi.py`) with no external dependencies beyond the system GTK/AppIndicator packages. Key components:

- **Decimal time conversion** — wall-clock decomposition (`h*3600 + m*60 + s`) scaled to 100,000 decimal seconds per day
- **Self-correcting timer** — a one-shot GLib timer that recalculates the next decimal-second boundary from the wall clock on every tick, preventing drift
- **Revolutionary calendar** — counts days from the Republican epoch (September 22, 1792), accounting for the Romme leap year convention
- **DBus single-instance** — claims `systems.simmons.Decadi` on the session bus; duplicates exit silently

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
