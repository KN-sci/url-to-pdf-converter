"""
Windows 11専用 確実動作版実行ファイル作成スクリプト
64bit Windows 11環境での動作を保証
"""

import subprocess
import sys
import os
import platform

def check_environment():
    """実行環境をチェック"""
    print("実行環境チェック:")
    print(f"  Python version: {sys.version}")
    print(f"  Platform: {platform.platform()}")
    print(f"  Architecture: {platform.architecture()[0]}")
    print(f"  Machine: {platform.machine()}")

def install_requirements():
    """必要なパッケージをインストール"""
    print("\n=== パッケージインストール ===")

    # 基本要件
    base_requirements = [
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'pyinstaller>=6.0.0'
    ]

    # PDF生成ライブラリ（複数選択肢）
    pdf_requirements = [
        'weasyprint>=61.0',  # 推奨
        'reportlab>=4.0.0',  # フォールバック
        'pillow>=10.0.0'     # 画像サポート
    ]

    all_requirements = base_requirements + pdf_requirements

    for package in all_requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package,
                '--upgrade', '--no-cache-dir'
            ])
        except subprocess.CalledProcessError as e:
            print(f"  警告: {package} のインストールに失敗: {e}")

def create_advanced_spec():
    """高度なPyInstaller設定ファイルを作成"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
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
'''

    with open('URLtoPDF_Win11.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    return 'URLtoPDF_Win11.spec'

def create_version_info():
    """バージョン情報ファイルを作成"""
    version_content = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'041103A4',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'URL to PDF Converter for Windows 11'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'URLtoPDF_Win11'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'URLtoPDF_Win11.exe'),
        StringStruct(u'ProductName', u'URL to PDF Converter'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1041, 932])])
  ]
)
'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)

def build_win11_executable():
    """Windows 11専用実行ファイルをビルド"""
    script_name = 'url_to_pdf_gui_win11.py'

    if not os.path.exists(script_name):
        print(f"エラー: {script_name} が見つかりません")
        return False

    print("\n=== Windows 11専用実行ファイルビルド ===")

    # バージョン情報とspec ファイルを作成
    create_version_info()
    spec_file = create_advanced_spec()

    print("設定ファイルを作成しました:")
    print(f"  - {spec_file}")
    print("  - version_info.txt")

    # PyInstallerでビルド
    cmd = ['pyinstaller', '--clean', spec_file]

    print(f"\nビルドコマンド: {' '.join(cmd)}")
    print("ビルド開始...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n✅ ビルド成功!")
            print("実行ファイル: dist/URLtoPDF_Win11.exe")

            # ファイルサイズ確認
            exe_path = "dist/URLtoPDF_Win11.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"ファイルサイズ: {size_mb:.1f} MB")

            return True
        else:
            print("\n❌ ビルド失敗!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"\n❌ ビルドエラー: {e}")
        return False

def create_test_files():
    """テスト用ファイルを作成"""
    print("\n=== テスト用ファイル作成 ===")

    # サンプルURLリスト
    sample_urls = """https://www.google.com
https://www.microsoft.com
https://github.com"""

    with open('sample_urls_win11.txt', 'w', encoding='utf-8') as f:
        f.write(sample_urls)

    print("作成完了: sample_urls_win11.txt")

def main():
    print("=" * 60)
    print("Windows 11専用 URL to PDF Converter ビルダー")
    print("=" * 60)

    # 環境チェック
    check_environment()

    # 64bit Windows 11チェック
    if platform.system() != 'Windows':
        print("\n警告: Windows以外の環境です。Windows 11での動作は保証されません。")

    if platform.architecture()[0] != '64bit':
        print("\n警告: 32bit環境です。64bit Windows 11での動作は保証されません。")

    # 必要なパッケージをインストール
    install_requirements()

    # 実行ファイルをビルド
    success = build_win11_executable()

    if success:
        # テストファイル作成
        create_test_files()

        print("\n" + "=" * 60)
        print("✅ Windows 11専用実行ファイル作成完了!")
        print("=" * 60)
        print("\n配布方法:")
        print("1. dist/URLtoPDF_Win11.exe をWindows 11 PCにコピー")
        print("2. sample_urls_win11.txt もコピー（テスト用）")
        print("3. URLtoPDF_Win11.exe をダブルクリックで実行")
        print("\n特徴:")
        print("- Windows 11 64bit専用最適化")
        print("- 複数PDFエンジン対応（自動フォールバック）")
        print("- 詳細エラーログ機能")
        print("- モダンなGUIデザイン")

    else:
        print("\n❌ ビルドに失敗しました。")
        print("上記のエラーメッセージを確認してください。")

if __name__ == "__main__":
    main()