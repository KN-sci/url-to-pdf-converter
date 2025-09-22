import pdfkit
import os
import re
from urllib.parse import urlparse

# 入力するテキストファイルのパスをユーザーに尋ねる
input_file_path = input("URLリストを含むテキストファイルのパスを入力してください: ")

# 出力するディレクトリをユーザーに尋ねる
output_dir = input("PDFファイルを保存するディレクトリを入力してください: ")
os.makedirs(output_dir, exist_ok=True)

def sanitize_filename(filename):
    # ファイル名から無効な文字を削除または置換する
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', filename)

def get_html_filename(url):
    # URLからHTMLファイル名を取得する
    parsed_url = urlparse(url)
    html_filename = os.path.basename(parsed_url.path)
    if not html_filename:
        html_filename = 'index'
    return html_filename

try:
    # URLリストを読み取る
    with open(input_file_path, 'r') as file:
        urls = file.readlines()

    # URLごとにPDFを生成して保存する
    for url in urls:
        url = url.strip()
        if url:
            try:
                html_filename = get_html_filename(url)
                filename = sanitize_filename(html_filename)[:100]  # ファイル名の長さを制限
                output_path = os.path.join(output_dir, f'{filename}.pdf')
                pdfkit.from_url(url, output_path)
                print(f'Successfully saved {url} to {output_path}')
            except Exception as e:
                print(f'Failed to save {url}: {e}')
except FileNotFoundError:
    print(f"ファイルが見つかりません: {input_file_path}")
except Exception as e:
    print(f"エラーが発生しました: {e}")

