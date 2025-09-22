"""
Windows実行ファイル作成用スクリプト
PyInstallerを使用してurl_to_pdf_converter.pyを実行ファイルに変換します
"""

import subprocess
import sys
import os

def install_requirements():
    """必要なパッケージをインストール"""
    requirements = [
        'pdfkit',
        'beautifulsoup4',
        'pyinstaller'
    ]

    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def build_executable():
    """実行ファイルをビルド"""
    script_name = 'url_to_pdf_converter.py'

    if not os.path.exists(script_name):
        print(f"エラー: {script_name} が見つかりません")
        return False

    # PyInstallerコマンドを構築
    cmd = [
        'pyinstaller',
        '--onefile',           # 単一の実行ファイル
        '--console',           # コンソールアプリケーション
        '--name', 'URLtoPDF',  # 実行ファイル名
        script_name
    ]

    print("実行ファイルをビルド中...")
    print(f"コマンド: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n✓ ビルド成功!")
        print("実行ファイルは dist/URLtoPDF.exe に作成されました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ビルド失敗: {e}")
        return False

def main():
    print("Windows実行ファイル作成ツール")
    print("=" * 40)

    # 必要なパッケージをインストール
    try:
        install_requirements()
        print("\n必要なパッケージのインストールが完了しました")
    except Exception as e:
        print(f"パッケージインストールエラー: {e}")
        return

    # 実行ファイルをビルド
    success = build_executable()

    if success:
        print("\n使用方法:")
        print("1. dist/URLtoPDF.exe をWindows PCにコピー")
        print("2. URLリストのテキストファイルを準備")
        print("3. URLtoPDF.exe を実行")
        print("\nまたは、コマンドラインで:")
        print("URLtoPDF.exe urls.txt output_folder")

if __name__ == "__main__":
    main()