import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from .core.registry import Registry
from .core.actions import delete
from .core.types import Risk
from .utils.size import human_size
from .scanners.temp_cache import TempCacheScanner
from .scanners.large_files import LargeFilesScanner
from .scanners.duplicates import DuplicatesScanner
from .scanners.old_files import OldFilesScanner
from .scanners.pkg_cache import PkgCacheScanner
from .scanners.empty_dirs import EmptyDirsScanner
from .scanners.remnants import RemnantsScanner

console = Console()

RISK_STYLE = {
    Risk.SAFE: "green",
    Risk.CAUTION: "yellow",
    Risk.DANGEROUS: "red",
}


def make_reg() -> Registry:
    r = Registry()
    r.register(TempCacheScanner())
    r.register(LargeFilesScanner())
    r.register(DuplicatesScanner())
    r.register(OldFilesScanner())
    r.register(PkgCacheScanner())
    r.register(EmptyDirsScanner())
    r.register(RemnantsScanner())
    return r


@click.group()
def cli():
    """Cathartic — A clean system, a clear mind."""


@cli.command()
@click.option("--only", help="Comma-separated categories to scan")
def scan(only):
    """Scan for cleanable files."""
    reg = make_reg()
    filt = set(c.strip().lower() for c in only.split(",")) if only else None

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Scanning...", total=None)
        results = reg.run_all()

    if filt:
        results = [r for r in results if r.category.lower() in filt or r.scanner.lower() in filt]

    table = Table(box=box.ROUNDED, title="Scan Results")
    table.add_column("Category", style="cyan")
    table.add_column("Items", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Risk")

    total_items = 0
    total_size = 0

    for r in results:
        if not r.items:
            continue
        color = RISK_STYLE.get(r.items[0].risk, "white")
        table.add_row(r.category, str(len(r.items)), human_size(r.total_size), f"[{color}]{r.items[0].risk.value}[/]")
        total_items += len(r.items)
        total_size += r.total_size

    table.add_row("[bold]Total[/]", f"[bold]{total_items}[/]", f"[bold]{human_size(total_size)}[/]", "")
    console.print(table)
    console.print("\nRun [bold]cathartic clean[/] to interactively clean up.")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without deleting")
def clean(dry_run):
    """Scan and clean up junk files interactively."""
    reg = make_reg()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Scanning...", total=None)
        results = reg.run_all()

    total_deleted = 0
    total_freed = 0

    for r in results:
        if not r.items:
            continue

        color = RISK_STYLE.get(r.items[0].risk, "white")
        console.print(f"\n[{color}]■[/] {r.category} — {human_size(r.total_size)} ({len(r.items)} items)")

        if click.confirm("  Clean these files?", default=False):
            if click.confirm("  Show items?", default=False):
                for item in r.items:
                    c = RISK_STYLE[item.risk]
                    console.print(f"    {item.path} ({human_size(item.size)}) [{c}]{item.risk.value}[/]")

            if dry_run:
                console.print(f"  [yellow]Would delete {len(r.items)} items ({human_size(r.total_size)})[/]")
                total_deleted += len(r.items)
                total_freed += r.total_size
            else:
                deleted = delete(r.items)
                freed = sum(i.size for i in r.items if i.path in deleted)
                total_deleted += len(deleted)
                total_freed += freed
                console.print(f"  [green]Deleted {len(deleted)} items ({human_size(freed)})[/]")

    if dry_run:
        console.print(f"\n[yellow]Dry run: would delete {total_deleted} items, free {human_size(total_freed)}[/]")
    elif total_deleted:
        console.print(f"\n[green]Done! Deleted {total_deleted} items, freed {human_size(total_freed)}[/]")
    else:
        console.print("\nNothing was cleaned.")


@cli.command()
def gui():
    """Launch the graphical interface."""
    try:
        from .gui import run_gui
        run_gui()
    except ImportError as e:
        console.print(f"[red]Error: {e}[/]")
        console.print("Make sure tkinter is installed (python3-tk on Linux).")


if __name__ == "__main__":
    cli()
