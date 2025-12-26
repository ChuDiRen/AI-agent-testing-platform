#!/usr/bin/env python3
"""
LangGraph API 服务器

支持开发模式和生产模式：
- 开发模式: python simple_server.py 或 python simple_server.py dev
- 生产模式: python simple_server.py prod
"""

import os
import sys
import json
import argparse
from pathlib import Path


def setup_environment(mode: str = "dev"):
    """设置必要的环境变量
    
    Args:
        mode: 运行模式，"dev" 或 "prod"
    """
    # 将 src 添加到 Python 路径
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # 设置工作目录为 agent-backend 目录
    work_dir = Path(__file__).parent
    os.chdir(work_dir)

    # 从 langgraph.json 加载图配置
    config_path = work_dir / "langgraph.json"
    graphs = {}

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            graphs = config.get("graphs", {})
    
    # 开发模式环境变量（使用内存存储）
    dev_env = {
        # 内存模式
        "DATABASE_URI": ":memory:",
        "REDIS_URI": "fake",
        "MIGRATIONS_PATH": "__inmem",
        # 服务器配置
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_RUNTIME_EDITION": "inmem",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "200",
        # 图配置
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        # 开发模式特有
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_API_URL": "http://localhost:2025",
        "N_JOBS_PER_WORKER": "1",
    }
    
    # 生产模式环境变量（使用 PostgreSQL + Redis）
    prod_env = {
        # PostgreSQL 数据库（从环境变量读取，提供默认值）
        "DATABASE_URI": os.getenv(
            "DATABASE_URI",
            "postgresql://postgres:postgres@localhost:5432/langgraph?sslmode=disable"
        ),
        # Redis 缓存
        "REDIS_URI": os.getenv("REDIS_URI", "redis://localhost:6379"),
        # 数据库迁移路径
        "MIGRATIONS_PATH": os.getenv("MIGRATIONS_PATH", "/app/migrations"),
        # 服务器配置
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_RUNTIME_EDITION": "postgres",  # 生产使用 postgres runtime
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "true",  # 生产禁用文件持久化
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "200",
        # 图配置
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        # 生产模式特有
        "LANGGRAPH_UI_BUNDLER": "false",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "production",
        "N_JOBS_PER_WORKER": "4",
    }
    
    # 根据模式设置环境变量
    if mode == "prod":
        os.environ.update(prod_env)
    else:
        os.environ.update(dev_env)
    
    # 如果存在 .env 文件则加载（会覆盖上面的默认值）
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file, override=True)
        except ImportError:
            pass


def get_server_config(mode: str = "dev") -> dict:
    """获取服务器配置
    
    Args:
        mode: 运行模式
        
    Returns:
        uvicorn 配置字典
    """
    # 开发模式配置
    dev_config = {
        "host": "0.0.0.0",
        "port": 2025,
        "reload": True,
        "access_log": False,
        "workers": 1,
        "log_level": "info",
    }
    
    # 生产模式配置
    prod_config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", "8000")),
        "reload": False,
        "access_log": True,
        "workers": int(os.getenv("WORKERS", "4")),
        "log_level": "warning",
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
    }
    
    base_log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter" if mode == "prod" else "logging.Formatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            }
        },
        "handlers": {
            "default": {
                "formatter": "json" if mode == "prod" else "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "level": "WARNING" if mode == "prod" else "INFO",
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn": {"level": "WARNING" if mode == "prod" else "INFO"},
            "uvicorn.error": {"level": "WARNING" if mode == "prod" else "INFO"},
            "uvicorn.access": {"level": "WARNING"},
        }
    }
    
    config = prod_config if mode == "prod" else dev_config
    config["log_config"] = base_log_config
    
    return config


def main():
    """启动服务器"""
    parser = argparse.ArgumentParser(description="LangGraph API Server")
    parser.add_argument(
        "mode", 
        nargs="?", 
        default="dev", 
        choices=["dev", "prod"],
        help="运行模式: dev(开发) 或 prod(生产)，默认 dev"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="服务端口（覆盖默认值）"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=None,
        help="工作进程数（仅生产模式有效）"
    )
    
    args = parser.parse_args()
    mode = args.mode
    
    # 设置环境
    setup_environment(mode)
    
    # 获取服务器配置
    server_config = get_server_config(mode)
    
    # 命令行参数覆盖
    if args.port:
        server_config["port"] = args.port
    if args.workers and mode == "prod":
        server_config["workers"] = args.workers
    
    # 打印启动信息
    if mode == "dev":
        print("🚀 启动 LangGraph API 服务器 [开发模式]")
        print("=" * 60)
        print(f"📍 服务器地址: http://localhost:{server_config['port']}")
        print(f"📚 API 文档: http://localhost:{server_config['port']}/docs")
        print(f"🎨 Studio 界面: http://localhost:{server_config['port']}/ui")
        print(f"💚 健康检查: http://localhost:{server_config['port']}/ok")
        print("=" * 60)
        print("⚠️  提示: 首次启动可能需要较长时间，请耐心等待...")
    else:
        print(f"🚀 启动 LangGraph API 服务器 [生产模式]")
        print(f"   端口: {server_config['port']}, 工作进程: {server_config['workers']}")

    try:
        import uvicorn
        
        # 生产模式使用多进程，不能用 reload
        if mode == "prod":
            uvicorn.run(
                "langgraph_api.server:app",
                host=server_config["host"],
                port=server_config["port"],
                workers=server_config["workers"],
                access_log=server_config["access_log"],
                log_level=server_config["log_level"],
                proxy_headers=server_config.get("proxy_headers", False),
                forwarded_allow_ips=server_config.get("forwarded_allow_ips", None),
            )
        else:
            uvicorn.run(
                "langgraph_api.server:app",
                host=server_config["host"],
                port=server_config["port"],
                reload=server_config["reload"],
                access_log=server_config["access_log"],
                log_config=server_config["log_config"],
            )
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
