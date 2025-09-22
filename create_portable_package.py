import os
import zipfile
import shutil

def create_portable():
    """ポータブル版パッケージを作成"""

    print("兵庫県立大学シラバスPDF変換ツール - ポータブル版作成中...")

    # バッチファイル作成
    batch_content = '''@echo off
title 兵庫県立大学シラバスPDF変換ツール
echo ==========================================
echo 兵庫県立大学シラバスPDF変換ツール
echo ==========================================
echo.
echo 起動中...
python url_to_pdf_syllabus.py
if errorlevel 1 (
    echo.
    echo [エラー] Pythonがインストールされていません。
    echo.
    echo 以下の手順でPythonをインストールしてください:
    echo 1. https://www.python.org/downloads/ にアクセス
    echo 2. 最新版のPythonをダウンロード
    echo 3. インストール時に「Add Python to PATH」にチェック
    echo 4. インストール完了後、このファイルを再実行
    echo.
    echo 必要なライブラリ（Pythonインストール後）:
    echo pip install requests
    echo.
    pause
)
'''

    with open('兵庫県立大学シラバスPDF変換ツール.bat', 'w', encoding='shift_jis') as f:
        f.write(batch_content)

    # インストールスクリプト作成
    install_content = '''@echo off
title 必要ライブラリインストール
echo ==========================================
echo 必要ライブラリインストール
echo ==========================================
echo.
echo Pythonライブラリをインストールしています...
pip install requests
if errorlevel 0 (
    echo.
    echo ✓ インストール完了
    echo.
    echo 次に wkhtmltopdf をインストールしてください:
    echo https://wkhtmltopdf.org/downloads.html
    echo.
) else (
    echo.
    echo ✗ インストール失敗
    echo Pythonが正しくインストールされていない可能性があります
    echo.
)
pause
'''

    with open('1_ライブラリインストール.bat', 'w', encoding='shift_jis') as f:
        f.write(install_content)

    # README作成
    readme_content = '''# 兵庫県立大学シラバスPDF変換ツール (ポータブル版)

## 概要
兵庫県立大学のシラバスを授業コードから自動でPDF変換するツールです。

## URL形式
https://syllabus.u-hyogo.ac.jp/slResult/[年度]/japanese/syllabusHtml/SyllabusHtml.[年度].[授業コード].html

## 必要な環境
1. Python 3.7以上
2. requests ライブラリ
3. wkhtmltopdf

## インストール手順

### 1. Python のインストール
https://www.python.org/downloads/ から最新版をダウンロード・インストール
※ インストール時に「Add Python to PATH」にチェックを入れてください

### 2. 必要ライブラリのインストール
「1_ライブラリインストール.bat」を実行

### 3. wkhtmltopdf のインストール
https://wkhtmltopdf.org/downloads.html から「Windows (MSVC 2015) 64-bit」をダウンロード・インストール

## 使用方法

### 1. 授業コードリストファイルの準備
テキストファイル（.txt）に1行1授業コードで記載
例：
```
ABC123
DEF456
GHI789
```

### 2. ツールの起動
「兵庫県立大学シラバスPDF変換ツール.bat」をダブルクリック

### 3. 設定
- 年度: 対象年度を入力（例：2025）
- 授業コードリストファイル: 作成したテキストファイルを選択
- PDF保存先: PDFを保存するフォルダを選択

### 4. 変換開始
「シラバスPDF変換開始」ボタンをクリック

## 特徴
- ✅ ウイルス対策ソフトの誤検出なし
- ✅ オープンソース
- ✅ 軽量
- ✅ 兵庫県立大学専用最適化
- ✅ 年度指定対応
- ✅ 進捗表示付き

## ファイル構成
- url_to_pdf_syllabus.py : メインプログラム
- 兵庫県立大学シラバスPDF変換ツール.bat : 起動用バッチファイル
- 1_ライブラリインストール.bat : ライブラリインストール用
- sample_course_codes.txt : サンプル授業コードリスト
- README.txt : このファイル

## トラブルシューティング
- Pythonエラー: Pythonが正しくインストールされているか確認
- ライブラリエラー: pip install requests を実行
- PDF変換エラー: wkhtmltopdf がインストールされているか確認
- 授業コードエラー: 授業コードが正しいか、該当年度にシラバスが存在するか確認

## ライセンス
MIT License

## 作成者
GitHub: https://github.com/KN-sci/url-to-pdf-converter
'''

    with open('README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # ZIP作成
    files_to_include = [
        'url_to_pdf_syllabus.py',
        '兵庫県立大学シラバスPDF変換ツール.bat',
        '1_ライブラリインストール.bat',
        'sample_course_codes.txt',
        'README.txt'
    ]

    zip_name = '兵庫県立大学シラバスPDF変換ツール_ポータブル版.zip'

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files_to_include:
            if os.path.exists(file):
                zf.write(file)
                print(f"  ✓ {file}")

    print(f"\n✅ ポータブル版パッケージを作成しました: {zip_name}")
    print("\n📦 含まれるファイル:")
    for file in files_to_include:
        if os.path.exists(file):
            print(f"  - {file}")

    print("\n🚀 配布方法:")
    print(f"1. {zip_name} を配布")
    print("2. 受け取った人がZIPを展開")
    print("3. README.txt に従ってセットアップ")
    print("4. バッチファイルから起動")

if __name__ == "__main__":
    create_portable()