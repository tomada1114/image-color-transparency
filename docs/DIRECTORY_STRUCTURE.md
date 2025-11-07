# プロジェクト構造

## 概要

Transpalentorは、画像の色指定による透過処理を行うWebアプリケーションです。
本ドキュメントでは、プロジェクト全体のディレクトリ構造とその役割について説明します。

## ディレクトリ構成

```
image-color-transparency/
├── .claude/                      # Claude Code設定
│   └── commands/                # カスタムスラッシュコマンド
│       └── kiro/               # Kiro Spec-Driven Development コマンド
├── .kiro/                        # Kiro仕様書
│   ├── specs/                   # 機能仕様
│   │   └── image-color-transparency/
│   │       ├── requirements.md  # 要件定義
│   │       ├── design.md       # 技術設計
│   │       └── tasks.md        # 実装タスク
│   └── steering/                # プロジェクト全体のガイダンス
├── docs/                         # プロジェクトドキュメント
│   ├── DIRECTORY_STRUCTURE.md  # 本ドキュメント
│   ├── DEVELOPMENT_GUIDE.md    # 開発ガイド
│   └── API_REFERENCE.md        # API仕様
├── static/                       # 静的ファイル（フロントエンド）
│   ├── css/
│   │   └── style.css           # スタイルシート
│   ├── js/
│   │   └── app.js              # フロントエンドJavaScript
│   └── index.html              # メインHTMLページ
├── tests/                        # テストコード
│   ├── __init__.py
│   ├── test_app.py             # アプリケーション基本機能テスト
│   ├── test_error_handling.py  # エラーハンドリングテスト
│   ├── test_file_storage.py    # ファイルストレージテスト
│   ├── test_image_display.py   # 画像表示機能テスト
│   ├── test_transparency.py    # 透過処理ロジックテスト
│   ├── test_transparency_api.py # 透過処理APIテスト
│   └── test_upload.py          # アップロード機能テスト
├── tmp/                          # 一時ファイルストレージ
│   └── transpalentor/          # セッションごとのファイル保存
├── transpalentor/                # メインアプリケーションコード
│   ├── __init__.py
│   ├── application/            # アプリケーション層
│   │   ├── __init__.py
│   │   └── validation.py       # バリデーションロジック
│   ├── domain/                 # ドメイン層
│   │   ├── __init__.py
│   │   └── transparency.py     # 透過処理コアロジック
│   ├── infrastructure/         # インフラストラクチャ層
│   │   ├── __init__.py
│   │   ├── file_storage.py     # ファイル管理
│   │   └── logging_config.py   # ロギング設定
│   └── presentation/           # プレゼンテーション層
│       ├── __init__.py
│       ├── app.py              # FastAPIアプリケーション
│       ├── error_handlers.py   # エラーハンドラー
│       ├── exceptions.py       # カスタム例外
│       └── models.py           # Pydanticモデル
├── CLAUDE.md                     # Claude Codeプロジェクト説明
├── CONTRIBUTING.md               # コントリビューションガイド
├── README.md                     # プロジェクト概要
├── main.py                       # アプリケーションエントリーポイント
├── pyproject.toml               # Pythonプロジェクト設定
├── requirements.txt             # 本番環境依存関係
└── requirements-dev.txt         # 開発環境依存関係
```

## レイヤーアーキテクチャ

本プロジェクトは、責任の明確な分離を実現するため、以下の4層アーキテクチャを採用しています：

### 1. プレゼンテーション層 (`presentation/`)

**役割**: HTTPリクエスト/レスポンスの処理、ルーティング、入力バリデーション

**主要ファイル**:
- `app.py`: FastAPIアプリケーションのメインエントリーポイント、エンドポイント定義
- `models.py`: リクエスト/レスポンスのPydanticモデル
- `exceptions.py`: カスタムHTTP例外
- `error_handlers.py`: エラーハンドリングとHTTPエラーレスポンス生成

**主要エンドポイント**:
- `POST /api/upload`: 画像アップロード
- `GET /api/images/{session_id}/{filename}`: 画像取得
- `POST /api/process`: 透過処理実行
- `POST /api/erase`: 消しゴムツールによる透過処理

### 2. アプリケーション層 (`application/`)

**役割**: ビジネスロジックの調整、ユースケースの実装

**主要ファイル**:
- `validation.py`: 画像ファイルのバリデーション（形式、サイズ、内容）

**主要機能**:
- ファイル形式検証（PNG/JPEG/BMP）
- ファイルサイズ制限（10MB）
- 画像内容の整合性チェック
- セキュリティチェック（ディレクトリトラバーサル対策）

