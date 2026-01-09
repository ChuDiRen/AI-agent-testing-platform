# -*- coding: utf-8 -*-
"""
数据库初始化数据脚本

注意：菜单数据由 ViewScanService 自动从前端视图扫描生成，
本文件只负责初始化基础数据（部门、角色、用户）
"""

import logging
from datetime import datetime

from sqlmodel import Session, select
from app.models.DeptModel import Dept
from app.models.RoleModel import Role
from app.models.UserModel import User
from app.models.UserRoleModel import UserRole

from .database import engine

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

def create_initial_depts():
    """创建初始部门数据"""
    try:
        with Session(engine) as session:
            initial_depts = [
                {"dept_id": 1, "parent_id": 0, "dept_name": "总公司", "order_num": 1},
                {"dept_id": 2, "parent_id": 1, "dept_name": "技术部", "order_num": 1},
                {"dept_id": 3, "parent_id": 1, "dept_name": "产品部", "order_num": 2},
                {"dept_id": 4, "parent_id": 1, "dept_name": "运营部", "order_num": 3},
            ]

            for dept_data in initial_depts:
                existing = session.get(Dept, dept_data["dept_id"])
                if not existing:
                    dept = Dept(**dept_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(dept)
                    logger.info(f"创建部门: {dept_data['dept_name']}")

            session.commit()
            logger.info("初始部门数据创建完成")
    except Exception as e:
        logger.error(f"创建初始部门失败: {e}")
        raise

def create_initial_users():
    """创建初始用户数据"""
    try:
        with Session(engine) as session:
            initial_users = [
                {
                    "id": 1,
                    "username": "admin",
                    "password": "admin123",
                    "dept_id": 2, # 技术部
                    "email": "admin@example.com",
                    "mobile": "13800138000",
                    "status": "1",
                    "ssex": "0",
                    "avatar": "https://avatars.githubusercontent.com/u/1?v=4",
                    "description": "超级管理员",
                    "create_time": datetime.now(),
                    "modify_time": datetime.now()
                }
            ]

            for user_data in initial_users:
                statement = select(User).where(User.username == user_data["username"])
                existing_user = session.exec(statement).first()

                if not existing_user:
                    user = User(**user_data)
                    session.add(user)
                    logger.info(f"创建用户: {user_data['username']}")

            session.commit()
            logger.info("初始用户数据创建完成")
    except Exception as e:
        logger.error(f"创建初始用户失败: {e}")
        raise

def create_initial_roles():
    """创建初始角色数据"""
    try:
        with Session(engine) as session:
            initial_roles = [
                {"id": 1, "role_name": "超级管理员", "role_key": "admin", "role_sort": 1, "data_scope": "1", "status": "1", "del_flag": "0", "create_by": "admin", "create_time": datetime.now(), "update_by": "admin", "update_time": datetime.now(), "remark": "超级管理员"},
            ]

            for role_data in initial_roles:
                existing = session.get(Role, role_data["id"])
                if not existing:
                    role = Role(**role_data)
                    session.add(role)
                    logger.info(f"创建角色: {role_data['role_name']}")

            session.commit()
            logger.info("初始角色数据创建完成")
    except Exception as e:
        logger.error(f"创建初始角色失败: {e}")
        raise

def create_initial_user_roles():
    """创建初始用户角色关系"""
    try:
        with Session(engine) as session:
            initial_user_roles = [
                {"user_id": 1, "role_id": 1},  # admin用户分配超级管理员角色
            ]

            for user_role_data in initial_user_roles:
                statement = select(UserRole).where(
                    UserRole.user_id == user_role_data["user_id"],
                    UserRole.role_id == user_role_data["role_id"]
                )
                existing = session.exec(statement).first()

                if not existing:
                    user_role = UserRole(**user_role_data)
                    session.add(user_role)
                    logger.info(f"创建用户角色关系: 用户{user_role_data['user_id']} -> 角色{user_role_data['role_id']}")

            session.commit()
            logger.info("初始用户角色关系创建完成")
    except Exception as e:
        logger.error(f"创建初始用户角色关系失败: {e}")
        raise

def init_data():
    """
    初始化所有数据
    
    注意：菜单数据由 sync_frontend_views() 在 database.py 中自动生成，
    这里只初始化基础数据（部门、角色、用户）
    """
    try:
        logger.info("开始初始化数据库数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过初始化")
            return
        
        # 按顺序创建基础数据（菜单由 ViewScanService 自动生成）
        create_initial_depts()
        create_initial_roles()
        create_initial_users()
        create_initial_user_roles()
        
        logger.info("数据库基础数据初始化完成！")
    except Exception as e:
        logger.error(f"数据库数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_data()
