import os
import re
from bs4 import BeautifulSoup

def debug_html_file(html_file_path):
    """HTMLファイルの内容をデバッグ表示"""
    print(f"\n=== デバッグ: {html_file_path} ===")

    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        print(f"ファイルサイズ: {len(content)} 文字")

        # 内容の一部を表示
        print("\n--- ファイル内容（最初の500文字）---")
        print(content[:500])
        print("..." if len(content) > 500 else "")

        # BeautifulSoupでパース
        soup = BeautifulSoup(content, 'html.parser')

        # 全てのリンクを確認
        links = soup.find_all('a', href=True)
        print(f"\n--- 見つかったリンク数: {len(links)} ---")

        for i, link in enumerate(links[:10]):  # 最初の10個だけ表示
            href = link['href']
            text = link.get_text(strip=True)[:50]
            print(f"{i+1}. {href} (テキスト: {text})")

        if len(links) > 10:
            print("...")

        # SyllabusHTML を含むパターンを広く検索
        patterns = [
            r'SyllabusHTML',
            r'syllabus',
            r'\.html',
            r'2025',
            r'https://[^"\s]*\.html'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"\nパターン '{pattern}' の一致: {len(matches)}個")
                for match in matches[:5]:  # 最初の5個だけ表示
                    print(f"  {match}")
                if len(matches) > 5:
                    print("  ...")

    except Exception as e:
        print(f"エラー: {e}")

def main():
    search_dir = input("HTMLファイルを検索するディレクトリを入力してください: ")

    if not os.path.exists(search_dir):
        print(f"ディレクトリが見つかりません: {search_dir}")
        return

    # HTMLファイルを検索
    html_files = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    if not html_files:
        print("HTMLファイルが見つかりませんでした。")
        return

    print(f"見つかったHTMLファイル数: {len(html_files)}")

    # 最初の3つのファイルをデバッグ
    for html_file in html_files[:3]:
        debug_html_file(html_file)

        user_input = input("\n次のファイルを確認しますか？ (y/n/q): ")
        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 'n':
            continue

if __name__ == "__main__":
    main()