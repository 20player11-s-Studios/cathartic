import shutil

from ..core.scanner import Scanner
from ..core.types import FileInfo, ScanResult, Risk
from ..utils.platform import home, is_lin


class RemnantsScanner(Scanner):
    name = "remnants"
    category = "App Remnants"
    description = "Leftover files from uninstalled applications"

    def scan(self) -> ScanResult:
        items = []
        h = home()

        known_orphans = [
            ".adobe", ".macromedia", ".oracle_jre_usage",
            ".texlive", ".wine",
        ]
        for name in known_orphans:
            p = h / name
            if not p.exists():
                continue
            total = 0
            count = 0
            try:
                for f in p.rglob("*"):
                    if f.is_file():
                        try:
                            total += f.stat().st_size
                            count += 1
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass
            if count > 0:
                items.append(FileInfo(
                    path=p, size=total, risk=Risk.CAUTION,
                    note=f"orphan config ({count} files)",
                ))

        if is_lin():
            apps = h / ".local/share/applications"
            if apps.exists():
                try:
                    for f in apps.iterdir():
                        if f.suffix == ".desktop":
                            try:
                                text = f.read_text()
                                for line in text.splitlines():
                                    if line.startswith("Exec="):
                                        exe = line[5:].split()[0] if line[5:].strip() else ""
                                        if exe and not shutil.which(exe):
                                            sz = f.stat().st_size
                                            items.append(FileInfo(
                                                path=f, size=sz, risk=Risk.DANGEROUS,
                                                note="orphan .desktop",
                                            ))
                                        break
                            except (PermissionError, OSError):
                                pass
                except (PermissionError, OSError):
                    pass

        return ScanResult(
            scanner=self.name, category=self.category,
            description=self.description, items=items,
        )
