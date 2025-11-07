"""
FastAPIアプリケーションの基本構成のテスト
"""
import pytest
from fastapi.testclient import TestClient


def test_app_creation() -> None:
    """アプリケーションが正常に作成できることをテスト"""
    from transpalentor.presentation.app import app

    assert app is not None
    assert app.title == "Transpalentor"


def test_health_endpoint() -> None:
    """ヘルスチェックエンドポイントが正常に動作することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_cors_middleware() -> None:
    """CORSミドルウェアが設定されていることをテスト"""
    from transpalentor.presentation.app import app

    # ミドルウェアスタックにCORSMiddlewareが含まれているか確認
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_classes


def test_static_files_mount() -> None:
    """静的ファイルマウントが設定されていることをテスト"""
    from transpalentor.presentation.app import app

    # ルートリストから静的ファイルマウントを確認
    routes = [route.path for route in app.routes]
    assert "/static" in routes or any("/static" in route for route in routes)


def test_root_endpoint() -> None:
    """ルートエンドポイントがindex.htmlを返すことをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
