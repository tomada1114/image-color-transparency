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
    rgb: list[int] | list[list[int]] = Field(
        ...,
        description="透過対象色 [R, G, B] または [[R, G, B], [R, G, B], ...]（最大3色）",
    )
    threshold: int = Field(default=30, ge=0, le=255, description="色の許容範囲 (0-255)")

    @field_validator("rgb")
    @classmethod
    def validate_rgb(cls, v: list[int] | list[list[int]]) -> list[int] | list[list[int]]:
        """RGB値のバリデーション"""
        # 単一色の場合（後方互換性）
        if len(v) == 3 and all(isinstance(x, int) for x in v):
            for value in v:
                if not 0 <= value <= 255:
                    raise ValueError(f"RGB値は0-255の範囲である必要があります: {value}")
            return v

        # 複数色の場合
        if not all(isinstance(color, list) for color in v):
            raise ValueError("rgbは [R, G, B] または [[R, G, B], ...] の形式である必要があります")

        if len(v) > 3:
            raise ValueError("最大3色まで指定できます")

        if len(v) == 0:
            raise ValueError("少なくとも1色を指定してください")

        for color in v:
            if len(color) != 3:
                raise ValueError(f"各色は[R, G, B]の形式である必要があります: {color}")
            for value in color:
                if not isinstance(value, int) or not 0 <= value <= 255:
                    raise ValueError(f"RGB値は0-255の整数である必要があります: {value}")

        return v


class ProcessResponse(BaseModel):
    """透過処理レスポンス"""

    session_id: str = Field(..., description="セッションID")
    processed_url: str = Field(..., description="処理済み画像のURL")
    filename: str = Field(..., description="ファイル名")


class EraseRequest(BaseModel):
    """消しゴムツールリクエスト"""

    session_id: str = Field(..., description="セッションID")
    filename: str = Field(..., description="処理対象のファイル名")
    strokes: list[list[int]] = Field(..., description="ストローク座標 [[x, y], [x, y], ...]")
    brush_size: int = Field(default=10, ge=1, le=100, description="ブラシサイズ (1-100)")

    @field_validator("strokes")
    @classmethod
    def validate_strokes(cls, v: list[list[int]]) -> list[list[int]]:
        """ストローク座標のバリデーション"""
        for coord in v:
            if len(coord) != 2:
                raise ValueError(f"座標は[x, y]の形式である必要があります: {coord}")
            if coord[0] < 0 or coord[1] < 0:
                raise ValueError(f"座標は0以上である必要があります: {coord}")
        return v


class EraseResponse(BaseModel):
    """消しゴムツールレスポンス"""

    session_id: str = Field(..., description="セッションID")
    processed_url: str = Field(..., description="処理済み画像のURL")
    filename: str = Field(..., description="ファイル名")


class CleanupResponse(BaseModel):
    """クリーンアップレスポンス"""

    session_id: str = Field(..., description="セッションID")
    status: str = Field(..., description="削除ステータス")
