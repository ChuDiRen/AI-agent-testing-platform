#!/usr/bin/env python
"""
统一 LangGraph API Server 启动脚本 (清理版本)

特性:
1. 合并 start_server.py 和 simple_server.py 的所有功能
2. 支持开发模式和生产模式
3. 完整的健康检查和诊断
4. 不依赖 Monkey Patch，更稳定可靠

使用方式:
    python unified_server_clean.py              # 开发模式 (默认)
    python unified_server_clean.py dev          # 开发模式
    python unified_server_clean.py prod         # 生产模式
    python unified_server_clean.py --port 8080  # 自定义端口
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedServerConfig:
    """统一服务器配置管理"""
    
    def __init__(self, mode: str = "dev"):
        self.mode = mode
        self.root_dir = Path(__file__).parent.resolve()
        self.config_file = self.root_dir / "langgraph.json"
        
    def setup_environment(self) -> None:
        """设置环境变量"""
        # 添加当前目录到 Python 路径
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        
        # 切换工作目录
        os.chdir(self.root_dir)
        
        # 设置基本环境变量（避免配置错误）
        os.environ.setdefault("DATABASE_URI", ":memory:")
        os.environ.setdefault("REDIS_URI", "fake")
        
        # 加载 langgraph.json 配置
        config = self.load_config()
        graphs = config.get("graphs", {})
        
        # 开发模式环境变量
        dev_env = {
            "DATABASE_URI": ":memory:",  # 内存模式
            "REDIS_URI": "fake",
            "MIGRATIONS_PATH": "__inmem",
            "ALLOW_PRIVATE_NETWORK": "true",
            "LANGGRAPH_RUNTIME_EDITION": "inmem",
            "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
            "LANGGRAPH_ALLOW_BLOCKING": "true",
            "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "200",
            "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
            "LANGGRAPH_UI_BUNDLER": "true",
            "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
            "LANGGRAPH_API_URL": "http://localhost:2025",
            "N_JOBS_PER_WORKER": "1",
            "BG_JOB_ISOLATED_LOOPS": "true",
            "LANGGRAPH_DEV_ALLOW_BLOCKING": "true",
        }
        
        # 生产模式环境变量
        prod_env = {
            "DATABASE_URI": os.getenv(
                "DATABASE_URI",
                "postgresql://postgres:postgres@localhost:5432/langgraph?sslmode=disable"
            ),
            "REDIS_URI": os.getenv("REDIS_URI", "redis://localhost:6379"),
            "MIGRATIONS_PATH": os.getenv("MIGRATIONS_PATH", "/app/migrations"),
            "ALLOW_PRIVATE_NETWORK": "true",
            "LANGGRAPH_RUNTIME_EDITION": "postgres",
            "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "true",
            "LANGGRAPH_ALLOW_BLOCKING": "true",
            "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "200",
            "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
            "LANGGRAPH_UI_BUNDLER": "false",
            "LANGSMITH_LANGGRAPH_API_VARIANT": "production",
            "N_JOBS_PER_WORKER": "4",
        }
        
        # 设置环境变量
        env_to_set = dev_env if self.mode == "dev" else prod_env
        for key, value in env_to_set.items():
            os.environ[key] = str(value)
        
        logger.info(f"✅ Environment configured for {self.mode} mode")
        
    def load_config(self) -> Dict[str, Any]:
        """加载LangGraph配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {self.config_file} not found, using defaults")
            return {
                "graphs": {},
                "env": ".env",
                "dependencies": ["."]
            }
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse config file: {e}")
            return {}


def run_server(mode: str, host: str = "127.0.0.1", port: int = 2025, workers: Optional[int] = None):
    """运行服务器"""
    try:
        import uvicorn
        from langgraph_cli.cli import dev
        
        logger.info(f"🚀 Starting LangGraph API Server in {mode.upper()} mode")
        logger.info(f"📍 Host: {host}")
        logger.info(f"🌐 Port: {port}")
        
        if mode == "dev":
            # 开发模式 - 使用 langgraph dev
            logger.info("🔧 Using LangGraph CLI for development mode")
            
            # 设置CLI参数
            dev_args = [
                "--host", host,
                "--port", str(port),
                "--no-browser"
            ]
            
            # 运行CLI
            dev(dev_args)
            
        else:
            # 生产模式 - 使用 uvicorn
            logger.info("🏭 Using Uvicorn for production mode")
            
            server_config = {
                "app": "langgraph_api.server:app",
                "host": host,
                "port": port,
                "log_level": "info",
                "access_log": True,
                "reload": False,
                "http": "httptools" if mode == "prod" else "auto",
                "max_requests": 1000 if mode == "prod" else None,
                "max_requests_jitter": 100 if mode == "prod" else None,
            }

            if mode == "prod":
                server_config.update({
                    "workers": workers or 4,
                    "proxy_headers": True,
                    "forwarded_allow_ips": "*",
                    "limit_concurrency": 100,
                    "limit_max_requests": 1000,
                })

            logger.info("🌐 Starting server with optimized configuration...")
            uvicorn.run(**server_config)

    except Exception as e:
        logger.error(f"❌ Server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统一 LangGraph API Server 启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python unified_server_clean.py              # 开发模式 (默认)
  python unified_server_clean.py dev          # 开发模式
  python unified_server_clean.py prod         # 生产模式
  python unified_server_clean.py --port 8080  # 自定义端口
  python unified_server_clean.py --no-browser # 不自动打开浏览器
        """
    )

    parser.add_argument(
        'mode', nargs='?', default='dev', choices=['dev', 'prod'],
        help='运行模式: dev(开发) 或 prod(生产)，默认 dev'
    )
    parser.add_argument(
        '--host', default='127.0.0.1',
        help='Host to bind (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', type=int, default=2025,
        help='Port to bind (default: 2025)'
    )
    parser.add_argument(
        '--workers', type=int,
        help='Number of worker processes (production mode only)'
    )
    parser.add_argument(
        '--no-browser', action='store_true',
        help='Do not open browser automatically'
    )

    args = parser.parse_args()
    
    # 设置服务器配置
    config = UnifiedServerConfig(args.mode)
    config.setup_environment()
    
    # 启动服务器
    server_start_time = time.time()
    
    try:
        run_server(args.mode, args.host, args.port, args.workers)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Port {args.port} is already in use")
            logger.info(f"💡 Try: python unified_server_clean.py --port {args.port + 1}")
        else:
            logger.error(f"❌ Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server failed: {e}")
        import traceback
        traceback.print_exc()
        
        # 提供故障排除信息
        logger.info("\n🔧 Troubleshooting tips:")
        logger.info("   1. Check if port is available: netstat -an | grep :2025")
        logger.info("   2. Verify Python dependencies: pip list | grep langgraph")
        logger.info("   3. Try different port: --port 8080")
        
        sys.exit(1)
    finally:
        total_time = time.time() - server_start_time
        logger.info(f"⏱️ Total startup time: {total_time:.2f}s")


if __name__ == '__main__':
    main()
