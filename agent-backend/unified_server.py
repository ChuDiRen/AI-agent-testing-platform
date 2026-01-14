#!/usr/bin/env python
"""
统一 LangGraph API Server 启动脚本 (方案B: 深度整合)

特性:
1. 合并 start_server.py 和 simple_server.py 的所有功能
2. 预初始化自定义 checkpointer 和 store，确保在 langgraph dev 中生效
3. 完整的记忆系统健康检查和诊断
4. 支持开发模式和生产模式
5. 不依赖 Monkey Patch，更稳定可靠

使用方式:
    python unified_server.py              # 开发模式 (默认)
    python unified_server.py dev          # 开发模式
    python unified_server.py prod         # 生产模式
    python unified_server.py --port 8080  # 自定义端口
"""

import os
import sys
import json
import argparse
import logging
import asyncio
import aiosqlite
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
        self.data_dir = self.root_dir / "data"
        self.config_file = self.root_dir / "langgraph.json"
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_environment(self) -> None:
        """设置环境变量"""
        # 添加当前目录到 Python 路径
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        
        # 切换工作目录
        os.chdir(self.root_dir)
        
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
        
        # 应用环境变量
        env = prod_env if self.mode == "prod" else dev_env
        os.environ.update(env)
        
        # 加载 .env 文件（覆盖默认值）
        env_file = self.root_dir / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file, override=True)
            except ImportError:
                pass
    
    def load_config(self) -> Dict[str, Any]:
        """加载 langgraph.json 配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


class MemorySystemManager:
    """记忆系统管理器 - 预初始化和健康检查 - 纯异步实现"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "agent_memory.db"
        self.checkpointer = None
        self.store = None

    async def initialize(self) -> bool:
        """预初始化记忆系统 - 异步优化版本"""
        try:
            logger.info("🧠 Initializing Memory System (Optimized)...")

            # 延迟导入以避免启动时的昂贵操作
            import asyncio
            from memory.checkpointer import get_checkpointer
            from memory.store import get_store

            # 使用并发初始化减少总时间
            logger.info("   🔄 Starting concurrent initialization...")
            
            # 并发初始化 checkpointer 和 store
            checkpointer_task = asyncio.create_task(get_checkpointer())
            store_task = asyncio.create_task(get_store())
            
            # 等待并发初始化完成
            self.checkpointer, self.store = await asyncio.gather(
                checkpointer_task, store_task, return_exceptions=True
            )

            # 检查初始化结果
            if isinstance(self.checkpointer, Exception):
                logger.error(f"   ❌ Checkpointer initialization failed: {self.checkpointer}")
                self.checkpointer = None
            elif self.checkpointer:
                logger.info(f"   ✅ Checkpointer: {type(self.checkpointer).__name__}")

            if isinstance(self.store, Exception):
                logger.error(f"   ❌ Store initialization failed: {self.store}")
                self.store = None
            elif self.store:
                logger.info(f"   ✅ Store: {type(self.store).__name__}")

            logger.info(f"   ✅ Database: {self.db_path}")

            # 异步验证数据库连接
            await self._verify_database()

            return self.checkpointer is not None or self.store is not None

        except Exception as e:
            logger.error(f"   ❌ Memory system initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def _verify_database(self) -> None:
        """验证数据库连接和表结构 - 异步"""
        try:
            conn = await aiosqlite.connect(str(self.db_path))

            # 检查 checkpointer 表
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
            )
            has_checkpoints = await cursor.fetchone() is not None

            # 检查 store 表
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='long_term_memory'"
            )
            has_store = await cursor.fetchone() is not None

            await conn.close()

            logger.info(f"   📊 Database Tables: checkpoints={has_checkpoints}, store={has_store}")

        except Exception as e:
            logger.warning(f"   ⚠️ Database verification failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """记忆系统健康检查 - 简化版本"""
        try:
            from memory.config import MEMORY_CONFIG
            from memory.plugins.manager import MemoryPluginManager
            from memory.plugins.checkpointer_plugin import CheckpointerPlugin
            from memory.plugins.store_plugin import StorePlugin
            from memory.plugins.user_memory_plugin import UserMemoryPlugin

            mgr = MemoryPluginManager(MEMORY_CONFIG.db_path)
            existing = [p["name"] for p in mgr.list_plugins()]
            for plugin_cls in (CheckpointerPlugin, StorePlugin, UserMemoryPlugin):
                if plugin_cls.name not in existing:
                    mgr.register(plugin_cls)
                    existing.append(plugin_cls.name)

            for plugin_name in MEMORY_CONFIG.enabled_plugins:
                await mgr.enable_plugin(plugin_name)

            checkpointer_type = "unknown"
            store_type = "unknown"
            sessions_count = 0

            checkpointer_plugin = mgr.get("checkpointer")
            if checkpointer_plugin is not None:
                saver = await checkpointer_plugin.get_saver()
                checkpointer_type = type(saver).__name__
                sessions = await checkpointer_plugin.list_threads()
                sessions_count = len(sessions)

            store_plugin = mgr.get("store")
            if store_plugin is not None:
                store_type = type(store_plugin).__name__

            return {
                "status": "healthy",
                "checkpointer_type": checkpointer_type,
                "store_type": store_type,
                "database_path": str(self.db_path),
                "database_exists": self.db_path.exists(),
                "sessions_count": sessions_count,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


def print_banner(mode: str, host: str, port: int) -> None:
    """打印启动横幅"""
    logger.info("=" * 70)
    logger.info("🚀 LangGraph API Server - Unified Launcher (方案B)")
    logger.info("=" * 70)
    logger.info(f"   Mode: {mode.upper()}")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info("=" * 70)
    logger.info("")


def start_dev_server(config: UnifiedServerConfig, host: str, port: int,
                     open_browser: bool = True) -> None:
    """启动开发模式服务器 - 性能优化版本"""
    try:
        # 延迟导入以避免启动时的昂贵操作
        logger.info("🌐 Starting development server...")
        
        # 预检查 langgraph_api 可用性
        try:
            from langgraph_api.cli import run_server
            use_langgraph_cli = True
        except ImportError:
            logger.warning("⚠️ langgraph_api.cli not available, will use uvicorn")
            use_langgraph_cli = False

        # 加载配置
        lg_config = config.load_config()

        logger.info(f"   📍 Server: http://{host}:{port}")
        logger.info(f"   📚 API Docs: http://{host}:{port}/docs")
        logger.info(f"   🎨 Studio UI: http://{host}:{port}/ui")
        logger.info(f"   💚 Health: http://{host}:{port}/ok")
        logger.info("")

        if use_langgraph_cli:
            # 使用 langgraph_api.cli.run_server（优化版本）
            logger.info("🚀 Starting with langgraph_api.cli...")
            
            # 优化配置传递
            server_config = {
                "host": host,
                "port": port,
                "reload": True,
                "open_browser": open_browser,
                "allow_blocking": True,  # 允许阻塞操作（MCP客户端等第三方库）
                "graphs": lg_config.get('graphs'),
                "env": lg_config.get('env'),
                "store": lg_config.get('store'),
                "checkpointer": lg_config.get('checkpointer'),
                "auth": lg_config.get('auth'),
            }
            
            # 过滤 None 值
            filtered_config = {k: v for k, v in server_config.items() if v is not None}
            
            run_server(**filtered_config)
        else:
            # 回退到 uvicorn
            logger.info("🔄 Falling back to uvicorn...")
            start_uvicorn_server(host, port, mode="dev")

    except Exception as e:
        logger.error(f"❌ Development server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def start_prod_server(host: str, port: int, workers: Optional[int] = None) -> None:
    """启动生产模式服务器"""
    start_uvicorn_server(host, port, mode="prod", workers=workers)


def start_uvicorn_server(host: str, port: int, mode: str = "dev",
                         workers: Optional[int] = None) -> None:
    """使用 uvicorn 启动服务器 - 性能优化版本"""
    try:
        import uvicorn

        logger.info(f"🚀 Starting with uvicorn on http://{host}:{port}")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Workers: {workers or 1 if mode == 'prod' else 'dev'}")

        # 优化服务器配置
        server_config = {
            "app": "langgraph_api.server:app",
            "host": host,
            "port": port,
            "reload": mode == "dev",
            "access_log": mode == "prod",
            "log_level": "info" if mode == "dev" else "warning",
            # 性能优化配置
            "loop": "uvloop" if mode == "prod" else "asyncio",
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
        logger.error(f"❌ Uvicorn server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统一 LangGraph API Server 启动脚本 (方案B)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python unified_server.py              # 开发模式 (默认)
  python unified_server.py dev          # 开发模式
  python unified_server.py prod         # 生产模式
  python unified_server.py --port 8080  # 自定义端口
  python unified_server.py --no-browser # 不自动打开浏览器
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
        '--workers', type=int, default=None,
        help='工作进程数（仅生产模式有效）'
    )
    parser.add_argument(
        '--no-browser', action='store_true',
        help='不自动打开浏览器'
    )
    parser.add_argument(
        '--skip-memory-check', action='store_true',
        help='跳过记忆系统初始化检查'
    )

    args = parser.parse_args()

    # 打印横幅
    print_banner(args.mode, args.host, args.port)

    # 初始化配置
    config = UnifiedServerConfig(mode=args.mode)
    config.setup_environment()

    logger.info("📄 Configuration loaded from: langgraph.json")
    lg_config = config.load_config()
    logger.info(f"   Graphs: {list(lg_config.get('graphs', {}).keys())}")
    logger.info("")

    # 初始化记忆系统（异步）
    if not args.skip_memory_check:
        import asyncio
        
        logger.info("🔄 Initializing memory system...")
        memory_start_time = time.time()
        
        try:
            memory_manager = MemorySystemManager(config.data_dir)
            
            # 使用超时控制初始化时间
            async def initialize_with_timeout():
                try:
                    return await asyncio.wait_for(
                        memory_manager.initialize(), 
                        timeout=30.0  # 30秒超时
                    )
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Memory system initialization timed out after 30s")
                    return False
            
            if asyncio.run(initialize_with_timeout()):
                # 打印健康检查信息（异步调用）
                health_start_time = time.time()
                health = asyncio.run(memory_manager.health_check())
                health_time = time.time() - health_start_time
                
                logger.info(f"   💚 Memory Health: {health.get('status', 'unknown')} ({health_time:.2f}s)")
                logger.info(f"   📊 Checkpointer: {health.get('checkpointer_type', 'N/A')}")
                logger.info(f"   📊 Store: {health.get('store_type', 'N/A')}")
                logger.info(f"   📊 Sessions: {health.get('sessions_count', 0)}")
                logger.info("")
            else:
                logger.warning("⚠️ Memory system initialization failed, continuing anyway...")
                logger.info("")
                
        except Exception as e:
            logger.error(f"❌ Memory system check failed: {e}")
            logger.info("   💡 Continuing without memory system...")
            logger.info("")
        
        memory_time = time.time() - memory_start_time
        logger.info(f"⏱️ Memory initialization took: {memory_time:.2f}s")
        logger.info("")

    # 启动服务器
    server_start_time = time.time()
    logger.info("🚀 Starting server initialization...")
    
    try:
        if args.mode == "dev":
            start_dev_server(config, args.host, args.port, not args.no_browser)
        else:
            start_prod_server(args.host, args.port, args.workers)
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("💡 Try: pip install langgraph-api uvicorn")
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Port {args.port} is already in use")
            logger.info(f"💡 Try: python unified_server.py --port {args.port + 1}")
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
        logger.info("   3. Check memory system: python -c 'import asyncio; from memory import get_checkpointer; asyncio.run(get_checkpointer()); print(\"OK\")'")
        logger.info("   4. Try skipping memory check: --skip-memory-check")
        
        sys.exit(1)
    finally:
        total_time = time.time() - server_start_time
        logger.info(f"⏱️ Total startup time: {total_time:.2f}s")


if __name__ == '__main__':
    main()
