import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import requests
from urllib.parse import urlparse
import subprocess
import sys
import tempfile
import datetime

class PDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("URL to PDF Converter - wkhtmltopdf版")
        self.root.geometry("700x600")
        self.converting = False
        self.wkhtmltopdf_path = self.find_wkhtmltopdf()
        self.create_widgets()

    def find_wkhtmltopdf(self):
        """wkhtmltopdfの場所を探す"""
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"wkhtmltopdf.exe"  # PATH環境変数にある場合
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        return None

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        ttk.Label(main_frame, text="URL to PDF Converter",
                 font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Status
        if self.wkhtmltopdf_path:
            status_text = "✅ wkhtmltopdf 検出済み - PDF変換可能"
            ttk.Label(main_frame, text=status_text, foreground="green").grid(row=1, column=0, columnspan=3, pady=(0, 15))
        else:
            status_text = "❌ wkhtmltopdf が見つかりません"
            ttk.Label(main_frame, text=status_text, foreground="red").grid(row=1, column=0, columnspan=3, pady=(0, 5))

            help_text = "インストール: https://wkhtmltopdf.org/downloads.html"
            ttk.Label(main_frame, text=help_text, foreground="blue").grid(row=2, column=0, columnspan=3, pady=(0, 15))

        # File selection
        ttk.Label(main_frame, text="URLリストファイル:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.file_path_var, width=60).grid(row=3, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=3, column=2, pady=5)

        # Output directory
        ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=60).grid(row=4, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=4, column=2, pady=5)

        # Convert button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=15)

        self.convert_button = ttk.Button(button_frame, text="PDF変換開始", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Progress
        progress_frame = ttk.LabelFrame(main_frame, text="進捗", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)

        self.progress_var = tk.StringVar(value="待機中...")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10,0))

        # Log
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=85)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="URLリストファイルを選択してください",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(filename))
            self.log(f"URLリストファイル選択: {os.path.basename(filename)}")

    def select_output_dir(self):
        dirname = filedialog.askdirectory(title="PDF保存先ディレクトリを選択してください")
        if dirname:
            self.output_dir_var.set(dirname)
            self.log(f"出力ディレクトリ選択: {dirname}")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def convert_url_to_pdf(self, url, output_path):
        """wkhtmltopdfを使用してPDF変換"""
        try:
            if not self.wkhtmltopdf_path:
                return False

            cmd = [
                self.wkhtmltopdf_path,
                "--page-size", "A4",
                "--orientation", "Portrait",
                "--margin-top", "0.75in",
                "--margin-right", "0.75in",
                "--margin-bottom", "0.75in",
                "--margin-left", "0.75in",
                "--encoding", "UTF-8",
                "--load-error-handling", "ignore",
                "--load-media-error-handling", "ignore",
                "--quiet",
                url,
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0

        except Exception as e:
            self.log(f"    PDF変換エラー: {str(e)}")
            return False

    def start_conversion(self):
        if not self.wkhtmltopdf_path:
            messagebox.showerror("エラー", "wkhtmltopdf がインストールされていません。\n\nhttps://wkhtmltopdf.org/downloads.html\n\nからダウンロードしてインストールしてください。")
            return

        if not self.file_path_var.get():
            messagebox.showerror("エラー", "URLリストファイルを選択してください")
            return

        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("エラー", "URLリストファイルが見つかりません")
            return

        if not self.output_dir_var.get():
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.converting = True

        self.log_text.delete(1.0, tk.END)
        self.conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.conversion_thread.start()

    def stop_conversion(self):
        self.converting = False
        self.log("停止が要求されました...")

    def conversion_worker(self):
        try:
            os.makedirs(self.output_dir_var.get(), exist_ok=True)

            with open(self.file_path_var.get(), 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]

            if not urls:
                self.log("URLが見つかりませんでした")
                return

            total_urls = len(urls)
            self.progress_bar.config(maximum=total_urls)

            self.log(f"PDF変換開始: {total_urls}個のURL")
            self.log(f"出力先: {self.output_dir_var.get()}")
            self.log("=" * 60)

            success_count = 0

            for i, url in enumerate(urls):
                if not self.converting:
                    self.log("変換が停止されました")
                    break

                self.progress_var.set(f"[{i+1}/{total_urls}] PDF変換中...")
                self.progress_bar.config(value=i)

                try:
                    # ファイル名を生成
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path) or f"page_{i+1}"
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'

                    # 安全なファイル名に変換
                    filename = "".join(c for c in filename if c.isalnum() or c in '.-_').rstrip()
                    if not filename:
                        filename = f"page_{i+1}.pdf"

                    output_path = os.path.join(self.output_dir_var.get(), filename)

                    # 既存ファイルチェック
                    if os.path.exists(output_path):
                        self.log(f"[{i+1}/{total_urls}] スキップ（既存）: {filename}")
                        success_count += 1
                        continue

                    self.log(f"[{i+1}/{total_urls}] PDF変換中: {url}")
                    success = self.convert_url_to_pdf(url, output_path)

                    if success and os.path.exists(output_path):
                        file_size = os.path.getsize(output_path) / 1024
                        self.log(f"    ✓ 成功: {filename} ({file_size:.1f} KB)")
                        success_count += 1
                    else:
                        self.log(f"    ✗ 失敗: PDF作成エラー")

                except Exception as e:
                    self.log(f"[{i+1}/{total_urls}] エラー: {str(e)}")

            self.progress_bar.config(value=total_urls)
            self.progress_var.set("完了")

            self.log("=" * 60)
            self.log(f"PDF変換完了: {success_count}/{total_urls} 件のPDFを作成")

            if self.converting:
                messagebox.showinfo("完了", f"{success_count}/{total_urls} 件のPDFを作成しました")

        except Exception as e:
            self.log(f"予期しないエラー: {str(e)}")
            messagebox.showerror("エラー", f"予期しないエラー: {str(e)}")

        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.converting = False

def main():
    try:
        root = tk.Tk()
        app = PDFConverter(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました: {str(e)}")

if __name__ == "__main__":
    main()