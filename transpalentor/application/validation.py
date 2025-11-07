"""
画像ファイルのバリデーション
"""
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile
from PIL import Image

from ..presentation.exceptions import FileTooLargeError, UnsupportedFormatError

# サポートされている画像形式
SUPPORTED_FORMATS = {"PNG", "JPEG", "BMP"}

# 最大ファイルサイズ (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


async def validate_image_file(file: UploadFile) -> Tuple[str, int]:
    """
    アップロードされた画像ファイルをバリデーション

    Args:
        file: アップロードされたファイル

    Returns:
        タプル (format, size)

    Raises:
        FileTooLargeError: ファイルサイズが制限を超える場合
        UnsupportedFormatError: サポートされていない形式の場合
    """
    # ファイルサイズを取得
    content = await file.read()
    file_size = len(content)

    # ファイルサイズをチェック
    if file_size > MAX_FILE_SIZE:
        raise FileTooLargeError(
            size=file_size, max_size=MAX_FILE_SIZE, filename=file.filename or ""
        )

    # ファイルを先頭に戻す
    await file.seek(0)

    # Pillowで画像形式を検証
    try:
        img = Image.open(file.file)
        img_format = img.format

        if img_format not in SUPPORTED_FORMATS:
            raise UnsupportedFormatError(format_name=img_format or "unknown")

        # ファイルを再度先頭に戻す
        await file.seek(0)

        return img_format, file_size
    except Exception as e:
        # Pillowが画像を開けない場合
        if isinstance(e, UnsupportedFormatError):
            raise
        raise UnsupportedFormatError(
            format_name="corrupted or invalid", filename=file.filename or ""
        )


def get_file_extension(format_name: str) -> str:
    """
    画像形式から適切な拡張子を取得

    Args:
        format_name: 画像形式名

    Returns:
        拡張子 (ドット付き)
    """
    extension_map = {"PNG": ".png", "JPEG": ".jpg", "BMP": ".bmp"}

    return extension_map.get(format_name, ".png")
