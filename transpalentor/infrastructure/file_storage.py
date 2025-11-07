"""
ファイルストレージの基盤機能
一時ファイルの保存・管理を担当
"""
import re
import uuid
from pathlib import Path
from typing import Optional

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TMP_DIR = BASE_DIR / "tmp" / "transpalentor"


def generate_session_id() -> str:
    """
    新しいセッションIDをUUID v4形式で生成

    Returns:
        UUID v4形式の文字列
    """
    return str(uuid.uuid4())


def validate_session_id(session_id: str) -> bool:
    """
    セッションIDがUUID v4形式であることを検証

    Args:
        session_id: 検証するセッションID

    Returns:
        有効な場合True、無効な場合False
    """
    try:
        uuid_obj = uuid.UUID(session_id, version=4)
        return str(uuid_obj) == session_id
    except (ValueError, AttributeError):
        return False


def get_session_directory(session_id: str) -> Path:
    """
    セッションIDに対応するディレクトリパスを取得

    Args:
        session_id: セッションID(UUID v4形式)

    Returns:
        セッションディレクトリのPath
    """
    return TMP_DIR / session_id


def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズし、安全な形式に変換
    ディレクトリトラバーサル攻撃を防止

    Args:
        filename: 元のファイル名

    Returns:
        サニタイズされたファイル名
    """
    # パス区切り文字を除去
    filename = filename.replace("/", "_").replace("\\", "_")

    # ..を除去
    filename = filename.replace("..", "_")

    # 英数字、ハイフン、アンダースコア、ドットのみ許可
    filename = re.sub(r"[^a-zA-Z0-9\-_.]", "_", filename)

    # 空文字列の場合はデフォルト名を返す
    if not filename:
        filename = "unnamed_file"

    return filename


def ensure_session_directory(session_id: str) -> Path:
    """
    セッションディレクトリが存在することを確認し、必要に応じて作成

    Args:
        session_id: セッションID(UUID v4形式)

    Returns:
        セッションディレクトリのPath

    Raises:
        ValueError: セッションIDが無効な形式の場合
    """
    if not validate_session_id(session_id):
        raise ValueError(f"Invalid session_id format: {session_id}")

    session_dir = get_session_directory(session_id)
    session_dir.mkdir(parents=True, exist_ok=True)

    return session_dir


def is_path_safe(file_path: Path, allowed_base: Optional[Path] = None) -> bool:
    """
    ファイルパスが許可されたディレクトリ配下にあるか検証
    ディレクトリトラバーサル攻撃を防止

    Args:
        file_path: 検証するファイルパス
        allowed_base: 許可されたベースディレクトリ(デフォルトはTMP_DIR)

    Returns:
        安全な場合True、危険な場合False
    """
    if allowed_base is None:
        allowed_base = TMP_DIR

    try:
        # パスを絶対パスに解決
        resolved_path = file_path.resolve()
        resolved_base = allowed_base.resolve()

        # ベースディレクトリ配下にあるか確認
        return resolved_path.is_relative_to(resolved_base)
    except (ValueError, RuntimeError):
        return False


async def save_uploaded_file(
    session_id: str, filename: str, file_content: bytes
) -> Path:
    """
    アップロードされたファイルを保存

    Args:
        session_id: セッションID
        filename: ファイル名(サニタイズ済み)
        file_content: ファイルの内容

    Returns:
        保存されたファイルのパス

    Raises:
        ValueError: セッションIDが無効な場合
        RuntimeError: ファイル保存に失敗した場合
    """
    # セッションディレクトリを確保
    session_dir = ensure_session_directory(session_id)

    # ファイルパスを構築
    file_path = session_dir / filename

    # パスの安全性を検証
    if not is_path_safe(file_path):
        raise RuntimeError(f"Unsafe file path detected: {file_path}")

    # ファイルを保存
    try:
        file_path.write_bytes(file_content)
        return file_path
    except Exception as e:
        raise RuntimeError(f"Failed to save file: {e}")
