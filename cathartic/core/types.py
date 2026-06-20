from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Risk(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"


@dataclass
class FileInfo:
    path: Path
    size: int
    risk: Risk = Risk.SAFE
    note: str = ""


@dataclass
class ScanResult:
    scanner: str
    category: str
    description: str
    items: list[FileInfo] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        return sum(i.size for i in self.items)
