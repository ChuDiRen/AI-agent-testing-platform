# -*- coding: utf-8 -*-
"""数据库初始化数据脚本"""

from sqlmodel import Session, select
from core.database import engine
from sysmanage.model.user import User
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_exists() -> bool:
    """检查数据库中是否已有数据"""
    try:
        with Session(engine) as session:
            # 检查用户表是否有数据
            statement = select(User)
            users = session.exec(statement).all()
            return len(users) > 0
    except Exception as e:
        logger.error(f"检查数据失败: {e}")
        return False

def create_initial_users():
    """创建初始用户数据"""
    try:
        with Session(engine) as session:
            # 定义初始用户数据 - 仅保留管理员账号
            initial_users = [
                {
                    "id": 1,
                    "username": "admin",
                    "password": "admin123",
                    "create_time": datetime.now()
                }
            ]

            # 检查每个用户是否已存在，不存在则创建
            for user_data in initial_users:
                statement = select(User).where(User.username == user_data["username"])
                existing_user = session.exec(statement).first()

                if not existing_user:
                    user = User(**user_data)
                    session.add(user)
                    logger.info(f"创建用户: {user_data['username']}")
                else:
                    logger.info(f"用户已存在: {user_data['username']}")

            session.commit()
            logger.info("初始用户数据创建完成")

    except Exception as e:
        logger.error(f"创建初始用户失败: {e}")
        raise

def init_all_data():
    """初始化所有数据"""
    try:
        logger.info("开始初始化数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过初始化")
            return
        
        # 创建初始用户
        create_initial_users()
        
        logger.info("数据初始化完成！")
        logger.info("=" * 50)
        logger.info("可用的登录账号:")
        logger.info("admin / admin123 (管理员)")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_all_data()
