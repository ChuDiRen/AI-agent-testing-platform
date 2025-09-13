# Copyright (c) 2025 左岚. All rights reserved.
"""
数据库切换脚本
帮助用户在SQLite和PostgreSQL之间切换数据库
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.logger import get_logger

logger = get_logger(__name__)


def update_env_file(database_type: str, **kwargs):
    """
    更新.env文件中的数据库配置
    
    Args:
        database_type: 数据库类型 ('sqlite' 或 'postgresql')
        **kwargs: 其他配置参数
    """
    env_file = Path(".env")
    env_example_file = Path(".env.example")
    
    # 如果.env文件不存在，从.env.example复制
    if not env_file.exists() and env_example_file.exists():
        logger.info("Creating .env file from .env.example")
        env_file.write_text(env_example_file.read_text(encoding='utf-8'), encoding='utf-8')
    
    if not env_file.exists():
        logger.error(".env file not found and .env.example not available")
        return False
    
    # 读取现有配置
    lines = []
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    updated_lines = []
    database_type_updated = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('DATABASE_TYPE='):
            updated_lines.append(f'DATABASE_TYPE={database_type}\n')
            database_type_updated = True
        elif database_type == 'sqlite' and line.startswith('SQLITE_FILE='):
            sqlite_file = kwargs.get('sqlite_file', './ai_agent.db')
            updated_lines.append(f'SQLITE_FILE={sqlite_file}\n')
        elif database_type == 'postgresql':
            if line.startswith('POSTGRES_HOST='):
                host = kwargs.get('host', 'localhost')
                updated_lines.append(f'POSTGRES_HOST={host}\n')
            elif line.startswith('POSTGRES_PORT='):
                port = kwargs.get('port', '5432')
                updated_lines.append(f'POSTGRES_PORT={port}\n')
            elif line.startswith('POSTGRES_USER='):
                user = kwargs.get('user', 'postgres')
                updated_lines.append(f'POSTGRES_USER={user}\n')
            elif line.startswith('POSTGRES_PASSWORD='):
                password = kwargs.get('password', 'password')
                updated_lines.append(f'POSTGRES_PASSWORD={password}\n')
            elif line.startswith('POSTGRES_DB='):
                db = kwargs.get('database', 'ai_agent_db')
                updated_lines.append(f'POSTGRES_DB={db}\n')
            else:
                updated_lines.append(line + '\n' if not line.endswith('\n') else line)
        else:
            updated_lines.append(line + '\n' if not line.endswith('\n') else line)
    
    # 如果DATABASE_TYPE没有找到，添加它
    if not database_type_updated:
        updated_lines.append(f'DATABASE_TYPE={database_type}\n')
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    logger.info(f"Updated .env file with DATABASE_TYPE={database_type}")
    return True


def switch_to_sqlite(sqlite_file: str = "./ai_agent.db"):
    """
    切换到SQLite数据库
    
    Args:
        sqlite_file: SQLite数据库文件路径
    """
    logger.info(f"Switching to SQLite database: {sqlite_file}")
    
    success = update_env_file('sqlite', sqlite_file=sqlite_file)
    if success:
        logger.info("Successfully switched to SQLite")
        logger.info(f"Database file: {sqlite_file}")
        logger.info("Please restart the application to apply changes")
    else:
        logger.error("Failed to switch to SQLite")


def switch_to_postgresql(host: str = "localhost", port: str = "5432", 
                        user: str = "postgres", password: str = "password", 
                        database: str = "ai_agent_db"):
    """
    切换到PostgreSQL数据库
    
    Args:
        host: PostgreSQL主机地址
        port: PostgreSQL端口
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名称
    """
    logger.info(f"Switching to PostgreSQL database: {user}@{host}:{port}/{database}")
    
    success = update_env_file('postgresql', 
                             host=host, port=port, user=user, 
                             password=password, database=database)
    if success:
        logger.info("Successfully switched to PostgreSQL")
        logger.info(f"Connection: postgresql://{user}:***@{host}:{port}/{database}")
        logger.info("Please restart the application to apply changes")
        logger.info("Make sure PostgreSQL server is running and accessible")
    else:
        logger.error("Failed to switch to PostgreSQL")


def show_current_config():
    """
    显示当前数据库配置
    """
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        logger.info("Current database configuration:")
        logger.info(f"  Database Type: {settings.DATABASE_TYPE}")
        logger.info(f"  Database URL: {settings.DATABASE_URL}")
        
        if settings.DATABASE_TYPE == 'sqlite':
            logger.info(f"  SQLite File: {settings.SQLITE_FILE}")
        elif settings.DATABASE_TYPE == 'postgresql':
            logger.info(f"  PostgreSQL Host: {settings.POSTGRES_HOST}")
            logger.info(f"  PostgreSQL Port: {settings.POSTGRES_PORT}")
            logger.info(f"  PostgreSQL User: {settings.POSTGRES_USER}")
            logger.info(f"  PostgreSQL Database: {settings.POSTGRES_DB}")
            
    except Exception as e:
        logger.error(f"Failed to load current configuration: {str(e)}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="数据库切换工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # SQLite命令
    sqlite_parser = subparsers.add_parser('sqlite', help='切换到SQLite数据库')
    sqlite_parser.add_argument('--file', default='./ai_agent.db', 
                              help='SQLite数据库文件路径 (默认: ./ai_agent.db)')
    
    # PostgreSQL命令
    pg_parser = subparsers.add_parser('postgresql', help='切换到PostgreSQL数据库')
    pg_parser.add_argument('--host', default='localhost', help='PostgreSQL主机地址')
    pg_parser.add_argument('--port', default='5432', help='PostgreSQL端口')
    pg_parser.add_argument('--user', default='postgres', help='数据库用户名')
    pg_parser.add_argument('--password', default='password', help='数据库密码')
    pg_parser.add_argument('--database', default='ai_agent_db', help='数据库名称')
    
    # 显示当前配置命令
    subparsers.add_parser('show', help='显示当前数据库配置')
    
    args = parser.parse_args()
    
    if args.command == 'sqlite':
        switch_to_sqlite(args.file)
    elif args.command == 'postgresql':
        switch_to_postgresql(args.host, args.port, args.user, args.password, args.database)
    elif args.command == 'show':
        show_current_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
