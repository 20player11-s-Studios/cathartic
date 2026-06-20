# -*- mode: python ; coding: utf-8 -*-
import sys, os
from pathlib import Path

ROOT = Path(os.getcwd())

a = Analysis(
    [str(ROOT / "cathartic/__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "prompt_toolkit",
        "prompt_toolkit.styles",
        "prompt_toolkit.shortcuts",
        "send2trash",
        "send2trash.plat_linux",
        "send2trash.plat_gio",
        "send2trash.plat_other",
        "rich",
        "rich.table",
        "rich.panel",
        "rich.progress",
        "rich.text",
        "rich.box",
        "rich.console",
        "rich.style",
        "rich.color",
        "rich.align",
        "questionary",
        "questionary.checkbox",
        "questionary.select",
        "questionary.text",
        "questionary.confirm",
        "questionary.question",
        "click",
        "wcwidth",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="cathartic",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
