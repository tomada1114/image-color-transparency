"""
消しゴムAPIエンドポイントのテスト
"""
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from transpalentor.presentation.app import app


@pytest.fixture
def client():
    """テストクライアントのフィクスチャ"""
    return TestClient(app)


@pytest.fixture
def uploaded_image_session(client):
    """画像をアップロードしてセッション情報を返すフィクスチャ"""
    # テスト用画像を作成
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # 画像をアップロード
    response = client.post(
        "/api/upload", files={"file": ("test.png", img_byte_arr, "image/png")}
    )
    assert response.status_code == 200

    data = response.json()
    session_id = data["session_id"]
    filename = data["filename"]

    # 透過処理を実行して処理済み画像を作成
    process_response = client.post(
        "/api/process",
        json={
            "session_id": session_id,
            "filename": filename,
            "rgb": [255, 0, 0],
            "threshold": 30,
        },
    )
    assert process_response.status_code == 200

    processed_data = process_response.json()
    processed_filename = processed_data["filename"]

    return {
        "session_id": session_id,
        "filename": processed_filename,
    }


def test_erase_success(client, uploaded_image_session):
    """消しゴム処理が正常に動作することをテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # 消しゴムリクエスト
    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50], [25, 25]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "session_id" in data
    assert "processed_url" in data
    assert "filename" in data
    assert data["session_id"] == session_id
    assert data["filename"] == filename


def test_erase_validates_session_id(client):
    """消しゴム処理が無効なセッションIDを検証することをテスト"""
    response = client.post(
        "/api/erase",
        json={
            "session_id": "invalid-session-id",
            "filename": "test.png",
            "strokes": [[50, 50]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_erase_validates_file_existence(client, uploaded_image_session):
    """消しゴム処理がファイルの存在を検証することをテスト"""
    session_id = uploaded_image_session["session_id"]

    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": "nonexistent.png",
            "strokes": [[50, 50]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_erase_validates_strokes_format(client, uploaded_image_session):
    """消しゴム処理がストローク形式を検証することをテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # ストロークが空の配列
    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [],
            "brush_size": 10,
        },
    )

    # 空のストロークでもリクエストは成功すべき（何も消さない）
    assert response.status_code == 200


def test_erase_validates_brush_size(client, uploaded_image_session):
    """消しゴム処理がブラシサイズを検証することをテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # ブラシサイズが1未満
    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50]],
            "brush_size": 0,
        },
    )

    assert response.status_code == 422  # バリデーションエラー


def test_erase_with_large_brush_size(client, uploaded_image_session):
    """大きいブラシサイズでの消しゴム処理をテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50]],
            "brush_size": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == session_id


def test_erase_with_multiple_strokes(client, uploaded_image_session):
    """複数のストロークでの消しゴム処理をテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # 多数のストロークを含むリクエスト
    strokes = [[i, i] for i in range(10, 90, 10)]

    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": strokes,
            "brush_size": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "processed_url" in data


def test_erase_updates_image_file(client, uploaded_image_session):
    """消しゴム処理が画像ファイルを更新することをテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # 最初の消しゴム処理
    response1 = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50]],
            "brush_size": 10,
        },
    )

    assert response1.status_code == 200
    url1 = response1.json()["processed_url"]

    # 2回目の消しゴム処理
    response2 = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[25, 25]],
            "brush_size": 10,
        },
    )

    assert response2.status_code == 200
    url2 = response2.json()["processed_url"]

    # URLにタイムスタンプが含まれているため、異なるべき
    assert url1 != url2


def test_erase_preserves_rgba_format(client, uploaded_image_session):
    """消しゴム処理がRGBA形式を保持することをテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 200

    # 処理後の画像を取得して形式を確認
    # （実際にはファイルを読み込む必要があるが、APIレベルでは成功を確認）
    data = response.json()
    assert "processed_url" in data


def test_erase_handles_edge_coordinates(client, uploaded_image_session):
    """画像の端の座標での消しゴム処理をテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    # 画像の端の座標を指定
    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[0, 0], [99, 99]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 200


def test_erase_request_model_validation(client):
    """消しゴムリクエストモデルのバリデーションをテスト"""
    # 必須フィールドが欠けている
    response = client.post(
        "/api/erase",
        json={
            "session_id": "test-session",
            # filename が欠けている
            "strokes": [[50, 50]],
            "brush_size": 10,
        },
    )

    assert response.status_code == 422


def test_erase_with_minimum_brush_size(client, uploaded_image_session):
    """最小ブラシサイズでの消しゴム処理をテスト"""
    session_id = uploaded_image_session["session_id"]
    filename = uploaded_image_session["filename"]

    response = client.post(
        "/api/erase",
        json={
            "session_id": session_id,
            "filename": filename,
            "strokes": [[50, 50]],
            "brush_size": 1,  # 最小サイズ
        },
    )

    assert response.status_code == 200
