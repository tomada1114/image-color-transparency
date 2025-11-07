# 開発ガイド

## 目次

1. [環境構築](#環境構築)
2. [開発ワークフロー](#開発ワークフロー)
3. [コーディング規約](#コーディング規約)
4. [テスト](#テスト)
5. [デバッグ](#デバッグ)
6. [デプロイ](#デプロイ)
7. [トラブルシューティング](#トラブルシューティング)

## 環境構築

### 必要な環境

- **Python**: 3.10以上
- **pip**: 最新版推奨
- **仮想環境**: venv または virtualenv

### セットアップ手順

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd image-color-transparency
```

#### 2. 仮想環境の作成

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

#### 3. 依存関係のインストール

```bash
# 本番環境の依存関係
pip install -r requirements.txt

# 開発環境の依存関係（テスト、リンターなど）
pip install -r requirements-dev.txt
```

#### 4. ディレクトリの作成

```bash
# 一時ファイル用ディレクトリ
mkdir -p tmp/transpalentor

# ドキュメント用ディレクトリ（存在しない場合）
mkdir -p docs
```

#### 5. アプリケーションの起動

```bash
# 開発サーバーの起動
python main.py

# または uvicorn を直接使用
uvicorn transpalentor.presentation.app:app --reload --host 0.0.0.0 --port 8000
```

#### 6. ブラウザでアクセス

```
http://localhost:8000
```

## 開発ワークフロー

### Kiro Spec-Driven Development

本プロジェクトは、Kiroスタイルのスペック駆動開発を採用しています。

#### 基本ワークフロー

1. **仕様の初期化**
   ```
   /kiro:spec-init <feature-name> <description>
   ```

2. **要件定義**
   ```
   /kiro:spec-requirements <feature-name>
   ```

3. **技術設計**
   ```
   /kiro:spec-design <feature-name>
   ```

4. **タスク分解**
   ```
   /kiro:spec-tasks <feature-name>
   ```

5. **進捗確認**
   ```
   /kiro:spec-status <feature-name>
   ```

### Git ワークフロー

#### ブランチ戦略

- `main`: 本番環境向けの安定版
- `develop`: 開発版
- `feature/<feature-name>`: 新機能開発
- `bugfix/<bug-name>`: バグ修正
- `hotfix/<issue-name>`: 緊急修正

#### コミットメッセージ規約

```
<type>: <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル（フォーマット、セミコロンなど）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド、ツール設定など

**例**:
```
feat: 消しゴムツールによる透過処理機能を追加

ユーザーが処理後の画像に対して、部分的に透過処理を適用できる
消しゴムツールを実装。ブラシサイズの調整も可能。

Closes #123
```

## コーディング規約

### Python

#### コードフォーマット

**ツール**: Black

```bash
# すべてのPythonファイルをフォーマット
black .

# 特定のファイルをフォーマット
black transpalentor/presentation/app.py
```

**設定** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ["py310"]
```

#### リンティング

**ツール**: flake8

```bash
# すべてのPythonファイルをチェック
flake8 transpalentor tests

# 特定のファイルをチェック
flake8 transpalentor/presentation/app.py
```

#### 型チェック

**ツール**: mypy

```bash
# すべてのPythonファイルを型チェック
mypy transpalentor

# 特定のファイルを型チェック
mypy transpalentor/presentation/app.py
```

**設定** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### コーディングスタイル

#### 命名規則

- **モジュール/パッケージ**: `lowercase_with_underscores`
- **クラス**: `CapWords`
- **関数/変数**: `lowercase_with_underscores`
- **定数**: `UPPERCASE_WITH_UNDERSCORES`
- **プライベート**: `_leading_underscore`

#### ドキュメント文字列

```python
def process_transparency(
    image: Image.Image,
    target_color: tuple[int, int, int],
    threshold: int = 30
) -> Image.Image:
    """
    画像の指定色を透過処理する。

    Args:
        image: 処理対象の画像
        target_color: 透過する色のRGB値
        threshold: 色の許容範囲（0-100）

    Returns:
        透過処理後の画像

    Raises:
        ValueError: 閾値が範囲外の場合
    """
    ...
```

#### インポート順序

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール

```python
import os
from pathlib import Path

from fastapi import FastAPI
from PIL import Image

from transpalentor.domain.transparency import process_transparency
```

### JavaScript

#### コーディングスタイル

- **変数宣言**: `const` を優先、変更が必要な場合のみ `let`
- **関数**: アロー関数を推奨（`() => {}`）
- **命名**: camelCase
- **セミコロン**: 使用する
- **インデント**: 4スペース

#### 例

```javascript
const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        displayImage(data.image_url);
    } catch (error) {
        showError(error.message);
    }
};
```

## テスト

### テストの実行

#### すべてのテストを実行

```bash
pytest
```

#### 特定のテストファイルを実行

```bash
pytest tests/test_upload.py
```

#### 特定のテスト関数を実行

```bash
pytest tests/test_upload.py::test_upload_success
```

#### カバレッジ付きで実行

```bash
pytest --cov=transpalentor --cov-report=term-missing
```

#### HTMLカバレッジレポート生成

```bash
pytest --cov=transpalentor --cov-report=html
# htmlcov/index.html をブラウザで開く
```

### テストの書き方

#### テストファイルの構成

```python
"""
テストモジュールのドキュメント文字列
"""
import pytest
from fastapi.testclient import TestClient

from transpalentor.presentation.app import app

# フィクスチャ
@pytest.fixture
def client():
    """テストクライアントのフィクスチャ"""
    return TestClient(app)

# テスト関数
def test_feature_name(client):
    """
    機能のテスト

    Given: 前提条件
    When: 実行する操作
    Then: 期待される結果
    """
    # Arrange (準備)
    test_data = {"key": "value"}

    # Act (実行)
    response = client.post("/api/endpoint", json=test_data)

    # Assert (検証)
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

#### テストカバレッジ目標

- **全体**: 100%近く（現在76%）
- **クリティカルパス**: 100%
- **エラーハンドリング**: 100%

#### テスト優先順位

1. **Critical**: コア機能（透過処理、アップロード）
2. **High**: セキュリティ、バリデーション
3. **Medium**: エラーハンドリング、エッジケース
4. **Low**: UI、ロギング

### モック

```python
from unittest.mock import Mock, patch

def test_with_mock(mocker):
    """mockerフィクスチャを使用したテスト"""
    mock_storage = mocker.patch('transpalentor.infrastructure.file_storage.FileStorage')
    mock_storage.save_file.return_value = "test_file.png"

    # テストコード
    result = some_function()

    mock_storage.save_file.assert_called_once()
```

## デバッグ

### ロギング

#### ログレベル

- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 通常の動作情報
- `WARNING`: 警告
- `ERROR`: エラー
- `CRITICAL`: クリティカルなエラー

#### ロギング例

```python
import logging

logger = logging.getLogger(__name__)

def process_image(image_path: str):
    logger.info(f"Processing image: {image_path}")

    try:
        # 処理
        logger.debug(f"Image size: {image.size}")
        result = perform_operation()
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise
```

### デバッグツール

#### pdb（Python Debugger）

```python
import pdb

def debug_function():
    x = 10
    pdb.set_trace()  # ブレークポイント
    y = x * 2
    return y
```

#### FastAPI デバッグモード

```bash
uvicorn transpalentor.presentation.app:app --reload --log-level debug
```

## デプロイ

### 本番環境の準備

#### 1. 環境変数の設定

```bash
export PYTHONPATH=/path/to/project
export LOG_LEVEL=INFO
export TMP_DIR=/var/tmp/transpalentor
```

#### 2. Gunicornでの起動

```bash
pip install gunicorn

gunicorn transpalentor.presentation.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

#### 3. systemdサービス（例）

```ini
[Unit]
Description=Transpalentor Web Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/transpalentor
Environment="PYTHONPATH=/opt/transpalentor"
ExecStart=/opt/transpalentor/venv/bin/gunicorn \
    transpalentor.presentation.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### Docker化

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p tmp/transpalentor

EXPOSE 8000

CMD ["uvicorn", "transpalentor.presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# ビルド
docker build -t transpalentor:latest .

# 実行
docker run -p 8000:8000 -v $(pwd)/tmp:/app/tmp transpalentor:latest
```

## トラブルシューティング

### よくある問題と解決策

#### 問題: モジュールが見つからない

```
ModuleNotFoundError: No module named 'transpalentor'
```

**解決策**:
```bash
# PYTHONPATHを設定
export PYTHONPATH=/path/to/project

# または、プロジェクトをインストール
pip install -e .
```

#### 問題: テストが失敗する

```
ImportError: No module named 'httpx'
```

**解決策**:
```bash
# 開発依存関係をインストール
pip install -r requirements-dev.txt
```

#### 問題: ポートが既に使用されている

```
OSError: [Errno 98] Address already in use
```

**解決策**:
```bash
# 使用中のプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>

# または、別のポートを使用
uvicorn transpalentor.presentation.app:app --port 8001
```

#### 問題: ファイルアップロードが失敗する

**チェックリスト**:
1. `tmp/transpalentor` ディレクトリが存在するか
2. ディレクトリの書き込み権限があるか
3. ファイルサイズが10MB以下か
4. サポートされている形式（PNG/JPEG/BMP）か

```bash
# ディレクトリの作成と権限設定
mkdir -p tmp/transpalentor
chmod 755 tmp/transpalentor
```

## パフォーマンスプロファイリング

### cProfile

```bash
python -m cProfile -o profile.stats main.py
```

### メモリプロファイリング

```bash
pip install memory_profiler

python -m memory_profiler transpalentor/domain/transparency.py
```

## セキュリティチェック

### 依存関係の脆弱性スキャン

```bash
pip install safety

safety check
```

### セキュリティリンティング

```bash
pip install bandit

bandit -r transpalentor
```

## 貢献ガイドライン

プルリクエストを送信する前に：

1. すべてのテストが通ること
2. カバレッジが低下していないこと
3. コードがフォーマットされていること（Black）
4. リンターエラーがないこと（flake8）
5. 型チェックが通ること（mypy）
6. ドキュメントが更新されていること

```bash
# チェックリスト実行
black . && flake8 transpalentor tests && mypy transpalentor && pytest --cov=transpalentor
```

## リソース

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [Pillow ドキュメント](https://pillow.readthedocs.io/)
- [pytest ドキュメント](https://docs.pytest.org/)
- [PEP 8 -- Python コーディングスタイルガイド](https://pep8-ja.readthedocs.io/)

## ライセンス

プロジェクトのライセンスについては、`LICENSE` ファイルを参照してください。
