# URL to PDF Converter

シンプルなURL変換ツール - URLリストからPDFファイルを一括生成

## 機能

- テキストファイルに記載されたURLリストを読み込み
- 各URLのHTMLをPDFに変換
- コマンドライン引数またはインタラクティブ入力に対応
- 既存ファイルのスキップ機能
- Windows実行ファイル化対応

## 使用方法

### 1. Python環境での実行

```bash
# インタラクティブモード
python url_to_pdf_converter.py

# コマンドライン引数
python url_to_pdf_converter.py urls.txt output_folder
```

### 2. Windows実行ファイルの作成

```bash
# 必要なパッケージのインストールと実行ファイル作成
python build_executable.py

# または手動で
pip install -r requirements.txt
pyinstaller --onefile --console --name URLtoPDF url_to_pdf_converter.py
```

### 3. Windows実行ファイルの使用

```cmd
# インタラクティブモード
URLtoPDF.exe

# コマンドライン引数
URLtoPDF.exe urls.txt output_folder
```

## URLリストファイルの形式

テキストファイル（UTF-8）に1行1URLで記載：

```
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.ABC123.html
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.DEF456.html
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.GHI789.html
```

## 出力ファイル名

- シラバス形式URL: コースID（例: `ABC123.pdf`）
- その他のURL: URLから推測されるファイル名

## 必要な環境

### Python実行時
- Python 3.6+
- wkhtmltopdf（システムにインストール必要）

### Windows実行ファイル
- wkhtmltopdf（システムにインストール必要）
- Pythonインストール不要

## wkhtmltopdfのインストール

Windows: https://wkhtmltopdf.org/downloads.html からダウンロードしてインストール

## 注意事項

- インターネット接続が必要
- URLアクセスに時間がかかる場合があります
- 一部のサイトではアクセス制限がある場合があります