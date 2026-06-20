import os
import time

from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import temp_dirs, browser_cache_dirs
from ..utils.walk import dir_size


class TempCacheScanner(Scanner):
    name = "temp_cache"
    category = "Temp & Cache Files"
    description = "Temporary files and browser caches"

    def scan(self) -> ScanResult:
        items = []

        for root in browser_cache_dirs():
            total, count = dir_size(root)
            if total > 0:
                items.append(FileInfo(path=root, size=total, risk=Risk.SAFE, note=f"browser cache ({count} files)"))

        now = time.time()
        for root in temp_dirs():
            if not root.exists():
                continue
            try:
                for ent in os.scandir(root):
                    if ent.is_symlink() or not ent.is_file():
                        continue
                    try:
                        info = ent.stat()
                        if info.st_size > 0 and now - info.st_mtime > 3600:
                            items.append(FileInfo(path=root / ent.name, size=info.st_size, risk=Risk.SAFE, note="temp file"))
                    except (PermissionError, OSError):
                        pass
            except (PermissionError, OSError):
                pass

        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
