.PHONY: help install install-dev test test-cov clean run format lint type-check all-checks

help:
	@echo "Transpalentor - 開発用コマンド"
	@echo ""
	@echo "使用可能なコマンド:"
	@echo "  make install       - 本番依存関係をインストール"
	@echo "  make install-dev   - 開発依存関係をインストール"
	@echo "  make run          - 開発サーバーを起動"
	@echo "  make test         - テストを実行"
	@echo "  make test-cov     - カバレッジ付きでテストを実行"
	@echo "  make format       - コードをフォーマット (Black)"
	@echo "  make lint         - リンターを実行 (Flake8)"
	@echo "  make type-check   - 型チェックを実行 (mypy)"
	@echo "  make all-checks   - 全チェック (format + lint + type-check + test)"
	@echo "  make clean        - 一時ファイルを削除"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python main.py

test:
	pytest -v

test-cov:
	pytest --cov=transpalentor --cov-report=html --cov-report=term
	@echo "HTMLレポートを生成しました: htmlcov/index.html"

format:
	black transpalentor tests
	@echo "コードフォーマット完了"

lint:
	flake8 transpalentor tests --max-line-length=100
	@echo "リンターチェック完了"

type-check:
	mypy transpalentor
	@echo "型チェック完了"

all-checks: format lint type-check test
	@echo "全チェック完了 ✓"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf tmp/transpalentor/* 2>/dev/null || true
	@echo "クリーンアップ完了"
