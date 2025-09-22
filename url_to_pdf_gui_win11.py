import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import re
import sys
import traceback
import logging
from datetime import datetime

# Windows 11対応のためのインポート
try:
    import requests
    from urllib.parse import urlparse
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# PDF生成ライブラリ（複数の選択肢）
PDF_LIBRARIES = []

try:
    import weasyprint
    from weasyprint import HTML, CSS
    PDF_LIBRARIES.append('weasyprint')
except ImportError:
    pass

try:
    import pdfkit
    PDF_LIBRARIES.append('pdfkit')
except ImportError:
    pass

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from bs4 import BeautifulSoup
    PDF_LIBRARIES.append('reportlab')
except ImportError:
    pass

class URLtoPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("URL to PDF Converter - Windows 11")
        self.root.geometry("800x700")

        # Windows 11スタイル設定
        self.setup_windows11_style()

        # ログ設定
        self.setup_logging()

        # 変換中フラグ
        self.converting = False
        self.stop_requested = False

        # 利用可能なPDFライブラリをチェック
        self.available_libraries = PDF_LIBRARIES
        if not self.available_libraries:
            messagebox.showerror("エラー", "PDFライブラリが見つかりません。\nweasyprint, pdfkit, または reportlab が必要です。")
            sys.exit(1)

        self.create_widgets()
        self.log_system_info()

    def setup_windows11_style(self):
        """Windows 11スタイルの設定"""
        try:
            # Windows 11のテーマカラーに近い設定
            style = ttk.Style()
            style.theme_use('winnative')

            # カスタムスタイル定義
            style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
            style.configure('Heading.TLabel', font=('Segoe UI', 10, 'bold'))
            style.configure('Info.TLabel', font=('Segoe UI', 9))

        except Exception as e:
            print(f"Style setup warning: {e}")

    def setup_logging(self):
        """ログ設定"""
        log_filename = f"url_to_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_system_info(self):
        """システム情報をログに記録"""
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        self.logger.info(f"Available PDF libraries: {self.available_libraries}")

    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        title_label = ttk.Label(main_frame, text="URL to PDF Converter", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # サブタイトル
        subtitle_label = ttk.Label(main_frame, text="Windows 11 Compatible Version", style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # ライブラリ情報表示
        lib_info = f"使用可能なPDFエンジン: {', '.join(self.available_libraries)}"
        ttk.Label(main_frame, text=lib_info, style='Info.TLabel').grid(row=2, column=0, columnspan=3, pady=(0, 15))

        # URLリストファイル選択
        ttk.Label(main_frame, text="URLリストファイル:", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=60, font=('Segoe UI', 9))
        file_entry.grid(row=3, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=3, column=2, pady=5)

        # 出力ディレクトリ選択
        ttk.Label(main_frame, text="出力ディレクトリ:", style='Heading.TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=60, font=('Segoe UI', 9))
        output_entry.grid(row=4, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=4, column=2, pady=5)

        # オプション
        options_frame = ttk.LabelFrame(main_frame, text="オプション", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)

        self.skip_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="既存ファイルをスキップ",
                       variable=self.skip_existing_var).grid(row=0, column=0, sticky=tk.W)

        self.detailed_log_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="詳細ログを表示",
                       variable=self.detailed_log_var).grid(row=0, column=1, sticky=tk.W, padx=20)

        # PDFライブラリ選択
        ttk.Label(options_frame, text="PDFエンジン:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.pdf_library_var = tk.StringVar(value=self.available_libraries[0])
        library_combo = ttk.Combobox(options_frame, textvariable=self.pdf_library_var,
                                   values=self.available_libraries, state="readonly", width=15)
        library_combo.grid(row=1, column=1, sticky=tk.W, padx=20, pady=(10,0))

        # 変換ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=15)

        self.convert_button = ttk.Button(button_frame, text="変換開始",
                                        command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止",
                                     command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # 進捗表示
        progress_frame = ttk.LabelFrame(main_frame, text="進捗状況", padding="10")
        progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)

        self.progress_var = tk.StringVar(value="待機中...")
        ttk.Label(progress_frame, textvariable=self.progress_var, style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10,0))

        # ログ表示
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=90,
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="URLリストファイルを選択してください",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if filename:
            self.file_path_var.set(filename)
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(filename))
            self.log(f"URLリストファイルを選択: {filename}")

    def select_output_dir(self):
        dirname = filedialog.askdirectory(
            title="PDF保存先ディレクトリを選択してください",
            initialdir=os.path.expanduser("~")
        )
        if dirname:
            self.output_dir_var.set(dirname)
            self.log(f"出力ディレクトリを選択: {dirname}")

    def log(self, message):
        """ログメッセージを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

        # ファイルログにも記録
        self.logger.info(message)

    def sanitize_filename(self, filename):
        """ファイル名から無効な文字を削除"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def extract_course_id_from_url(self, url):
        """URLからコースIDを抽出"""
        # シラバス形式
        match = re.search(r'SyllabusHtml\.2025\.([A-Za-z0-9]+)\.html', url)
        if match:
            return match.group(1)

        # その他のURL
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

    def convert_url_to_pdf_weasyprint(self, url, output_path):
        """WeasyPrintでPDF変換"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'

            css_style = CSS(string="""
                @page { size: A4; margin: 2cm; }
                body { font-family: "Yu Gothic", "Meiryo", sans-serif; font-size: 12pt; line-height: 1.4; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            """)

            html_doc = HTML(string=response.text, base_url=url)
            html_doc.write_pdf(output_path, stylesheets=[css_style])
            return True

        except Exception as e:
            self.log(f"    WeasyPrint変換エラー: {str(e)}")
            return False

    def convert_url_to_pdf_pdfkit(self, url, output_path):
        """pdfkitでPDF変換"""
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8"
            }
            pdfkit.from_url(url, output_path, options=options)
            return True
        except Exception as e:
            self.log(f"    pdfkit変換エラー: {str(e)}")
            return False

    def convert_url_to_pdf_reportlab(self, url, output_path):
        """ReportLabでPDF変換（フォールバック）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            paragraphs = text.split('\n\n')
            for para in paragraphs[:100]:
                if para.strip():
                    story.append(Paragraph(para.strip()[:500], styles['Normal']))

            doc.build(story)
            return True
        except Exception as e:
            self.log(f"    ReportLab変換エラー: {str(e)}")
            return False

    def convert_url_to_pdf(self, url, output_path):
        """選択されたライブラリでPDF変換"""
        library = self.pdf_library_var.get()

        if library == 'weasyprint' and 'weasyprint' in self.available_libraries:
            return self.convert_url_to_pdf_weasyprint(url, output_path)
        elif library == 'pdfkit' and 'pdfkit' in self.available_libraries:
            return self.convert_url_to_pdf_pdfkit(url, output_path)
        elif library == 'reportlab' and 'reportlab' in self.available_libraries:
            return self.convert_url_to_pdf_reportlab(url, output_path)
        else:
            # フォールバック
            for lib in self.available_libraries:
                if lib == 'weasyprint':
                    return self.convert_url_to_pdf_weasyprint(url, output_path)
                elif lib == 'pdfkit':
                    return self.convert_url_to_pdf_pdfkit(url, output_path)
                elif lib == 'reportlab':
                    return self.convert_url_to_pdf_reportlab(url, output_path)

        return False

    def start_conversion(self):
        """変換開始"""
        # 入力検証
        if not self.file_path_var.get():
            messagebox.showerror("エラー", "URLリストファイルを選択してください")
            return

        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("エラー", "URLリストファイルが見つかりません")
            return

        if not self.output_dir_var.get():
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        # UI状態変更
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.converting = True
        self.stop_requested = False

        # ログクリア
        if not self.detailed_log_var.get():
            self.log_text.delete(1.0, tk.END)

        # 変換スレッド開始
        self.conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.conversion_thread.start()

    def stop_conversion(self):
        """変換停止"""
        self.stop_requested = True
        self.log("停止が要求されました...")

    def conversion_worker(self):
        """変換処理ワーカー"""
        try:
            # 出力ディレクトリ作成
            os.makedirs(self.output_dir_var.get(), exist_ok=True)

            # URLリスト読み込み
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]

            if not urls:
                self.log("URLが見つかりませんでした")
                return

            total_urls = len(urls)
            self.progress_bar.config(maximum=total_urls)

            self.log(f"変換開始: {total_urls}個のURL")
            self.log(f"出力先: {self.output_dir_var.get()}")
            self.log(f"使用エンジン: {self.pdf_library_var.get()}")
            self.log("=" * 60)

            success_count = 0

            for i, url in enumerate(urls):
                if self.stop_requested:
                    self.log("変換が停止されました")
                    break

                # 進捗更新
                self.progress_var.set(f"[{i+1}/{total_urls}] 処理中...")
                self.progress_bar.config(value=i)

                try:
                    course_id = self.extract_course_id_from_url(url)
                    filename = self.sanitize_filename(f"{course_id}.pdf")
                    output_path = os.path.join(self.output_dir_var.get(), filename)

                    # 既存ファイルチェック
                    if self.skip_existing_var.get() and os.path.exists(output_path):
                        self.log(f"[{i+1}/{total_urls}] スキップ（既存）: {filename}")
                        success_count += 1
                        continue

                    self.log(f"[{i+1}/{total_urls}] 変換中: {url}")
                    if self.detailed_log_var.get():
                        self.log(f"    → {filename}")

                    success = self.convert_url_to_pdf(url, output_path)

                    if success:
                        self.log("    ✓ 成功")
                        success_count += 1
                    else:
                        self.log("    ✗ 失敗")

                except Exception as e:
                    self.log(f"[{i+1}/{total_urls}] エラー: {str(e)}")
                    if self.detailed_log_var.get():
                        self.log(f"    詳細: {traceback.format_exc()}")

            # 完了
            self.progress_bar.config(value=total_urls)
            self.progress_var.set("完了")

            self.log("=" * 60)
            self.log(f"変換完了: {success_count}/{total_urls} 件のPDFを生成")

            if not self.stop_requested:
                messagebox.showinfo("完了", f"{success_count}/{total_urls} 件のPDFを生成しました")

        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            self.log(error_msg)
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            messagebox.showerror("エラー", error_msg)

        finally:
            # UI状態復元
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.converting = False
            self.stop_requested = False

def main():
    try:
        root = tk.Tk()
        app = URLtoPDFConverter(root)
        root.mainloop()
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        print(traceback.format_exc())
        input("Enterキーを押して終了...")

if __name__ == "__main__":
    main()