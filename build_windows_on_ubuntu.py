"""
Ubuntu環境でWindows用実行ファイルを作成するスクリプト
クロスコンパイル対応
"""

import subprocess
import sys
import os
import platform

def check_wine_installation():
    """Wine（Windows互換レイヤー）の確認"""
    try:
        result = subprocess.run(['wine', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Wine installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("Wine not found. Installing Wine...")
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'wine'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Wine installation failed.")
        return False

def install_windows_python_via_wine():
    """Wine経由でWindows版Pythonをインストール"""
    print("Installing Windows Python via Wine...")

    # Python for Windows インストーラーをダウンロード
    python_installer = "python-3.11.0-amd64.exe"
    download_url = f"https://www.python.org/ftp/python/3.11.0/{python_installer}"

    try:
        # ダウンロード
        subprocess.run(['wget', download_url], check=True)

        # Wine経由でインストール
        subprocess.run(['wine', python_installer, '/quiet'], check=True)

        print("Windows Python installed via Wine")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Windows Python installation failed: {e}")
        return False

def create_windows_spec_file():
    """Windows専用specファイルを作成"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Ubuntu環境でWindows用実行ファイル作成用設定

block_cipher = None

a = Analysis(
    ['url_to_pdf_gui_win11.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
        'tkinter.messagebox', 'tkinter.scrolledtext',
        'weasyprint', 'requests', 'beautifulsoup4',
        'lxml', 'PIL', 'reportlab'
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
    name='URLtoPDF_Windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open('URLtoPDF_Windows.spec', 'w') as f:
        f.write(spec_content)

    return 'URLtoPDF_Windows.spec'

def build_with_docker():
    """Docker を使用してWindows用実行ファイルを作成"""
    dockerfile_content = '''FROM ubuntu:22.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    wine \\
    wget \\
    xvfb

# Python パッケージをインストール
RUN pip3 install pyinstaller weasyprint requests beautifulsoup4 lxml pillow reportlab

# 作業ディレクトリを設定
WORKDIR /app

# スクリプトをコピー
COPY url_to_pdf_gui_win11.py .
COPY URLtoPDF_Windows.spec .

# Windows用実行ファイルを作成
RUN pyinstaller URLtoPDF_Windows.spec

# 出力ディレクトリを作成
RUN mkdir -p /output

CMD ["cp", "dist/URLtoPDF_Windows", "/output/URLtoPDF_Windows.exe"]
'''

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    print("Building Windows executable using Docker...")

    try:
        # Docker イメージをビルド
        subprocess.run(['docker', 'build', '-t', 'url-to-pdf-builder', '.'], check=True)

        # コンテナを実行して実行ファイルを作成
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/dist:/output',
            'url-to-pdf-builder'
        ], check=True)

        print("Windows executable created successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Docker build failed: {e}")
        return False

def create_simple_cross_platform_version():
    """シンプルなクロスプラットフォーム対応版を作成"""
    print("Creating cross-platform compatible version...")

    # PyInstaller でプラットフォーム固有の設定
    commands = {
        'linux': [
            'pyinstaller', '--onefile', '--name', 'URLtoPDF_Linux',
            'url_to_pdf_gui_win11.py'
        ],
        'windows_simulation': [
            'pyinstaller', '--onefile', '--windowed',
            '--name', 'URLtoPDF_Windows.exe',
            '--target-arch', 'x86_64',
            'url_to_pdf_gui_win11.py'
        ]
    }

    print("Building Linux version...")
    try:
        subprocess.run(commands['linux'], check=True)
        print("✅ Linux version created: dist/URLtoPDF_Linux")
    except subprocess.CalledProcessError as e:
        print(f"❌ Linux build failed: {e}")

    print("\nAttempting Windows-compatible build...")
    try:
        subprocess.run(commands['windows_simulation'], check=True)
        print("✅ Windows-style executable created: dist/URLtoPDF_Windows.exe")
        print("   注意: Ubuntu環境で作成されたため、Windows DLLは含まれていません")
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows simulation build failed: {e}")

def main():
    print("=" * 60)
    print("Ubuntu環境でWindows用実行ファイル作成ツール")
    print("=" * 60)

    print(f"Current platform: {platform.system()} {platform.machine()}")

    print("\n選択してください:")
    print("1. シンプル版（Linux実行ファイル + Windows形式ファイル）")
    print("2. Docker使用（推奨：完全なWindows互換性）")
    print("3. Wine使用（上級者向け）")

    choice = input("\n選択 (1/2/3): ").strip()

    if choice == "1":
        create_simple_cross_platform_version()

        print("\n" + "=" * 50)
        print("作成されたファイル:")
        print("- dist/URLtoPDF_Linux (Linux用)")
        print("- dist/URLtoPDF_Windows.exe (Windows形式、但しLinux環境で作成)")
        print("\n⚠️ 注意:")
        print("Ubuntu環境で作成したファイルは、Windows固有のDLLを含みません。")
        print("Windows用実行ファイルは、Windows環境で作成することを推奨します。")

    elif choice == "2":
        if not os.path.exists('url_to_pdf_gui_win11.py'):
            print("❌ url_to_pdf_gui_win11.py が見つかりません")
            return

        spec_file = create_windows_spec_file()
        build_with_docker()

    elif choice == "3":
        if check_wine_installation():
            if install_windows_python_via_wine():
                print("Wine経由でのビルドが可能です")
            else:
                print("Wine環境のセットアップに失敗しました")
        else:
            print("Wine のインストールに失敗しました")

    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()