"""
APIリクエスト/レスポンスのPydanticモデル
"""
from typing import Optional, Annotated

from pydantic import BaseModel, Field, field_validator


class RGBColor(BaseModel):
    """RGB色モデル"""

    r: int = Field(..., ge=0, le=255, description="Red (0-255)")
    g: int = Field(..., ge=0, le=255, description="Green (0-255)")
    b: int = Field(..., ge=0, le=255, description="Blue (0-255)")


class UploadResponse(BaseModel):
    """画像アップロードレスポンス"""

    session_id: str = Field(..., description="セッションID (UUID v4)")
    image_url: str = Field(..., description="アップロードされた画像のURL")
    filename: str = Field(..., description="ファイル名")
    size: int = Field(..., description="ファイルサイズ (bytes)")


class ProcessRequest(BaseModel):
    """透過処理リクエスト"""

    session_id: str = Field(..., description="セッションID")
    filename: str = Field(..., description="処理対象のファイル名")
    rgb: list[int] = Field(..., min_length=3, max_length=3, description="透過対象色 [R, G, B]")
    threshold: int = Field(default=30, ge=0, le=255, description="色の許容範囲 (0-255)")

    @field_validator("rgb")
    @classmethod
    def validate_rgb_range(cls, v: list[int]) -> list[int]:
        """RGB値の範囲をバリデーション"""
        for value in v:
            if not 0 <= value <= 255:
                raise ValueError(f"RGB値は0-255の範囲である必要があります: {value}")
        return v


class ProcessResponse(BaseModel):
    """透過処理レスポンス"""

    session_id: str = Field(..., description="セッションID")
    processed_url: str = Field(..., description="処理済み画像のURL")
    filename: str = Field(..., description="ファイル名")


class CleanupResponse(BaseModel):
    """クリーンアップレスポンス"""

    session_id: str = Field(..., description="セッションID")
    status: str = Field(..., description="削除ステータス")
