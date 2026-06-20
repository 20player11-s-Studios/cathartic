from abc import ABC, abstractmethod
from .types import ScanResult


class Scanner(ABC):
    name: str = ""
    category: str = ""
    description: str = ""

    @abstractmethod
    def scan(self) -> ScanResult: ...
