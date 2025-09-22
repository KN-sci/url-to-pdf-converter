  import tkinter as tk
  from tkinter import ttk, filedialog, messagebox, scrolledtext
  import threading
  import os
  import requests
  from urllib.parse import urlparse

  # reportlab（軽量PDF生成）
  try:
      from reportlab.pdfgen import canvas
      from reportlab.lib.pagesizes import A4, letter
      from reportlab.lib.styles import getSampleStyleSheet
      from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
      from reportlab.lib.units import inch
      PDF_AVAILABLE = True
      print("reportlab loaded successfully")
  except ImportError:
      PDF_AVAILABLE = False
      print("reportlab not available")

  # HTML解析
  try:
      from bs4 import BeautifulSoup
      SOUP_AVAILABLE = True
  except ImportError:
      SOUP_AVAILABLE = False

  class URLtoPDFConverter:
      def __init__(self, root):
          self.root = root
          self.root.title("URL to PDF Converter - ReportLab")
          self.root.geometry("700x500")
          self.converting = False
          self.create_widgets()

      def create_widgets(self):
          main_frame = ttk.Frame(self.root, padding="10")
          main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

          # Title
          ttk.Label(main_frame, text="URL to PDF Converter (ReportLab)",
                   font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))

          status = "PDF生成可能" if PDF_AVAILABLE else "PDF生成不可（HTMLダウンロードのみ）"
          ttk.Label(main_frame, text=status).grid(row=1, column=0, columnspan=3, pady=(0, 10))

          # File selection
          ttk.Label(main_frame, text="URLリストファイル:").grid(row=2, column=0, sticky=tk.W, pady=5)
          self.file_path_var = tk.StringVar()
          ttk.Entry(main_frame, textvariable=self.file_path_var, width=50).grid(row=2, column=1, padx=5, pady=5)
          ttk.Button(main_frame, text="参照", command=self.select_file).grid(row=2, column=2, pady=5)

          # Output directory
          ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=3, column=0, sticky=tk.W, pady=5)
          self.output_dir_var = tk.StringVar()
          ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50).grid(row=3, column=1, padx=5, pady=5)
          ttk.Button(main_frame, text="参照", command=self.select_output_dir).grid(row=3, column=2, pady=5)

          # Convert button
          self.convert_button = ttk.Button(main_frame, text="変換開始", command=self.start_conversion)
          self.convert_button.grid(row=4, column=0, columnspan=3, pady=15)

          # Log
          ttk.Label(main_frame, text="ログ:").grid(row=5, column=0, sticky=tk.W)
          self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
          self.log_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

          # Grid configuration
          self.root.columnconfigure(0, weight=1)
          self.root.rowconfigure(0, weight=1)
          main_frame.columnconfigure(1, weight=1)
          main_frame.rowconfigure(6, weight=1)

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

      def create_pdf_from_text(self, text, output_path):
          """ReportLabでテキストからPDFを作成"""
          try:
              doc = SimpleDocTemplate(output_path, pagesize=A4)
              styles = getSampleStyleSheet()
              story = []

              # タイトル
              story.append(Paragraph("Webページ内容", styles['Title']))
              story.append(Spacer(1, 12))

              # テキストを段落に分割
              paragraphs = text.split('\n\n')
              for para in paragraphs[:50]:  # 最初の50段落
                  if para.strip():
                      # 長すぎる段落は切り詰め
                      clean_para = para.strip()[:1000]
                      story.append(Paragraph(clean_para, styles['Normal']))
                      story.append(Spacer(1, 6))

              doc.build(story)
              return True
          except Exception as e:
              self.log(f"    PDF作成エラー: {str(e)}")
              return False

      def convert_url(self, url, output_path):
          try:
              headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
              response = requests.get(url, headers=headers, timeout=30)
              response.raise_for_status()

              # HTMLからテキストを抽出
              if SOUP_AVAILABLE:
                  soup = BeautifulSoup(response.text, 'html.parser')
                  # スクリプトとスタイルを除去
                  for script in soup(["script", "style"]):
                      script.decompose()
                  text = soup.get_text()
              else:
                  # BeautifulSoupがない場合は生HTMLをそのまま使用
                  text = response.text

              if PDF_AVAILABLE:
                  return self.create_pdf_from_text(text, output_path)
              else:
                  # フォールバック: HTMLファイルとして保存
                  html_output = output_path.replace('.pdf', '.html')
                  with open(html_output, 'w', encoding='utf-8') as f:
                      f.write(response.text)
                  return True

          except Exception as e:
              self.log(f"    変換エラー: {str(e)}")
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
                      # ファイル名を生成
                      parsed_url = urlparse(url)
                      filename = os.path.basename(parsed_url.path) or f"page_{i}"

                      if PDF_AVAILABLE:
                          if not filename.endswith('.pdf'):
                              filename += '.pdf'
                      else:
                          if not filename.endswith('.html'):
                              filename += '.html'

                      output_path = os.path.join(self.output_dir_var.get(), filename)

                      self.log(f"[{i}/{len(urls)}] 変換中: {url}")

                      success = self.convert_url(url, output_path)
                      if success:
                          self.log(f"    ✓ 成功: {filename}")
                          success_count += 1
                      else:
                          self.log(f"    ✗ 失敗")

                  except Exception as e:
                      self.log(f"[{i}/{len(urls)}] エラー: {str(e)}")

              self.log(f"完了: {success_count}/{len(urls)} 件を処理")
              messagebox.showinfo("完了", f"{success_count}/{len(urls)} 件を処理しました")

          except Exception as e:
              self.log(f"エラー: {str(e)}")
              messagebox.showerror("エラー", str(e))

          finally:
              self.convert_button.config(state=tk.NORMAL)
              self.converting = False

  def main():
      root = tk.Tk()
      app = URLtoPDFConverter(root)
      root.mainloop()

  if __name__ == "__main__":
      main()
  EOF
