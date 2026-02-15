# -*- mode: python ; coding: utf-8 -*-


import tkinterdnd2
import os

tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[(tkdnd_path, 'tkinterdnd2/tkdnd')],
    hiddenimports=['tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDF Stitcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDF Stitcher',
)
app = BUNDLE(
    coll,
    name='PDF Stitcher.app',
    icon='icon.icns',
    bundle_identifier=None,
)
