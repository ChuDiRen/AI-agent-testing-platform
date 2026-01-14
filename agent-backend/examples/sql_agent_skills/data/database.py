"""
数据库管理模块
负责Chinook数据库的下载、创建和连接（纯异步实现）
"""

import aiosqlite
import aiohttp
from pathlib import Path

CHINOOK_DB_URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

class DatabaseManager:
    """Chinook数据库管理器（纯异步实现）"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def setup_database(self) -> None:
        """自动下载并设置Chinook数据库（纯异步）"""
        db_url = CHINOOK_DB_URL

        # 检查现有数据库（异步方式）
        if await self._verify_database():
            print(f"[Chinook] 数据库已存在: {self.db_path}")
            return

        # 下载数据库（纯异步）
        try:
            print(f"[Chinook] 正在下载数据库到: {self.db_path}")
            await self._download_database(db_url)

            # 验证下载
            if not await self._verify_database():
                raise SystemExit(f"数据库下载失败，请手动下载: {db_url}")
            print(f"[Chinook] 下载完成: {self.db_path}")
        except Exception as e:
            raise SystemExit(f"数据库下载失败: {e}\n手动下载: {db_url}")

    async def _verify_database(self) -> bool:
        """验证数据库是否有效（异步）"""
        if not self.db_path.exists():
            return False
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = await cursor.fetchall()
                return len(tables) > 0
        except Exception:
            return False

    async def _download_database(self, url: str) -> None:
        """异步下载数据库"""
        import aiofiles
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                async with aiofiles.open(self.db_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)

    async def get_connection(self):
        """获取数据库连接（异步）"""
        return await aiosqlite.connect(self.db_path)
