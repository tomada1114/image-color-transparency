"""
Transpalentorアプリケーションのメインエントリーポイント
Uvicornサーバーを起動
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "transpalentor.presentation.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 開発環境では自動リロードを有効化
        log_level="info",
    )
