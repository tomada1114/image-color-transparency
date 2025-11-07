"""
画像表示機能のテスト
"""
import io
import shutil

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def create_test_image(format: str = "PNG", size: tuple = (100, 100)) -> io.BytesIO:
    """テスト用の画像を作成"""
    image = Image.new("RGB", size, color="blue")
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer


def test_get_image_success() -> None:
    """アップロードした画像を取得できることをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG")
    upload_response = client.post(
        "/api/upload", files={"file": ("test.png", image_data, "image/png")}
    )

    assert upload_response.status_code == 200
    upload_data = upload_response.json()

    # 画像を取得
    image_url = upload_data["image_url"]
    get_response = client.get(image_url)

    assert get_response.status_code == 200
    assert "image/" in get_response.headers["content-type"]

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(upload_data["session_id"])
    shutil.rmtree(session_dir)


def test_get_image_not_found() -> None:
    """存在しない画像を取得しようとすると404が返ることをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # 存在しないセッションIDとファイル名
    response = client.get("/api/images/12345678-1234-4234-8234-123456789abc/nonexistent.png")

    assert response.status_code == 404


def test_get_image_invalid_session_id() -> None:
    """無効なセッションIDで画像を取得しようとすると404が返ることをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # 無効なセッションID
    response = client.get("/api/images/invalid-session-id/test.png")

    assert response.status_code == 404
