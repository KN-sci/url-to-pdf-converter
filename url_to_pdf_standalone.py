import os
import re
import sys
import requests
from urllib.parse import urlparse
import weasyprint
from weasyprint import HTML, CSS

def sanitize_filename(filename):
    """ファイル名から無効な文字を削除または置換する"""
    return re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)

def extract_course_id_from_url(url):
    """URLからコースIDを抽出する（syllabus形式の場合）"""
    match = re.search(r'SyllabusHtml\.2025\.([A-Za-z0-9]+)\.html', url)
    if match:
        return match.group(1)

    # syllabus形式でない場合は、URLから適当なファイル名を生成
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if filename and filename.endswith('.html'):
        return filename[:-5]  # .htmlを除去
    elif filename:
        return filename
    else:
        # パスからファイル名を生成
        path_parts = [part for part in parsed_url.path.split('/') if part]
        if path_parts:
            return path_parts[-1]
        else:
            return parsed_url.netloc.replace('.', '_')

def convert_url_to_pdf_weasyprint(url, output_path):
    """WeasyPrintを使用してURLをPDFに変換する（外部依存なし）"""
    try:
        # HTMLコンテンツを取得
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

        # HTMLからPDFを生成
        html_doc = HTML(string=response.text, base_url=url)
        html_doc.write_pdf(output_path, stylesheets=[css_style])

        return True

    except requests.exceptions.RequestException as e:
        print(f'URL取得失敗 {url}: {e}')
        return False
    except Exception as e:
        print(f'PDF変換失敗 {url}: {e}')
        return False

def convert_url_to_pdf_fallback(url, output_path):
    """フォールバック：requestsとreportlabを使用（より基本的な方法）"""
    try:
        import requests
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from bs4 import BeautifulSoup

        # HTMLコンテンツを取得
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'

        # HTMLからテキストを抽出
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # PDFを生成
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # テキストを段落に分割してPDFに追加
        paragraphs = text.split('\n\n')
        for para in paragraphs[:50]:  # 最初の50段落のみ
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))

        doc.build(story)
        return True

    except Exception as e:
        print(f'フォールバック変換失敗 {url}: {e}')
        return False

def main():
    print("URL to PDF Converter (Standalone)")
    print("=" * 40)

    # URLリストファイルのパスを取得
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        input_file_path = input("URLリストファイルのパスを入力してください: ")

    if not os.path.exists(input_file_path):
        print(f"ファイルが見つかりません: {input_file_path}")
        input("Enterキーを押して終了...")
        return

    # 出力ディレクトリを取得
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = input("PDFファイルを保存するディレクトリを入力してください（空白で現在のディレクトリ）: ").strip()
        if not output_dir:
            output_dir = os.path.dirname(os.path.abspath(input_file_path))

    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)

    try:
        # URLリストを読み取る
        with open(input_file_path, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]

        if not urls:
            print("URLが見つかりませんでした。")
            input("Enterキーを押して終了...")
            return

        print(f"\n{len(urls)}個のURLを変換します...")
        print(f"出力先: {output_dir}")
        print("変換方法: WeasyPrint (外部依存なし)")
        print()

        success_count = 0

        # URLごとにPDFを生成
        for i, url in enumerate(urls, 1):
            try:
                # ファイル名を生成
                course_id = extract_course_id_from_url(url)
                filename = sanitize_filename(f"{course_id}.pdf")
                output_path = os.path.join(output_dir, filename)

                # 既にファイルが存在する場合はスキップ
                if os.path.exists(output_path):
                    print(f"[{i}/{len(urls)}] スキップ（既に存在）: {filename}")
                    success_count += 1
                    continue

                print(f"[{i}/{len(urls)}] 変換中: {url}")
                print(f"                -> {filename}")

                # WeasyPrintで変換を試行
                success = convert_url_to_pdf_weasyprint(url, output_path)

                if success:
                    print(f"                ✓ 成功")
                    success_count += 1
                else:
                    print(f"                ✗ 失敗")

            except Exception as e:
                print(f"[{i}/{len(urls)}] エラー: {url} - {e}")

        print()
        print(f"完了: {success_count}/{len(urls)} 件のPDFを生成しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    input("Enterキーを押して終了...")

if __name__ == "__main__":
    main()