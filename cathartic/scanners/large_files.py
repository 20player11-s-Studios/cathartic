from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import user_dirs, should_skip
from ..utils.walk import walk_files


class LargeFilesScanner(Scanner):
    name = "large_files"
    category = "Large Files"

    def __init__(self, threshold_mb: int = 100):
        self._threshold = threshold_mb * 1024 * 1024
        self.description = f"Files larger than {threshold_mb} MB"

    def scan(self) -> ScanResult:
        items = []
        for root in user_dirs():
            if not root.exists():
                continue
            for p, sz in walk_files(root, pred=lambda p: not should_skip(p)):
                if sz >= self._threshold:
                    items.append(FileInfo(path=p, size=sz, risk=Risk.CAUTION, note="large file"))
        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
