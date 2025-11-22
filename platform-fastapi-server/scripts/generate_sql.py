"""
生成数据库初始化SQL脚本
从SQLModel模型自动生成CREATE TABLE语句
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlmodel import SQLModel, create_engine
from datetime import datetime


def generate_sqlite_sql():
    """生成SQLite的SQL语句"""
    print("=" * 80)
    print("生成 SQLite 初始化脚本")
    print("=" * 80)
    
    # 导入所有模型
    from sysmanage.model.user import User
    from sysmanage.model.role import Role
    from sysmanage.model.menu import Menu
    from sysmanage.model.dept import Dept
    
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
    
    from msgmanage.model.RobotConfigModel import RobotConfig
    from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
    
    from aiassistant.model.AiModel import AiModel
    from aiassistant.model.TestCaseModel import TestCase
    from aiassistant.model.AiConversation import AiConversation
    from aiassistant.model.AiMessage import AiMessage
    from aiassistant.model.PromptTemplate import PromptTemplate
    
    # 创建临时SQLite引擎
    engine = create_engine("sqlite:///temp.db", echo=False)
    
    # 生成所有表
    SQLModel.metadata.create_all(engine)
    
    # 获取SQL语句
    from sqlalchemy.schema import CreateTable
    
    sql_statements = []
    sql_statements.append("-- ============================================")
    sql_statements.append("-- AI Agent Testing Platform - SQLite Schema")
    sql_statements.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_statements.append("-- ============================================\n")
    
    # 按模块分组
    modules = {
        "系统管理模块": [User, Role, Menu, Dept],
        "API测试模块": [
            ApiProject, ApiDbBase, ApiKeyWord, OperationType,
            ApiMeta, ApiInfo, ApiInfoGroup, ApiInfoCase, ApiInfoCaseStep,
            ApiCollectionInfo, ApiCollectionDetail, ApiHistory
        ],
        "消息管理模块": [RobotConfig, RobotMsgConfig],
        "AI助手模块": [AiModel, AiConversation, AiMessage, PromptTemplate, TestCase]
    }
    
    for module_name, models in modules.items():
        sql_statements.append(f"\n-- {module_name}")
        sql_statements.append("-" * 80 + "\n")
        
        for model in models:
            table = model.__table__
            create_stmt = str(CreateTable(table).compile(engine))
            sql_statements.append(f"-- 表: {table.name}")
            sql_statements.append(create_stmt + ";\n")
    
    # 写入文件
    output_file = BASE_DIR / "scripts" / "migrations" / "001_init_sqlite.sql"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ SQLite脚本已生成: {output_file}")
    print(f"   包含 {len(modules)} 个模块, {sum(len(m) for m in modules.values())} 张表")
    
    # 清理临时数据库
    import os
    try:
        if os.path.exists("temp.db"):
            os.remove("temp.db")
    except:
        pass  # 忽略删除失败
    
    return output_file


def generate_mysql_sql():
    """生成MySQL的SQL语句"""
    print("\n" + "=" * 80)
    print("生成 MySQL 初始化脚本")
    print("=" * 80)
    
    # 导入所有模型
    from sysmanage.model.user import User
    from sysmanage.model.role import Role
    from sysmanage.model.menu import Menu
    from sysmanage.model.dept import Dept
    
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
    
    from msgmanage.model.RobotConfigModel import RobotConfig
    from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
    
    from aiassistant.model.AiModel import AiModel
    from aiassistant.model.TestCaseModel import TestCase
    from aiassistant.model.AiConversation import AiConversation
    from aiassistant.model.AiMessage import AiMessage
    from aiassistant.model.PromptTemplate import PromptTemplate
    
    # 创建临时MySQL引擎
    engine = create_engine(
        "mysql+pymysql://root:root@localhost:3306/temp_db?charset=utf8mb4",
        echo=False
    )
    
    # 生成所有表
    try:
        SQLModel.metadata.create_all(engine)
    except:
        # 如果MySQL不可用,使用SQLite引擎生成然后转换
        engine = create_engine("sqlite:///temp.db", echo=False)
        SQLModel.metadata.create_all(engine)
    
    # 获取SQL语句
    from sqlalchemy.schema import CreateTable
    
    sql_statements = []
    sql_statements.append("-- ============================================")
    sql_statements.append("-- AI Agent Testing Platform - MySQL Schema")
    sql_statements.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_statements.append("-- ============================================\n")
    
    sql_statements.append("-- 设置字符集")
    sql_statements.append("SET NAMES utf8mb4;")
    sql_statements.append("SET FOREIGN_KEY_CHECKS = 0;\n")
    
    # 按模块分组
    modules = {
        "系统管理模块": [User, Role, Menu, Dept],
        "API测试模块": [
            ApiProject, ApiDbBase, ApiKeyWord, OperationType,
            ApiMeta, ApiInfo, ApiInfoGroup, ApiInfoCase, ApiInfoCaseStep,
            ApiCollectionInfo, ApiCollectionDetail, ApiHistory
        ],
        "消息管理模块": [RobotConfig, RobotMsgConfig],
        "AI助手模块": [AiModel, AiConversation, AiMessage, PromptTemplate, TestCase]
    }
    
    for module_name, models in modules.items():
        sql_statements.append(f"\n-- {module_name}")
        sql_statements.append("-" * 80 + "\n")
        
        for model in models:
            table = model.__table__
            create_stmt = str(CreateTable(table).compile(engine))
            
            # MySQL特定优化
            create_stmt = create_stmt.replace("DATETIME", "DATETIME DEFAULT CURRENT_TIMESTAMP")
            create_stmt = create_stmt.replace("INTEGER", "INT")
            
            sql_statements.append(f"-- 表: {table.name}")
            sql_statements.append(f"DROP TABLE IF EXISTS `{table.name}`;")
            sql_statements.append(create_stmt + " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n")
    
    sql_statements.append("\nSET FOREIGN_KEY_CHECKS = 1;")
    
    # 写入文件
    output_file = BASE_DIR / "scripts" / "migrations" / "001_init_mysql.sql"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ MySQL脚本已生成: {output_file}")
    print(f"   包含 {len(modules)} 个模块, {sum(len(m) for m in modules.values())} 张表")
    
    # 清理临时数据库
    import os
    try:
        if os.path.exists("temp.db"):
            os.remove("temp.db")
    except:
        pass  # 忽略删除失败
    
    return output_file


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("数据库SQL脚本生成器")
    print("=" * 80)
    
    try:
        # 生成SQLite脚本
        sqlite_file = generate_sqlite_sql()
        
        # 生成MySQL脚本
        mysql_file = generate_mysql_sql()
        
        print("\n" + "=" * 80)
        print("✅ 所有SQL脚本生成完成!")
        print("=" * 80)
        print(f"SQLite: {sqlite_file}")
        print(f"MySQL:  {mysql_file}")
        print("\n提示: 可以使用这些脚本手动初始化数据库")
        
        return 0
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
