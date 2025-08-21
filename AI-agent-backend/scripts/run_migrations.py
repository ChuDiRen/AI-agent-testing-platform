"""
数据库迁移脚本
运行Alembic数据库迁移
"""

import sys
import os
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.logger import get_logger

logger = get_logger(__name__)


def run_command(command):
    """
    运行命令
    
    Args:
        command: 要运行的命令
        
    Returns:
        命令执行结果
    """
    try:
        logger.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        if result.returncode == 0:
            logger.info(f"Command executed successfully: {command}")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Command failed: {command}")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, command)
        
        return result
        
    except Exception as e:
        logger.error(f"Error running command '{command}': {str(e)}")
        raise


def create_migration(message):
    """
    创建新的迁移文件
    
    Args:
        message: 迁移消息
    """
    try:
        logger.info(f"Creating migration: {message}")
        command = f"alembic revision --autogenerate -m \"{message}\""
        run_command(command)
        logger.info("Migration created successfully")
        
    except Exception as e:
        logger.error(f"Error creating migration: {str(e)}")
        raise


def upgrade_database(revision="head"):
    """
    升级数据库到指定版本
    
    Args:
        revision: 目标版本，默认为最新版本
    """
    try:
        logger.info(f"Upgrading database to revision: {revision}")
        command = f"alembic upgrade {revision}"
        run_command(command)
        logger.info("Database upgraded successfully")
        
    except Exception as e:
        logger.error(f"Error upgrading database: {str(e)}")
        raise


def downgrade_database(revision):
    """
    降级数据库到指定版本
    
    Args:
        revision: 目标版本
    """
    try:
        logger.info(f"Downgrading database to revision: {revision}")
        command = f"alembic downgrade {revision}"
        run_command(command)
        logger.info("Database downgraded successfully")
        
    except Exception as e:
        logger.error(f"Error downgrading database: {str(e)}")
        raise


def show_current_revision():
    """
    显示当前数据库版本
    """
    try:
        logger.info("Getting current database revision")
        command = "alembic current"
        result = run_command(command)
        return result.stdout.strip()
        
    except Exception as e:
        logger.error(f"Error getting current revision: {str(e)}")
        raise


def show_migration_history():
    """
    显示迁移历史
    """
    try:
        logger.info("Getting migration history")
        command = "alembic history"
        result = run_command(command)
        return result.stdout
        
    except Exception as e:
        logger.error(f"Error getting migration history: {str(e)}")
        raise


def stamp_database(revision):
    """
    标记数据库版本（不执行迁移）
    
    Args:
        revision: 要标记的版本
    """
    try:
        logger.info(f"Stamping database with revision: {revision}")
        command = f"alembic stamp {revision}"
        run_command(command)
        logger.info("Database stamped successfully")
        
    except Exception as e:
        logger.error(f"Error stamping database: {str(e)}")
        raise


def create_initial_migration():
    """
    创建初始迁移
    """
    try:
        logger.info("Creating initial migration")
        
        # 首先检查是否已有迁移文件
        versions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic", "versions")
        if os.path.exists(versions_dir) and os.listdir(versions_dir):
            logger.info("Migration files already exist")
            return
        
        # 创建初始迁移
        create_migration("Initial migration")
        
        logger.info("Initial migration created successfully")
        
    except Exception as e:
        logger.error(f"Error creating initial migration: {str(e)}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 创建迁移
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # 升级数据库
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision (default: head)")
    
    # 降级数据库
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    
    # 显示当前版本
    subparsers.add_parser("current", help="Show current revision")
    
    # 显示历史
    subparsers.add_parser("history", help="Show migration history")
    
    # 标记版本
    stamp_parser = subparsers.add_parser("stamp", help="Stamp database with revision")
    stamp_parser.add_argument("revision", help="Revision to stamp")
    
    # 初始迁移
    subparsers.add_parser("init", help="Create initial migration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "create":
            create_migration(args.message)
        elif args.command == "upgrade":
            upgrade_database(args.revision)
        elif args.command == "downgrade":
            downgrade_database(args.revision)
        elif args.command == "current":
            current = show_current_revision()
            print(f"Current revision: {current}")
        elif args.command == "history":
            history = show_migration_history()
            print(history)
        elif args.command == "stamp":
            stamp_database(args.revision)
        elif args.command == "init":
            create_initial_migration()
        
    except Exception as e:
        logger.error(f"Migration command failed: {str(e)}")
        sys.exit(1)
