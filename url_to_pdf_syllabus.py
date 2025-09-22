import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import requests
import subprocess
import sys
import datetime

class SyllabusPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("兵庫県立大学 シラバス PDF変換ツール")
        self.root.geometry("750x650")
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
                # Windowsでコマンドプロンプトウィンドウを表示しないように設定
                startupinfo = None
                if os.name == 'nt':  # Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, startupinfo=startupinfo)
                if result.returncode == 0:
                    return path
            except:
                continue
        return None

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        ttk.Label(main_frame, text="兵庫県立大学 シラバス PDF変換ツール",
                 font=("Yu Gothic", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # Status
        if self.wkhtmltopdf_path:
            status_text = "✅ wkhtmltopdf 検出済み - PDF変換可能"
            ttk.Label(main_frame, text=status_text, foreground="green").grid(row=1, column=0, columnspan=4, pady=(0, 15))
        else:
            status_text = "❌ wkhtmltopdf が見つかりません"
            ttk.Label(main_frame, text=status_text, foreground="red").grid(row=1, column=0, columnspan=4, pady=(0, 5))

            help_text = "インストール: https://wkhtmltopdf.org/downloads.html"
            ttk.Label(main_frame, text=help_text, foreground="blue").grid(row=2, column=0, columnspan=4, pady=(0, 15))

        # Year input
        year_frame = ttk.LabelFrame(main_frame, text="年度設定", padding="10")
        year_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(year_frame, text="年度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.year_var = tk.StringVar(value="2025")
        year_spinbox = ttk.Spinbox(year_frame, from_=2020, to=9999, textvariable=self.year_var, width=10)
        year_spinbox.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(year_frame, text="例: 2025年度のシラバスの場合は「2025」を入力",
                 foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))

        # File selection
        ttk.Label(main_frame, text="授業コードリストファイル:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.file_path_var, width=50).grid(row=4, column=1, columnspan=2, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=4, column=3, pady=5)

        # File format info
        info_text = "授業コードリスト形式: 1行1授業コード（例: ABC123, DEF456）"
        ttk.Label(main_frame, text=info_text, foreground="gray").grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        # Output directory
        ttk.Label(main_frame, text="PDF保存先ディレクトリ:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50).grid(row=6, column=1, columnspan=2, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=6, column=3, pady=5)

        # Convert button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=15)

        self.convert_button = ttk.Button(button_frame, text="シラバスPDF変換開始", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Progress
        progress_frame = ttk.LabelFrame(main_frame, text="進捗", padding="10")
        progress_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15)

        self.progress_var = tk.StringVar(value="待機中...")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10,0))

        # Log
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=90)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
        year_frame.columnconfigure(2, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def generate_syllabus_url(self, course_code, year):
        """授業コードと年度からシラバスURLを生成"""
        return f"https://syllabus.u-hyogo.ac.jp/slResult/{year}/japanese/syllabusHtml/SyllabusHtml.{year}.{course_code}.html"

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="授業コードリストファイルを選択してください",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(filename))
            self.log(f"授業コードリストファイル選択: {os.path.basename(filename)}")

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

            # Windowsでコマンドプロンプトウィンドウを表示しないように設定
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, startupinfo=startupinfo)
            return result.returncode == 0

        except Exception as e:
            self.log(f"    PDF変換エラー: {str(e)}")
            return False

    def start_conversion(self):
        if not self.wkhtmltopdf_path:
            messagebox.showerror("エラー", "wkhtmltopdf がインストールされていません。\n\nhttps://wkhtmltopdf.org/downloads.html\n\nからダウンロードしてインストールしてください。")
            return

        if not self.file_path_var.get():
            messagebox.showerror("エラー", "授業コードリストファイルを選択してください")
            return

        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("エラー", "授業コードリストファイルが見つかりません")
            return

        if not self.output_dir_var.get():
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        if not self.year_var.get():
            messagebox.showerror("エラー", "年度を入力してください")
            return

        try:
            year = int(self.year_var.get())
            if year < 2020:
                raise ValueError("年度は2020年以降で入力してください")
        except ValueError as e:
            messagebox.showerror("エラー", f"年度の入力が正しくありません: {e}")
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

            # 授業コードリストを読み込み
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as file:
                course_codes = [line.strip() for line in file.readlines() if line.strip()]

            if not course_codes:
                self.log("授業コードが見つかりませんでした")
                return

            year = self.year_var.get()
            total_codes = len(course_codes)
            self.progress_bar.config(maximum=total_codes)

            self.log(f"シラバスPDF変換開始: {total_codes}件の授業コード")
            self.log(f"対象年度: {year}年度")
            self.log(f"出力先: {self.output_dir_var.get()}")
            self.log("=" * 70)

            success_count = 0

            for i, course_code in enumerate(course_codes):
                if not self.converting:
                    self.log("変換が停止されました")
                    break

                self.progress_var.set(f"[{i+1}/{total_codes}] {course_code} 変換中...")
                self.progress_bar.config(value=i)

                try:
                    # URLを生成
                    url = self.generate_syllabus_url(course_code, year)

                    # ファイル名を生成（授業コード.pdf）
                    filename = f"{course_code}.pdf"
                    output_path = os.path.join(self.output_dir_var.get(), filename)

                    # 既存ファイルチェック
                    if os.path.exists(output_path):
                        self.log(f"[{i+1}/{total_codes}] スキップ（既存）: {course_code}")
                        success_count += 1
                        continue

                    self.log(f"[{i+1}/{total_codes}] 変換中: {course_code}")
                    self.log(f"    URL: {url}")

                    success = self.convert_url_to_pdf(url, output_path)

                    if success and os.path.exists(output_path):
                        file_size = os.path.getsize(output_path) / 1024
                        self.log(f"    ✓ 成功: {filename} ({file_size:.1f} KB)")
                        success_count += 1
                    else:
                        self.log(f"    ✗ 失敗: PDF作成エラー（シラバスが存在しない可能性）")

                except Exception as e:
                    self.log(f"[{i+1}/{total_codes}] エラー: {course_code} - {str(e)}")

            self.progress_bar.config(value=total_codes)
            self.progress_var.set("完了")

            self.log("=" * 70)
            self.log(f"シラバスPDF変換完了: {success_count}/{total_codes} 件のPDFを作成")

            if self.converting:
                messagebox.showinfo("完了", f"{success_count}/{total_codes} 件のシラバスPDFを作成しました")

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
        app = SyllabusPDFConverter(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました: {str(e)}")

if __name__ == "__main__":
    main()