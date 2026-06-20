from .scanner import Scanner
from .types import ScanResult


class Registry:
    def __init__(self):
        self._scanners: list[Scanner] = []

    def register(self, s: Scanner):
        self._scanners.append(s)

    def run_all(self) -> list[ScanResult]:
        out = []
        for s in self._scanners:
            try:
                out.append(s.scan())
            except Exception as e:
                out.append(ScanResult(
                    scanner=s.name,
                    category=s.category,
                    description=f"Error: {e}",
                ))
        return out

    @property
    def scanners(self) -> list[Scanner]:
        return self._scanners
