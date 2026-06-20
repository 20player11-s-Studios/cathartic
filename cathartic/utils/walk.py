import os
from pathlib import Path
from typing import Callable, Iterator


def walk_files(root: Path, pred: Callable[[Path], bool] | None = None, max_depth: int = 50) -> Iterator[tuple[Path, int]]:
    """Fast recursive file walker using os.scandir. Yields (path, size)."""
    if not root.exists():
        return
    stack = [(root, 0)]
    while stack:
        path, depth = stack.pop()
        if depth > max_depth:
            continue
        try:
            for ent in os.scandir(path):
                if ent.is_symlink():
                    continue
                p = Path(ent.path)
                if ent.is_dir():
                    stack.append((p, depth + 1))
                elif ent.is_file():
                    if pred is None or pred(p):
                        try:
                            yield p, ent.stat().st_size
                        except (PermissionError, OSError):
                            pass
        except (PermissionError, OSError):
            pass


def dir_size(root: Path) -> tuple[int, int]:
    """Total size and file count of a directory tree."""
    total = 0
    count = 0
    if not root.exists():
        return 0, 0
    try:
        stack = [root]
        while stack:
            path = stack.pop()
            try:
                for ent in os.scandir(path):
                    if ent.is_symlink():
                        continue
                    if ent.is_dir():
                        stack.append(Path(ent.path))
                    elif ent.is_file():
                        try:
                            sz = ent.stat().st_size
                            if sz > 0:
                                total += sz
                                count += 1
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass
    return total, count
