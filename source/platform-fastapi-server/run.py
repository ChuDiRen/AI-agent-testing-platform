"""应用启动脚本"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:application",
        host="0.0.0.0",
        port=8000,
        reload=True, # 开发环境启用热重载
        log_level="info",
        access_log=True
    )

