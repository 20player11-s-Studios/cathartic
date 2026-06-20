from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import pkg_cache_dirs
from ..utils.walk import dir_size


class PkgCacheScanner(Scanner):
    name = "pkg_cache"
    category = "Package Manager Caches"
    description = "pip, npm, cargo, apt, brew caches"

    def scan(self) -> ScanResult:
        items = []
        for root in pkg_cache_dirs():
            total, count = dir_size(root)
            if total > 0:
                items.append(FileInfo(path=root, size=total, risk=Risk.SAFE, note=f"{count} cache files"))
        return ScanResult(scanner=self.name, category=self.category, description=self.description, items=items)
