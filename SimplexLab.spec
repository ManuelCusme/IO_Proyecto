# -*- mode: python ; coding: utf-8 -*-
"""Configuración de distribución local para PyInstaller 6.x."""

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("gui/help", "gui/help"), ("resources/styles", "resources/styles")],
    hiddenimports=["matplotlib.backends.backend_qtagg"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["scipy", "pytest", "black", "ruff", "PySide6.QtWebEngineCore",
              "PySide6.QtWebEngineWidgets", "PySide6.QtQml", "PySide6.QtQuick"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="SimplexLab",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="SimplexLab")
