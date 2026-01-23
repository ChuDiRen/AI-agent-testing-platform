"""
应用启动脚本
"""
import uvicorn

from config.settings import settings


def main():
    """主函数"""
    print(f"""
    ╔══════════════════════════════════════╗
    ║  {settings.APP_NAME} v{settings.APP_VERSION}   ║
    ╚══════════════════════════════════════╝
    """)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
