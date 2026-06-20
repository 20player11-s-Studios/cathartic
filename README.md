# Cathartic - [BETA]

> A clean system, a clear mind.

Cathartic is a cross-platform PC cleaner that scans your storage, finds junk files, and cleans with your consent. Features a terminal UI (TUI), CLI, and GUI.

## Features

- **Temp & Cache Files** — browser caches (Chrome, Firefox, Safari, Edge, Brave), system temp files
- **Large Files** — files above a configurable threshold in your home directories
- **Duplicate Files** — byte-identical duplicates detected via SHA-256 hashing
- **Old/Unused Files** — files untouched for a configurable number of days
- **Package Manager Caches** — pip, npm, cargo, apt, brew, Homebrew
- **Empty Directories** — safely removable empty folders
- **App Remnants** — orphaned config files and stale `.desktop` entries

## Install

### AppImage (Linux)

```bash
git clone https://github.com/20player11/cathartic.git
cd cathartic
make appimage
./install.sh
```

Or download the latest AppImage from the [releases page](https://github.com/20player11/cathartic/releases).

### pip

```bash
pip install cathartic
```

## Usage

```bash
# TUI (default)
cathartic

# CLI
cathartic scan
cathartic clean
cathartic clean --dry-run

# GUI
cathartic gui
```

## Development

```bash
git clone https://github.com/20player11/cathartic.git
cd cathartic
python -m venv .venv && source .venv/bin/activate
pip install -e .
cathartic
```

## License

MIT
