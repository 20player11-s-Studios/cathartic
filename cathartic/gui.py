import tkinter as tk
from tkinter import ttk, messagebox

from .core.registry import Registry
from .core.actions import delete
from .utils.size import human_size
from .scanners.temp_cache import TempCacheScanner
from .scanners.large_files import LargeFilesScanner
from .scanners.duplicates import DuplicatesScanner
from .scanners.old_files import OldFilesScanner
from .scanners.pkg_cache import PkgCacheScanner
from .scanners.empty_dirs import EmptyDirsScanner
from .scanners.remnants import RemnantsScanner


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


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cathartic")
        self.root.minsize(700, 500)

        self.reg = make_reg()
        self.results = []
        self.selected: dict[str, set[str]] = {}
        self.trees: dict[str, ttk.Treeview] = {}

        self._build()

    def _build(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(toolbar, text="Scan Now", command=self.run_scan).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clean Selected", command=self.clean_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=2)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.summary = ttk.Label(self.root, text="Ready. Click 'Scan Now' to start.")
        self.summary.pack(fill=tk.X, padx=8, pady=4)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")

    def run_scan(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.results = []
        self.selected = {}
        self.trees = {}

        self.progress.pack(fill=tk.X, padx=8, pady=2)
        self.progress.start()
        self.summary.config(text="Scanning...")
        self.root.update_idletasks()

        self.results = self.reg.run_all()

        self.progress.stop()
        self.progress.pack_forget()

        total_items = 0
        total_size = 0
        for r in self.results:
            if not r.items:
                continue
            total_items += len(r.items)
            total_size += r.total_size
            self.selected[r.category] = set()
            self._add_tab(r)

        if total_items == 0:
            self.summary.config(text="No cleanable files found.")
        else:
            self.summary.config(text=f"Found {total_items} items ({human_size(total_size)}) across {len(self.results)} categories.")

    def _add_tab(self, result):
        frame = ttk.Frame(self.notebook)
        tree = ttk.Treeview(
            frame, columns=("sel", "path", "size", "note"),
            show="headings", selectmode="none",
        )
        tree.heading("sel", text="✓")
        tree.heading("path", text="Path")
        tree.heading("size", text="Size")
        tree.heading("note", text="Note")
        tree.column("sel", width=30, anchor="center")
        tree.column("path", width=450)
        tree.column("size", width=80, anchor="e")
        tree.column("note", width=120)

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree.tag_configure("selected", background="#e8f5e9")

        for item in result.items:
            tree.insert("", tk.END, iid=str(item.path), values=("☐", str(item.path), human_size(item.size), item.note))

        tree.bind("<ButtonRelease-1>", lambda e, t=tree, c=result.category: self._toggle(e, t, c))

        self.trees[result.category] = tree
        self.notebook.add(frame, text=f"{result.category} ({len(result.items)})")

    def _toggle(self, _e, tree, category):
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        cur = tree.set(iid, "sel")
        if cur == "☐":
            tree.set(iid, "sel", "☑")
            tree.tag_add("selected", iid)
            self.selected[category].add(iid)
        else:
            tree.set(iid, "sel", "☐")
            tree.tag_remove("selected", iid)
            self.selected[category].discard(iid)

    def select_all(self):
        for cat, tree in self.trees.items():
            for child in tree.get_children():
                tree.set(child, "sel", "☑")
                tree.tag_add("selected", child)
                self.selected[cat].add(child)

    def deselect_all(self):
        for cat, tree in self.trees.items():
            for child in tree.get_children():
                tree.set(child, "sel", "☐")
                tree.tag_remove("selected", child)
                self.selected[cat].discard(child)

    def clean_selected(self):
        all_paths = set()
        for paths in self.selected.values():
            all_paths.update(paths)

        if not all_paths:
            messagebox.showinfo("No Selection", "Select items to clean first.")
            return

        to_remove = []
        total = 0
        for r in self.results:
            for item in r.items:
                if str(item.path) in all_paths:
                    to_remove.append(item)
                    total += item.size

        ok = messagebox.askyesno(
            "Confirm Cleanup",
            f"Delete {len(to_remove)} item(s) ({human_size(total)})?\n\nItems will be moved to Trash if possible.",
        )
        if not ok:
            return

        deleted = delete(to_remove)
        freed = sum(item.size for item in to_remove if item.path in deleted)
        messagebox.showinfo("Cleanup Complete", f"Deleted {len(deleted)} item(s), freed {human_size(freed)}.")
        self.run_scan()


def run_gui():
    root = tk.Tk()
    App(root)
    root.mainloop()
