#!/usr/bin/env python3
"""
Docker コンテナ内でWindows用実行ファイルを作成
"""

import subprocess
import os

def create_windows_spec():
    """Windows用PyInstaller設定"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['url_to_pdf_gui_win11.py'],
    pathex=['/app'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext',
        'weasyprint', 'weasyprint.css', 'weasyprint.html', 'weasyprint.pdf',
        'cairocffi', 'cffi', 'cssselect2', 'tinycss2', 'pyphen', 'fonttools', 'html5lib',
        'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
        'beautifulsoup4', 'bs4', 'lxml', 'lxml.etree', 'lxml.html',
        'PIL', 'PIL.Image', 'PIL.ImageFont', 'PIL.ImageDraw',
        'reportlab', 'reportlab.pdfgen', 'reportlab.lib', 'reportlab.platypus',
        'threading', 'logging', 'datetime', 're', 'os', 'sys', 'traceback'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
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
    name='URLtoPDF_Windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    with open('/app/windows_build.spec', 'w') as f:
        f.write(spec_content)

def main():
    print("🐳 Container内でWindows用実行ファイルをビルド中...")

    # Spec ファイルを作成
    create_windows_spec()

    # PyInstaller でビルド
    try:
        subprocess.run([
            'pyinstaller',
            '--clean',
            '/app/windows_build.spec'
        ], check=True)

        # 結果確認
        exe_path = '/app/dist/URLtoPDF_Windows'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ ビルド成功! サイズ: {size_mb:.1f} MB")

            # Windows用に拡張子を追加
            subprocess.run(['mv', exe_path, exe_path + '.exe'], check=True)
            print("✅ Windows用拡張子 (.exe) を追加")
        else:
            print("❌ 実行ファイルが見つかりません")

    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")

if __name__ == "__main__":
    main()
