import pdfkit
import os
import re
import sys
from urllib.parse import urlparse

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

def convert_url_to_pdf(url, output_path):
    """URLをPDFに変換する"""
    try:
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_url(url, output_path, options=options)
        return True
    except Exception as e:
        print(f'PDF変換失敗 {url}: {e}')
        return False

def main():
    print("URL to PDF Converter")
    print("=" * 30)

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

                success = convert_url_to_pdf(url, output_path)

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