# -*- mode: python ; coding: utf-8 -*-
# Windows 11 64bit専用設定

import sys
import os

block_cipher = None

# 隠しインポート（すべての依存関係を明示）
hiddenimports = [
    # tkinter関連
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
    'tkinter.messagebox', 'tkinter.scrolledtext', '_tkinter',

    # HTTP/Web関連
    'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
    'requests.adapters', 'requests.auth', 'requests.cookies',
    'requests.models', 'requests.sessions', 'requests.utils',

    # HTML/XML解析
    'bs4', 'beautifulsoup4', 'lxml', 'lxml.etree', 'lxml.html',

    # PDF生成（weasyprint）
    'weasyprint', 'weasyprint.css', 'weasyprint.html', 'weasyprint.pdf',
    'cairocffi', 'cffi', 'cssselect2', 'tinycss2', 'pyphen',
    'fonttools', 'html5lib',

    # PDF生成（reportlab - フォールバック）
    'reportlab', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas',
    'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles',
    'reportlab.platypus',

    # 画像処理
    'PIL', 'PIL.Image', 'PIL.ImageFont', 'PIL.ImageDraw',

    # 標準ライブラリ
    'threading', 'logging', 'datetime', 're', 'os', 'sys',
    'traceback', 'urllib.parse'
]

# データファイル
datas = []

# バイナリファイル
binaries = []

a = Analysis(
    ['url_to_pdf_gui_win11.py'],
    pathex=[os.getcwd()],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],  # 不要なライブラリを除外
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
    name='URLtoPDF_Win11',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーション
    disable_windowed_traceback=False,
    target_arch='x86_64',  # 64bit専用
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=None
)
