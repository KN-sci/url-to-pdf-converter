"""
より堅牢なGUI版実行ファイル作成用スクリプト
互換性とエラー回避を重視した設定
"""

import subprocess
import sys
import os

def install_requirements():
    """必要なパッケージをインストール"""
    requirements = [
        'weasyprint',
        'requests',
        'beautifulsoup4',
        'pyinstaller',
        'pillow',  # 画像処理用
        'lxml'     # XML/HTML解析用
    ]

    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def create_spec_file():
    """PyInstallerの詳細設定ファイルを作成"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['url_to_pdf_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'weasyprint',
        'weasyprint.css',
        'weasyprint.html',
        'cairocffi',
        'cffi',
        'cssselect2',
        'tinycss2',
        'cairosvg',
        'pyphen',
        'fonttools',
        'html5lib',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        '_tkinter'
    ],
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
    name='URLtoPDF_GUI_Robust',
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
)
'''

    with open('URLtoPDF_GUI_Robust.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    return 'URLtoPDF_GUI_Robust.spec'

def build_robust_executable():
    """堅牢な実行ファイルをビルド"""
    script_name = 'url_to_pdf_gui.py'

    if not os.path.exists(script_name):
        print(f"エラー: {script_name} が見つかりません")
        return False

    print("詳細設定ファイルを作成中...")
    spec_file = create_spec_file()

    print("堅牢な実行ファイルをビルド中...")

    try:
        # specファイルを使用してビルド
        subprocess.check_call(['pyinstaller', spec_file])
        print("\n✓ ビルド成功!")
        print("実行ファイルは dist/URLtoPDF_GUI_Robust.exe に作成されました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ビルド失敗: {e}")
        return False

def build_compatible_executable():
    """互換性重視の代替ビルド"""
    script_name = 'url_to_pdf_gui.py'

    # より互換性の高い設定
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'URLtoPDF_GUI_Compatible',
        '--add-data', 'url_to_pdf_gui.py;.',
        '--hidden-import', 'weasyprint',
        '--hidden-import', 'requests',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'tkinter.messagebox',
        '--collect-all', 'weasyprint',
        '--collect-all', 'requests',
        script_name
    ]

    print("互換性重視版をビルド中...")
    print(f"コマンド: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n✓ 互換性版ビルド成功!")
        print("実行ファイルは dist/URLtoPDF_GUI_Compatible.exe に作成されました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 互換性版ビルド失敗: {e}")
        return False

def main():
    print("堅牢なGUI版Windows実行ファイル作成ツール")
    print("=" * 60)

    # 必要なパッケージをインストール
    try:
        install_requirements()
        print("\n必要なパッケージのインストールが完了しました")
    except Exception as e:
        print(f"パッケージインストールエラー: {e}")
        return

    print("\nビルドオプション:")
    print("1. 堅牢版 (推奨)")
    print("2. 互換性版")
    print("3. 両方")

    choice = input("\n選択してください (1/2/3): ").strip()

    if choice in ['1', '3']:
        print("\n--- 堅牢版ビルド ---")
        build_robust_executable()

    if choice in ['2', '3']:
        print("\n--- 互換性版ビルド ---")
        build_compatible_executable()

    print("\nトラブルシューティング:")
    print("- エラーが出る場合は互換性版を試してください")
    print("- それでも動かない場合は、対象PCにVisual C++ 再頒布可能パッケージをインストール")
    print("- セキュリティエラーの場合は「詳細情報」→「実行」をクリック")

if __name__ == "__main__":
    main()