### 3. ドメイン層 (`domain/`)

**役割**: コアビジネスロジック、アルゴリズム実装

**主要ファイル**:
- `transparency.py`: 透過処理アルゴリズム

**主要機能**:
- 色指定による透過処理（RGB + 閾値）
- 消しゴムツールによる部分的な透過処理
- ピクセル単位の色距離計算
- アルファチャンネル操作

### 4. インフラストラクチャ層 (`infrastructure/`)

**役割**: 外部システムとのインテグレーション、技術的な詳細

**主要ファイル**:
- `file_storage.py`: ファイルシステム操作、セッション管理
- `logging_config.py`: ロギング設定、構造化ログ

**主要機能**:
- 一時ファイルの保存・削除
- セッションベースのファイル管理（UUID v4）
- 自動クリーンアップ（APScheduler）
- 構造化ロギング（JSON形式）

## フロントエンド (`static/`)

**技術スタック**:
- バニラJavaScript（ES6+）
- CSS3（Flexbox、Grid）
- EyeDropper API（色選択）
- Canvas API（消しゴムツール）

**主要機能**:
- 画像アップロード
- スポイトツールによる色選択
- RGB手動入力
- 色の許容範囲調整（閾値）
- 消しゴムツール（ブラシサイズ調整可能）
- リアルタイムプレビュー

## テスト (`tests/`)

**テストフレームワーク**: pytest + pytest-cov

**現在のカバレッジ**: 76%

**テストファイル**:
- `test_app.py`: アプリケーション基本機能（起動、ルート、静的ファイル）
- `test_error_handling.py`: エラーハンドリング
- `test_file_storage.py`: ファイルストレージ操作
- `test_image_display.py`: 画像表示機能
- `test_transparency.py`: 透過処理ロジック
- `test_transparency_api.py`: 透過処理API
- `test_upload.py`: アップロード機能

## 一時ファイル管理 (`tmp/`)

**構造**:
```
tmp/
└── transpalentor/
    └── {session_id}/
        ├── original_{filename}
        └── processed_{filename}
```

**セッション管理**:
- セッションIDはUUID v4
- 各セッションは独立したディレクトリ
- 古いファイルは自動削除（デフォルト: 1時間後）

## 設定ファイル

### `pyproject.toml`
- プロジェクトメタデータ
- 依存関係定義
- pytest、black、mypyの設定

### `requirements.txt`
- 本番環境の依存関係
- FastAPI、Pillow、APSchedulerなど

### `requirements-dev.txt`
- 開発環境の依存関係
- pytest、black、flake8、mypyなど

## ドキュメント (`docs/`)

- `DIRECTORY_STRUCTURE.md`: 本ドキュメント
- `DEVELOPMENT_GUIDE.md`: 開発ガイド（セットアップ、テスト、デプロイ）
- `API_REFERENCE.md`: REST API仕様

## Kiro Spec-Driven Development (`.kiro/`, `.claude/`)

本プロジェクトはKiroスタイルのSpec-Driven Developmentを採用しています。

**主要コマンド**:
- `/kiro:spec-init`: 仕様の初期化
- `/kiro:spec-requirements`: 要件定義生成
- `/kiro:spec-design`: 技術設計生成
- `/kiro:spec-tasks`: タスク分解
- `/kiro:spec-status`: 進捗確認

詳細は`CLAUDE.md`を参照してください。

## セキュリティ考慮事項

1. **ディレクトリトラバーサル対策**: ファイル名の検証により、親ディレクトリへのアクセスを防止
2. **ファイルサイズ制限**: 10MB制限によりDoS攻撃を緩和
3. **ファイル形式検証**: MIMEタイプとマジックバイトの両方を検証
4. **セッション分離**: 各ユーザーセッションは独立したディレクトリ
5. **自動クリーンアップ**: 古いファイルの自動削除により、ストレージ枯渇を防止

## パフォーマンス最適化

1. **非同期処理**: FastAPIの非同期エンドポイント
2. **効率的な画像処理**: Pillow（PIL）による最適化
3. **キャッシュバスティング**: タイムスタンプによる画像キャッシュ回避
4. **レスポンシブデザイン**: モバイル対応のUI

## 今後の拡張計画

- [ ] フロントエンドテストの追加（Jest、Cypress）
- [ ] パフォーマンステストの拡充
- [ ] Docker化
- [ ] CI/CDパイプライン
- [ ] データベース統合（セッション永続化）
- [ ] ユーザー認証
- [ ] 複数画像の一括処理
- [ ] より高度な透過アルゴリズム
