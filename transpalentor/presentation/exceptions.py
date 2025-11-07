"""
カスタム例外クラス
"""


class TranspalentorException(Exception):
    """Transpalentorアプリケーションのベース例外"""

    pass


class SessionNotFoundError(TranspalentorException):
    """セッションが見つからない場合の例外"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class FileValidationError(TranspalentorException):
    """ファイルバリデーションエラー"""

    def __init__(self, message: str, filename: str = ""):
        self.filename = filename
        super().__init__(message)


class FileTooLargeError(FileValidationError):
    """ファイルサイズが大きすぎる場合の例外"""

    def __init__(self, size: int, max_size: int, filename: str = ""):
        self.size = size
        self.max_size = max_size
        message = f"File size {size} bytes exceeds maximum limit of {max_size} bytes"
        super().__init__(message, filename)


class UnsupportedFormatError(FileValidationError):
    """サポートされていないファイル形式の例外"""

    def __init__(self, format_name: str, filename: str = ""):
        self.format_name = format_name
        message = f"Unsupported file format: {format_name}"
        super().__init__(message, filename)


class ImageProcessingError(TranspalentorException):
    """画像処理エラー"""

    pass


class ColorNotSpecifiedError(TranspalentorException):
    """透過対象色が指定されていない場合の例外"""

    def __init__(self):
        super().__init__("Target color not specified for transparency processing")
