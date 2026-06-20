from pathlib import Path
from .types import FileInfo
import shutil


def to_trash(path: Path) -> bool:
    try:
        import send2trash
        send2trash.send2trash(str(path))
        return True
    except Exception:
        return False


def remove(path: Path) -> bool:
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()
        return True
    except (PermissionError, OSError):
        return False


def delete(items: list[FileInfo]) -> list[Path]:
    deleted = []
    for item in items:
        if not item.path.exists():
            continue
        if to_trash(item.path):
            deleted.append(item.path)
        elif remove(item.path):
            deleted.append(item.path)
    return deleted
