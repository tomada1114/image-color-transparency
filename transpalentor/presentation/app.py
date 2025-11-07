"""
FastAPIアプリケーションのメインエントリーポイント
"""
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .error_handlers import register_exception_handlers
from .models import UploadResponse, ProcessRequest, ProcessResponse, EraseRequest, EraseResponse
from .exceptions import SessionNotFoundError
from ..application.validation import validate_image_file, get_file_extension
from ..infrastructure.file_storage import (
    generate_session_id,
    sanitize_filename,
    save_uploaded_file,
    validate_session_id,
    get_session_directory,
)


def _convert_rgb_to_domain_format(
    rgb: list[int] | list[list[int]]
) -> tuple[int, int, int] | list[tuple[int, int, int]]:
    """
    APIリクエストのRGB形式をドメインロジックの形式に変換

    Args:
        rgb: APIリクエストのRGB値
             - 単一色: [R, G, B]
             - 複数色: [[R, G, B], [R, G, B], ...]

    Returns:
        ドメインロジック用のRGB値
        - 単一色: (R, G, B)
        - 複数色: [(R, G, B), (R, G, B), ...]
    """
    if len(rgb) == 3 and all(isinstance(x, int) for x in rgb):
        # 単一色の場合
        return tuple(rgb)
    else:
        # 複数色の場合
        return [tuple(color) for color in rgb]

# プロジェクトのルートディレクトリを取得
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
TMP_DIR = BASE_DIR / "tmp" / "transpalentor"

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Transpalentor",
    description="画像の色指定による透過処理アプリケーション",
    version="0.1.0",
)

# グローバル例外ハンドラーの登録
register_exception_handlers(app)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境では全てのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    ヘルスチェックエンドポイント

    Returns:
        サーバーの状態を示す辞書
    """
    return {"status": "healthy"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)) -> UploadResponse:
    """
    画像ファイルをアップロード

    Args:
        file: アップロードされた画像ファイル

    Returns:
        アップロード結果

    Raises:
        FileTooLargeError: ファイルサイズが10MBを超える場合
        UnsupportedFormatError: サポートされていない形式の場合
    """
    # 画像ファイルのバリデーション
    img_format, file_size = await validate_image_file(file)

    # セッションIDを生成
    session_id = generate_session_id()

    # ファイル名をサニタイズ
    original_filename = file.filename or "image"
    safe_filename = sanitize_filename(original_filename)

    # 拡張子を適切なものに設定
    extension = get_file_extension(img_format)
    if not safe_filename.endswith(extension):
        safe_filename = safe_filename.rsplit(".", 1)[0] + extension

    # ファイルを読み込んで保存
    file_content = await file.read()
    file_path = await save_uploaded_file(session_id, safe_filename, file_content)

    # 画像URLを生成
    image_url = f"/api/images/{session_id}/{safe_filename}"

    return UploadResponse(
        session_id=session_id,
        image_url=image_url,
        filename=safe_filename,
        size=file_size,
    )


@app.get("/api/images/{session_id}/{filename}")
async def get_image(session_id: str, filename: str) -> FileResponse:
    """
    セッションIDとファイル名から画像を取得

    Args:
        session_id: セッションID
        filename: ファイル名

    Returns:
        画像ファイル

    Raises:
        SessionNotFoundError: セッションが見つからない場合
    """
    # セッションIDのバリデーション
    if not validate_session_id(session_id):
        raise SessionNotFoundError(session_id=session_id)

    # セッションディレクトリを取得
    session_dir = get_session_directory(session_id)

    # ファイルパスを構築
    file_path = session_dir / filename

    # ファイルが存在するか確認
    if not file_path.exists():
        raise SessionNotFoundError(session_id=session_id)

    # MIMEタイプを推測
    import mimetypes

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    return FileResponse(str(file_path), media_type=mime_type)


@app.post("/api/process", response_model=ProcessResponse)
async def process_transparency(request: ProcessRequest) -> ProcessResponse:
    """
    画像の透過処理を実行

    Args:
        request: 透過処理リクエスト（セッションID、ファイル名、RGB値）

    Returns:
        処理済み画像のURL

    Raises:
        SessionNotFoundError: セッションまたはファイルが見つからない場合
    """
    from PIL import Image
    from ..domain.transparency import make_transparent

    # セッションIDのバリデーション
    if not validate_session_id(request.session_id):
        raise SessionNotFoundError(session_id=request.session_id)

    # セッションディレクトリを取得
    session_dir = get_session_directory(request.session_id)

    # 元画像のパスを構築
    original_path = session_dir / request.filename

    # ファイルが存在するか確認
    if not original_path.exists():
        raise SessionNotFoundError(session_id=request.session_id)

    # 画像を読み込み
    image = Image.open(original_path)

    # 透過処理を実行
    rgb_data = _convert_rgb_to_domain_format(request.rgb)
    processed_image = make_transparent(
        image, rgb=rgb_data, threshold=request.threshold
    )

    # 処理済み画像のファイル名を生成
    name_without_ext = original_path.stem
    ext = original_path.suffix
    processed_filename = f"{name_without_ext}_processed{ext}"

    # 処理済み画像を保存
    processed_path = session_dir / processed_filename
    processed_image.save(str(processed_path), format="PNG")

    # 処理済み画像のURLを生成
    processed_url = f"/api/images/{request.session_id}/{processed_filename}"

    return ProcessResponse(
        session_id=request.session_id,
        processed_url=processed_url,
        filename=processed_filename,
    )


@app.post("/api/erase", response_model=EraseResponse)
async def erase_transparency(request: EraseRequest) -> EraseResponse:
    """
    消しゴムツールで指定座標を透過処理

    Args:
        request: 消しゴムツールリクエスト（セッションID、ファイル名、座標、ブラシサイズ）

    Returns:
        処理済み画像のURL

    Raises:
        SessionNotFoundError: セッションまたはファイルが見つからない場合
    """
    from PIL import Image
    from ..domain.transparency import erase_at_coordinates

    # セッションIDのバリデーション
    if not validate_session_id(request.session_id):
        raise SessionNotFoundError(session_id=request.session_id)

    # セッションディレクトリを取得
    session_dir = get_session_directory(request.session_id)

    # 画像のパスを構築
    image_path = session_dir / request.filename

    # ファイルが存在するか確認
    if not image_path.exists():
        raise SessionNotFoundError(session_id=request.session_id)

    # 画像を読み込み
    image = Image.open(image_path)

    # 消しゴム処理を実行
    processed_image = erase_at_coordinates(
        image, strokes=request.strokes, brush_size=request.brush_size
    )

    # 処理済み画像を同じファイルに上書き保存
    processed_image.save(str(image_path), format="PNG")

    # 処理済み画像のURLを生成（キャッシュ回避のためタイムスタンプを追加）
    import time
    timestamp = int(time.time() * 1000)
    processed_url = f"/api/images/{request.session_id}/{request.filename}?t={timestamp}"

    return EraseResponse(
        session_id=request.session_id,
        processed_url=processed_url,
        filename=request.filename,
    )


@app.get("/")
async def root() -> FileResponse:
    """
    ルートエンドポイント - index.htmlを返す

    Returns:
        index.htmlファイル
    """
    index_path = STATIC_DIR / "index.html"
    return FileResponse(str(index_path), media_type="text/html")


# 一時ディレクトリが存在しない場合は作成
TMP_DIR.mkdir(parents=True, exist_ok=True)
