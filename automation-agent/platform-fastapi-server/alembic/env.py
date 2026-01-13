"""
Alembic 环境配置
"""
from logging.config import fileConfig
from logging import getLogger

fileConfig('alembic.ini')

logger = getLogger('alembic')

# 用于 Alembic 的数据库 URL（同步版本，因为 Alembic 需要）
# 注意：FastAPI 使用异步驱动，但 Alembic 生成迁移时使用同步连接
from app.core.config import settings

# 将异步 URL 转换为同步 URL（用于迁移生成）
SYNC_DATABASE_URL = settings.DATABASE_URL.replace('aiomysql', 'pymysql')

# 元数据命名约定
target_metadata = None
naming_convention = None
version_table_schema = None
version_path_schema = None
