import tkinter as tk
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
        self.log_text.insert(tk.END, message + "\n")
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
