import time

from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import user_dirs, should_skip
from ..utils.walk import walk_files


class OldFilesScanner(Scanner):
    name = "old_files"
    category = "Old/Unused Files"

    def __init__(self, days: int = 90):
        self._cutoff = days * 24 * 3600
        self.description = f"Files not accessed in {days} days"

    def scan(self) -> ScanResult:
        items = []
        now = time.time()
        for root in user_dirs():
            if not root.exists():
                continue
            for p, sz in walk_files(root, pred=lambda p: not should_skip(p)):
                try:
                    st = p.stat()
                    age = now - max(st.st_atime, st.st_mtime)
                    if age > self._cutoff:
                        items.append(FileInfo(path=p, size=sz, risk=Risk.CAUTION, note=f"unused {int(age/86400)}d"))
                except (PermissionError, OSError):
                    pass
        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
