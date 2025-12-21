"""应用启动脚本"""
import logging
import os
import sys
from pathlib import Path

# 自动检测并使用虚拟环境
def ensure_venv():
    """确保使用虚拟环境运行"""
    # 获取项目根目录（run.py 的上级目录）
    project_root = Path(__file__).parent.parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    # 如果虚拟环境存在，且当前不是用虚拟环境运行的
    if venv_python.exists():
        current_python = Path(sys.executable).resolve()
        venv_python_resolved = venv_python.resolve()
        
        if current_python != venv_python_resolved:
            print(f"⚠️  检测到未使用虚拟环境，正在切换...")
            print(f"   当前 Python: {current_python}")
            print(f"   虚拟环境 Python: {venv_python_resolved}")
            # 用虚拟环境的 Python 重新执行当前脚本
            os.execv(str(venv_python_resolved), [str(venv_python_resolved)] + sys.argv)

ensure_venv()

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
        logger.info("=" * 60)
        logger.info("📡 FastAPI服务器: http://localhost:5000")
        logger.info("📖 API文档: http://localhost:5000/docs")
        logger.info("🤖 LangGraph API: http://localhost:5000/api/langgraph")
        logger.info("=" * 60)
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


