"""
数据库初始化脚本

创建所有数据库表并插入初始数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

# 修复导入路径
try:
    from app.core.logger import setup_logger
    from app.core.security import get_password_hash
    # 从 config.settings 导入，需要添加 config 到路径
    config_path = Path(__file__).parent.parent / "config"
    sys.path.insert(0, str(config_path))
    from settings import settings
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的目录下运行此脚本")
    sys.exit(1)

# 导入所有模型（避免循环导入）
try:
    from app.models import user
    from app.models import role
    from app.models import permission
    from app.models import department
    from app.models import document
    from app.models import document_chunk
    from app.models import vector_store
    from app.models import feedback
    from app.models import operation_log
    from app.models import system_config
    from app.models import chat_history
except ImportError as e:
    print(f"模型导入错误: {e}")
    sys.exit(1)

logger = setup_logger(__name__)


def create_tables(engine):
    """创建所有数据库表"""
    logger.info("开始创建数据库表...")

    try:
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建完成")
        return True
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        return False


def init_default_data(session: Session):
    """初始化默认数据"""
    logger.info("开始初始化默认数据...")

    try:
        # 1. 创建默认角色
        init_roles(session)

        # 2. 创建默认部门
        init_departments(session)

        # 3. 创建管理员用户
        init_admin_user(session)

        # 4. 创建系统配置
        init_system_config(session)

        session.commit()
        logger.info("默认数据初始化完成")
        return True
    except Exception as e:
        logger.error(f"初始化默认数据失败: {str(e)}")
        session.rollback()
        return False


def init_roles(session: Session):
    """初始化角色"""
    logger.info("初始化角色...")

    # 检查是否已有角色
    existing = session.exec(select(role.Role)).first()
    if existing:
        logger.info("角色已存在，跳过初始化")
        return

    # 创建角色
    roles_data = [
        {
            "name": "系统管理员",
            "code": "superadmin",
            "description": "拥有系统所有权限，可以管理所有数据和配置",
            "status": 1,
            "sort": 1,
            "is_system": True
        },
        {
            "name": "部门管理员",
            "code": "dept_admin",
            "description": "可以管理本部门的用户和文档",
            "status": 1,
            "sort": 2,
            "is_system": False
        },
        {
            "name": "普通用户",
            "code": "user",
            "description": "可以上传文档、向知识库提问",
            "status": 1,
            "sort": 3,
            "is_system": False
        }
    ]

    for role_data in roles_data:
        db_role = role.Role(**role_data)
        session.add(db_role)

    logger.info(f"创建了 {len(roles_data)} 个角色")


def init_departments(session: Session):
    """初始化部门"""
    logger.info("初始化部门...")

    # 检查是否已有部门
    existing = session.exec(select(department.Department)).first()
    if existing:
        logger.info("部门已存在，跳过初始化")
        return

    # 创建默认部门
    depts_data = [
        {
            "name": "默认部门",
            "code": "default",
            "description": "系统默认部门",
            "parent_id": None,
            "status": 1,
            "sort": 1
        },
        {
            "name": "技术部",
            "code": "tech",
            "description": "技术研发部门",
            "parent_id": None,
            "status": 1,
            "sort": 2
        },
        {
            "name": "产品部",
            "code": "product",
            "description": "产品部门",
            "parent_id": None,
            "status": 1,
            "sort": 3
        },
        {
            "name": "市场部",
            "code": "marketing",
            "description": "市场营销部门",
            "parent_id": None,
            "status": 1,
            "sort": 4
        },
        {
            "name": "人力资源部",
            "code": "hr",
            "description": "人力资源部门",
            "parent_id": None,
            "status": 1,
            "sort": 5
        }
    ]

    for dept_data in depts_data:
        db_dept = department.Department(**dept_data)
        session.add(db_dept)

    logger.info(f"创建了 {len(depts_data)} 个部门")


def init_admin_user(session: Session):
    """初始化管理员用户"""
    logger.info("初始化管理员用户...")

    # 检查是否已有用户
    existing = session.exec(select(user.User)).first()
    if existing:
        logger.info("用户已存在，跳过管理员初始化")
        return

    # 获取系统管理员角色
    admin_role = session.exec(
        select(role.Role).where(role.Role.code == "superadmin")
    ).first()

    # 获取默认部门
    default_dept = session.exec(
        select(department.Department).where(department.Department.code == "default")
    ).first()

    # 创建管理员用户
    admin_data = {
        "username": "admin",
        "password_hash": get_password_hash("admin123"),  # 默认密码
        "email": "admin@enterprise.com",
        "full_name": "系统管理员",
        "role_id": admin_role.id if admin_role else None,
        "dept_id": default_dept.id if default_dept else None,
        "is_active": True,
        "is_superuser": True,
        "status": 1
    }

    admin_user = user.User(**admin_data)
    session.add(admin_user)

    logger.info("创建了管理员用户 (username: admin, password: admin123)")


def init_system_config(session: Session):
    """初始化系统配置"""
    logger.info("初始化系统配置...")

    # 检查是否已有配置
    existing = session.exec(select(system_config.SystemConfig)).first()
    if existing:
        logger.info("系统配置已存在，跳过初始化")
        return

    # 创建默认配置
    configs_data = [
        {
            "key": "embedding_provider",
            "value": "local",
            "description": "嵌入模型提供者",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "embedding_model",
            "value": "BAAI/bge-large-zh-v1.5",
            "description": "嵌入模型名称",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "chunk_size",
            "value": "512",
            "description": "文本块大小",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "chunk_overlap",
            "value": "64",
            "description": "文本块重叠大小",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "top_k",
            "value": "5",
            "description": "检索结果数量",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "similarity_threshold",
            "value": "0.7",
            "description": "相似度阈值",
            "category": "rag",
            "is_public": True,
            "status": 1
        },
        {
            "key": "llm_provider",
            "value": "openai",
            "description": "LLM提供者",
            "category": "llm",
            "is_public": True,
            "status": 1
        },
        {
            "key": "llm_model",
            "value": "gpt-4",
            "description": "LLM模型名称",
            "category": "llm",
            "is_public": True,
            "status": 1
        },
        {
            "key": "llm_temperature",
            "value": "0.7",
            "description": "LLM温度参数",
            "category": "llm",
            "is_public": True,
            "status": 1
        },
        {
            "key": "llm_max_tokens",
            "value": "2000",
            "description": "LLM最大token数",
            "category": "llm",
            "is_public": True,
            "status": 1
        },
        {
            "key": "max_file_size",
            "value": "52428800",
            "description": "最大文件大小（50MB）",
            "category": "system",
            "is_public": True,
            "status": 1
        }
    ]

    for config_data in configs_data:
        db_config = system_config.SystemConfig(**config_data)
        session.add(db_config)

    logger.info(f"创建了 {len(configs_data)} 个系统配置项")


def reset_database(session: Session):
    """重置数据库（危险操作）"""
    logger.warning("警告：即将删除所有数据库表！")

    confirm = input("确认要删除所有数据库表吗？此操作不可逆！(yes/no): ")
    if confirm.lower() != "yes":
        logger.info("取消重置数据库操作")
        return

    # 删除所有表
    SQLModel.metadata.drop_all(engine)

    # 重新创建
    create_tables(engine)

    # 初始化默认数据
    init_default_data(session)

    session.commit()

    logger.info("数据库重置完成")


def check_database_connection(engine):
    """检查数据库连接"""
    try:
        with Session(engine) as session:
            session.execute(select(1))
        logger.info("数据库连接成功")
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return False


def init_database(engine):
    """初始化数据库"""
    logger.info("=" * 50)
    logger.info("开始初始化数据库...")
    logger.info("=" * 50)
    logger.info(f"数据库URL: {settings.DATABASE_URL}")

    # 检查数据库连接
    if not check_database_connection(engine):
        logger.error("数据库连接失败，请检查配置")
        return False

    # 创建表
    if not create_tables(engine):
        return False

    # 创建会话
    with Session(engine) as session:
        # 初始化默认数据
        if not init_default_data(session):
            return False

    logger.info("=" * 50)
    logger.info("数据库初始化完成！")
    logger.info("=" * 50)
    logger.info("管理员账号:")
    logger.info("  用户名: admin")
    logger.info("  密码: admin123")
    logger.info("请及时修改默认密码！")
    logger.info("=" * 50)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有表并重新初始化）")
    parser.add_argument("--create-tables-only", action="store_true", help="只创建表，不初始化默认数据")
    parser.add_argument("--init-data-only", action="store_true", help="只初始化默认数据，不创建表")
    parser.add_argument("--check", action="store_true", help="只检查数据库连接")

    args = parser.parse_args()

    # 创建数据库引擎
    try:
        engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    except Exception as e:
        print(f"创建数据库引擎失败: {str(e)}")
        print("请检查 DATABASE_URL 配置")
        sys.exit(1)

    if args.check:
        # 只检查连接
        check_database_connection(engine)
    elif args.create_tables_only:
        # 只创建表
        create_tables(engine)
    elif args.init_data_only:
        # 只初始化数据
        with Session(engine) as session:
            init_default_data(session)
    elif args.reset:
        # 重置数据库
        with Session(engine) as session:
            reset_database(session)
    else:
        # 完整初始化
        init_database(engine)
