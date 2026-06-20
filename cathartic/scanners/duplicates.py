from collections import defaultdict

from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import user_dirs, should_skip
from ..utils.walk import walk_files
from ..utils.hasher import partial_hash, hash_file


class DuplicatesScanner(Scanner):
    name = "duplicates"
    category = "Duplicate Files"

    def __init__(self, min_size_mb: int = 1):
        self._min = min_size_mb * 1024 * 1024
        self.description = f"Duplicate files larger than {min_size_mb} MB"

    def scan(self) -> ScanResult:
        size_map = defaultdict(list)
        roots = [d for d in user_dirs() if d.exists()]

        for root in roots:
            for p, sz in walk_files(root, pred=lambda p: not should_skip(p)):
                if sz >= self._min:
                    size_map[sz].append(p)

        partial_map = defaultdict(list)
        for sz, paths in size_map.items():
            if len(paths) < 2:
                continue
            for p in paths:
                try:
                    h = partial_hash(str(p))
                    partial_map[(sz, h)].append(p)
                except (PermissionError, OSError):
                    pass

        full_map = defaultdict(list)
        for (sz, _ph), paths in partial_map.items():
            if len(paths) < 2:
                continue
            for p in paths:
                try:
                    h = hash_file(str(p))
                    full_map[(sz, h)].append(p)
                except (PermissionError, OSError):
                    pass

        items = []
        for (sz, _h), paths in full_map.items():
            if len(paths) < 2:
                continue
            for i, p in enumerate(paths):
                items.append(FileInfo(path=p, size=sz, risk=Risk.CAUTION, note="duplicate" if i > 0 else "original"))

        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
