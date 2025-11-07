"""
エラーハンドラー
FastAPIのグローバル例外ハンドラー
"""
from typing import Any, Dict, List, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .exceptions import (
    ColorNotSpecifiedError,
    FileTooLargeError,
    ImageProcessingError,
    SessionNotFoundError,
    TranspalentorException,
    UnsupportedFormatError,
)


def format_validation_error(error: ValidationError) -> Dict[str, Any]:
    """
    Pydanticのバリデーションエラーを標準フォーマットに変換

    Args:
        error: Pydanticのバリデーションエラー

    Returns:
        フォーマットされたエラー辞書
    """
    errors = []
    for err in error.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        errors.append({"field": field, "message": err["msg"], "type": err["type"]})

    return {"detail": "Validation error", "errors": errors, "fields": {}}


async def session_not_found_handler(
    request: Request, exc: SessionNotFoundError
) -> JSONResponse:
    """
    SessionNotFoundErrorのハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        404エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Session not found",
            "error_code": "SESSION_NOT_FOUND",
            "session_id": exc.session_id,
        },
    )


async def file_too_large_handler(request: Request, exc: FileTooLargeError) -> JSONResponse:
    """
    FileTooLargeErrorのハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        413エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={
            "detail": "File size exceeds maximum limit",
            "error_code": "FILE_TOO_LARGE",
            "max_size_mb": exc.max_size / (1024 * 1024),
            "uploaded_size_mb": exc.size / (1024 * 1024),
        },
    )


async def unsupported_format_handler(
    request: Request, exc: UnsupportedFormatError
) -> JSONResponse:
    """
    UnsupportedFormatErrorのハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        422エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Unsupported image format",
            "error_code": "UNSUPPORTED_FORMAT",
            "supported_formats": ["PNG", "JPEG", "BMP"],
            "provided_format": exc.format_name,
        },
    )


async def color_not_specified_handler(
    request: Request, exc: ColorNotSpecifiedError
) -> JSONResponse:
    """
    ColorNotSpecifiedErrorのハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        400エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Target color not specified",
            "error_code": "COLOR_NOT_SPECIFIED",
        },
    )


async def image_processing_error_handler(
    request: Request, exc: ImageProcessingError
) -> JSONResponse:
    """
    ImageProcessingErrorのハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        500エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred during image processing",
            "error_code": "PROCESSING_ERROR",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    汎用例外ハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        500エラーレスポンス
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
        },
    )


def register_exception_handlers(app: Any) -> None:
    """
    FastAPIアプリケーションに例外ハンドラーを登録

    Args:
        app: FastAPIアプリケーション
    """
    app.add_exception_handler(SessionNotFoundError, session_not_found_handler)
    app.add_exception_handler(FileTooLargeError, file_too_large_handler)
    app.add_exception_handler(UnsupportedFormatError, unsupported_format_handler)
    app.add_exception_handler(ColorNotSpecifiedError, color_not_specified_handler)
    app.add_exception_handler(ImageProcessingError, image_processing_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
