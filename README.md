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
