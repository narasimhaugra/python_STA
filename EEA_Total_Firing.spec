# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('nidaqmx')
datas += copy_metadata('opencv_python')
datas += copy_metadata('openpyxl')
datas += copy_metadata('pyserial')
datas += copy_metadata('WMI')
datas += copy_metadata('imagehash')
datas += copy_metadata('gtts')
datas += copy_metadata('simple_colors')


a = Analysis(
    ['C:\\Users\\SVC.devops-signia\\Desktop\\STA-EEA\\EEA_Total_Firing.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='EEA_Total_Firing',
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
