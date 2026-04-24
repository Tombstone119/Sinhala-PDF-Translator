# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for SinhalaTranslator
# Build with: pyinstaller translator.spec

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all files/binaries/hidden-imports for packages that need it
datas_qt,     bins_qt,     hidden_qt     = collect_all('PyQt6')
datas_mupdf,  bins_mupdf,  hidden_mupdf  = collect_all('pymupdf')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=bins_qt + bins_mupdf,
    datas=(
        [('fonts/NotoSansSinhala-Regular.ttf', 'fonts')]
        + datas_qt
        + datas_mupdf
    ),
    hiddenimports=hidden_qt + hidden_mupdf,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SinhalaTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='app.ico',       # Uncomment after adding app.ico to project root
)
