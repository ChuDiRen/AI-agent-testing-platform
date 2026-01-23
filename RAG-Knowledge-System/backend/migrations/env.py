"""
Alembic 环境配置文件

用于配置数据库迁移的环境和上下文
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入 SQLModel 的 metadata
from sqlmodel import SQLModel

# 导入所有模型以确保它们被注册到 metadata 中
from app.models import user, role, permission, department, document
from app.models import document_chunk, vector_store, feedback, operation_log
from app.models import system_config, chat_history

# 导入配置
import config.settings as settings_module

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 从 settings 获取数据库 URL
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings_module.settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """在"离线"模式下运行迁移。

    这配置上下文，只需一个 URL 而不是 Engine，
    虽然在这里也接受 Engine 和 Engine之外的连接构造函数。
    通过跳过 Engine 创建，我们甚至不需要 DBAPI 可用。

    对生成脚本和"离线"运行迁移很有用。

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 比较列类型
        compare_server_default=True,  # 比较默认值
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在"在线"模式下运行迁移。

    在这种情况下，我们需要创建一个 Engine
    并将连接与该上下文关联。

    """
    # 创建引擎配置
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 比较列类型
            compare_server_default=True,  # 比较默认值
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
