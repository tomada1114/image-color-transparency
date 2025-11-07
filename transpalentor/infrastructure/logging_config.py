"""
ロギング設定
構造化ロギングとログレベルの管理
"""
import logging
import sys
from pathlib import Path
from typing import Optional

# ログディレクトリ
LOG_DIR = Path("/var/log/transpalentor")
LOG_FILE = LOG_DIR / "app.log"

# ログフォーマット
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_LOG_FORMAT = (
    '{"timestamp": "%(asctime)s", "logger": "%(name)s", '
    '"level": "%(levelname)s", "message": "%(message)s"}'
)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    指定された名前のロガーを取得

    Args:
        name: ロガー名(通常はモジュール名)
        level: ログレベル(デフォルトはINFO)

    Returns:
        設定されたロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # ハンドラーが既に設定されている場合はスキップ
    if logger.handlers:
        return logger

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(console_handler)

    return logger


def setup_file_logging(
    logger: logging.Logger, log_file: Optional[Path] = None, level: int = logging.INFO
) -> None:
    """
    ファイルログハンドラーを設定

    Args:
        logger: 設定するロガー
        log_file: ログファイルパス(デフォルトはLOG_FILE)
        level: ログレベル(デフォルトはINFO)
    """
    if log_file is None:
        log_file = LOG_FILE

    # ログディレクトリが存在しない場合は作成を試みる
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # ファイルハンドラーの設定
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)
    except PermissionError:
        # ログディレクトリの作成権限がない場合は警告を出すのみ
        logger.warning(f"Cannot create log directory: {log_file.parent}")


def get_structured_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    JSON形式の構造化ロギングを行うロガーを取得

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        JSON形式でログを出力するロガー
    """
    logger = logging.getLogger(f"{name}.json")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    json_formatter = logging.Formatter(JSON_LOG_FORMAT)
    console_handler.setFormatter(json_formatter)

    logger.addHandler(console_handler)

    return logger
