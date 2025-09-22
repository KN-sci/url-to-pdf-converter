"""
GUI版実行ファイル作成用スクリプト
PyInstallerを使用してurl_to_pdf_gui.pyを実行ファイルに変換します
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
        'pyinstaller'
    ]

    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def build_gui_executable():
    """GUI実行ファイルをビルド"""
    script_name = 'url_to_pdf_gui.py'

    if not os.path.exists(script_name):
        print(f"エラー: {script_name} が見つかりません")
        return False

    # PyInstallerコマンドを構築
    cmd = [
        'pyinstaller',
        '--onefile',                # 単一の実行ファイル
        '--windowed',               # GUIアプリケーション（コンソールウィンドウなし）
        '--name', 'URLtoPDF_GUI',   # 実行ファイル名
        '--icon=NONE',              # アイコン指定（必要に応じて変更）
        script_name
    ]

    print("GUI実行ファイルをビルド中...")
    print(f"コマンド: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n✓ ビルド成功!")
        print("実行ファイルは dist/URLtoPDF_GUI.exe に作成されました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ビルド失敗: {e}")
        return False

def main():
    print("GUI版Windows実行ファイル作成ツール")
    print("=" * 50)

    # 必要なパッケージをインストール
    try:
        install_requirements()
        print("\n必要なパッケージのインストールが完了しました")
    except Exception as e:
        print(f"パッケージインストールエラー: {e}")
        return

    # 実行ファイルをビルド
    success = build_gui_executable()

    if success:
        print("\n使用方法:")
        print("1. dist/URLtoPDF_GUI.exe をWindows PCにコピー")
        print("2. URLtoPDF_GUI.exe をダブルクリックで実行")
        print("3. GUIでファイルを選択して変換開始")
        print("\n特徴:")
        print("- ファイル選択ダイアログ")
        print("- リアルタイム進捗表示")
        print("- ログ表示機能")
        print("- 変換停止機能")

if __name__ == "__main__":
    main()