# -*- mode: python ; coding: utf-8 -*-
# Build with: pyinstaller translator.spec

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# PyMuPDF registers itself under both 'fitz' and 'pymupdf' — collect both
datas_fitz,      bins_fitz,      hidden_fitz      = collect_all('fitz')
datas_mupdf,     bins_mupdf,     hidden_mupdf     = collect_all('pymupdf')
datas_qt,        bins_qt,        hidden_qt        = collect_all('PyQt6')
datas_reportlab, bins_reportlab, hidden_reportlab = collect_all('reportlab')
datas_requests,  bins_requests,  hidden_requests  = collect_all('requests')

all_datas = (
    [('fonts/NotoSansSinhala-Regular.ttf', 'fonts')]
    + datas_fitz
    + datas_mupdf
    + datas_qt
    + datas_reportlab
    + datas_requests
)

all_binaries = bins_fitz + bins_mupdf + bins_qt + bins_reportlab + bins_requests

all_hidden = (
    hidden_fitz
    + hidden_mupdf
    + hidden_qt
    + hidden_reportlab
    + hidden_requests
    + [
        'services.pdf_extractor',
        'services.chunker',
        'services.translator',
        'services.pdf_writer',
        'services.pipeline',
    ]
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='app.ico',
)
