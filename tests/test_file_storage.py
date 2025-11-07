"""
一時ファイルストレージの初期化テスト
"""
import uuid
from pathlib import Path

import pytest


def test_session_id_generation() -> None:
    """セッションIDがUUID v4形式で生成されることをテスト"""
    from transpalentor.infrastructure.file_storage import generate_session_id

    session_id = generate_session_id()

    # UUID v4形式であることを確認
    assert isinstance(session_id, str)
    uuid_obj = uuid.UUID(session_id, version=4)
    assert str(uuid_obj) == session_id


def test_get_session_directory() -> None:
    """セッションディレクトリのパスが正しく生成されることをテスト"""
    from transpalentor.infrastructure.file_storage import get_session_directory

    session_id = "12345678-1234-4234-8234-123456789abc"
    session_dir = get_session_directory(session_id)

    assert isinstance(session_dir, Path)
    assert session_id in str(session_dir)
    assert "transpalentor" in str(session_dir)


def test_validate_session_id_valid() -> None:
    """有効なセッションIDがバリデーションをパスすることをテスト"""
    from transpalentor.infrastructure.file_storage import validate_session_id

    valid_session_id = str(uuid.uuid4())
    assert validate_session_id(valid_session_id) is True


def test_validate_session_id_invalid() -> None:
    """無効なセッションIDがバリデーションで拒否されることをテスト"""
    from transpalentor.infrastructure.file_storage import validate_session_id

    invalid_ids = [
        "not-a-uuid",
        "12345",
        "",
        "12345678-1234-1234-1234-12345678",  # 不完全なUUID
    ]

    for invalid_id in invalid_ids:
        assert validate_session_id(invalid_id) is False


def test_sanitize_filename() -> None:
    """ファイル名のサニタイゼーションが正しく動作することをテスト"""
    from transpalentor.infrastructure.file_storage import sanitize_filename

    # 安全な文字のみを含むファイル名はそのまま
    assert sanitize_filename("test_image.png") == "test_image.png"
    assert sanitize_filename("image-123.jpg") == "image-123.jpg"

    # 危険な文字を含むファイル名はサニタイズされる
    assert ".." not in sanitize_filename("../../etc/passwd")
    assert "/" not in sanitize_filename("path/to/file.png")
    assert "\\" not in sanitize_filename("path\\to\\file.png")
