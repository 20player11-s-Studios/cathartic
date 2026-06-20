#!/usr/bin/env python3
"""Cathartic — Interactive TUI. Gradient colors, arrow keys, enter to select."""

from prompt_toolkit.styles import Style as PTStyle
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text
import questionary

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
_last = []
_cfg = {"large": 100, "old": 90, "dup": 1}

QT_STYLE = PTStyle([
    ("qmark",      "fg:#00d4ff bold"),
    ("question",   "fg:#ffffff bold"),
    ("pointer",    "fg:#00d4ff bold"),
    ("highlighted","fg:#00d4ff bold"),
    ("selected",   "fg:#00d4ff"),
    ("text",       "fg:#e0e0e0"),
    ("instruction","fg:#888888"),
    ("answer",     "fg:#00d4ff bold"),
])

GRAD = ["bright_blue","blue","cyan","bright_cyan","white",
        "white","bright_cyan","cyan","blue","bright_blue"]


def reg():
    r = Registry()
    r.register(TempCacheScanner())
    r.register(LargeFilesScanner(threshold_mb=_cfg["large"]))
    r.register(DuplicatesScanner(min_size_mb=_cfg["dup"]))
    r.register(OldFilesScanner(days=_cfg["old"]))
    r.register(PkgCacheScanner())
    r.register(EmptyDirsScanner())
    r.register(RemnantsScanner())
    return r


def clear():
    console.clear()


def banner():
    t = Text()
    t.append("◇  ", style="bright_cyan")
    for i, ch in enumerate("CATHARTIC"):
        t.append(ch, style=f"bold {GRAD[i]}")
    t.append("  ◇", style="bright_cyan")
    body = Text()
    body.append(t)
    body.append("\n")
    body.append("─" * 22, style="blue")
    body.append("\n")
    body.append("Scan · Detect · Clean", style="cyan")
    body.append("\n")
    body.append("A clean system, a clear mind", style="dim cyan")
    console.print(Panel(body, border_style="bright_blue", box=box.ROUNDED, padding=(1, 4), subtitle="v0.1.0", subtitle_align="right", expand=False))


def wait(msg="Press any key to return ..."):
    questionary.press_any_key_to_continue(msg).ask()


def qsel(prompt, choices, **kw):
    return questionary.select(prompt, choices=choices, qmark=">", pointer=">", style=QT_STYLE, **kw).ask()


def qchk(prompt, choices, **kw):
    return questionary.checkbox(prompt, choices=choices, pointer=">", style=QT_STYLE, **kw).ask()


def qtxt(prompt, **kw):
    return questionary.text(prompt, style=QT_STYLE, **kw).ask()


def qcon(prompt, **kw):
    return questionary.confirm(prompt, style=QT_STYLE, **kw).ask()


def run_scan(categories=None):
    global _last
    r = reg()
    if categories:
        r2 = Registry()
        for s in r.scanners:
            if s.category in categories or s.name in categories:
                cls = type(s)
                kw = {}
                if cls.__name__ == "LargeFilesScanner":
                    kw = {"threshold_mb": _cfg["large"]}
                elif cls.__name__ == "OldFilesScanner":
                    kw = {"days": _cfg["old"]}
                elif cls.__name__ == "DuplicatesScanner":
                    kw = {"min_size_mb": _cfg["dup"]}
                r2.register(cls(**kw))
        r = r2
    clear()
    banner()
    console.print("\n  [bold]Scanning storage[/] ...\n")
    with Progress(SpinnerColumn(), TextColumn("  {task.description}"), console=console, transient=True) as p:
        p.add_task("Analyzing files ...", total=None)
        _last = r.run_all()
    show(_last)


def show(results):
    total_n = 0
    total_sz = 0
    has = False
    tbl = Table(box=box.ROUNDED, title=" Scan Results ", border_style="cyan", padding=(0,1),
                header_style="bold cyan")
    tbl.add_column("Category", style="cyan")
    tbl.add_column("Items", justify="right", style="bright_white")
    tbl.add_column("Size", justify="right", style="bright_white")
    tbl.add_column("Risk", justify="center")
    clr = {"safe":"green","caution":"yellow","dangerous":"red"}
    for r in results:
        if not r.items:
            continue
        has = True
        c = clr.get(r.items[0].risk.value, "white")
        total_n += len(r.items)
        total_sz += r.total_size
        tbl.add_row(r.category, str(len(r.items)), human_size(r.total_size), f"[{c}]\u25cf {r.items[0].risk.value}[/]")
    if not has:
        console.print("\n  [green]No cleanable files found - system is tidy.[/]\n")
        return
    tbl.add_row("[bold]Total[/]", f"[bold]{total_n}[/]", f"[bold]{human_size(total_sz)}[/]", "")
    console.print()
    console.print(tbl)
    console.print(f"\n  [dim]Estimated space to reclaim:[/] [bold bright_white]{human_size(total_sz)}[/]")
    console.print()


def main():
    try:
        _main()
    except KeyboardInterrupt:
        console.print("\n\n  [cyan]Goodbye.[/]")
        raise SystemExit(0)


