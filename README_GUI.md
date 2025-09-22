# URL to PDF Converter (GUI版)

直感的なGUIで操作できるURL→PDF変換ツール

## 特徴

- **使いやすいGUI**: ファイル選択ダイアログとボタン操作
- **リアルタイム進捗表示**: 進捗バーと詳細ログ
- **外部依存なし**: wkhtmltopdf不要（WeasyPrint使用）
- **変換停止機能**: 途中で停止可能
- **既存ファイルスキップ**: 重複変換を自動回避

## GUI画面の説明

### メイン画面
```
┌─────────────────────────────────────────┐
│          URL to PDF Converter           │
├─────────────────────────────────────────┤
│ URLリストファイル: [urls.txt    ] [参照] │
│ 出力ディレクトリ:  [C:\MyPDFs   ] [参照] │
├─────────────────────────────────────────┤
│ ☑ 既存ファイルをスキップ                │
│                                         │
│        [変換開始]    [停止]             │
├─────────────────────────────────────────┤
│ 進捗: [2/5] 変換中...                   │
│ ████████████░░░░░░░░░░ 40%              │
├─────────────────────────────────────────┤
│ ログ:                                   │
│ [1/5] 変換中: https://example.com...    │
│     -> ABC123.pdf                       │
│     ✓ 成功                              │
│ [2/5] 変換中: https://example.com...    │
│     -> DEF456.pdf                       │
│     ✓ 成功                              │
└─────────────────────────────────────────┘
```

## 実行ファイルの作成

```bash
# GUI版実行ファイルを作成
python build_gui_executable.py

# または手動で
pip install weasyprint requests beautifulsoup4 pyinstaller
pyinstaller --onefile --windowed --name URLtoPDF_GUI url_to_pdf_gui.py
```

## 使用方法

### 1. 実行ファイルの起動
```
URLtoPDF_GUI.exe をダブルクリック
```

### 2. ファイル選択
1. **URLリストファイル**: [参照]ボタンでtxtファイルを選択
2. **出力ディレクトリ**: [参照]ボタンで保存先フォルダを選択

### 3. オプション設定
- **既存ファイルをスキップ**: チェックすると同名ファイルを再変換しない

### 4. 変換開始
- **[変換開始]**ボタンをクリック
- 進捗バーとログで変換状況を確認
- 必要に応じて**[停止]**ボタンで中断可能

## URLリストファイルの形式

```txt
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.ABC123.html
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.DEF456.html
https://example.university.ac.jp/syllabus/SyllabusHtml.2025.GHI789.html
```

## 出力ファイル名

- **シラバス形式**: `ABC123.pdf` (コースIDを抽出)
- **その他**: URLから推測される名前

## トラブルシューティング

- **変換が遅い**: インターネット速度とサイトの応答時間に依存
- **変換失敗**: アクセス制限やサイトエラーが原因の場合がある
- **文字化け**: 一部のサイトで発生する可能性があります

## 技術仕様

- **GUI**: tkinter (Python標準ライブラリ)
- **PDF変換**: WeasyPrint
- **HTTP通信**: requests
- **実行ファイル**: PyInstaller
- **対応OS**: Windows (exe形式)