#!/usr/bin/env python
"""
数据库初始化CLI工具
支持初始化、重置、备份、恢复等操作
"""
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlmodel import SQLModel, create_engine, Session
from config.dev_settings import settings
from core.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.db_type = settings.DB_TYPE
        self.database_url = settings.SQLALCHEMY_DATABASE_URI
        
    def connect(self):
        """连接数据库"""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            logger.info(f"✅ 已连接到 {self.db_type.upper()} 数据库")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def init_tables(self):
        """初始化数据库表"""
        print("\n" + "=" * 80)
        print("初始化数据库表")
        print("=" * 80)
        
        try:
            # 导入所有模型
            self._import_all_models()
            
            # 创建所有表
            print("正在创建数据库表...")
            SQLModel.metadata.create_all(self.engine)
            
            # 统计表数量
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            print(f"✅ 成功创建 {len(tables)} 张表:")
            for table in sorted(tables):
                print(f"   - {table}")
            
            return True
        except Exception as e:
            logger.error(f"❌ 创建表失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def init_data(self):
        """初始化基础数据"""
        print("\n" + "=" * 80)
        print("初始化基础数据")
        print("=" * 80)
        
        try:
            from core.init_data import init_all_data
            init_all_data()
            print("✅ 基础数据初始化完成")
            return True
        except Exception as e:
            logger.error(f"❌ 数据初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def drop_all_tables(self):
        """删除所有表"""
        print("\n" + "=" * 80)
        print("⚠️  删除所有数据库表")
        print("=" * 80)
        
        try:
            # 导入所有模型
            self._import_all_models()
            
            # 删除所有表
            print("正在删除数据库表...")
            SQLModel.metadata.drop_all(self.engine)
            
            print("✅ 所有表已删除")
            return True
        except Exception as e:
            logger.error(f"❌ 删除表失败: {e}")
            return False
    
    def backup_database(self, backup_path: str = None):
        """备份数据库"""
        print("\n" + "=" * 80)
        print("备份数据库")
        print("=" * 80)
        
        if self.db_type != "sqlite":
            print("⚠️  当前仅支持SQLite数据库备份")
            print("   MySQL备份请使用 mysqldump 命令")
            return False
        
        try:
            # 生成备份文件名
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir = BASE_DIR / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"database_backup_{timestamp}.db"
            
            # 复制数据库文件
            db_file = Path(settings.SQLITE_DATABASE)
            if not db_file.exists():
                print(f"❌ 数据库文件不存在: {db_file}")
                return False
            
            shutil.copy2(db_file, backup_path)
            print(f"✅ 数据库已备份到: {backup_path}")
            print(f"   文件大小: {Path(backup_path).stat().st_size / 1024:.2f} KB")
            return True
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            return False
    
    def restore_database(self, backup_path: str):
        """恢复数据库"""
        print("\n" + "=" * 80)
        print("恢复数据库")
        print("=" * 80)
        
        if self.db_type != "sqlite":
            print("⚠️  当前仅支持SQLite数据库恢复")
            return False
        
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                print(f"❌ 备份文件不存在: {backup_file}")
                return False
            
            # 恢复数据库文件
            db_file = Path(settings.SQLITE_DATABASE)
            shutil.copy2(backup_file, db_file)
            
            print(f"✅ 数据库已从备份恢复: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 恢复失败: {e}")
            return False
    
    def show_info(self):
        """显示数据库信息"""
        print("\n" + "=" * 80)
        print("数据库信息")
        print("=" * 80)
        
        try:
            print(f"数据库类型: {self.db_type.upper()}")
            print(f"连接URL: {self.database_url}")
            
            if self.db_type == "sqlite":
                db_file = Path(settings.SQLITE_DATABASE)
                if db_file.exists():
                    size = db_file.stat().st_size / 1024
                    print(f"数据库文件: {db_file}")
                    print(f"文件大小: {size:.2f} KB")
                else:
                    print(f"数据库文件: {db_file} (不存在)")
            
            # 获取表信息
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            print(f"\n数据库表数量: {len(tables)}")
            if tables:
                print("\n表列表:")
                for table in sorted(tables):
                    # 获取表的行数
                    try:
                        with Session(self.engine) as session:
                            result = session.execute(f"SELECT COUNT(*) FROM {table}")
                            count = result.scalar()
                            print(f"   - {table:40s} ({count} 行)")
                    except:
                        print(f"   - {table}")
            
            return True
        except Exception as e:
            logger.error(f"❌ 获取信息失败: {e}")
            return False
    
    def _import_all_models(self):
        """导入所有模型"""
        # 系统管理模块
        from sysmanage.model.user import User
        from sysmanage.model.role import Role
        from sysmanage.model.menu import Menu
        from sysmanage.model.dept import Dept
        
        # API测试模块
        from apitest.model.ApiProjectModel import ApiProject
        from apitest.model.ApiDbBaseModel import ApiDbBase
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        from apitest.model.ApiOperationTypeModel import OperationType
        from apitest.model.ApiMetaModel import ApiMeta
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        from apitest.model.ApiHistoryModel import ApiHistory
        from apitest.model.ApiInfoGroupModel import ApiInfoGroup
        
        # 消息管理模块
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        # AI助手模块
        from aiassistant.model.AiModel import AiModel
        from aiassistant.model.TestCaseModel import TestCase
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiMessage import AiMessage
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        # 插件模块
        from plugin.model.PluginModel import Plugin


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI Agent Testing Platform - 数据库初始化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化数据库(创建表+初始数据)
  python scripts/init_database.py init
  
  # 仅创建表结构
  python scripts/init_database.py create-tables
  
  # 仅初始化数据
  python scripts/init_database.py init-data
  
  # 重置数据库(删除所有表并重新初始化)
  python scripts/init_database.py reset
  
  # 备份数据库
  python scripts/init_database.py backup
  
  # 恢复数据库
  python scripts/init_database.py restore backups/database_backup_20251122_154500.db
  
  # 查看数据库信息
  python scripts/init_database.py info
        """
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'create-tables', 'init-data', 'reset', 'backup', 'restore', 'info'],
        help='要执行的命令'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='命令参数(如restore命令的备份文件路径)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制执行,跳过确认提示'
    )
    
    args = parser.parse_args()
    
    # 创建数据库管理器
    db_manager = DatabaseManager()
    
    print("\n" + "=" * 80)
    print("AI Agent Testing Platform - 数据库初始化工具")
    print("=" * 80)
    print(f"数据库类型: {db_manager.db_type.upper()}")
    print(f"连接URL: {db_manager.database_url}")
    
    # 连接数据库
    if not db_manager.connect():
        return 1
    
    # 执行命令
    success = False
    
    if args.command == 'init':
        # 完整初始化
        if not args.force:
            confirm = input("\n⚠️  将初始化数据库(创建表+初始数据),继续吗? [y/N]: ")
            if confirm.lower() != 'y':
                print("❌ 操作已取消")
                return 0
        
        success = db_manager.init_tables() and db_manager.init_data()
    
    elif args.command == 'create-tables':
        # 仅创建表
        success = db_manager.init_tables()
    
    elif args.command == 'init-data':
        # 仅初始化数据
        success = db_manager.init_data()
    
    elif args.command == 'reset':
        # 重置数据库
        if not args.force:
            confirm = input("\n⚠️  将删除所有表并重新初始化,所有数据将丢失!继续吗? [y/N]: ")
            if confirm.lower() != 'y':
                print("❌ 操作已取消")
                return 0
        
        success = (
            db_manager.drop_all_tables() and
            db_manager.init_tables() and
            db_manager.init_data()
        )
    
    elif args.command == 'backup':
        # 备份数据库
        backup_path = args.args[0] if args.args else None
        success = db_manager.backup_database(backup_path)
    
    elif args.command == 'restore':
        # 恢复数据库
        if not args.args:
            print("❌ 请指定备份文件路径")
            return 1
        
        if not args.force:
            confirm = input(f"\n⚠️  将从备份恢复数据库,当前数据将被覆盖!继续吗? [y/N]: ")
            if confirm.lower() != 'y':
                print("❌ 操作已取消")
                return 0
        
        success = db_manager.restore_database(args.args[0])
    
    elif args.command == 'info':
        # 显示信息
        success = db_manager.show_info()
    
    # 输出结果
    print("\n" + "=" * 80)
    if success:
        print("✅ 操作完成!")
    else:
        print("❌ 操作失败,请检查日志")
    print("=" * 80 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
