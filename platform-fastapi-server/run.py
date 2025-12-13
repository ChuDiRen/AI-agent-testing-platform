"""应用启动脚本"""
import logging

import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    try:
        logger.info("正在启动服务器...")
        uvicorn.run(
            "app:application",
            host="0.0.0.0",
            port=5000,
            reload=True,
            reload_excludes=["temp", "data", "*.log", "*.pyc", "__pycache__"],
            reload_dirs=["plugin", "core", "apitest", "login", "sysmanage", "generator", "aiassistant", "msgmanage"],
            log_level="info"
        )
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


