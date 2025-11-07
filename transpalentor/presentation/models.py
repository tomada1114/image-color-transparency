"""
APIリクエスト/レスポンスのPydanticモデル
"""
from typing import Optional

from pydantic import BaseModel, Field


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
    target_color: RGBColor = Field(..., description="透過対象色")


class ProcessResponse(BaseModel):
    """透過処理レスポンス"""

    session_id: str = Field(..., description="セッションID")
    processed_image_url: str = Field(..., description="処理済み画像のURL")
    filename: str = Field(..., description="ファイル名")


class CleanupResponse(BaseModel):
    """クリーンアップレスポンス"""

    session_id: str = Field(..., description="セッションID")
    status: str = Field(..., description="削除ステータス")
