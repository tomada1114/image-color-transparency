# 開発ガイド

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます!

## 開発環境のセットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/tomada1114/image-color-transparency.git
cd image-color-transparency
```

### 2. 仮想環境の作成 (推奨)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements-dev.txt
```

## 開発ワークフロー

### TDD (Test-Driven Development)

このプロジェクトではTDD手法を採用しています:

1. **RED**: 失敗するテストを書く
2. **GREEN**: テストをパスする最小限のコードを書く
3. **REFACTOR**: コードをクリーンアップし改善する

### テストの実行

```bash
# 全テストを実行
pytest

# 詳細な出力
pytest -v

# 特定のテストファイルのみ実行
pytest tests/test_upload.py

# カバレッジレポート生成
pytest --cov=transpalentor --cov-report=html
```

### コード品質チェック

```bash
# コードフォーマット (Black)
black transpalentor tests

# リンター (Flake8)
flake8 transpalentor tests

# 型チェック (mypy)
mypy transpalentor
```

### サーバーの起動

```bash
# 開発サーバー (自動リロード有効)
python main.py

# または
uvicorn transpalentor.presentation.app:app --reload
```

## プロジェクト構造

```
image-color-transparency/
├── .kiro/                    # Kiro仕様管理
│   └── specs/
│       └── image-color-transparency/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── transpalentor/           # メインアプリケーション
│   ├── presentation/        # FastAPI endpoints
│   ├── application/         # ビジネスロジック
│   ├── domain/             # ドメインロジック
│   └── infrastructure/     # インフラストラクチャ
├── tests/                  # テストコード
├── static/                 # 静的ファイル (HTML/CSS/JS)
└── tmp/                    # 一時ファイル保存先
```

## コーディング規約

### Python コードスタイル

- **フォーマッター**: Black (line-length=100)
- **リンター**: Flake8
- **型ヒント**: 必須 (mypy でチェック)
- **ドキュメンテーション**: Google スタイルのdocstring

例:
```python
async def process_image(session_id: str, color: RGBColor) -> ProcessedImage:
    """
    画像を透過処理する

    Args:
        session_id: セッションID
        color: 透過対象色

    Returns:
        処理済み画像

    Raises:
        SessionNotFoundError: セッションが見つからない場合
    """
    # 実装
```

### コミットメッセージ

Conventional Commits形式を使用:

```
<type>(<scope>): <subject>

<body>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `test`: テスト追加・修正
- `refactor`: リファクタリング
- `chore`: ビルド・設定変更

**例:**
```
feat(upload): Add support for WebP image format

- Update validation to support WebP
- Add WebP MIME type handling
- Update tests
```

## Spec-Driven Development

このプロジェクトはKiro-style Spec Driven Developmentを採用しています。

### 仕様ドキュメント

実装前に必ず以下のドキュメントを確認:
- `.kiro/specs/image-color-transparency/requirements.md` - 要件定義
- `.kiro/specs/image-color-transparency/design.md` - 技術設計
- `.kiro/specs/image-color-transparency/tasks.md` - 実装タスク

### タスク管理

実装完了時は `tasks.md` のチェックボックスを更新:

```markdown
- [x] 1.1 Pythonプロジェクトの初期化と依存関係管理
```

## Pull Request の作成

### 1. ブランチの作成

```bash
git checkout -b feature/your-feature-name
```

### 2. 変更のコミット

```bash
git add .
git commit -m "feat: your commit message"
```

### 3. テストの確認

```bash
pytest
```

### 4. プッシュ

```bash
git push origin feature/your-feature-name
```

### 5. PR の作成

GitHub上でPull Requestを作成し、以下を含めてください:
- 変更内容の説明
- 関連するIssue番号
- スクリーンショット (UI変更の場合)
- テスト結果

## よくある質問

### Q: テストが失敗する

A: 依存関係が最新か確認してください:
```bash
pip install -r requirements-dev.txt
```

### Q: ファイルアップロードのテストでエラーが出る

A: 一時ディレクトリが作成されているか確認:
```bash
mkdir -p tmp/transpalentor
```

### Q: ポート8000が既に使用されている

A: 別のポートを指定して起動:
```bash
uvicorn transpalentor.presentation.app:app --port 8001
```

## サポート

質問やサポートが必要な場合:
- GitHub Issues で質問を投稿
- CLAUDE.md で開発プロセスを確認

---

Happy coding! 🚀
