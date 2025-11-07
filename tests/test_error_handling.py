"""
ロギングとエラーハンドリング基盤のテスト
"""
import logging

import pytest
from fastapi.testclient import TestClient


def test_logger_configuration() -> None:
    """ロガーが正しく設定されていることをテスト"""
    from transpalentor.infrastructure.logging_config import get_logger

    logger = get_logger("test_module")

    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_error_response_format() -> None:
    """エラーレスポンスが標準フォーマットに従っていることをテスト"""
    from transpalentor.presentation.app import app

    client = TestClient(app)
    # 存在しないエンドポイントにアクセス
    response = client.get("/nonexistent")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_validation_error_handling() -> None:
    """バリデーションエラーが適切に処理されることをテスト"""
    from transpalentor.presentation.error_handlers import format_validation_error
    from pydantic import BaseModel, ValidationError

    class TestModel(BaseModel):
        value: int

    # バリデーションエラーを発生させる
    try:
        TestModel(value="not_an_int")
    except ValidationError as e:
        formatted_error = format_validation_error(e)
        assert "detail" in formatted_error
        assert "fields" in formatted_error or "errors" in formatted_error


def test_custom_exception_handling() -> None:
    """カスタム例外が適切に処理されることをテスト"""
    from transpalentor.presentation.exceptions import SessionNotFoundError

    error = SessionNotFoundError(session_id="test-123")

    assert error.session_id == "test-123"
    assert "test-123" in str(error)
