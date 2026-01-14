"""
SQL Agent Skills 主程序
基于LangChain官方文档的skills-sql-assistant示例
演示如何使用progressive disclosure技术实现技能的按需加载

架构说明：
- skills/ : 技能定义模块，包含Chinook音乐商店分析技能
- data/ : 数据管理模块，负责Chinook数据库下载和管理
- logic/ : 逻辑模块，包含agent创建和核心业务逻辑
- main/ : 主程序模块，包含演示和程序入口
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main.demo import run_demo

def main():
    """主程序入口"""
    print("="*60)
    print("🎵 SQL Agent Skills 主程序")
    print("="*60)
    print("📁 架构说明：")
    print("  - skills/ : 技能定义模块")
    print("  - data/ : 数据管理模块")
    print("  - logic/ : 逻辑模块")
    print("  - main/ : 主程序模块")
    print("="*60)
    
    # 运行演示
    asyncio.run(run_demo())

if __name__ == "__main__":
    main()
