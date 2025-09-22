import pdfkit
import os
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import glob

def sanitize_filename(filename):
    """ファイル名から無効な文字を削除または置換する"""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', filename)

def extract_syllabus_urls(html_file_path):
    """HTMLファイルからシラバスURLを抽出する"""
    urls = []
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            # href属性からシラバスURLのパターンを検索
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # https://△△/・・・・/SyllabusHtml.2025.dddddd.html の形式をチェック（英数字対応）
                if re.search(r'https://[^/]+/.*?/SyllabusHtml\.2025\.[A-Za-z0-9]+\.html', href):
                    urls.append(href)

            # srcやその他の属性からもURLを検索（念のため）
            pattern = r'https://[^"\s]+/SyllabusHtml\.2025\.[A-Za-z0-9]+\.html'
            matches = re.findall(pattern, content)
            urls.extend(matches)

    except Exception as e:
        print(f"HTMLファイルの読み込みエラー ({html_file_path}): {e}")

    return list(set(urls))  # 重複を除去

def extract_course_id(url):
    """URLからコースID（英数字部分）を抽出する"""
    match = re.search(r'SyllabusHtml\.2025\.([A-Za-z0-9]+)\.html', url)
    return match.group(1) if match else None

def convert_url_to_pdf(url, output_path):
    """URLをPDFに変換する（既存のprint_pdf.pyのロジックを使用）"""
    try:
        pdfkit.from_url(url, output_path)
        return True
    except Exception as e:
        print(f'PDF変換失敗 {url}: {e}')
        return False

def main():
    # 検索対象のディレクトリを取得
    search_dir = input("HTMLファイルを検索するディレクトリを入力してください: ")

    if not os.path.exists(search_dir):
        print(f"ディレクトリが見つかりません: {search_dir}")
        return

    # 全てのサブディレクトリからHTMLファイルを検索
    html_files = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    if not html_files:
        print("HTMLファイルが見つかりませんでした。")
        return

    print(f"見つかったHTMLファイル数: {len(html_files)}")

    # 各HTMLファイルを処理
    for html_file in html_files:
        print(f"\n処理中: {html_file}")

        # HTMLファイルからディレクトリ名を取得（1-2, 4-3などの形式）
        dir_name = os.path.basename(os.path.dirname(html_file))

        # シラバスURLを抽出
        urls = extract_syllabus_urls(html_file)

        if not urls:
            print(f"  シラバスURLが見つかりませんでした")
            continue

        print(f"  見つかったURL数: {len(urls)}")

        # 出力ディレクトリを作成（HTMLファイルと同じディレクトリ名）
        output_dir = os.path.join(search_dir, dir_name)
        os.makedirs(output_dir, exist_ok=True)

        # 各URLをPDFに変換
        for url in urls:
            course_id = extract_course_id(url)
            if course_id:
                pdf_filename = f"{course_id}.pdf"
                output_path = os.path.join(output_dir, pdf_filename)

                # 既にファイルが存在する場合はスキップ
                if os.path.exists(output_path):
                    print(f"    スキップ（既に存在）: {pdf_filename}")
                    continue

                print(f"    変換中: {url} -> {pdf_filename}")
                success = convert_url_to_pdf(url, output_path)

                if success:
                    print(f"    成功: {pdf_filename}")
                else:
                    print(f"    失敗: {pdf_filename}")
            else:
                print(f"    コースID抽出失敗: {url}")

if __name__ == "__main__":
    main()