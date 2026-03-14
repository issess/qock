# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qock is a Python weather desk clock for Raspberry Pi with a 2.7-inch e-paper (e-ink) display. It shows time, date, weather conditions, and a 5-day forecast using OpenWeatherMap API.

## Running

- Foreground: `python Qock.py`
- Daemon: `python QockDaemon.py {start|stop|restart}`
- Service: `/etc/init.d/qock {start|stop|restart}`
- Logs: `/var/log/qock/qock.log` (RotatingFileHandler, 512MB, 3 backups)

## Setup

1. `tools/setup.sh` — installs system packages (Pillow, pyowm, RPi.GPIO, python-daemon, GitPython, gratis EPD drivers)
2. `tools/install.sh` — registers init.d service, creates `/var/run/qock` and `/var/log/qock`
3. Copy `owm_config.py-SAMPLE` to `owm_config.py` and add OpenWeatherMap API key + location

## Architecture

**Rendering hierarchy** — composite pattern for display elements:
- `QockObject.py`: abstract base (name, position, type)
- `QockContainer.py`: holds child objects
- `QockText.py`: text rendering with font/position
- `QockFont.py`: PIL TrueType font wrapper

**Main application (`Qock.py`)**:
- `Settings27` class defines the full screen layout (all UI element positions/fonts for the 2.7" panel)
- Main loop updates display every minute (partial), full refresh every 30 minutes
- Weather fetched every 60 minutes via pyowm; failures show "?? °C"
- GPIO buttons (pins 16, 19, 20, 26) with LED feedback (pins 5, 6, 12), 500ms debounce

**Hardware layer**:
- `EPD.py`: interfaces with `/dev/epd/` device files (version, panel, command)
- `QockDaemon.py`: python-daemon wrapper

**Font system** (`FontManager.py`):
- Discovers `.ttf` files from `fonts/{default,text,weather}/` subdirectories
- Pre-configured sizes: 9, 12, 20, 22, 30, 45, 80px

## Key Conventions

- Python 2/3 compatible, UTF-8 encoding headers
- Korean locale for weekday names
- Display constants: `WHITE=1`, `BLACK=0`
- Weather icon codes map to weather font glyphs (OpenWeatherMap code format: 01d, 02n, etc.)
- `owm_config.py` is gitignored — never commit API keys
- Auto-update on startup via `tools/check-for-update.sh` → `git pull --rebase`

## No Test Suite

There are no automated tests in this repository.
