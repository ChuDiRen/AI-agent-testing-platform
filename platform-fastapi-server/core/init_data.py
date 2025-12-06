# -*- coding: utf-8 -*-
"""数据库初始化数据脚本"""

import logging
from datetime import datetime

from apitest.model.ApiOperationTypeModel import OperationType
from sqlmodel import Session, select
from sysmanage.model.dept import Dept
from sysmanage.model.menu import Menu
from sysmanage.model.role import Role
from sysmanage.model.role_menu import RoleMenu
from sysmanage.model.user import User
from sysmanage.model.user_role import UserRole

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

def create_initial_roles():
    """创建初始角色数据"""
    try:
        with Session(engine) as session:
            initial_roles = [
                {"role_id": 1, "role_name": "超级管理员", "remark": "拥有所有权限"},
                {"role_id": 2, "role_name": "管理员", "remark": "拥有部分管理权限"},
                {"role_id": 3, "role_name": "普通用户", "remark": "拥有基本权限"},
            ]

            for role_data in initial_roles:
                existing = session.get(Role, role_data["role_id"])
                if not existing:
                    role = Role(**role_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(role)
                    logger.info(f"创建角色: {role_data['role_name']}")

            session.commit()
            logger.info("初始角色数据创建完成")
    except Exception as e:
        logger.error(f"创建初始角色失败: {e}")
        raise

def create_initial_menus():
    """创建初始菜单数据（参考RuoYi-Vue-Plus设计）"""
    try:
        with Session(engine) as session:
            initial_menus = [
                # ================================
                # 系统总览（首页）
                # ================================
                # 0. 系统总览（菜单 C）
                {"id": 0, "parent_id": 0, "menu_name": "系统总览", "path": "/Statistics", "component": "Statistics", "query": None, "perms": "system:statistics:view", "icon": "DataLine", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 0, "remark": "系统总览首页"},
                
                # ================================
                # 系统管理模块
                # ================================
                # 1. 系统管理（目录 M）
                {"id": 1, "parent_id": 0, "menu_name": "系统管理", "path": "/system", "component": None, "query": None, "perms": None, "icon": "Setting", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "系统管理目录"},

                # 1.1 用户管理（菜单 C）
                {"id": 100, "parent_id": 1, "menu_name": "用户管理", "path": "/system/user", "component": "userList", "query": None, "perms": "system:user:list", "icon": "User", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "用户管理菜单"},
                {"id": 1001, "parent_id": 100, "menu_name": "用户查询", "path": None, "component": None, "query": None, "perms": "system:user:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 1002, "parent_id": 100, "menu_name": "用户新增", "path": None, "component": None, "query": None, "perms": "system:user:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 1003, "parent_id": 100, "menu_name": "用户修改", "path": None, "component": None, "query": None, "perms": "system:user:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 1004, "parent_id": 100, "menu_name": "用户删除", "path": None, "component": None, "query": None, "perms": "system:user:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 1005, "parent_id": 100, "menu_name": "用户导出", "path": None, "component": None, "query": None, "perms": "system:user:export", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},

                # 1.2 角色管理（菜单 C）
                {"id": 101, "parent_id": 1, "menu_name": "角色管理", "path": "/system/role", "component": "roleList", "query": None, "perms": "system:role:list", "icon": "UserFilled", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "角色管理菜单"},
                {"id": 1011, "parent_id": 101, "menu_name": "角色查询", "path": None, "component": None, "query": None, "perms": "system:role:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 1012, "parent_id": 101, "menu_name": "角色新增", "path": None, "component": None, "query": None, "perms": "system:role:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 1013, "parent_id": 101, "menu_name": "角色修改", "path": None, "component": None, "query": None, "perms": "system:role:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 1014, "parent_id": 101, "menu_name": "角色删除", "path": None, "component": None, "query": None, "perms": "system:role:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 1.3 菜单管理（菜单 C）
                {"id": 102, "parent_id": 1, "menu_name": "菜单管理", "path": "/system/menu", "component": "menuList", "query": None, "perms": "system:menu:list", "icon": "Menu", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "菜单管理菜单"},
                {"id": 1021, "parent_id": 102, "menu_name": "菜单查询", "path": None, "component": None, "query": None, "perms": "system:menu:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 1022, "parent_id": 102, "menu_name": "菜单新增", "path": None, "component": None, "query": None, "perms": "system:menu:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 1023, "parent_id": 102, "menu_name": "菜单修改", "path": None, "component": None, "query": None, "perms": "system:menu:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 1024, "parent_id": 102, "menu_name": "菜单删除", "path": None, "component": None, "query": None, "perms": "system:menu:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 1.4 部门管理（菜单 C）
                {"id": 103, "parent_id": 1, "menu_name": "部门管理", "path": "/system/dept", "component": "deptList", "query": None, "perms": "system:dept:list", "icon": "OfficeBuilding", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "部门管理菜单"},
                {"id": 1031, "parent_id": 103, "menu_name": "部门查询", "path": None, "component": None, "query": None, "perms": "system:dept:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 1032, "parent_id": 103, "menu_name": "部门新增", "path": None, "component": None, "query": None, "perms": "system:dept:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 1033, "parent_id": 103, "menu_name": "部门修改", "path": None, "component": None, "query": None, "perms": "system:dept:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 1034, "parent_id": 103, "menu_name": "部门删除", "path": None, "component": None, "query": None, "perms": "system:dept:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
            ]

            for menu_data in initial_menus:
                menu_id = menu_data.get("id")
                existing = session.get(Menu, menu_id)
                if not existing:
                    menu = Menu(**menu_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(menu)
                    logger.info(f"创建菜单: {menu_data['menu_name']} (ID: {menu_id})")

            # ================================
            # API测试模块
            # ================================
            # 2. API自动化（目录 M）
            api_menus = [
                {"id": 200, "parent_id": 0, "menu_name": "API自动化", "path": "/apitest", "component": None, "query": None, "perms": None, "icon": "Promotion", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "API自动化测试模块"},

                # 2.1 项目管理（菜单 C）
                {"id": 2000, "parent_id": 200, "menu_name": "项目管理", "path": "/apitest/project", "component": "ApiProjectList", "query": None, "perms": "apitest:project:list", "icon": "Folder", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "API项目管理"},
                {"id": 2001, "parent_id": 2000, "menu_name": "项目查询", "path": None, "component": None, "query": None, "perms": "apitest:project:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2002, "parent_id": 2000, "menu_name": "项目新增", "path": None, "component": None, "query": None, "perms": "apitest:project:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2003, "parent_id": 2000, "menu_name": "项目修改", "path": None, "component": None, "query": None, "perms": "apitest:project:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2004, "parent_id": 2000, "menu_name": "项目删除", "path": None, "component": None, "query": None, "perms": "apitest:project:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.2 接口信息管理（菜单 C）
                {"id": 201, "parent_id": 200, "menu_name": "接口信息", "path": "/apitest/apiinfo", "component": "ApiInfoList", "query": None, "perms": "apitest:api:list", "icon": "Monitor", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "接口信息管理"},
                {"id": 2011, "parent_id": 201, "menu_name": "接口查询", "path": None, "component": None, "query": None, "perms": "apitest:api:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2012, "parent_id": 201, "menu_name": "接口新增", "path": None, "component": None, "query": None, "perms": "apitest:api:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2013, "parent_id": 201, "menu_name": "接口修改", "path": None, "component": None, "query": None, "perms": "apitest:api:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2014, "parent_id": 201, "menu_name": "接口删除", "path": None, "component": None, "query": None, "perms": "apitest:api:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.3 关键字管理（菜单 C）
                {"id": 203, "parent_id": 200, "menu_name": "关键字管理", "path": "/apitest/keyword", "component": "ApiKeyWordList", "query": None, "perms": "apitest:keyword:list", "icon": "Key", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "关键字管理"},
                {"id": 2031, "parent_id": 203, "menu_name": "关键字查询", "path": None, "component": None, "query": None, "perms": "apitest:keyword:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2032, "parent_id": 203, "menu_name": "关键字新增", "path": None, "component": None, "query": None, "perms": "apitest:keyword:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2033, "parent_id": 203, "menu_name": "关键字修改", "path": None, "component": None, "query": None, "perms": "apitest:keyword:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2034, "parent_id": 203, "menu_name": "关键字删除", "path": None, "component": None, "query": None, "perms": "apitest:keyword:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.4 素材管理（菜单 C）
                {"id": 204, "parent_id": 200, "menu_name": "素材管理", "path": "/apitest/mate", "component": "ApiMateManageList", "query": None, "perms": "apitest:mate:list", "icon": "Picture", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "素材管理"},
                {"id": 2041, "parent_id": 204, "menu_name": "素材查询", "path": None, "component": None, "query": None, "perms": "apitest:mate:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2042, "parent_id": 204, "menu_name": "素材新增", "path": None, "component": None, "query": None, "perms": "apitest:mate:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2043, "parent_id": 204, "menu_name": "素材修改", "path": None, "component": None, "query": None, "perms": "apitest:mate:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2044, "parent_id": 204, "menu_name": "素材删除", "path": None, "component": None, "query": None, "perms": "apitest:mate:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.5 用例管理（菜单 C）
                {"id": 206, "parent_id": 200, "menu_name": "用例管理", "path": "/ApiInfoCaseList", "component": "ApiInfoCaseList", "query": None, "perms": "apitest:case:list", "icon": "Document", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": "API用例管理"},
                {"id": 2061, "parent_id": 206, "menu_name": "用例查询", "path": None, "component": None, "query": None, "perms": "apitest:case:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2062, "parent_id": 206, "menu_name": "用例新增", "path": None, "component": None, "query": None, "perms": "apitest:case:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2063, "parent_id": 206, "menu_name": "用例修改", "path": None, "component": None, "query": None, "perms": "apitest:case:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2064, "parent_id": 206, "menu_name": "用例删除", "path": None, "component": None, "query": None, "perms": "apitest:case:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 2065, "parent_id": 206, "menu_name": "用例执行", "path": None, "component": None, "query": None, "perms": "apitest:case:execute", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},

                # 2.6 测试计划（菜单 C）
                {"id": 207, "parent_id": 200, "menu_name": "测试计划", "path": "/ApiCollectionInfoList", "component": "ApiCollectionInfoList", "query": None, "perms": "apitest:plan:list", "icon": "DataAnalysis", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 6, "remark": "API测试计划管理"},
                {"id": 2071, "parent_id": 207, "menu_name": "计划查询", "path": None, "component": None, "query": None, "perms": "apitest:plan:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2072, "parent_id": 207, "menu_name": "计划新增", "path": None, "component": None, "query": None, "perms": "apitest:plan:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2073, "parent_id": 207, "menu_name": "计划修改", "path": None, "component": None, "query": None, "perms": "apitest:plan:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2074, "parent_id": 207, "menu_name": "计划删除", "path": None, "component": None, "query": None, "perms": "apitest:plan:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 2075, "parent_id": 207, "menu_name": "计划执行", "path": None, "component": None, "query": None, "perms": "apitest:plan:execute", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},

                # 2.7 测试历史（菜单 C）
                {"id": 205, "parent_id": 200, "menu_name": "测试历史", "path": "/apitest/testhistory", "component": "ApiTestHistory", "query": None, "perms": "apitest:history:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 7, "remark": "测试历史记录"},
                {"id": 2051, "parent_id": 205, "menu_name": "历史查询", "path": None, "component": None, "query": None, "perms": "apitest:history:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2052, "parent_id": 205, "menu_name": "历史删除", "path": None, "component": None, "query": None, "perms": "apitest:history:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},

                # ================================
                # AI配置模块
                # ================================
                # 3. AI配置（目录 M）
                {"id": 300, "parent_id": 0, "menu_name": "AI配置", "path": "/ai-config", "component": None, "query": None, "perms": None, "icon": "Setting", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "AI配置管理模块"},

                # 3.1 AI模型管理（菜单 C）
                {"id": 301, "parent_id": 300, "menu_name": "AI模型", "path": "/ai-models", "component": "AiModelList", "query": None, "perms": "ai:model:list", "icon": "Cpu", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "AI模型管理"},
                {"id": 3011, "parent_id": 301, "menu_name": "模型查询", "path": None, "component": None, "query": None, "perms": "ai:model:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 3012, "parent_id": 301, "menu_name": "模型新增", "path": None, "component": None, "query": None, "perms": "ai:model:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 3013, "parent_id": 301, "menu_name": "模型修改", "path": None, "component": None, "query": None, "perms": "ai:model:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 3014, "parent_id": 301, "menu_name": "模型删除", "path": None, "component": None, "query": None, "perms": "ai:model:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 3.2 提示词模板管理（菜单 C）
                {"id": 302, "parent_id": 300, "menu_name": "提示词", "path": "/ai-prompts", "component": "PromptTemplateList", "query": None, "perms": "ai:prompt:list", "icon": "Edit", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "提示词模板管理"},
                {"id": 3021, "parent_id": 302, "menu_name": "模板查询", "path": None, "component": None, "query": None, "perms": "ai:prompt:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 3022, "parent_id": 302, "menu_name": "模板新增", "path": None, "component": None, "query": None, "perms": "ai:prompt:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 3023, "parent_id": 302, "menu_name": "模板修改", "path": None, "component": None, "query": None, "perms": "ai:prompt:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 3024, "parent_id": 302, "menu_name": "模板删除", "path": None, "component": None, "query": None, "perms": "ai:prompt:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 3.3 智能体聊天（菜单 C）
                {"id": 304, "parent_id": 300, "menu_name": "智能体聊天", "path": "/agent-chat", "component": "AgentChatIntegrated", "query": None, "perms": "ai:agent:chat", "icon": "ChatDotRound", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "智能体聊天"},
                
                # 3.4 测试用例管理（菜单 C）
                {"id": 305, "parent_id": 300, "menu_name": "测试用例", "path": "/test-cases", "component": "TestCaseList", "query": None, "perms": "ai:testcase:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "测试用例管理"},
                {"id": 3051, "parent_id": 305, "menu_name": "用例查询", "path": None, "component": None, "query": None, "perms": "ai:testcase:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 3052, "parent_id": 305, "menu_name": "用例新增", "path": None, "component": None, "query": None, "perms": "ai:testcase:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 3053, "parent_id": 305, "menu_name": "用例修改", "path": None, "component": None, "query": None, "perms": "ai:testcase:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 3054, "parent_id": 305, "menu_name": "用例删除", "path": None, "component": None, "query": None, "perms": "ai:testcase:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # ================================
                # 代码生成器模块
                # ================================
                # 4. 代码生成器（目录 M）
                {"id": 400, "parent_id": 0, "menu_name": "代码生成", "path": "/generator", "component": None, "query": None, "perms": None, "icon": "Document", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "代码生成器模块"},

                # 4.1 表配置管理（菜单 C）
                {"id": 401, "parent_id": 400, "menu_name": "表配置", "path": "/generator/table", "component": "GenTableList", "query": None, "perms": "generator:table:list", "icon": "Grid", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "代码生成器表配置管理"},
                {"id": 4011, "parent_id": 401, "menu_name": "表配置查询", "path": None, "component": None, "query": None, "perms": "generator:table:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 4012, "parent_id": 401, "menu_name": "导入表", "path": None, "component": None, "query": None, "perms": "generator:table:import", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 4013, "parent_id": 401, "menu_name": "表配置修改", "path": None, "component": None, "query": None, "perms": "generator:table:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 4014, "parent_id": 401, "menu_name": "表配置删除", "path": None, "component": None, "query": None, "perms": "generator:table:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 4.2 代码生成（菜单 C）
                {"id": 402, "parent_id": 400, "menu_name": "代码生成", "path": "/generator/code", "component": "GeneratorCode", "query": None, "perms": "generator:code:list", "icon": "EditPen", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "代码生成器"},
                {"id": 4021, "parent_id": 402, "menu_name": "代码预览", "path": None, "component": None, "query": None, "perms": "generator:code:preview", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 4022, "parent_id": 402, "menu_name": "代码下载", "path": None, "component": None, "query": None, "perms": "generator:code:download", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 4023, "parent_id": 402, "menu_name": "批量下载", "path": None, "component": None, "query": None, "perms": "generator:code:batchDownload", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                
                # 4.3 生成历史（菜单 C）
                {"id": 403, "parent_id": 400, "menu_name": "生成历史", "path": "/generator/history", "component": "GenHistory", "query": None, "perms": "generator:history:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "生成历史记录"},
                {"id": 4031, "parent_id": 403, "menu_name": "历史查询", "path": None, "component": None, "query": None, "perms": "generator:history:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 4032, "parent_id": 403, "menu_name": "历史删除", "path": None, "component": None, "query": None, "perms": "generator:history:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},

                # ================================
                # 消息管理模块
                # ================================
                # 5. 消息管理（目录 M）
                {"id": 500, "parent_id": 0, "menu_name": "消息管理", "path": "/msgmanage", "component": None, "query": None, "perms": None, "icon": "Message", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": "消息管理模块"},

                # 5.1 机器人配置（菜单 C）
                {"id": 501, "parent_id": 500, "menu_name": "机器人配置", "path": "/RobotConfigList", "component": "RobotConfigList", "query": None, "perms": "msgmanage:robot:list", "icon": "Cpu", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "机器人配置"},
                {"id": 5011, "parent_id": 501, "menu_name": "机器人查询", "path": None, "component": None, "query": None, "perms": "msgmanage:robot:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 5012, "parent_id": 501, "menu_name": "机器人新增", "path": None, "component": None, "query": None, "perms": "msgmanage:robot:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 5013, "parent_id": 501, "menu_name": "机器人修改", "path": None, "component": None, "query": None, "perms": "msgmanage:robot:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 5014, "parent_id": 501, "menu_name": "机器人删除", "path": None, "component": None, "query": None, "perms": "msgmanage:robot:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 5.2 消息模板管理（菜单 C）
                {"id": 502, "parent_id": 500, "menu_name": "消息模板", "path": "/RobotMsgConfigList", "component": "RobotMsgConfigList", "query": None, "perms": "msgmanage:template:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "消息模板管理"},
                {"id": 5021, "parent_id": 502, "menu_name": "模板查询", "path": None, "component": None, "query": None, "perms": "msgmanage:template:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 5022, "parent_id": 502, "menu_name": "模板新增", "path": None, "component": None, "query": None, "perms": "msgmanage:template:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 5023, "parent_id": 502, "menu_name": "模板修改", "path": None, "component": None, "query": None, "perms": "msgmanage:template:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {" id": 5024, "parent_id": 502, "menu_name": "模板删除", "path": None, "component": None, "query": None, "perms": "msgmanage:template:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                
                # ================================
                # 插件管理模块
                # ================================
                # 6. 插件管理（目录 M）
                {"id": 600, "parent_id": 0, "menu_name": "插件管理", "path": "/plugin", "component": None, "query": None, "perms": None, "icon": "Setting", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 6, "remark": "插件管理模块"},
                
                # 6.1 插件市场（菜单 C）
                {"id": 601, "parent_id": 600, "menu_name": "插件市场", "path": "/plugin/market", "component": "plugin/PluginMarket", "query": None, "perms": "plugin:market:list", "icon": "Shop", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "插件市场"},
                {"id": 6011, "parent_id": 601, "menu_name": "插件查询", "path": None, "component": None, "query": None, "perms": "plugin:market:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 6012, "parent_id": 601, "menu_name": "插件注册", "path": None, "component": None, "query": None, "perms": "plugin:market:register", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 6013, "parent_id": 601, "menu_name": "插件修改", "path": None, "component": None, "query": None, "perms": "plugin:market:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 6014, "parent_id": 601, "menu_name": "插件删除", "path": None, "component": None, "query": None, "perms": "plugin:market:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 6015, "parent_id": 601, "menu_name": "插件启用/禁用", "path": None, "component": None, "query": None, "perms": "plugin:market:toggle", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},
            ]

            for menu_data in api_menus:
                menu_id = menu_data.get("id")
                existing = session.get(Menu, menu_id)
                if not existing:
                    menu = Menu(**menu_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(menu)
                    logger.info(f"创建菜单: {menu_data['menu_name']} (ID: {menu_id})")

            session.commit()
            logger.info("初始菜单数据创建完成")
    except Exception as e:
        logger.error(f"创建初始菜单失败: {e}")
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
                else:
                    logger.info(f"用户已存在: {user_data['username']}")

            session.commit()
            logger.info("初始用户数据创建完成")

    except Exception as e:
        logger.error(f"创建初始用户失败: {e}")
        raise

def create_initial_user_roles():
    """创建初始用户-角色关联数据"""
    try:
        with Session(engine) as session:
            initial_user_roles = [
                {"user_id": 1, "role_id": 1}, # admin -> 超级管理员
            ]

            for ur_data in initial_user_roles:
                statement = select(UserRole).where(
                    UserRole.user_id == ur_data["user_id"],
                    UserRole.role_id == ur_data["role_id"]
                )
                existing = session.exec(statement).first()
                if not existing:
                    user_role = UserRole(**ur_data)
                    session.add(user_role)
                    logger.info(f"分配角色: 用户{ur_data['user_id']} -> 角色{ur_data['role_id']}")

            session.commit()
            logger.info("初始用户角色关联创建完成")
    except Exception as e:
        logger.error(f"创建用户角色关联失败: {e}")
        raise

def create_initial_role_menus():
    """创建初始角色-菜单关联数据"""
    try:
        with Session(engine) as session:
            # 获取所有菜单ID
            statement = select(Menu)
            all_menus = session.exec(statement).all()
            all_menu_ids = [menu.id for menu in all_menus]

            # 超级管理员（角色ID=1）拥有所有权限
            for menu_id in all_menu_ids:
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 1,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                if not existing:
                    role_menu = RoleMenu(role_id=1, menu_id=menu_id)
                    session.add(role_menu)
            logger.info("超级管理员权限分配完成")

            # 管理员（角色ID=2）拥有系统管理、API测试和代码生成器权限
            admin_menu_ids = [
                # 系统总览
                0,
                # 系统管理
                1, 100, 101, 1001, 1002, 1003, 1004, 1005, 1011, 1012, 1013, 1014,
                # API测试模块
                200,
                # 项目管理
                2000, 2001, 2002, 2003, 2004,
                # 接口信息
                201, 2011, 2012, 2013, 2014,
                # 接口分组
                202, 2021, 2022, 2023, 2024,
                # 关键字管理
                203, 2031, 2032, 2033, 2034,
                # 素材管理
                204, 2041, 2042, 2043, 2044,
                # 测试历史
                205, 2051, 2052,
                # 用例管理
                206, 2061, 2062, 2063, 2064, 2065,
                # 测试计划
                207, 2071, 2072, 2073, 2074, 2075,
                # 代码生成器模块
                300,
                # 表配置
                3000, 3001, 3002, 3003, 3004,
                # 代码生成
                3100, 3101, 3102, 3103,
                # 生成历史
                3200, 3201
            ]
            for menu_id in admin_menu_ids:
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 2,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                if not existing:
                    role_menu = RoleMenu(role_id=2, menu_id=menu_id)
                    session.add(role_menu)
            logger.info("管理员权限分配完成")

            # 普通用户（角色ID=3）只有API测试查看权限
            user_menu_ids = [
                # 系统总览
                0,
                # API测试模块
                200,
                # 项目查询
                2000, 2001,
                # 接口查询
                201, 2011,
                # 分组查询
                202, 2021,
                # 关键字查询
                203, 2031,
                # 素材查询
                204, 2041,
                # 测试历史查询
                205, 2051,
                # 用例查询
                206, 2061,
                # 测试计划查询
                207, 2071
            ]
            for menu_id in user_menu_ids:
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 3,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                if not existing:
                    role_menu = RoleMenu(role_id=3, menu_id=menu_id)
                    session.add(role_menu)
            logger.info("普通用户权限分配完成")

            session.commit()
            logger.info("初始角色菜单关联创建完成")
    except Exception as e:
        logger.error(f"创建角色菜单关联失败: {e}")
        raise

def create_initial_operation_types():
    """创建初始操作类型数据"""
    try:
        with Session(engine) as session:
            # 检查是否已存在操作类型数据
            existing = session.exec(select(OperationType)).first()
            if existing:
                logger.info("操作类型数据已存在，跳过初始化")
                return
            
            initial_types = [
                {"id": 1, "operation_type_name": "HTTP请求", "ex_fun_name": "http_request"},
                {"id": 2, "operation_type_name": "数据提取", "ex_fun_name": "data_extract"},
                {"id": 3, "operation_type_name": "断言验证", "ex_fun_name": "assertion"},
                {"id": 4, "operation_type_name": "数据库操作", "ex_fun_name": "database"},
                {"id": 5, "operation_type_name": "工具方法", "ex_fun_name": "utility"},
                {"id": 6, "operation_type_name": "文件操作", "ex_fun_name": "file_operation"},
            ]
            
            for type_data in initial_types:
                op_type = OperationType(**type_data, create_time=datetime.now())
                session.add(op_type)
                logger.info(f"创建操作类型: {type_data['operation_type_name']}")
            
            session.commit()
            logger.info(f"初始操作类型数据创建完成，共创建{len(initial_types)}个操作类型")
    except Exception as e:
        logger.error(f"创建初始操作类型失败: {e}")
        raise

def init_all_data():
    """初始化所有数据"""
    try:
        logger.info("开始初始化RBAC数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过RBAC初始化")
            # 但仍然尝试初始化AI数据（如果未初始化）
            from .init_ai_data import init_all_ai_data
            with Session(engine) as session:
                init_all_ai_data(session)
            return
        
        # 按顺序创建初始数据
        create_initial_depts() # 1. 创建部门
        create_initial_roles() # 2. 创建角色
        create_initial_menus() # 3. 创建菜单
        create_initial_users() # 4. 创建用户
        create_initial_user_roles() # 5. 分配用户角色
        create_initial_role_menus() # 6. 分配角色权限
        
        # 初始化AI数据
        logger.info("开始初始化AI数据...")
        from .init_ai_data import init_all_ai_data
        with Session(engine) as session:
            init_all_ai_data(session)
        
        # 初始化操作类型数据
        logger.info("开始初始化操作类型数据...")
        create_initial_operation_types()
        
        # 关键字数据不再预设，通过"从引擎同步"功能动态添加
        # 插件数据不再预设，通过"上传执行器"功能动态添加
        
        logger.info("系统数据初始化完成！")
        logger.info("=" * 70)
        logger.info("默认登录账号:")
        logger.info("  admin / admin123 (超级管理员)")
        logger.info("")
        logger.info("RBAC功能清单:")
        logger.info("  ✓ 4个部门 (总公司、技术部、产品部、运营部)")
        logger.info("  ✓ 3个角色 (超级管理员、管理员、普通用户)")
        logger.info("  ✓ 完整菜单权限体系 (系统管理 + API测试 + AI配置)")
        logger.info("  ✓ 系统管理: 用户、角色、菜单、部门管理")
        logger.info("  ✓ API测试: 项目、接口、分组、关键字、素材、测试历史")
        logger.info("  ✓ AI配置: 模型、提示词、助手、用例管理")
        logger.info("  ✓ 用户-角色-菜单权限关联")
        logger.info("  ✓ 按钮级权限控制 (查询、新增、修改、删除)")
        logger.info("")
        logger.info("关键字功能:")
        logger.info("  ✓ 关键字通过\"从引擎同步\"功能从执行器插件动态导入")
        logger.info("")
        logger.info("插件系统清单:")
        logger.info("  ✓ 1个执行器插件 (Web Engine)")
        logger.info("  ✓ 支持命令行调用方式")
        logger.info("  ✓ 插件市场管理界面")
        logger.info("  ✓ 任务调度和执行监控")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_all_data()
