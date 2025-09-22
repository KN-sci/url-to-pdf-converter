# 🎓 兵庫県立大学シラバスPDF変換ツール（完全版）

## ✨ 特徴

- ✅ **Pythonインストール不要**（完全自立型実行ファイル）
- ✅ **ウイルス対策ソフト誤検出なし**
- ✅ **兵庫県立大学シラバス専用最適化**
- ✅ **年度指定対応**（2020-2030年）
- ✅ **進捗表示・ログ機能**
- ✅ **バッチ処理対応**

## 📦 配布パッケージ内容

```
兵庫県立大学シラバスPDF変換ツール_完全版.zip
├── 兵庫県立大学シラバスPDF変換ツール.exe  ← メイン実行ファイル
├── sample_course_codes.txt                  ← サンプル授業コードリスト
├── 使用方法.txt                             ← 詳細マニュアル
└── wkhtmltopdf自動インストール.bat          ← 自動セットアップ
```

## 🚀 配布・セットアップ手順

### 受け取る人（Pythonなし環境）の作業

1. **ZIPファイルを展開**
2. **`wkhtmltopdf自動インストール.bat` を実行**（管理者権限で）
3. **`兵庫県立大学シラバスPDF変換ツール.exe` を実行**

### 配布する人の作業

1. **GitHubで実行ファイル作成**
   ```bash
   git add .
   git commit -m "Add standalone syllabus converter"
   git push
   ```

2. **GitHub Actions で手動実行**
   - GitHub → Actions → "Build Standalone Executable"
   - "Run workflow" ボタンをクリック

3. **完成品をダウンロード**
   - Artifacts から `兵庫県立大学シラバスPDF変換ツール_完全版.zip` をダウンロード

## 📋 使用方法（受け取った人）

### 1. 授業コードリスト準備
```txt
ABC123
DEF456
GHI789
JKL012
```

### 2. ツール操作
1. **年度入力**: `2025`
2. **ファイル選択**: 授業コードリスト.txt
3. **保存先選択**: PDFフォルダ
4. **変換開始**

### 3. 結果
各授業コードのPDFファイルが自動生成
- `ABC123.pdf`
- `DEF456.pdf`
- `GHI789.pdf`

## 🔗 対応URL形式

```
https://syllabus.u-hyogo.ac.jp/slResult/[年度]/japanese/syllabusHtml/SyllabusHtml.[年度].[授業コード].html
```

## 💡 配布のメリット

- ✅ **受け取る人の作業最小限**（実行ファイル起動のみ）
- ✅ **セットアップ自動化**（wkhtmltopdf自動インストール）
- ✅ **トラブル回避**（依存関係問題なし）
- ✅ **即使用可能**（展開→実行）

## 🆘 サポート情報

配布先でのトラブル時は以下を確認：
- Windows 10/11 64bit環境
- インターネット接続
- wkhtmltopdfインストール状況
- ウイルス対策ソフトの除外設定