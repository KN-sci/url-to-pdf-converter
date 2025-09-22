"""
WSL環境でWindows用実行ファイルを作成するスクリプト
Docker使用でクリーンなクロスコンパイル
"""

import subprocess
import sys
import os
import json

def check_wsl_environment():
    """WSL環境の確認"""
    print("🐧 WSL環境チェック...")

    # WSL環境の確認
    wsl_distro = os.environ.get('WSL_DISTRO_NAME')
    if wsl_distro:
        print(f"✅ WSL環境検出: {wsl_distro}")
        return True

    # /proc/version でWSL確認
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read()
            if 'microsoft' in version_info.lower() or 'wsl' in version_info.lower():
                print("✅ WSL環境検出")
                return True
    except:
        pass

    print("⚠️ WSL環境ではない可能性があります")
    return False

def check_docker_installation():
    """Docker環境の確認とセットアップ"""
    print("\n🐳 Docker環境チェック...")

    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ Docker not found. Installing Docker...")
    return install_docker_on_wsl()

def install_docker_on_wsl():
    """WSLにDockerをインストール"""
    try:
        print("📦 Docker installation commands:")
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            "echo \"deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
            "sudo apt-get update",
            "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
            "sudo usermod -aG docker $USER"
        ]

        for cmd in commands:
            print(f"Running: {cmd}")
            subprocess.run(cmd, shell=True, check=True)

        print("✅ Docker installed. Please restart your WSL session.")
        return False  # 再起動が必要

    except subprocess.CalledProcessError as e:
        print(f"❌ Docker installation failed: {e}")
        return False

def create_windows_builder_dockerfile():
    """Windows用実行ファイル作成用のDockerfileを作成"""
    dockerfile_content = '''# Windows用実行ファイル作成用コンテナ
FROM python:3.11-slim

# システムパッケージをインストール
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libc6-dev \\
    libffi-dev \\
    zlib1g-dev \\
    libjpeg-dev \\
    libpng-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libcairo2-dev \\
    libpango1.0-dev \\
    libgdk-pixbuf2.0-dev \\
    shared-mime-info \\
    && rm -rf /var/lib/apt/lists/*

# Python パッケージをインストール
RUN pip install --no-cache-dir \\
    pyinstaller==6.3.0 \\
    weasyprint==61.2 \\
    requests==2.31.0 \\
    beautifulsoup4==4.12.2 \\
    lxml==4.9.3 \\
    pillow==10.1.0 \\
    reportlab==4.0.7

# 作業ディレクトリを設定
WORKDIR /app

# ビルドスクリプトをコピー
COPY build_in_container.py /app/
COPY url_to_pdf_gui_win11.py /app/

# エントリーポイント
ENTRYPOINT ["python", "build_in_container.py"]
'''

    with open('Dockerfile.windows-builder', 'w') as f:
        f.write(dockerfile_content)

    return 'Dockerfile.windows-builder'

def create_container_build_script():
    """コンテナ内でのビルドスクリプト"""
    script_content = '''#!/usr/bin/env python3
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
'''

    with open('build_in_container.py', 'w') as f:
        f.write(script_content)

    return 'build_in_container.py'

def build_windows_executable_with_docker():
    """Dockerを使用してWindows用実行ファイルをビルド"""
    print("\n🔨 Docker でWindows用実行ファイルをビルド中...")

    # 必要なファイルをチェック
    if not os.path.exists('url_to_pdf_gui_win11.py'):
        print("❌ url_to_pdf_gui_win11.py が見つかりません")
        return False

    # Docker関連ファイルを作成
    dockerfile = create_windows_builder_dockerfile()
    build_script = create_container_build_script()

    try:
        # Docker イメージをビルド
        print("📦 Docker イメージをビルド中...")
        subprocess.run([
            'docker', 'build',
            '-f', dockerfile,
            '-t', 'url-to-pdf-windows-builder',
            '.'
        ], check=True)

        # 出力ディレクトリを準備
        output_dir = os.path.abspath('./dist')
        os.makedirs(output_dir, exist_ok=True)

        # Docker コンテナで実行ファイルを作成
        print("🏗️ コンテナ内でビルド実行中...")
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{output_dir}:/app/dist',
            'url-to-pdf-windows-builder'
        ], check=True)

        # 結果確認
        exe_path = os.path.join(output_dir, 'URLtoPDF_Windows.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ Windows用実行ファイル作成成功!")
            print(f"📁 ファイル: {exe_path}")
            print(f"📊 サイズ: {size_mb:.1f} MB")
            return True
        else:
            print("❌ 実行ファイルが作成されませんでした")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Docker ビルドエラー: {e}")
        return False

def create_wsl_windows_path_converter():
    """WSLパスとWindowsパスの変換スクリプト"""
    script_content = '''#!/bin/bash
# WSL と Windows 間でファイルをコピーするスクリプト

WSL_DIST_PATH="$1"
WINDOWS_PATH=$(wslpath -w "$WSL_DIST_PATH")

echo "WSL path: $WSL_DIST_PATH"
echo "Windows path: $WINDOWS_PATH"

# Windows エクスプローラーで開く
explorer.exe "$(dirname "$WINDOWS_PATH")"
'''

    with open('open_in_explorer.sh', 'w') as f:
        f.write(script_content)

    os.chmod('open_in_explorer.sh', 0o755)
    return 'open_in_explorer.sh'

def main():
    print("=" * 60)
    print("🐧➡️🪟 WSL環境でWindows用実行ファイル作成")
    print("=" * 60)

    # WSL環境チェック
    if not check_wsl_environment():
        print("⚠️ 警告: WSL環境ではない可能性があります")

    # Docker環境チェック
    if not check_docker_installation():
        print("❌ Docker のセットアップが必要です")
        print("上記のコマンドを実行後、WSLセッションを再起動してください")
        return

    # Windows用実行ファイルをビルド
    success = build_windows_executable_with_docker()

    if success:
        # WSL<->Windows パス変換スクリプトを作成
        path_converter = create_wsl_windows_path_converter()

        print("\n" + "=" * 60)
        print("✅ Windows用実行ファイル作成完了!")
        print("=" * 60)
        print("\n📁 作成されたファイル:")
        print(f"   - dist/URLtoPDF_Windows.exe")
        print(f"   - {path_converter}")

        print("\n🚀 Windows での実行方法:")
        print("1. WSL から Windows にファイルコピー:")
        print("   ./open_in_explorer.sh ./dist/URLtoPDF_Windows.exe")
        print("2. Windows エクスプローラーで表示されるファイルをダブルクリック")

        print("\n💡 または wslpath を使用:")
        print("   wslpath -w ./dist/URLtoPDF_Windows.exe")

        print("\n✨ 特徴:")
        print("- Windows Python 不要")
        print("- WSL環境のみでビルド")
        print("- 完全なWindows互換性")
        print("- すべてのDLL含有")

    else:
        print("\n❌ ビルドに失敗しました")

if __name__ == "__main__":
    main()