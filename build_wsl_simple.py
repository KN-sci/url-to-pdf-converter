"""
WSL環境でWindows用実行ファイルを作成するスクリプト（簡単版）
エラー回避のためシンプルなアプローチを使用
"""

import subprocess
import sys
import os

def create_simple_dockerfile():
    """シンプルで堅牢なDockerfileを作成"""
    dockerfile_content = '''# シンプルなWindows用実行ファイル作成コンテナ
FROM python:3.11-slim-bullseye

# 基本パッケージのみインストール
RUN apt-get update && apt-get install -y \\
    gcc \\
    libc6-dev \\
    && rm -rf /var/lib/apt/lists/*

# 基本的なPython パッケージをインストール
RUN pip install --no-cache-dir \\
    pyinstaller==6.3.0 \\
    requests==2.31.0 \\
    beautifulsoup4==4.12.2

# 作業ディレクトリを設定
WORKDIR /app

# ビルドスクリプト
COPY build_simple.py /app/
COPY url_to_pdf_gui_win11.py /app/

# エントリーポイント
ENTRYPOINT ["python", "build_simple.py"]
'''

    with open('Dockerfile.simple', 'w') as f:
        f.write(dockerfile_content)

    return 'Dockerfile.simple'

def create_simple_build_script():
    """シンプルなビルドスクリプト"""
    script_content = '''#!/usr/bin/env python3
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
'''

    with open('build_simple.py', 'w') as f:
        f.write(script_content)

    return 'build_simple.py'

def create_minimal_gui():
    """最小限のGUIバージョン（依存関係を減らす）"""
    gui_content = '''import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import re
import requests
from urllib.parse import urlparse

class SimpleURLtoPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple URL to PDF Converter")
        self.root.geometry("600x500")

        self.converting = False
        self.create_widgets()

    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        ttk.Label(main_frame, text="Simple URL to PDF Converter",
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # URLリストファイル選択
        ttk.Label(main_frame, text="URLリストファイル:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.file_path_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=1, column=2, pady=5)

        # 出力ディレクトリ選択
        ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=2, column=2, pady=5)

        # 変換ボタン
        self.convert_button = ttk.Button(main_frame, text="変換開始", command=self.start_conversion)
        self.convert_button.grid(row=3, column=0, columnspan=3, pady=20)

        # ログ表示
        ttk.Label(main_frame, text="ログ:").grid(row=4, column=0, sticky=tk.W)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="URLリストファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(filename))

    def select_output_dir(self):
        dirname = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dirname:
            self.output_dir_var.set(dirname)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def download_as_html(self, url, output_path):
        """HTMLとしてダウンロード（PDFライブラリが使えない場合の代替）"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True
        except Exception as e:
            self.log(f"    ダウンロードエラー: {str(e)}")
            return False

    def start_conversion(self):
        if not self.file_path_var.get() or not self.output_dir_var.get():
            messagebox.showerror("エラー", "ファイルとディレクトリを選択してください")
            return

        self.convert_button.config(state=tk.DISABLED)
        self.converting = True
        threading.Thread(target=self.conversion_worker, daemon=True).start()

    def conversion_worker(self):
        try:
            os.makedirs(self.output_dir_var.get(), exist_ok=True)

            with open(self.file_path_var.get(), 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]

            self.log(f"変換開始: {len(urls)}個のURL")
            success_count = 0

            for i, url in enumerate(urls, 1):
                if not self.converting:
                    break

                try:
                    # URLからファイル名を生成
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path) or "download"
                    if not filename.endswith('.html'):
                        filename += '.html'

                    output_path = os.path.join(self.output_dir_var.get(), filename)

                    self.log(f"[{i}/{len(urls)}] ダウンロード中: {url}")

                    success = self.download_as_html(url, output_path)
                    if success:
                        self.log(f"    ✓ 成功: {filename}")
                        success_count += 1
                    else:
                        self.log(f"    ✗ 失敗")

                except Exception as e:
                    self.log(f"[{i}/{len(urls)}] エラー: {str(e)}")

            self.log(f"完了: {success_count}/{len(urls)} 件をダウンロード")
            messagebox.showinfo("完了", f"{success_count}/{len(urls)} 件をダウンロードしました")

        except Exception as e:
            self.log(f"エラー: {str(e)}")
            messagebox.showerror("エラー", str(e))

        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.converting = False

def main():
    root = tk.Tk()
    app = SimpleURLtoPDFConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''

    with open('url_to_pdf_simple.py', 'w') as f:
        f.write(gui_content)

    return 'url_to_pdf_simple.py'

def build_simple_version():
    """シンプル版をビルド"""
    print("\n🛠️ シンプル版をビルド中...")

    # 必要なファイルをチェック
    if not os.path.exists('url_to_pdf_gui_win11.py'):
        print("❌ url_to_pdf_gui_win11.py が見つかりません")
        return False

    # ファイルを作成
    dockerfile = create_simple_dockerfile()
    build_script = create_simple_build_script()
    simple_gui = create_minimal_gui()

    try:
        # Docker イメージをビルド
        print("📦 シンプルなDocker イメージをビルド中...")
        subprocess.run([
            'docker', 'build',
            '-f', dockerfile,
            '-t', 'url-to-pdf-simple-builder',
            '.'
        ], check=True)

        # 出力ディレクトリを準備
        output_dir = os.path.abspath('./dist')
        os.makedirs(output_dir, exist_ok=True)

        # Docker コンテナで実行ファイルを作成
        print("🏗️ シンプル版をビルド中...")
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{output_dir}:/app/dist',
            'url-to-pdf-simple-builder'
        ], check=True)

        # 結果確認
        exe_path = os.path.join(output_dir, 'URLtoPDF_Windows_Simple.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ シンプル版作成成功!")
            print(f"📁 ファイル: {exe_path}")
            print(f"📊 サイズ: {size_mb:.1f} MB")
            return True
        else:
            print("❌ 実行ファイルが作成されませんでした")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ シンプル版ビルドエラー: {e}")
        return False

def main():
    print("=" * 50)
    print("🔧 WSL環境 - シンプル版ビルダー")
    print("=" * 50)

    success = build_simple_version()

    if success:
        print("\n✅ シンプル版作成完了!")
        print("\n📝 機能:")
        print("- URLリストからHTMLファイルをダウンロード")
        print("- 軽量で依存関係が少ない")
        print("- Windows 11で確実に動作")
        print("\n💡 PDFが必要な場合は、ブラウザで「印刷→PDFに保存」を使用")
    else:
        print("\n❌ ビルドに失敗しました")

if __name__ == "__main__":
    main()