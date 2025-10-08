#!/usr/bin/env python3
"""
AI Agent Testing Platform - 统一启动脚本
一键启动所有服务: FastAPI + Celery Worker + Celery Beat
"""
import os
import sys
import signal
import subprocess
import time
import multiprocessing
from typing import List


def check_redis():
    """检查Redis连接"""
    print("🔍 检查 Redis 连接...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        print("✅ Redis 连接正常\n")
        return True
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        print("💡 提示: 请先启动 Redis 服务")
        print("   Windows: redis-server")
        print("   Linux: sudo systemctl start redis")
        print("   Mac: brew services start redis\n")
        return False


def start_celery_worker():
    """启动Celery Worker进程"""
    print("🚀 正在启动 Celery Worker...")
    from app.core.celery_app import celery_app
    
    # 在子进程中启动Celery Worker
    argv = [
        'celery',
        '-A', 'app.core.celery_app',
        'worker',
        '--loglevel=info',
        '--pool=solo'  # Windows兼容
    ]
    celery_app.worker_main(argv)


def start_celery_beat():
    """启动Celery Beat进程"""
    print("🚀 正在启动 Celery Beat...")
    from app.core.celery_app import celery_app
    
    argv = [
        'celery',
        '-A', 'app.core.celery_app',
        'beat',
        '--loglevel=info'
    ]
    celery_app.start(argv)


def start_fastapi():
    """启动FastAPI服务"""
    print("🚀 正在启动 FastAPI 服务...\n")
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 多进程模式下禁用reload
        log_level="info"
    )


def print_banner():
    """打印启动横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🤖 AI Agent Testing Platform - API引擎插件            ║
║                                                           ║
║   统一启动 v1.0.0                                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函数"""
    print_banner()
    
    # 检查Redis
    if not check_redis():
        print("❌ 启动失败: Redis 未运行")
        sys.exit(1)
    
    # 启动Celery Worker进程
    celery_worker_process = multiprocessing.Process(target=start_celery_worker)
    celery_worker_process.daemon = True
    celery_worker_process.start()
    print(f"✅ Celery Worker 已启动 (PID: {celery_worker_process.pid})\n")
    
    time.sleep(2)
    
    # 启动Celery Beat进程(可选)
    try:
        celery_beat_process = multiprocessing.Process(target=start_celery_beat)
        celery_beat_process.daemon = True
        celery_beat_process.start()
        print(f"✅ Celery Beat 已启动 (PID: {celery_beat_process.pid})\n")
    except Exception as e:
        print(f"⚠️  Celery Beat 启动失败 (可选服务): {e}\n")
    
    time.sleep(1)
    
    print("="*60)
    print("📊 所有服务已启动")
    print("="*60)
    print("\n访问地址:")
    print("  • FastAPI Docs: http://localhost:8000/docs")
    print("  • API健康检查: http://localhost:8000/api/v1/api-engine/health")
    print("\n按 Ctrl+C 停止所有服务\n")
    print("="*60 + "\n")
    
    try:
        # 启动FastAPI (主进程)
        start_fastapi()
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止所有服务...")
        celery_worker_process.terminate()
        try:
            celery_beat_process.terminate()
        except:
            pass
        print("✅ 所有服务已停止")
        sys.exit(0)


if __name__ == "__main__":
    # Windows下需要设置
    if sys.platform == 'win32':
        multiprocessing.freeze_support()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

