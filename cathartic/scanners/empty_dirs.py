from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import user_dirs, should_skip

import os


class EmptyDirsScanner(Scanner):
    name = "empty_dirs"
    category = "Empty Directories"
    description = "Empty directories that can be removed"

    def scan(self) -> ScanResult:
        items = []
        seen = set()
        for root in user_dirs():
            if not root.exists():
                continue
            try:
                stack = [root]
                while stack:
                    path = stack.pop()
                    try:
                        for ent in os.scandir(path):
                            if ent.is_symlink():
                                continue
                            p = os.fsdecode(ent.path)
                            if ent.is_dir():
                                if should_skip(type(path)(p)):
                                    continue
                                if p not in seen:
                                    seen.add(p)
                                    stack.append(type(path)(p))
                    except (PermissionError, OSError):
                        pass
                    try:
                        if not any(True for _ in os.scandir(path)):
                            items.append(FileInfo(path=type(path)(path), size=0, risk=Risk.SAFE, note="empty dir"))
                    except (PermissionError, OSError):
                        pass
            except (PermissionError, OSError):
                pass
        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
