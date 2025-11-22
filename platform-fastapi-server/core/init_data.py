# -*- coding: utf-8 -*-
"""数据库初始化数据脚本"""

from sqlmodel import Session, select
from .database import engine
from sysmanage.model.user import User
from sysmanage.model.role import Role
from sysmanage.model.menu import Menu
from sysmanage.model.dept import Dept
from sysmanage.model.user_role import UserRole
from sysmanage.model.role_menu import RoleMenu
from apitest.model.ApiKeyWordModel import ApiKeyWord
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
                {"id": 201, "parent_id": 200, "menu_name": "接口信息", "path": "/apitest/apiinfo", "component": "ApiInfoList", "query": None, "perms": "apitest:apiinfo:list", "icon": "Monitor", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "接口信息管理"},
                {"id": 2011, "parent_id": 201, "menu_name": "接口查询", "path": None, "component": None, "query": None, "perms": "apitest:apiinfo:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2012, "parent_id": 201, "menu_name": "接口新增", "path": None, "component": None, "query": None, "perms": "apitest:apiinfo:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2013, "parent_id": 201, "menu_name": "接口修改", "path": None, "component": None, "query": None, "perms": "apitest:apiinfo:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2014, "parent_id": 201, "menu_name": "接口删除", "path": None, "component": None, "query": None, "perms": "apitest:apiinfo:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.3 接口分组管理（菜单 C）
                {"id": 202, "parent_id": 200, "menu_name": "接口分组", "path": "/apitest/apigroup", "component": "ApiGroupList", "query": None, "perms": "apitest:apigroup:list", "icon": "DocumentCopy", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "接口分组管理"},
                {"id": 2021, "parent_id": 202, "menu_name": "分组查询", "path": None, "component": None, "query": None, "perms": "apitest:apigroup:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2022, "parent_id": 202, "menu_name": "分组新增", "path": None, "component": None, "query": None, "perms": "apitest:apigroup:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2023, "parent_id": 202, "menu_name": "分组修改", "path": None, "component": None, "query": None, "perms": "apitest:apigroup:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2024, "parent_id": 202, "menu_name": "分组删除", "path": None, "component": None, "query": None, "perms": "apitest:apigroup:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.4 关键字管理（菜单 C）
                {"id": 203, "parent_id": 200, "menu_name": "关键字管理", "path": "/apitest/keyword", "component": "ApiKeyWordList", "query": None, "perms": "apitest:keyword:list", "icon": "Key", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "关键字管理"},
                {"id": 2031, "parent_id": 203, "menu_name": "关键字查询", "path": None, "component": None, "query": None, "perms": "apitest:keyword:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2032, "parent_id": 203, "menu_name": "关键字新增", "path": None, "component": None, "query": None, "perms": "apitest:keyword:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2033, "parent_id": 203, "menu_name": "关键字修改", "path": None, "component": None, "query": None, "perms": "apitest:keyword:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2034, "parent_id": 203, "menu_name": "关键字删除", "path": None, "component": None, "query": None, "perms": "apitest:keyword:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.5 素材管理（菜单 C）
                {"id": 204, "parent_id": 200, "menu_name": "素材管理", "path": "/apitest/mate", "component": "ApiMateManageList", "query": None, "perms": "apitest:mate:list", "icon": "Picture", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": "素材管理"},
                {"id": 2041, "parent_id": 204, "menu_name": "素材查询", "path": None, "component": None, "query": None, "perms": "apitest:mate:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2042, "parent_id": 204, "menu_name": "素材新增", "path": None, "component": None, "query": None, "perms": "apitest:mate:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2043, "parent_id": 204, "menu_name": "素材修改", "path": None, "component": None, "query": None, "perms": "apitest:mate:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2044, "parent_id": 204, "menu_name": "素材删除", "path": None, "component": None, "query": None, "perms": "apitest:mate:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 2.6 测试历史（菜单 C）
                {"id": 205, "parent_id": 200, "menu_name": "测试历史", "path": "/apitest/testhistory", "component": "ApiTestHistory", "query": None, "perms": "apitest:testhistory:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 6, "remark": "测试历史记录"},
                {"id": 2051, "parent_id": 205, "menu_name": "历史查询", "path": None, "component": None, "query": None, "perms": "apitest:testhistory:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2052, "parent_id": 205, "menu_name": "历史删除", "path": None, "component": None, "query": None, "perms": "apitest:testhistory:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},

                # 2.7 用例管理（菜单 C）
                {"id": 206, "parent_id": 200, "menu_name": "用例管理", "path": "/ApiCaseList", "component": "ApiCaseList", "query": None, "perms": "apitest:case:list", "icon": "Document", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 7, "remark": "API用例管理"},
                {"id": 2061, "parent_id": 206, "menu_name": "用例查询", "path": None, "component": None, "query": None, "perms": "apitest:case:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2062, "parent_id": 206, "menu_name": "用例新增", "path": None, "component": None, "query": None, "perms": "apitest:case:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2063, "parent_id": 206, "menu_name": "用例修改", "path": None, "component": None, "query": None, "perms": "apitest:case:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2064, "parent_id": 206, "menu_name": "用例删除", "path": None, "component": None, "query": None, "perms": "apitest:case:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 2065, "parent_id": 206, "menu_name": "用例执行", "path": None, "component": None, "query": None, "perms": "apitest:case:execute", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},

                # 2.8 测试计划（菜单 C）
                {"id": 207, "parent_id": 200, "menu_name": "测试计划", "path": "/ApiTestPlanList", "component": "ApiTestPlanList", "query": None, "perms": "apitest:plan:list", "icon": "DataAnalysis", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 8, "remark": "API测试计划管理"},
                {"id": 2071, "parent_id": 207, "menu_name": "计划查询", "path": None, "component": None, "query": None, "perms": "apitest:plan:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 2072, "parent_id": 207, "menu_name": "计划新增", "path": None, "component": None, "query": None, "perms": "apitest:plan:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 2073, "parent_id": 207, "menu_name": "计划修改", "path": None, "component": None, "query": None, "perms": "apitest:plan:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 2074, "parent_id": 207, "menu_name": "计划删除", "path": None, "component": None, "query": None, "perms": "apitest:plan:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
                {"id": 2075, "parent_id": 207, "menu_name": "计划执行", "path": None, "component": None, "query": None, "perms": "apitest:plan:execute", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 5, "remark": None},

                # ================================
                # AI配置模块
                # ================================
                # 3. AI配置（目录 M）
                {"id": 300, "parent_id": 0, "menu_name": "AI配置", "path": "/ai-config", "component": None, "query": None, "perms": None, "icon": "Setting", "menu_type": "M", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "AI配置管理模块"},

                # 3.1 AI模型管理（菜单 C）
                {"id": 301, "parent_id": 300, "menu_name": "AI模型", "path": "/ai-config/models", "component": "ai-models", "query": None, "perms": "ai:model:list", "icon": "Cpu", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": "AI模型管理"},
                {"id": 3011, "parent_id": 301, "menu_name": "模型查询", "path": None, "component": None, "query": None, "perms": "ai:model:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 3012, "parent_id": 301, "menu_name": "模型新增", "path": None, "component": None, "query": None, "perms": "ai:model:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 3013, "parent_id": 301, "menu_name": "模型修改", "path": None, "component": None, "query": None, "perms": "ai:model:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 3014, "parent_id": 301, "menu_name": "模型删除", "path": None, "component": None, "query": None, "perms": "ai:model:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 3.2 提示词模板管理（菜单 C）
                {"id": 302, "parent_id": 300, "menu_name": "提示词", "path": "/ai-config/prompts", "component": "ai-prompts", "query": None, "perms": "ai:prompt:list", "icon": "Edit", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": "提示词模板管理"},
                {"id": 3021, "parent_id": 302, "menu_name": "模板查询", "path": None, "component": None, "query": None, "perms": "ai:prompt:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
                {"id": 3022, "parent_id": 302, "menu_name": "模板新增", "path": None, "component": None, "query": None, "perms": "ai:prompt:add", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 2, "remark": None},
                {"id": 3023, "parent_id": 302, "menu_name": "模板修改", "path": None, "component": None, "query": None, "perms": "ai:prompt:edit", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": None},
                {"id": 3024, "parent_id": 302, "menu_name": "模板删除", "path": None, "component": None, "query": None, "perms": "ai:prompt:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},

                # 3.3 智能体聊天（菜单 C）
                {"id": 304, "parent_id": 300, "menu_name": "智能体聊天", "path": "/agent-chat", "component": "agent-chat", "query": None, "perms": "ai:agent:chat", "icon": "ChatDotRound", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 3, "remark": "智能体聊天"},
                
                # 3.4 测试用例管理（菜单 C）
                {"id": 305, "parent_id": 300, "menu_name": "测试用例", "path": "/test-cases", "component": "test-cases", "query": None, "perms": "ai:testcase:list", "icon": "Tickets", "menu_type": "C", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": "测试用例管理"},
                {" id": 3051, "parent_id": 305, "menu_name": "用例查询", "path": None, "component": None, "query": None, "perms": "ai:testcase:query", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 1, "remark": None},
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
                {"id": 5024, "parent_id": 502, "menu_name": "模板删除", "path": None, "component": None, "query": None, "perms": "msgmanage:template:delete", "icon": None, "menu_type": "F", "visible": "0", "status": "0", "is_cache": "0", "is_frame": "1", "order_num": 4, "remark": None},
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

def create_initial_keywords():
    """创建初始关键字数据"""
    try:
        with Session(engine) as session:
            # 检查是否已存在关键字数据
            existing_keywords = session.exec(select(ApiKeyWord)).first()
            if existing_keywords:
                logger.info("关键字数据已存在，跳过初始化")
                return
            
            initial_keywords = [
                # ================================
                # HTTP请求类关键字
                # ================================
                {
                    "name": "GET请求",
                    "keyword_desc": "发送GET请求",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_get",
                    "keyword_value": """def request_get(self, **kwargs):
    \"\"\"发送GET请求\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
    }
    response = requests.get(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "POST请求(JSON)",
                    "keyword_desc": "发送POST请求，数据格式为JSON",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_post_json",
                    "keyword_value": """def request_post_json(self, **kwargs):
    \"\"\"发送POST请求，数据格式为JSON\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    data = kwargs.get("DATA", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
        "json": data,
    }
    response = requests.post(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "POST请求(表单)",
                    "keyword_desc": "发送POST请求，数据格式为表单",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_post_form",
                    "keyword_value": """def request_post_form(self, **kwargs):
    \"\"\"发送POST请求，数据格式为表单\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    data = kwargs.get("DATA", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
        "data": data,
    }
    response = requests.post(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "POST请求(文件上传)",
                    "keyword_desc": "发送POST请求，支持文件上传",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_post_file",
                    "keyword_value": """def request_post_file(self, **kwargs):
    \"\"\"发送POST请求，支持文件上传\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    data = kwargs.get("DATA", None)
    files = kwargs.get("FILES", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
        "data": data,
        "files": files,
    }
    response = requests.post(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "PUT请求",
                    "keyword_desc": "发送PUT请求",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_put",
                    "keyword_value": """def request_put(self, **kwargs):
    \"\"\"发送PUT请求\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    data = kwargs.get("DATA", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
        "json": data,
    }
    response = requests.put(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "DELETE请求",
                    "keyword_desc": "发送DELETE请求",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_delete",
                    "keyword_value": """def request_delete(self, **kwargs):
    \"\"\"发送DELETE请求\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
    }
    response = requests.delete(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                {
                    "name": "PATCH请求",
                    "keyword_desc": "发送PATCH请求",
                    "operation_type_id": 1,
                    "keyword_fun_name": "request_patch",
                    "keyword_value": """def request_patch(self, **kwargs):
    \"\"\"发送PATCH请求\"\"\"
    url = kwargs.get("URL", None)
    params = kwargs.get("PARAMS", None)
    headers = kwargs.get("HEADERS", None)
    data = kwargs.get("DATA", None)
    
    request_data = {
        "url": url,
        "params": params,
        "headers": headers,
        "json": data,
    }
    response = requests.patch(**request_data)
    g_context().set_dict("current_response", response)
    return response""",
                    "is_enabled": "1"
                },
                
                # ================================
                # 数据提取类关键字
                # ================================
                {
                    "name": "提取JSON数据",
                    "keyword_desc": "使用JSONPath表达式提取响应中的JSON数据",
                    "operation_type_id": 2,
                    "keyword_fun_name": "extract_json_data",
                    "keyword_value": """def extract_json_data(self, **kwargs):
    \"\"\"使用JSONPath表达式提取JSON数据\"\"\"
    expression = kwargs.get("EXPRESSION", None)
    index = int(kwargs.get("INDEX", 0))
    var_name = kwargs.get("VAR_NAME", None)
    
    response = g_context().get_dict("current_response").json()
    extracted_data = jsonpath.jsonpath(response, expression)
    
    if extracted_data and len(extracted_data) > index:
        result = extracted_data[index]
        g_context().set_dict(var_name, result)
        return result
    else:
        raise ValueError(f"JSONPath提取失败: {expression}")""",
                    "is_enabled": "1"
                },
                {
                    "name": "提取正则数据",
                    "keyword_desc": "使用正则表达式提取响应中的数据",
                    "operation_type_id": 2,
                    "keyword_fun_name": "extract_regex_data",
                    "keyword_value": """def extract_regex_data(self, **kwargs):
    \"\"\"使用正则表达式提取数据\"\"\"
    expression = kwargs.get("EXPRESSION", None)
    index = int(kwargs.get("INDEX", 0))
    var_name = kwargs.get("VAR_NAME", None)
    
    response = g_context().get_dict("current_response").text
    matches = re.findall(expression, response)
    
    if matches and len(matches) > index:
        result = matches[index]
        g_context().set_dict(var_name, result)
        return result
    else:
        raise ValueError(f"正则表达式提取失败: {expression}")""",
                    "is_enabled": "1"
                },
                {
                    "name": "提取响应头",
                    "keyword_desc": "提取HTTP响应头信息",
                    "operation_type_id": 2,
                    "keyword_fun_name": "extract_header",
                    "keyword_value": """def extract_header(self, **kwargs):
    \"\"\"提取HTTP响应头信息\"\"\"
    header_name = kwargs.get("HEADER_NAME", None)
    var_name = kwargs.get("VAR_NAME", None)
    
    response = g_context().get_dict("current_response")
    header_value = response.headers.get(header_name)
    
    if header_value:
        g_context().set_dict(var_name, header_value)
        return header_value
    else:
        raise ValueError(f"响应头不存在: {header_name}")""",
                    "is_enabled": "1"
                },
                {
                    "name": "提取Cookie",
                    "keyword_desc": "提取响应中的Cookie信息",
                    "operation_type_id": 2,
                    "keyword_fun_name": "extract_cookie",
                    "keyword_value": """def extract_cookie(self, **kwargs):
    \"\"\"提取Cookie信息\"\"\"
    cookie_name = kwargs.get("COOKIE_NAME", None)
    var_name = kwargs.get("VAR_NAME", None)
    
    response = g_context().get_dict("current_response")
    cookie_value = response.cookies.get(cookie_name)
    
    if cookie_value:
        g_context().set_dict(var_name, cookie_value)
        return cookie_value
    else:
        raise ValueError(f"Cookie不存在: {cookie_name}")""",
                    "is_enabled": "1"
                },
                
                # ================================
                # 断言验证类关键字
                # ================================
                {
                    "name": "断言状态码",
                    "keyword_desc": "验证HTTP响应状态码",
                    "operation_type_id": 3,
                    "keyword_fun_name": "assert_status_code",
                    "keyword_value": """def assert_status_code(self, **kwargs):
    \"\"\"验证HTTP响应状态码\"\"\"
    expected_code = int(kwargs.get("EXPECTED_CODE", 200))
    
    response = g_context().get_dict("current_response")
    actual_code = response.status_code
    
    if actual_code != expected_code:
        raise AssertionError(f"状态码断言失败: 期望{expected_code}, 实际{actual_code}")
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "断言响应时间",
                    "keyword_desc": "验证响应时间是否在预期范围内",
                    "operation_type_id": 3,
                    "keyword_fun_name": "assert_response_time",
                    "keyword_value": """def assert_response_time(self, **kwargs):
    \"\"\"验证响应时间\"\"\"
    max_time = float(kwargs.get("MAX_TIME", 5.0))
    
    response = g_context().get_dict("current_response")
    actual_time = response.elapsed.total_seconds()
    
    if actual_time > max_time:
        raise AssertionError(f"响应时间断言失败: 期望<{max_time}s, 实际{actual_time}s")
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "断言包含文本",
                    "keyword_desc": "验证响应内容包含指定文本",
                    "operation_type_id": 3,
                    "keyword_fun_name": "assert_contains_text",
                    "keyword_value": """def assert_contains_text(self, **kwargs):
    \"\"\"验证响应内容包含指定文本\"\"\"
    expected_text = kwargs.get("EXPECTED_TEXT", None)
    
    response = g_context().get_dict("current_response")
    response_text = response.text
    
    if expected_text not in response_text:
        raise AssertionError(f"文本断言失败: 响应中不包含'{expected_text}'")
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "断言JSON字段",
                    "keyword_desc": "验证JSON响应中指定字段的值",
                    "operation_type_id": 3,
                    "keyword_fun_name": "assert_json_field",
                    "keyword_value": """def assert_json_field(self, **kwargs):
    \"\"\"验证JSON响应中指定字段的值\"\"\"
    json_path = kwargs.get("JSON_PATH", None)
    expected_value = kwargs.get("EXPECTED_VALUE", None)
    
    response = g_context().get_dict("current_response").json()
    actual_values = jsonpath.jsonpath(response, json_path)
    
    if not actual_values:
        raise AssertionError(f"JSON字段断言失败: 路径'{json_path}'不存在")
    
    actual_value = actual_values[0]
    if str(actual_value) != str(expected_value):
        raise AssertionError(f"JSON字段断言失败: 期望'{expected_value}', 实际'{actual_value}'")
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "断言数值比较",
                    "keyword_desc": "比较数值大小关系",
                    "operation_type_id": 3,
                    "keyword_fun_name": "assert_number_compare",
                    "keyword_value": """def assert_number_compare(self, **kwargs):
    \"\"\"比较数值大小关系\"\"\"
    actual_value = float(kwargs.get("ACTUAL_VALUE", 0))
    expected_value = float(kwargs.get("EXPECTED_VALUE", 0))
    operator = kwargs.get("OPERATOR", "==")
    
    operators = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        "==": lambda a, b: a == b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "!=": lambda a, b: a != b,
    }
    
    if operator not in operators:
        raise ValueError(f"不支持的操作符: {operator}")
    
    if not operators[operator](actual_value, expected_value):
        raise AssertionError(f"数值比较断言失败: {actual_value} {operator} {expected_value}")
    return True""",
                    "is_enabled": "1"
                },
                
                # ================================
                # 数据库操作类关键字
                # ================================
                {
                    "name": "执行SQL查询",
                    "keyword_desc": "执行SQL查询并将结果存储到变量",
                    "operation_type_id": 4,
                    "keyword_fun_name": "execute_sql_query",
                    "keyword_value": """def execute_sql_query(self, **kwargs):
    \"\"\"执行SQL查询\"\"\"
    import pymysql
    from pymysql import cursors
    
    db_name = kwargs.get("DB_NAME", None)
    sql = kwargs.get("SQL", None)
    var_names = kwargs.get("VAR_NAMES", [])
    
    config = {"cursorclass": cursors.DictCursor}
    db_config = g_context().get_dict("_database")[db_name]
    config.update(db_config)
    
    con = pymysql.connect(**config)
    cur = con.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    con.close()
    
    # 存储查询结果到变量
    if var_names:
        for i, row in enumerate(results, start=1):
            for j, (key, value) in enumerate(row.items()):
                if j < len(var_names):
                    g_context().set_dict(f"{var_names[j]}_{i}", value)
    
    return results""",
                    "is_enabled": "1"
                },
                {
                    "name": "执行SQL更新",
                    "keyword_desc": "执行SQL更新操作(INSERT/UPDATE/DELETE)",
                    "operation_type_id": 4,
                    "keyword_fun_name": "execute_sql_update",
                    "keyword_value": """def execute_sql_update(self, **kwargs):
    \"\"\"执行SQL更新操作\"\"\"
    import pymysql
    
    db_name = kwargs.get("DB_NAME", None)
    sql = kwargs.get("SQL", None)
    
    db_config = g_context().get_dict("_database")[db_name]
    
    con = pymysql.connect(**db_config)
    cur = con.cursor()
    affected_rows = cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
    
    return affected_rows""",
                    "is_enabled": "1"
                },
                
                # ================================
                # 工具类关键字
                # ================================
                {
                    "name": "等待时间",
                    "keyword_desc": "等待指定的时间(秒)",
                    "operation_type_id": 5,
                    "keyword_fun_name": "wait_time",
                    "keyword_value": """def wait_time(self, **kwargs):
    \"\"\"等待指定的时间\"\"\"
    import time
    
    seconds = float(kwargs.get("SECONDS", 1))
    time.sleep(seconds)
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "生成随机字符串",
                    "keyword_desc": "生成指定长度的随机字符串",
                    "operation_type_id": 5,
                    "keyword_fun_name": "generate_random_string",
                    "keyword_value": """def generate_random_string(self, **kwargs):
    \"\"\"生成随机字符串\"\"\"
    import random
    import string
    
    length = int(kwargs.get("LENGTH", 10))
    var_name = kwargs.get("VAR_NAME", None)
    
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(length))
    
    if var_name:
        g_context().set_dict(var_name, random_str)
    
    return random_str""",
                    "is_enabled": "1"
                },
                {
                    "name": "生成随机数字",
                    "keyword_desc": "生成指定范围的随机数字",
                    "operation_type_id": 5,
                    "keyword_fun_name": "generate_random_number",
                    "keyword_value": """def generate_random_number(self, **kwargs):
    \"\"\"生成随机数字\"\"\"
    import random
    
    min_val = int(kwargs.get("MIN_VALUE", 1))
    max_val = int(kwargs.get("MAX_VALUE", 100))
    var_name = kwargs.get("VAR_NAME", None)
    
    random_num = random.randint(min_val, max_val)
    
    if var_name:
        g_context().set_dict(var_name, random_num)
    
    return random_num""",
                    "is_enabled": "1"
                },
                {
                    "name": "获取当前时间戳",
                    "keyword_desc": "获取当前时间戳(毫秒)",
                    "operation_type_id": 5,
                    "keyword_fun_name": "get_timestamp",
                    "keyword_value": """def get_timestamp(self, **kwargs):
    \"\"\"获取当前时间戳\"\"\"
    import time
    
    var_name = kwargs.get("VAR_NAME", None)
    timestamp = int(time.time() * 1000)
    
    if var_name:
        g_context().set_dict(var_name, timestamp)
    
    return timestamp""",
                    "is_enabled": "1"
                },
                {
                    "name": "格式化时间",
                    "keyword_desc": "格式化当前时间为指定格式",
                    "operation_type_id": 5,
                    "keyword_fun_name": "format_datetime",
                    "keyword_value": """def format_datetime(self, **kwargs):
    \"\"\"格式化当前时间\"\"\"
    from datetime import datetime
    
    format_str = kwargs.get("FORMAT", "%Y-%m-%d %H:%M:%S")
    var_name = kwargs.get("VAR_NAME", None)
    
    formatted_time = datetime.now().strftime(format_str)
    
    if var_name:
        g_context().set_dict(var_name, formatted_time)
    
    return formatted_time""",
                    "is_enabled": "1"
                },
                {
                    "name": "MD5加密",
                    "keyword_desc": "对字符串进行MD5加密",
                    "operation_type_id": 5,
                    "keyword_fun_name": "md5_encrypt",
                    "keyword_value": """def md5_encrypt(self, **kwargs):
    \"\"\"MD5加密\"\"\"
    import hashlib
    
    text = kwargs.get("TEXT", "")
    var_name = kwargs.get("VAR_NAME", None)
    
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    
    if var_name:
        g_context().set_dict(var_name, md5_hash)
    
    return md5_hash""",
                    "is_enabled": "1"
                },
                {
                    "name": "Base64编码",
                    "keyword_desc": "对字符串进行Base64编码",
                    "operation_type_id": 5,
                    "keyword_fun_name": "base64_encode",
                    "keyword_value": """def base64_encode(self, **kwargs):
    \"\"\"Base64编码\"\"\"
    import base64
    
    text = kwargs.get("TEXT", "")
    var_name = kwargs.get("VAR_NAME", None)
    
    encoded = base64.b64encode(text.encode()).decode()
    
    if var_name:
        g_context().set_dict(var_name, encoded)
    
    return encoded""",
                    "is_enabled": "1"
                },
                {
                    "name": "Base64解码",
                    "keyword_desc": "对Base64字符串进行解码",
                    "operation_type_id": 5,
                    "keyword_fun_name": "base64_decode",
                    "keyword_value": """def base64_decode(self, **kwargs):
    \"\"\"Base64解码\"\"\"
    import base64
    
    encoded_text = kwargs.get("ENCODED_TEXT", "")
    var_name = kwargs.get("VAR_NAME", None)
    
    decoded = base64.b64decode(encoded_text).decode()
    
    if var_name:
        g_context().set_dict(var_name, decoded)
    
    return decoded""",
                    "is_enabled": "1"
                },
                
                # ================================
                # 文件操作类关键字
                # ================================
                {
                    "name": "读取文件",
                    "keyword_desc": "读取文件内容",
                    "operation_type_id": 6,
                    "keyword_fun_name": "read_file",
                    "keyword_value": """def read_file(self, **kwargs):
    \"\"\"读取文件内容\"\"\"
    file_path = kwargs.get("FILE_PATH", None)
    encoding = kwargs.get("ENCODING", "utf-8")
    var_name = kwargs.get("VAR_NAME", None)
    
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    
    if var_name:
        g_context().set_dict(var_name, content)
    
    return content""",
                    "is_enabled": "1"
                },
                {
                    "name": "写入文件",
                    "keyword_desc": "写入内容到文件",
                    "operation_type_id": 6,
                    "keyword_fun_name": "write_file",
                    "keyword_value": """def write_file(self, **kwargs):
    \"\"\"写入内容到文件\"\"\"
    file_path = kwargs.get("FILE_PATH", None)
    content = kwargs.get("CONTENT", "")
    encoding = kwargs.get("ENCODING", "utf-8")
    mode = kwargs.get("MODE", "w")
    
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)
    
    return True""",
                    "is_enabled": "1"
                },
                {
                    "name": "删除文件",
                    "keyword_desc": "删除指定文件",
                    "operation_type_id": 6,
                    "keyword_fun_name": "delete_file",
                    "keyword_value": """def delete_file(self, **kwargs):
    \"\"\"删除文件\"\"\"
    import os
    
    file_path = kwargs.get("FILE_PATH", None)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    else:
        raise FileNotFoundError(f"文件不存在: {file_path}")""",
                    "is_enabled": "1"
                }
            ]

            for keyword_data in initial_keywords:
                keyword = ApiKeyWord(**keyword_data, create_time=datetime.now())
                session.add(keyword)
                logger.info(f"创建关键字: {keyword_data['name']}")

            session.commit()
            logger.info(f"初始关键字数据创建完成，共创建{len(initial_keywords)}个关键字")
    except Exception as e:
        logger.error(f"创建初始关键字失败: {e}")
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
        
        # 初始化关键字数据
        logger.info("开始初始化关键字数据...")
        create_initial_keywords()
        
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
        logger.info("关键字功能清单:")
        logger.info("  ✓ 7个HTTP请求关键字 (GET/POST/PUT/DELETE/PATCH等)")
        logger.info("  ✓ 4个数据提取关键字 (JSON/正则/响应头/Cookie)")
        logger.info("  ✓ 5个断言验证关键字 (状态码/响应时间/文本/JSON字段/数值比较)")
        logger.info("  ✓ 2个数据库操作关键字 (查询/更新)")
        logger.info("  ✓ 8个工具类关键字 (等待/随机数/时间/加密/编码等)")
        logger.info("  ✓ 3个文件操作关键字 (读取/写入/删除)")
        logger.info("  ✓ 共计29个内置关键字，覆盖API测试全流程")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_all_data()
