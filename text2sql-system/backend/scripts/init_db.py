"""
数据库初始化脚本 - 下载Chinook示例数据库
"""
import os
import sys
import requests
from pathlib import Path
from loguru import logger


def download_chinook() -> str:
    """
    从GitHub下载Chinook SQLite数据库

    Returns:
        数据库文件路径
    """
    # GitHub上的Chinook数据库URL
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    # 定位到data目录
    # 脚本位置: backend/scripts/init_db.py
    # data目录: backend/../../data/
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data"
    db_path = data_dir / "chinook.db"

    # 检查数据库是否已存在
    if db_path.exists() and db_path.stat().st_size > 0:
        logger.info(f"数据库已存在: {db_path}")
        logger.info(f"数据库大小: {db_path.stat().st_size / 1024:.2f} KB")
        return str(db_path)

    # 确保data目录存在
    data_dir.mkdir(parents=True, exist_ok=True)

    # 下载Chinook数据库
    logger.info(f"正在从GitHub下载Chinook数据库...")
    logger.info(f"下载地址: {db_url}")

    try:
        response = requests.get(db_url, stream=True, timeout=30)
        response.raise_for_status()

        # 写入文件
        with open(db_path, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    # 显示进度
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        logger.info(f"下载进度: {progress:.1f}%")

        file_size = db_path.stat().st_size
        logger.info(f"下载成功！")
        logger.info(f"文件路径: {db_path}")
        logger.info(f"文件大小: {file_size / 1024:.2f} KB")

        return str(db_path)

    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"文件写入失败: {str(e)}")
        raise


def verify_database(db_path: str) -> bool:
    """
    验证下载的数据库文件是否有效

    Args:
        db_path: 数据库文件路径

    Returns:
        验证是否通过
    """
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        # Chinook数据库应该包含这些表
        expected_tables = ['Album', 'Artist', 'Customer', 'Employee', 'Genre',
                       'Invoice', 'InvoiceLine', 'MediaType', 'Playlist',
                       'PlaylistTrack', 'Track']

        actual_tables = [table[0] for table in tables]

        conn.close()

        # 检查是否包含关键表
        has_expected_tables = any(table in expected_tables for table in actual_tables)

        if has_expected_tables:
            logger.info(f"数据库验证成功，包含 {len(actual_tables)} 个表")
            return True
        else:
            logger.warning(f"数据库验证失败，表数量不匹配")
            return False

    except Exception as e:
        logger.error(f"数据库验证失败: {str(e)}")
        return False


def main():
    """主函数"""
    logger.info("开始Chinook数据库初始化...")

    try:
        # 下载数据库
        db_path = download_chinook()

        # 验证数据库
        if verify_database(db_path):
            logger.info("Chinook数据库初始化成功！")
            logger.info(f"可以使用以下环境变量配置:")
            logger.info(f"  DATABASE_URL=sqlite:///{db_path}")
            return 0
        else:
            logger.error("Chinook数据库验证失败！")
            return 1

    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
