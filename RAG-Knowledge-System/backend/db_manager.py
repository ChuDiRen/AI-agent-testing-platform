"""
数据库管理工具

提供数据库初始化、迁移、备份等功能的统一入口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="企业级RAG知识库 - 数据库管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化数据库（创建表和默认数据）
  python db_manager.py init

  # 只创建表
  python db_manager.py init --create-tables-only

  # 只初始化数据
  python db_manager.py init --init-data-only

  # 重置数据库（危险操作）
  python db_manager.py init --reset

  # 检查数据库连接
  python db_manager.py check

  # 创建新的迁移
  python db_manager.py migrate -m "添加新字段"

  # 应用所有迁移
  python db_manager.py upgrade

  # 回滚迁移
  python db_manager.py downgrade

  # 查看当前迁移状态
  python db_manager.py status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 初始化命令
    init_parser = subparsers.add_parser("init", help="初始化数据库")
    init_parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有表并重新初始化）")
    init_parser.add_argument("--create-tables-only", action="store_true", help="只创建表，不初始化默认数据")
    init_parser.add_argument("--init-data-only", action="store_true", help="只初始化默认数据，不创建表")

    # 检查命令
    subparsers.add_parser("check", help="检查数据库连接")

    # 迁移命令
    migrate_parser = subparsers.add_parser("migrate", help="创建新的数据库迁移")
    migrate_parser.add_argument("-m", "--message", required=True, help="迁移描述信息")

    # 升级命令
    upgrade_parser = subparsers.add_parser("upgrade", help="应用数据库迁移")
    upgrade_parser.add_argument("revision", nargs="?", help="升级到指定版本，默认为最新版本")

    # 降级命令
    downgrade_parser = subparsers.add_parser("downgrade", help="回滚数据库迁移")
    downgrade_parser.add_argument("revision", nargs="?", default="-1", help="降级到指定版本，默认为前一个版本")

    # 状态命令
    subparsers.add_parser("status", help="查看当前迁移状态")

    # 备份命令
    backup_parser = subparsers.add_parser("backup", help="备份数据库")
    backup_parser.add_argument("-o", "--output", help="备份文件路径")

    # 恢复命令
    restore_parser = subparsers.add_parser("restore", help="恢复数据库")
    restore_parser.add_argument("backup_file", help="备份文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    if args.command == "init":
        handle_init(args)
    elif args.command == "check":
        handle_check()
    elif args.command == "migrate":
        handle_migrate(args)
    elif args.command == "upgrade":
        handle_upgrade(args)
    elif args.command == "downgrade":
        handle_downgrade(args)
    elif args.command == "status":
        handle_status()
    elif args.command == "backup":
        handle_backup(args)
    elif args.command == "restore":
        handle_restore(args)


def handle_init(args):
    """处理初始化命令"""
    from scripts.init_db import init_database, create_tables, init_default_data, check_database_connection
    from sqlmodel import Session, create_engine
    from config.settings import settings

    print("\n" + "=" * 60)
    print("数据库初始化工具")
    print("=" * 60)

    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

    if args.create_tables_only:
        print("\n[模式] 只创建表...")
        create_tables(engine)
    elif args.init_data_only:
        print("\n[模式] 只初始化数据...")
        with Session(engine) as session:
            init_default_data(session)
    elif args.reset:
        print("\n[模式] 重置数据库...")
        from scripts.init_db import reset_database
        with Session(engine) as session:
            reset_database(session)
    else:
        print("\n[模式] 完整初始化...")
        init_database(engine)


def handle_check():
    """处理检查命令"""
    from scripts.init_db import check_database_connection
    from sqlmodel import create_engine
    from config.settings import settings

    print("\n" + "=" * 60)
    print("数据库连接检查")
    print("=" * 60)
    print(f"\n数据库URL: {settings.DATABASE_URL}")

    engine = create_engine(settings.DATABASE_URL, echo=False)

    if check_database_connection(engine):
        print("\n✓ 数据库连接成功！")
    else:
        print("\n✗ 数据库连接失败！")
        print("\n请检查:")
        print("  1. 数据库服务是否启动")
        print("  2. DATABASE_URL 配置是否正确")
        print("  3. 数据库用户权限是否足够")
        sys.exit(1)


def handle_migrate(args):
    """处理迁移命令"""
    import subprocess

    print("\n" + "=" * 60)
    print("创建数据库迁移")
    print("=" * 60)

    cmd = [
        "alembic",
        "revision",
        "--autogenerate",
        "-m",
        args.message
    ]

    print(f"\n执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_root / "backend"))

    if result.returncode == 0:
        print("\n✓ 迁移文件创建成功！")
    else:
        print("\n✗ 迁移文件创建失败！")
        sys.exit(1)


def handle_upgrade(args):
    """处理升级命令"""
    import subprocess

    print("\n" + "=" * 60)
    print("应用数据库迁移")
    print("=" * 60)

    cmd = ["alembic", "upgrade", "head"]
    if args.revision:
        cmd = ["alembic", "upgrade", args.revision]

    print(f"\n执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_root / "backend"))

    if result.returncode == 0:
        print("\n✓ 数据库迁移成功！")
    else:
        print("\n✗ 数据库迁移失败！")
        sys.exit(1)


def handle_downgrade(args):
    """处理降级命令"""
    import subprocess

    print("\n" + "=" * 60)
    print("回滚数据库迁移")
    print("=" * 60)

    cmd = ["alembic", "downgrade", args.revision]

    print(f"\n执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_root / "backend"))

    if result.returncode == 0:
        print("\n✓ 数据库回滚成功！")
    else:
        print("\n✗ 数据库回滚失败！")
        sys.exit(1)


def handle_status():
    """处理状态命令"""
    import subprocess

    print("\n" + "=" * 60)
    print("数据库迁移状态")
    print("=" * 60)

    cmd = ["alembic", "current"]
    result = subprocess.run(cmd, cwd=str(project_root / "backend"), capture_output=True, text=True)

    print(f"\n当前版本: {result.stdout.strip()}")

    cmd = ["alembic", "history"]
    result = subprocess.run(cmd, cwd=str(project_root / "backend"), capture_output=True, text=True)

    print("\n迁移历史:")
    print(result.stdout)


def handle_backup(args):
    """处理备份命令"""
    import shutil
    from datetime import datetime
    from config.settings import settings

    print("\n" + "=" * 60)
    print("备份数据库")
    print("=" * 60)

    # 解析数据库连接信息
    db_url = settings.DATABASE_URL
    # 这里简化处理，实际应该使用 mysqldump 命令
    # 示例: mysqldump -u root -p database_name > backup.sql

    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"backup_{timestamp}.sql"

    print(f"\n备份数据库到: {output_path}")
    print("\n注意: 需要安装 MySQL 客户端工具（mysqldump）")
    print("执行命令示例:")
    print(f"  mysqldump -h localhost -u root -p enterprise_rag_kb > {output_path}")


def handle_restore(args):
    """处理恢复命令"""
    print("\n" + "=" * 60)
    print("恢复数据库")
    print("=" * 60)

    print(f"\n从备份文件恢复: {args.backup_file}")
    print("\n注意: 恢复操作会覆盖当前数据库数据！")
    print("执行命令示例:")
    print(f"  mysql -h localhost -u root -p enterprise_rag_kb < {args.backup_file}")

    confirm = input("\n确认要恢复数据库吗？此操作不可逆！(yes/no): ")
    if confirm.lower() != "yes":
        print("取消恢复操作")
        return


if __name__ == "__main__":
    main()
