#!/usr/bin/env python3
"""
シンプルなWindows用実行ファイル作成
"""

import subprocess
import os

def main():
    print("🔨 シンプルなWindows用実行ファイルをビルド中...")

    try:
        # 最小限の設定でPyInstaller実行
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', 'URLtoPDF_Windows_Simple',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'tkinter.ttk',
            '--hidden-import', 'tkinter.filedialog',
            '--hidden-import', 'tkinter.messagebox',
            '--hidden-import', 'requests',
            '--hidden-import', 'beautifulsoup4',
            'url_to_pdf_gui_win11.py'
        ], check=True)

        # 結果確認
        exe_path = '/app/dist/URLtoPDF_Windows_Simple'
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
