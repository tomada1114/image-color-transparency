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

    # 空のファイル名はデフォルト名になる
    assert sanitize_filename("") == "unnamed_file"
    # "..." は "_." になる（.. は _ に置換され、最後の . は残る）
    assert sanitize_filename("...") == "_."


def test_ensure_session_directory_creates_directory() -> None:
    """ensure_session_directoryがディレクトリを作成することをテスト"""
    import shutil
    from transpalentor.infrastructure.file_storage import (
        ensure_session_directory,
        generate_session_id,
    )

    session_id = generate_session_id()

    try:
        session_dir = ensure_session_directory(session_id)

        # ディレクトリが作成されていることを確認
        assert session_dir.exists()
        assert session_dir.is_dir()
    finally:
        # クリーンアップ
        if session_dir.exists():
            shutil.rmtree(session_dir)


def test_ensure_session_directory_invalid_session_id() -> None:
    """無効なセッションIDでエラーが発生することをテスト"""
    from transpalentor.infrastructure.file_storage import ensure_session_directory

    with pytest.raises(ValueError, match="Invalid session_id format"):
        ensure_session_directory("invalid-session-id")
