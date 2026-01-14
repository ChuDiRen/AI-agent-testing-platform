"""
数据库初始化设置 - 纯异步实现
"""
import asyncio
import aiosqlite
import aiofiles
import aiohttp
from pathlib import Path
from typing import Optional


CHINOOK_DB_URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"


async def download_file_async(url: str, dest_path: Path) -> None:
    """异步下载文件"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            async with aiofiles.open(dest_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)


async def verify_database(db_path: Path) -> bool:
    """验证数据库是否有效"""
    if not db_path.exists():
        return False

    try:
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = await cursor.fetchall()
            return len(tables) > 0
    except Exception:
        return False


async def setup_chinook(db_path: Optional[Path] = None) -> Path:
    """自动下载并设置 Chinook 测试数据库 - 纯异步

    Args:
        db_path: 数据库路径，默认为 agent-backend/data/Chinook.db

    Returns:
        数据库文件路径
    """
    if db_path is None:
        # 使用相对路径
        db_path = Path(__file__).parent.parent.parent / "data" / "Chinook.db"

    # 检查是否已存在有效数据库
    if await verify_database(db_path):
        return db_path

    # 确保目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 下载数据库
    print(f"[Chinook] 正在下载数据库...")
    try:
        await download_file_async(CHINOOK_DB_URL, db_path)
        print(f"[Chinook] 下载完成: {db_path}")
        return db_path
    except Exception as e:
        raise RuntimeError(f"下载失败: {e}\n手动下载: {CHINOOK_DB_URL}")