CHOICES = [
    questionary.Choice(title="  Quick Scan           (all 7 scanners)", value="q"),
    questionary.Choice(title="  Custom Scan          (pick categories)", value="c"),
    questionary.Choice(title="  Clean Up             (review and delete)", value="cl"),
    questionary.Choice(title="  Report               (last scan results)", value="r"),
    questionary.Choice(title="  Settings             (configure thresholds)", value="s"),
    questionary.Choice(title="  About", value="a"),
    questionary.Choice(title="  Exit", value="x"),
]


def _main():
    while True:
        clear()
        banner()
        console.print()
        c = qsel("  What would you like to do?", CHOICES)
        if c == "q":
            run_scan()
            wait()
        elif c == "c":
            custom()
        elif c == "cl":
            clean()
        elif c == "r":
            report()
        elif c == "s":
            settings()
        elif c == "a":
            about()
        else:
            break
    console.print("\n  [cyan]Goodbye.[/]")


def custom():
    r = reg()
    picks = qchk("  Select categories  (Space to toggle, Enter to confirm)",
                 [questionary.Choice(title=f"  {s.category}", value=s.category) for s in r.scanners])
    if picks:
        run_scan(categories=set(picks))
        wait()


def clean():
    global _last
    if not _last or not any(r.items for r in _last):
        console.print("\n  [yellow]No scan data - run a scan first.[/]")
        wait()
        return
    clear()
    banner()
    cats = [questionary.Choice(title=f"  {r.category}  ({human_size(r.total_size)}, {len(r.items)} files)", value=r)
            for r in _last if r.items]
    if not cats:
        console.print("\n  [green]Nothing to clean.[/]")
        wait()
        return
    sel = qchk("  Select categories to clean:", cats)
    if not sel:
        return
    all_items = []
    total = 0
    for r in sel:
        console.print(f"\n  [bold bright_cyan]{r.category}[/]  ({human_size(r.total_size)})")
        its = []
        for item in r.items:
            p = str(item.path)
            if len(p) > 70:
                p = "..." + p[-67:]
            its.append(questionary.Choice(title=f"  \u25cf {p}  ({human_size(item.size)}, {item.risk.value})", value=item, checked=True))
        picked = qchk("  Select files to delete:", its)
        if picked:
            all_items.extend(picked)
            total += sum(i.size for i in picked)
    if not all_items:
        return
    console.print(f"\n  [bold yellow]Delete {len(all_items)} file(s) - {human_size(total)}[/]")
    if not qcon("  Proceed?"):
        console.print("  [yellow]Cancelled.[/]")
        wait()
        return
    with Progress(SpinnerColumn(), TextColumn("  {task.description}"), console=console, transient=True) as p:
        p.add_task("Deleting ...", total=None)
        deleted = delete(all_items)
    freed = sum(i.size for i in all_items if i.path in deleted)
    console.print(f"\n  [green]Deleted {len(deleted)} file(s), freed {human_size(freed)}.[/]")
    _last = reg().run_all()
    wait()


def report():
    if not _last or not any(r.items for r in _last):
        console.print("\n  [yellow]No scan data - run a scan first.[/]")
        wait()
        return
    clear()
    banner()
    show(_last)
    wait()


def settings():
    while True:
        clear()
        banner()
        console.print()
        c = qsel("  Settings", [
            questionary.Choice(title=f"  [1]  Large file threshold:   {_cfg['large']} MB", value="l"),
            questionary.Choice(title=f"  [2]  Old file cutoff:       {_cfg['old']} days", value="o"),
            questionary.Choice(title=f"  [3]  Min duplicate size:    {_cfg['dup']} MB", value="d"),
            questionary.Choice(title="  [4]  Back to main menu", value="b"),
        ])
        if c == "b":
            break
        v = qtxt({"l":"Large file threshold (MB):","o":"Old file cutoff (days):","d":"Min duplicate size (MB):"}[c],
                  default=str(_cfg[{"l":"large","o":"old","d":"dup"}[c]]),
                  validate=lambda x: x.isdigit() and int(x) > 0)
        if v:
            _cfg[{"l":"large","o":"old","d":"dup"}[c]] = int(v)


def about():
    clear()
    banner()
    console.print(Panel(
        "\n  [bold bright_white]Cathartic[/]  [cyan]v0.1.0[/]\n"
        "  [dim]A clean system, a clear mind.[/]\n\n"
        "  Cross-platform terminal cleaner.\n"
        "  Scans storage, finds junk,\n"
        "  cleans with your consent.\n\n"
        "  [bold bright_white]Scanners[/]\n"
        "    Temp and Cache Files\n"
        "    Large Files\n"
        "    Duplicate Files\n"
        "    Old and Unused Files\n"
        "    Package Manager Caches\n"
        "    Empty Directories\n"
        "    App Remnants\n\n"
        "  [bold bright_white]Controls[/]\n"
        "    up/down  move\n"
        "    space    toggle\n"
        "    enter    confirm\n"
        "    esc      back\n",
        border_style="cyan", box=box.ROUNDED, padding=(1,2),
    ))
    wait()


if __name__ == "__main__":
    main()
