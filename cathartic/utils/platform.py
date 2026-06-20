import sys
import os
from pathlib import Path


def is_win() -> bool:
    return sys.platform == "win32"


def is_mac() -> bool:
    return sys.platform == "darwin"


def is_lin() -> bool:
    return sys.platform == "linux"


def home() -> Path:
    return Path.home()


SKIP = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".eggs", "build", "dist", ".next", "target",
    ".shadowenv", ".svn", ".hg",
}


def should_skip(p: Path) -> bool:
    return p.name in SKIP or p.name.startswith(".")


def temp_dirs() -> list[Path]:
    dirs = []
    if is_win():
        tmp = os.environ.get("TEMP")
        if tmp:
            dirs.append(Path(tmp))
        win = os.environ.get("WINDIR")
        if win:
            dirs.append(Path(win) / "Temp")
    else:
        dirs.append(Path("/tmp"))
        t = os.environ.get("TMPDIR")
        if t:
            dirs.append(Path(t))
        dirs.append(Path("/var/tmp"))
    return dirs


def browser_cache_dirs() -> list[Path]:
    h = home()
    dirs = []
    if is_win():
        local = os.environ.get("LOCALAPPDATA", "")
        if local:
            dirs.append(Path(local) / "Google/Chrome/User Data/Default/Cache")
            dirs.append(Path(local) / "Microsoft/Edge/User Data/Default/Cache")
        app = os.environ.get("APPDATA", "")
        if app:
            dirs.append(Path(app) / "Mozilla/Firefox/Profiles")
    elif is_mac():
        dirs.append(h / "Library/Caches/Google/Chrome")
        dirs.append(h / "Library/Caches/Firefox")
        dirs.append(h / "Library/Caches/com.apple.Safari")
    else:
        dirs.append(h / ".cache/google-chrome")
        dirs.append(h / ".cache/chromium")
        dirs.append(h / ".cache/mozilla/firefox")
        dirs.append(h / ".cache/brave-browser")
        dirs.append(h / ".cache/msedge")
    return dirs


def pkg_cache_dirs() -> list[Path]:
    h = home()
    dirs = []
    if is_win():
        local = os.environ.get("LOCALAPPDATA")
        if local:
            dirs.append(Path(local) / "pip/cache")
    elif is_mac():
        dirs.append(h / "Library/Caches/pip")
        dirs.append(h / "Library/Caches/Homebrew")
        dirs.append(h / ".npm/_cacache")
    else:
        dirs.append(h / ".cache/pip")
        dirs.append(h / ".npm/_cacache")
        dirs.append(h / ".cargo/registry/cache")
        dirs.append(Path("/var/cache/apt/archives"))
    return dirs


def user_dirs() -> list[Path]:
    h = home()
    return [h / d for d in ("Downloads", "Desktop", "Documents", "Pictures", "Videos", "Music")]
