# Transpalentor - 画像透過処理アプリケーション

画像の指定した色を透過処理するWebアプリケーションです。ブラウザ上でローカル画像を選択し、スポイトツールまたはカラーピッカーで透過させたい色を指定し、リアルタイムでプレビューできます。

## 特徴

- 🎨 **簡単な色指定**: スポイトツール、カラーピッカー、RGB値直接入力に対応
- 🖼️ **複数フォーマット対応**: PNG、JPEG、BMP形式をサポート
- 👁️ **リアルタイムプレビュー**: 透過処理結果を即座に確認
- 🔒 **セキュア**: ファイルは一時保存され、処理後は自動削除
- 🚀 **高速処理**: 非同期処理により快適なユーザー体験

## 技術スタック

### バックエンド
- **FastAPI** 0.115+ - 高速な非同期Webフレームワーク
- **Pillow** 10.0+ - 画像処理ライブラリ
- **Pydantic** 2.0+ - データバリデーション
- **APScheduler** 3.10+ - タスクスケジューリング

### フロントエンド
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **EyeDropper API** (Chrome/Edge) + フォールバック対応

### アーキテクチャ
レイヤードアーキテクチャを採用:
```
transpalentor/
├── presentation/     # FastAPI endpoints, models, exceptions
├── application/      # Business logic, validation
├── domain/          # Core domain logic
└── infrastructure/  # File storage, logging
```

## セットアップ

### 必要要件
- Python 3.10+
- pip

### インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/tomada1114/image-color-transparency.git
cd image-color-transparency
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

開発環境の場合:
```bash
pip install -r requirements-dev.txt
```

### 起動

```bash
python main.py
```

サーバーが起動したら、ブラウザで以下にアクセス:
```
http://localhost:8000
```

## 使い方

1. **画像をアップロード**: ファイル選択ボタンから画像を選択
2. **色を指定**:
   - スポイトツールで画像から色を選択 (Chrome/Edge)
   - カラーピッカーで色を選択
   - RGB値を直接入力
3. **透過処理を実行**: 処理ボタンをクリック
4. **結果を確認**: 透過処理された画像をプレビュー
5. **ダウンロード**: 処理済み画像を保存

## API仕様

### エンドポイント

#### `POST /api/upload`
画像ファイルをアップロード

**リクエスト:**
- Content-Type: `multipart/form-data`
- Body: `file` (画像ファイル)

**レスポンス:**
```json
{
  "session_id": "uuid-v4-string",
  "image_url": "/api/images/{session_id}/{filename}",
  "filename": "sanitized-filename.png",
  "size": 123456
}
```

#### `GET /api/images/{session_id}/{filename}`
アップロードした画像を取得

**レスポンス:**
- Content-Type: `image/png`, `image/jpeg`, etc.
- Body: 画像バイナリデータ

#### `POST /api/process`
透過処理を実行 (実装予定)

#### `GET /health`
ヘルスチェック

**レスポンス:**
```json
{
  "status": "healthy"
}
```

## 開発

### テストの実行

```bash
# 全テストを実行
pytest

# 詳細な出力
pytest -v

# カバレッジ付き
pytest --cov=transpalentor --cov-report=html
```

### 開発状況

✅ **完了済み (Phase 1)**
- [x] プロジェクト基盤のセットアップ
- [x] 画像アップロード機能
- [x] 画像表示機能

🚧 **実装中 (Phase 2)**
- [ ] フロントエンドUI基盤
- [ ] 色指定機能
- [ ] 透過処理機能 (コア機能)

📋 **予定 (Phase 3)**
- [ ] フロントエンド・バックエンド統合
- [ ] ファイルクリーンアップとセッション管理
- [ ] パフォーマンス最適化

### テストカバレッジ

現在22個のテストが実装済み:
- ユニットテスト: ファイルストレージ、バリデーション、ロギング
- 統合テスト: APIエンドポイント
- エラーハンドリングテスト

## セキュリティ

- ✅ ファイルサイズ制限 (10MB)
- ✅ サポート形式のバリデーション
- ✅ ディレクトリトラバーサル攻撃対策
- ✅ ファイル名のサニタイゼーション
- ✅ セッションベースの分離管理

## ライセンス

このプロジェクトはオープンソースです。

## 貢献

Issue、Pull Requestを歓迎します!

## 開発アプローチ

このプロジェクトはKiro-style Spec Driven Developmentを採用しています。
詳細は [CLAUDE.md](./CLAUDE.md) を参照してください。
