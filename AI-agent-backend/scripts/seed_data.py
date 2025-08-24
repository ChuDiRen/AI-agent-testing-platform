# Copyright (c) 2025 左岚. All rights reserved.
"""
种子数据脚本
用于创建演示和测试数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.core.security import get_password_hash
from app.entity.user import User
from app.entity.role import Role
from app.entity.department import Department
from app.entity.user_role import UserRole

logger = get_logger(__name__)


def create_demo_data():
    """
    创建演示数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建演示数据...")
        
        # 创建更多部门
        create_more_departments(db)
        
        # 创建更多用户
        create_more_users(db)
        
        # 创建更多角色
        create_more_roles(db)
        
        db.commit()
        logger.info("演示数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建演示数据失败: {str(e)}")
        raise
    finally:
        db.close()


def create_more_departments(db):
    """创建更多部门"""
    try:
        # 获取现有部门
        tech_dept = db.query(Department).filter(Department.dept_name == "技术部").first()
        
        if tech_dept:
            # 创建技术部更多子部门
            departments = [
                {"parent_id": tech_dept.id, "dept_name": "前端组", "order_num": 1.4},
                {"parent_id": tech_dept.id, "dept_name": "后端组", "order_num": 1.5},
                {"parent_id": tech_dept.id, "dept_name": "移动端组", "order_num": 1.6},
                {"parent_id": tech_dept.id, "dept_name": "架构组", "order_num": 1.7},
            ]
            
            for dept_data in departments:
                existing = db.query(Department).filter(Department.dept_name == dept_data["dept_name"]).first()
                if not existing:
                    dept = Department(**dept_data)
                    db.add(dept)
                    logger.info(f"创建部门: {dept_data['dept_name']}")
        
        # 创建更多顶级部门
        top_departments = [
            {"parent_id": 0, "dept_name": "市场部", "order_num": 4.0},
            {"parent_id": 0, "dept_name": "销售部", "order_num": 5.0},
            {"parent_id": 0, "dept_name": "客服部", "order_num": 6.0},
        ]
        
        for dept_data in top_departments:
            existing = db.query(Department).filter(Department.dept_name == dept_data["dept_name"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
                logger.info(f"创建顶级部门: {dept_data['dept_name']}")
        
        db.flush()
        
    except Exception as e:
        logger.error(f"创建部门失败: {str(e)}")
        raise


def create_more_users(db):
    """创建更多用户"""
    try:
        # 获取部门信息
        frontend_dept = db.query(Department).filter(Department.dept_name == "前端组").first()
        backend_dept = db.query(Department).filter(Department.dept_name == "后端组").first()
        market_dept = db.query(Department).filter(Department.dept_name == "市场部").first()
        sales_dept = db.query(Department).filter(Department.dept_name == "销售部").first()
        
        # 创建更多用户
        users_data = [
            {
                "username": "frontend_lead",
                "password": get_password_hash("123456"),
                "email": "frontend.lead@example.com",
                "mobile": "17788888894",
                "dept_id": frontend_dept.dept_id if frontend_dept else 1,
                "ssex": "0",
                "avatar": "default.jpg",
                "description": "前端组组长"
            },
            {
                "username": "backend_lead",
                "password": get_password_hash("123456"),
                "email": "backend.lead@example.com",
                "mobile": "17788888895",
                "dept_id": backend_dept.dept_id if backend_dept else 1,
                "ssex": "1",
                "avatar": "default.jpg",
                "description": "后端组组长"
            },
            {
                "username": "ui_designer",
                "password": get_password_hash("123456"),
                "email": "ui.designer@example.com",
                "mobile": "17788888896",
                "dept_id": frontend_dept.dept_id if frontend_dept else 1,
                "ssex": "1",
                "avatar": "default.jpg",
                "description": "UI设计师"
            },
            {
                "username": "product_manager",
                "password": get_password_hash("123456"),
                "email": "pm@example.com",
                "mobile": "17788888897",
                "dept_id": market_dept.dept_id if market_dept else 1,
                "ssex": "0",
                "avatar": "default.jpg",
                "description": "产品经理"
            },
            {
                "username": "sales_manager",
                "password": get_password_hash("123456"),
                "email": "sales.manager@example.com",
                "mobile": "17788888898",
                "dept_id": sales_dept.dept_id if sales_dept else 1,
                "ssex": "1",
                "avatar": "default.jpg",
                "description": "销售经理"
            }
        ]
        
        for user_data in users_data:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
                logger.info(f"创建用户: {user_data['username']}")
        
        db.flush()
        
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        raise


def create_more_roles(db):
    """创建更多角色"""
    try:
        roles_data = [
            {"role_name": "组长", "remark": "小组组长，管理组内成员"},
            {"role_name": "设计师", "remark": "UI/UX设计师"},
            {"role_name": "产品经理", "remark": "产品经理，负责产品规划"},
            {"role_name": "销售", "remark": "销售人员"},
            {"role_name": "客服", "remark": "客服人员"},
        ]
        
        for role_data in roles_data:
            existing = db.query(Role).filter(Role.role_name == role_data["role_name"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
                logger.info(f"创建角色: {role_data['role_name']}")
        
        db.flush()
        
        # 为新用户分配角色
        assign_roles_to_users(db)
        
    except Exception as e:
        logger.error(f"创建角色失败: {str(e)}")
        raise


def assign_roles_to_users(db):
    """为用户分配角色"""
    try:
        # 获取角色
        leader_role = db.query(Role).filter(Role.role_name == "组长").first()
        designer_role = db.query(Role).filter(Role.role_name == "设计师").first()
        pm_role = db.query(Role).filter(Role.role_name == "产品经理").first()
        sales_role = db.query(Role).filter(Role.role_name == "销售").first()
        
        # 获取用户
        frontend_lead = db.query(User).filter(User.username == "frontend_lead").first()
        backend_lead = db.query(User).filter(User.username == "backend_lead").first()
        ui_designer = db.query(User).filter(User.username == "ui_designer").first()
        product_manager = db.query(User).filter(User.username == "product_manager").first()
        sales_manager = db.query(User).filter(User.username == "sales_manager").first()
        
        # 分配角色
        role_assignments = [
            (frontend_lead, leader_role),
            (backend_lead, leader_role),
            (ui_designer, designer_role),
            (product_manager, pm_role),
            (sales_manager, sales_role),
        ]
        
        for user, role in role_assignments:
            if user and role:
                existing = db.query(UserRole).filter(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id
                ).first()
                
                if not existing:
                    user_role = UserRole(user_id=user.user_id, role_id=role.role_id)
                    db.add(user_role)
                    logger.info(f"为用户 {user.username} 分配角色 {role.role_name}")
        
    except Exception as e:
        logger.error(f"分配角色失败: {str(e)}")
        raise


def clear_demo_data():
    """清除演示数据"""
    db = SessionLocal()
    try:
        logger.info("开始清除演示数据...")
        
        # 删除演示用户（保留基础用户）
        demo_usernames = ["frontend_lead", "backend_lead", "ui_designer", "product_manager", "sales_manager"]
        for username in demo_usernames:
            user = db.query(User).filter(User.username == username).first()
            if user:
                # 先删除用户角色关联
                db.query(UserRole).filter(UserRole.user_id == user.user_id).delete()
                # 删除用户
                db.delete(user)
                logger.info(f"删除演示用户: {username}")
        
        # 删除演示角色（保留基础角色）
        demo_roles = ["组长", "设计师", "产品经理", "销售", "客服"]
        for role_name in demo_roles:
            role = db.query(Role).filter(Role.role_name == role_name).first()
            if role:
                # 先删除角色菜单关联
                from app.entity.role_menu import RoleMenu
                db.query(RoleMenu).filter(RoleMenu.role_id == role.role_id).delete()
                # 删除角色
                db.delete(role)
                logger.info(f"删除演示角色: {role_name}")
        
        # 删除演示部门（保留基础部门）
        demo_departments = ["前端组", "后端组", "移动端组", "架构组", "市场部", "销售部", "客服部"]
        for dept_name in demo_departments:
            dept = db.query(Department).filter(Department.dept_name == dept_name).first()
            if dept:
                db.delete(dept)
                logger.info(f"删除演示部门: {dept_name}")
        
        db.commit()
        logger.info("演示数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除演示数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="种子数据管理脚本")
    parser.add_argument("--create", action="store_true", help="创建演示数据")
    parser.add_argument("--clear", action="store_true", help="清除演示数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_demo_data()
    elif args.clear:
        clear_demo_data()
    else:
        print("请指定操作: --create 或 --clear")
