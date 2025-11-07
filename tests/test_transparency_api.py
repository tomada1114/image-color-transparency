"""
透過処理APIエンドポイントのテスト
"""
import io
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def create_test_image(
    format: str = "PNG", size: tuple = (100, 100), color: tuple = (255, 0, 0)
) -> io.BytesIO:
    """
    テスト用の画像を作成

    Args:
        format: 画像フォーマット (PNG, JPEG, BMP)
        size: 画像サイズ (width, height)
        color: RGB色

    Returns:
        画像データを含むBytesIO
    """
    image = Image.new("RGB", size, color=color)
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer


def test_process_transparency_success() -> None:
    """透過処理が成功することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG", color=(255, 0, 0))
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    session_id = upload_data["session_id"]

    # 透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [255, 0, 0]},
    )

    assert process_response.status_code == 200
    process_data = process_response.json()
    assert "processed_url" in process_data
    assert "filename" in process_data
    assert session_id in process_data["processed_url"]

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_validates_rgb() -> None:
    """RGB値のバリデーションをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG")
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 無効なRGB値（範囲外）
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [256, 0, 0]},
    )
    assert process_response.status_code == 422

    # 無効なRGB値（負の値）
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [-1, 0, 0]},
    )
    assert process_response.status_code == 422

    # 無効なRGB値（要素数が不正）
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [255, 0]},
    )
    assert process_response.status_code == 422

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_missing_session() -> None:
    """存在しないセッションIDの処理をテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # 存在しないセッションIDで透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={
            "session_id": "nonexistent-session",
            "filename": "test.png",
            "rgb": [255, 0, 0],
        },
    )

    assert process_response.status_code == 404


def test_process_transparency_missing_file() -> None:
    """存在しないファイルの処理をテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG")
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 存在しないファイルで透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={
            "session_id": session_id,
            "filename": "nonexistent.png",
            "rgb": [255, 0, 0],
        },
    )

    assert process_response.status_code == 404

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_creates_processed_image() -> None:
    """透過処理が実際に画像を生成することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG", color=(0, 255, 0))
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [0, 255, 0]},
    )

    assert process_response.status_code == 200
    process_data = process_response.json()

    # 処理された画像を取得
    image_response = client.get(process_data["processed_url"])
    assert image_response.status_code == 200

    # 画像として読み込めることを確認
    processed_image = Image.open(io.BytesIO(image_response.content))
    assert processed_image.mode == "RGBA"

    # 透過処理が正しく行われたことを確認（すべて透明になっているはず）
    pixels = processed_image.load()
    r, g, b, a = pixels[0, 0]
    assert a == 0  # 透明

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_preserves_original() -> None:
    """透過処理が元画像を保持することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG")
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]
    original_url = upload_response.json()["image_url"]

    # 透過処理をリクエスト
    client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [255, 0, 0]},
    )

    # 元画像がまだ取得できることを確認
    original_response = client.get(original_url)
    assert original_response.status_code == 200

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_multiple_colors() -> None:
    """複数色の透過処理が成功することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG", color=(255, 0, 0))
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    session_id = upload_data["session_id"]

    # 複数色の透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={
            "session_id": session_id,
            "filename": "test_image.png",
            "rgb": [[255, 0, 0], [0, 255, 0]],
        },
    )

    assert process_response.status_code == 200
    process_data = process_response.json()
    assert "processed_url" in process_data
    assert "filename" in process_data
    assert session_id in process_data["processed_url"]

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_three_colors() -> None:
    """3色の透過処理が成功することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG", color=(255, 0, 0))
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 3色の透過処理をリクエスト
    process_response = client.post(
        "/api/process",
        json={
            "session_id": session_id,
            "filename": "test_image.png",
            "rgb": [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        },
    )

    assert process_response.status_code == 200
    process_data = process_response.json()
    assert "processed_url" in process_data

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_validates_max_colors() -> None:
    """最大3色の制限をテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG")
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 4色（制限オーバー）
    process_response = client.post(
        "/api/process",
        json={
            "session_id": session_id,
            "filename": "test_image.png",
            "rgb": [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]],
        },
    )
    assert process_response.status_code == 422

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)


def test_process_transparency_backwards_compatible() -> None:
    """単一色（従来形式）の透過処理が動作することをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)

    # まず画像をアップロード
    image_data = create_test_image("PNG", color=(255, 0, 0))
    upload_response = client.post(
        "/api/upload", files={"file": ("test_image.png", image_data, "image/png")}
    )
    session_id = upload_response.json()["session_id"]

    # 単一色の透過処理（従来形式: [R, G, B]）
    process_response = client.post(
        "/api/process",
        json={"session_id": session_id, "filename": "test_image.png", "rgb": [255, 0, 0]},
    )

    assert process_response.status_code == 200

    # クリーンアップ
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_dir = get_session_directory(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)
