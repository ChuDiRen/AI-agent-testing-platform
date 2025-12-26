#!/usr/bin/env python
"""
LangGraph API Server 启动脚本

在启动 langgraph dev 之前 patch 运行时，使自定义 SQLite checkpointer 生效。

使用方式：
    python start_server.py [--host HOST] [--port PORT]
    
或者直接运行：
    python -m start_server
"""

import os
import sys
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Start LangGraph API Server with SQLite persistence')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=2025, help='Port to bind (default: 2025)')
    parser.add_argument('--no-patch', action='store_true', help='Disable SQLite checkpointer patch')
    parser.add_argument('--no-browser', action='store_true', help='Disable auto browser opening')
    args = parser.parse_args()
    
    # 确保当前目录在 Python 路径中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 切换到项目目录
    os.chdir(current_dir)
    
    logger.info("=" * 60)
    logger.info("🚀 Starting LangGraph API Server with SQLite Persistence")
    logger.info("=" * 60)
    
    # Step 1: 应用 Runtime Patch
    if not args.no_patch:
        logger.info("📦 Applying runtime patch for SQLite checkpointer...")
        from memory.runtime_patch import patch_runtime_checkpointer
        if patch_runtime_checkpointer():
            logger.info("✅ SQLite checkpointer patch applied successfully")
        else:
            logger.warning("⚠️ Failed to apply patch, using default InMemorySaver")
    
    # Step 2: 加载配置
    import json
    config_path = os.path.join(current_dir, 'langgraph.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    logger.info(f"📄 Loaded config from: {config_path}")
    logger.info(f"   Graphs: {list(config.get('graphs', {}).keys())}")
    
    # Step 3: 启动服务器
    logger.info(f"🌐 Starting server on http://{args.host}:{args.port}")
    
    from langgraph_api.cli import run_server
    
    run_server(
        host=args.host,
        port=args.port,
        reload=True,
        graphs=config.get('graphs'),
        env=config.get('env'),
        store=config.get('store'),
        auth=config.get('auth'),
        open_browser=not args.no_browser,
    )


if __name__ == '__main__':
    main()
