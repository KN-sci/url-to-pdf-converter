import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import re
import requests
from urllib.parse import urlparse
import weasyprint
from weasyprint import HTML, CSS

class URLtoPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("URL to PDF Converter")
        self.root.geometry("700x600")

        # 変換中フラグ
        self.converting = False

        self.create_widgets()

    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        title_label = ttk.Label(main_frame, text="URL to PDF Converter",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # URLリストファイル選択
        ttk.Label(main_frame, text="URLリストファイル:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=1, column=2, pady=5)

        # 出力ディレクトリ選択
        ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=2, column=2, pady=5)

        # オプション
        options_frame = ttk.LabelFrame(main_frame, text="オプション", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.skip_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="既存ファイルをスキップ",
                       variable=self.skip_existing_var).grid(row=0, column=0, sticky=tk.W)

        # 変換ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.convert_button = ttk.Button(button_frame, text="変換開始",
                                        command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止",
                                     command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 進捗表示
        progress_frame = ttk.LabelFrame(main_frame, text="進捗", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.progress_var = tk.StringVar(value="待機中...")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # ログ表示
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="URLリストファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            # 出力ディレクトリが未設定の場合、同じディレクトリを設定
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(filename))

    def select_output_dir(self):
        dirname = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dirname:
            self.output_dir_var.set(dirname)

    def log(self, message):
        """ログメッセージを表示"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def sanitize_filename(self, filename):
        """ファイル名から無効な文字を削除または置換する"""
        return re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)

    def extract_course_id_from_url(self, url):
        """URLからコースIDを抽出する"""
        match = re.search(r'SyllabusHtml\.2025\.([A-Za-z0-9]+)\.html', url)
        if match:
            return match.group(1)

        # syllabus形式でない場合は、URLから適当なファイル名を生成
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if filename and filename.endswith('.html'):
            return filename[:-5]
        elif filename:
            return filename
        else:
            path_parts = [part for part in parsed_url.path.split('/') if part]
            if path_parts:
                return path_parts[-1]
            else:
                return parsed_url.netloc.replace('.', '_')

    def convert_url_to_pdf(self, url, output_path):
        """WeasyPrintを使用してURLをPDFに変換する"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'

            # CSS for better PDF formatting
            css_style = CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: "Helvetica", "Arial", sans-serif;
                    font-size: 12pt;
                    line-height: 1.4;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
            """)

            html_doc = HTML(string=response.text, base_url=url)
            html_doc.write_pdf(output_path, stylesheets=[css_style])

            return True

        except Exception as e:
            self.log(f"    エラー: {str(e)}")
            return False

    def start_conversion(self):
        """変換処理を開始"""
        # 入力チェック
        if not self.file_path_var.get():
            messagebox.showerror("エラー", "URLリストファイルを選択してください")
            return

        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("エラー", "URLリストファイルが見つかりません")
            return

        if not self.output_dir_var.get():
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        # UIの状態を変更
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.converting = True

        # ログをクリア
        self.log_text.delete(1.0, tk.END)

        # 別スレッドで変換処理を実行
        self.conversion_thread = threading.Thread(target=self.conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def stop_conversion(self):
        """変換処理を停止"""
        self.converting = False
        self.log("停止が要求されました...")

    def conversion_worker(self):
        """変換処理のワーカー"""
        try:
            # 出力ディレクトリを作成
            os.makedirs(self.output_dir_var.get(), exist_ok=True)

            # URLリストを読み取る
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]

            if not urls:
                self.log("URLが見つかりませんでした")
                return

            total_urls = len(urls)
            self.progress_bar.config(maximum=total_urls)

            self.log(f"変換開始: {total_urls}個のURL")
            self.log(f"出力先: {self.output_dir_var.get()}")
            self.log("=" * 50)

            success_count = 0

            for i, url in enumerate(urls):
                if not self.converting:
                    self.log("変換が停止されました")
                    break

                # 進捗更新
                self.progress_var.set(f"[{i+1}/{total_urls}] 変換中...")
                self.progress_bar.config(value=i)

                try:
                    # ファイル名を生成
                    course_id = self.extract_course_id_from_url(url)
                    filename = self.sanitize_filename(f"{course_id}.pdf")
                    output_path = os.path.join(self.output_dir_var.get(), filename)

                    # 既存ファイルのスキップチェック
                    if self.skip_existing_var.get() and os.path.exists(output_path):
                        self.log(f"[{i+1}/{total_urls}] スキップ（既に存在）: {filename}")
                        success_count += 1
                        continue

                    self.log(f"[{i+1}/{total_urls}] 変換中: {url}")
                    self.log(f"    -> {filename}")

                    success = self.convert_url_to_pdf(url, output_path)

                    if success:
                        self.log("    ✓ 成功")
                        success_count += 1
                    else:
                        self.log("    ✗ 失敗")

                except Exception as e:
                    self.log(f"[{i+1}/{total_urls}] エラー: {str(e)}")

            # 完了
            self.progress_bar.config(value=total_urls)
            self.progress_var.set("完了")

            self.log("=" * 50)
            self.log(f"変換完了: {success_count}/{total_urls} 件のPDFを生成しました")

            if self.converting:  # 正常完了の場合
                messagebox.showinfo("完了", f"{success_count}/{total_urls} 件のPDFを生成しました")

        except Exception as e:
            self.log(f"エラーが発生しました: {str(e)}")
            messagebox.showerror("エラー", f"エラーが発生しました: {str(e)}")

        finally:
            # UIの状態を戻す
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.converting = False

def main():
    root = tk.Tk()
    app = URLtoPDFConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()