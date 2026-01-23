"""
FastAPI 应用启动脚本
"""
import uvicorn
import sys

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
        access_log=True
    )
