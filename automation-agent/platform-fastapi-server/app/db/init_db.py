"""
数据库初始化模块
负责在应用启动时自动创建表和初始化数据
所有初始化数据直接硬编码在此文件中
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models import Base
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.api_resource import ApiResource
from app.models.dept import Dept
from app.models.audit_log import AuditLog
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu
from app.models.role_api import RoleApi
from app.models.dept_closure import DeptClosure
from app.core.logger import logger


# ========== 初始化数据定义 ==========

# 角色初始化数据
INIT_ROLES = [
    {
        "name": "超级管理员",
        "desc": "系统超级管理员，拥有所有权限"
    },
    {
        "name": "管理员",
        "desc": "系统管理员，拥有大部分管理权限"
    },
    {
        "name": "测试工程师",
        "desc": "测试工程师，可以执行测试和管理用例"
    },
    {
        "name": "开发人员",
        "desc": "开发人员，可以查看项目信息和接口文档"
    },
    {
        "name": "普通用户",
        "desc": "普通用户，只有基本查看权限"
    }
]

# 菜单初始化数据（与前端实际路由/组件对齐）
INIT_MENUS = [
    {
        "name": "首页",
        "menu_type": "menu",
        "icon": "HomeFilled",
        "path": "/home",
        "component": "home/home",
        "order": 1,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "数据统计",
        "menu_type": "menu",
        "icon": "DataAnalysis",
        "path": "/Statistics",
        "component": "statistics/statistics",
        "order": 2,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "API测试",
        "menu_type": "catalog",
        "icon": "Connection",
        "path": "/apitest",
        "order": 3,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": False
    },
    {
        "name": "项目管理",
        "menu_type": "menu",
        "icon": "Collection",
        "path": "/ApiProjectList",
        "component": "apitest/project/ApiProjectList",
        "order": 1,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "用例管理",
        "menu_type": "menu",
        "icon": "List",
        "path": "/ApiInfoCaseList",
        "component": "apitest/apiinfocase/ApiInfoCaseList",
        "order": 2,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "接口信息",
        "menu_type": "menu",
        "icon": "Document",
        "path": "/ApiInfoList",
        "component": "apitest/apiinfo/ApiInfoList",
        "order": 3,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "关键字管理",
        "menu_type": "menu",
        "icon": "Key",
        "path": "/ApikeywordList",
        "component": "apitest/keyword/ApiKeyWordList",
        "order": 4,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "素材维护",
        "menu_type": "menu",
        "icon": "Box",
        "path": "/ApiMateManageList",
        "component": "apitest/apiMate/ApiMateManageList",
        "order": 5,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "测试计划",
        "menu_type": "menu",
        "icon": "TrendCharts",
        "path": "/ApiCollectionInfoList",
        "component": "apitest/collection/ApiCollectionInfoList",
        "order": 6,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "消息配置",
        "menu_type": "catalog",
        "icon": "Message",
        "path": "/msgmanage",
        "order": 7,
        "parent_id": "API测试",
        "is_hidden": False,
        "keepalive": False
    },
    {
        "name": "企业微信",
        "menu_type": "menu",
        "icon": "ChatDotSquare",
        "path": "/WeChartMsgManageList",
        "component": "apitest/msgmanage/WeChartMsgManageList",
        "order": 1,
        "parent_id": "消息配置",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "钉钉",
        "menu_type": "menu",
        "icon": "Bell",
        "path": "/DingDingMsgManageList",
        "component": "apitest/msgmanage/DingDingMsgManageList",
        "order": 2,
        "parent_id": "消息配置",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "飞书",
        "menu_type": "menu",
        "icon": "MessageBox",
        "path": "/FeiShuMsgManageList",
        "component": "apitest/msgmanage/FeiShuMsgManageList",
        "order": 3,
        "parent_id": "消息配置",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "系统管理",
        "menu_type": "catalog",
        "icon": "Setting",
        "path": "/system",
        "order": 8,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": False
    },
    {
        "name": "用户管理",
        "menu_type": "menu",
        "icon": "User",
        "path": "/userList",
        "component": "users/userList",
        "order": 1,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "角色管理",
        "menu_type": "menu",
        "icon": "UserFilled",
        "path": "/roleList",
        "component": "roles/roleList",
        "order": 2,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "菜单管理",
        "menu_type": "menu",
        "icon": "Menu",
        "path": "/menuList",
        "component": "menus/menuList",
        "order": 3,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "部门管理",
        "menu_type": "menu",
        "icon": "OfficeBuilding",
        "path": "/deptList",
        "component": "depts/deptList",
        "order": 4,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "API资源",
        "menu_type": "menu",
        "icon": "Cpu",
        "path": "/apiList",
        "component": "apis/apiList",
        "order": 5,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "审计日志",
        "menu_type": "menu",
        "icon": "Document",
        "path": "/auditLogList",
        "component": "auditlogs/auditLogList",
        "order": 6,
        "parent_id": "系统管理",
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "个人中心",
        "menu_type": "menu",
        "icon": "User",
        "path": "/profile",
        "component": "profile/profile",
        "order": 9,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "系统设置",
        "menu_type": "menu",
        "icon": "Tools",
        "path": "/settings",
        "component": "settings/settings",
        "order": 10,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": True
    },
    {
        "name": "关于",
        "menu_type": "menu",
        "icon": "InfoFilled",
        "path": "/about",
        "component": "about",
        "order": 11,
        "parent_id": 0,
        "is_hidden": False,
        "keepalive": True
    }
]

# API资源初始化数据
INIT_API_RESOURCES = [
    {
        "path": "/api/v1/login",
        "method": "POST",
        "summary": "用户登录",
        "tags": "认证"
    },
    {
        "path": "/api/v1/logout",
        "method": "POST",
        "summary": "用户登出",
        "tags": "认证"
    },
    {
        "path": "/api/v1/users",
        "method": "GET",
        "summary": "获取用户列表",
        "tags": "用户管理"
    },
    {
        "path": "/api/v1/users",
        "method": "POST",
        "summary": "创建用户",
        "tags": "用户管理"
    },
    {
        "path": "/api/v1/users/{user_id}",
        "method": "GET",
        "summary": "获取用户详情",
        "tags": "用户管理"
    },
    {
        "path": "/api/v1/users/{user_id}",
        "method": "PUT",
        "summary": "更新用户",
        "tags": "用户管理"
    },
    {
        "path": "/api/v1/users/{user_id}",
        "method": "DELETE",
        "summary": "删除用户",
        "tags": "用户管理"
    },
    {
        "path": "/api/v1/roles",
        "method": "GET",
        "summary": "获取角色列表",
        "tags": "角色管理"
    },
    {
        "path": "/api/v1/roles",
        "method": "POST",
        "summary": "创建角色",
        "tags": "角色管理"
    },
    {
        "path": "/api/v1/roles/{role_id}",
        "method": "GET",
        "summary": "获取角色详情",
        "tags": "角色管理"
    },
    {
        "path": "/api/v1/roles/{role_id}",
        "method": "PUT",
        "summary": "更新角色",
        "tags": "角色管理"
    },
    {
        "path": "/api/v1/roles/{role_id}",
        "method": "DELETE",
        "summary": "删除角色",
        "tags": "角色管理"
    },
    {
        "path": "/api/v1/menus",
        "method": "GET",
        "summary": "获取菜单列表",
        "tags": "菜单管理"
    },
    {
        "path": "/api/v1/menus",
        "method": "POST",
        "summary": "创建菜单",
        "tags": "菜单管理"
    },
    {
        "path": "/api/v1/menus/{menu_id}",
        "method": "GET",
        "summary": "获取菜单详情",
        "tags": "菜单管理"
    },
    {
        "path": "/api/v1/menus/{menu_id}",
        "method": "PUT",
        "summary": "更新菜单",
        "tags": "菜单管理"
    },
    {
        "path": "/api/v1/menus/{menu_id}",
        "method": "DELETE",
        "summary": "删除菜单",
        "tags": "菜单管理"
    },
    {
        "path": "/api/v1/depts",
        "method": "GET",
        "summary": "获取部门列表",
        "tags": "部门管理"
    },
    {
        "path": "/api/v1/depts",
        "method": "POST",
        "summary": "创建部门",
        "tags": "部门管理"
    },
    {
        "path": "/api/v1/depts/{dept_id}",
        "method": "GET",
        "summary": "获取部门详情",
        "tags": "部门管理"
    },
    {
        "path": "/api/v1/depts/{dept_id}",
        "method": "PUT",
        "summary": "更新部门",
        "tags": "部门管理"
    },
    {
        "path": "/api/v1/depts/{dept_id}",
        "method": "DELETE",
        "summary": "删除部门",
        "tags": "部门管理"
    },
    {
        "path": "/api/v1/ApiProject",
        "method": "GET",
        "summary": "获取项目列表",
        "tags": "项目管理"
    },
    {
        "path": "/api/v1/ApiProject",
        "method": "POST",
        "summary": "创建项目",
        "tags": "项目管理"
    },
    {
        "path": "/api/v1/ApiProject/{project_id}",
        "method": "GET",
        "summary": "获取项目详情",
        "tags": "项目管理"
    },
    {
        "path": "/api/v1/ApiProject/{project_id}",
        "method": "PUT",
        "summary": "更新项目",
        "tags": "项目管理"
    },
    {
        "path": "/api/v1/ApiProject/{project_id}",
        "method": "DELETE",
        "summary": "删除项目",
        "tags": "项目管理"
    },
    {
        "path": "/api/v1/api",
        "method": "GET",
        "summary": "获取API列表",
        "tags": "API管理"
    },
    {
        "path": "/api/v1/api",
        "method": "POST",
        "summary": "创建API",
        "tags": "API管理"
    },
    {
        "path": "/api/v1/api/{api_id}",
        "method": "GET",
        "summary": "获取API详情",
        "tags": "API管理"
    },
    {
        "path": "/api/v1/api/{api_id}",
        "method": "PUT",
        "summary": "更新API",
        "tags": "API管理"
    },
    {
        "path": "/api/v1/api/{api_id}",
        "method": "DELETE",
        "summary": "删除API",
        "tags": "API管理"
    },
    {
        "path": "/api/v1/ApiInfoCase",
        "method": "GET",
        "summary": "获取用例列表",
        "tags": "用例管理"
    },
    {
        "path": "/api/v1/ApiInfoCase",
        "method": "POST",
        "summary": "创建用例",
        "tags": "用例管理"
    },
    {
        "path": "/api/v1/ApiInfoCase/{case_id}",
        "method": "GET",
        "summary": "获取用例详情",
        "tags": "用例管理"
    },
    {
        "path": "/api/v1/ApiInfoCase/{case_id}",
        "method": "PUT",
        "summary": "更新用例",
        "tags": "用例管理"
    },
    {
        "path": "/api/v1/ApiInfoCase/{case_id}",
        "method": "DELETE",
        "summary": "删除用例",
        "tags": "用例管理"
    },
    {
        "path": "/api/v1/ApiKeyWord",
        "method": "GET",
        "summary": "获取关键字列表",
        "tags": "关键字管理"
    },
    {
        "path": "/api/v1/ApiKeyWord",
        "method": "POST",
        "summary": "创建关键字",
        "tags": "关键字管理"
    },
    {
        "path": "/api/v1/ApiKeyWord/{keyword_id}",
        "method": "GET",
        "summary": "获取关键字详情",
        "tags": "关键字管理"
    },
    {
        "path": "/api/v1/ApiKeyWord/{keyword_id}",
        "method": "PUT",
        "summary": "更新关键字",
        "tags": "关键字管理"
    },
    {
        "path": "/api/v1/ApiKeyWord/{keyword_id}",
        "method": "DELETE",
        "summary": "删除关键字",
        "tags": "关键字管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo",
        "method": "GET",
        "summary": "获取集合列表",
        "tags": "集合管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo",
        "method": "POST",
        "summary": "创建集合",
        "tags": "集合管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo/{collection_id}",
        "method": "GET",
        "summary": "获取集合详情",
        "tags": "集合管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo/{collection_id}",
        "method": "PUT",
        "summary": "更新集合",
        "tags": "集合管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo/{collection_id}",
        "method": "DELETE",
        "summary": "删除集合",
        "tags": "集合管理"
    },
    {
        "path": "/api/v1/ApiCollectionInfo/{collection_id}/execute",
        "method": "POST",
        "summary": "执行集合测试",
        "tags": "测试执行"
    },
    {
        "path": "/api/v1/auditlog",
        "method": "GET",
        "summary": "获取审计日志",
        "tags": "审计日志"
    }
]

# 部门初始化数据
INIT_DEPTS = [
    {
        "name": "总公司",
        "desc": "总公司",
        "order": 1,
        "children": [
            {
                "name": "技术部",
                "desc": "技术研发部门，负责产品开发和架构设计",
                "order": 1,
                "children": [
                    {
                        "name": "前端开发组",
                        "desc": "前端界面开发",
                        "order": 1
                    },
                    {
                        "name": "后端开发组",
                        "desc": "后端服务开发",
                        "order": 2
                    },
                    {
                        "name": "移动开发组",
                        "desc": "移动应用开发",
                        "order": 3
                    }
                ]
            },
            {
                "name": "测试部",
                "desc": "质量保证部门，负责产品测试和质量控制",
                "order": 2,
                "children": [
                    {
                        "name": "功能测试组",
                        "desc": "功能测试和验收测试",
                        "order": 1
                    },
                    {
                        "name": "性能测试组",
                        "desc": "性能测试和压力测试",
                        "order": 2
                    },
                    {
                        "name": "自动化测试组",
                        "desc": "自动化测试和持续集成",
                        "order": 3
                    }
                ]
            },
            {
                "name": "运维部",
                "desc": "运维部门，负责系统部署和维护",
                "order": 3,
                "children": [
                    {
                        "name": "系统运维组",
                        "desc": "系统监控和维护",
                        "order": 1
                    },
                    {
                        "name": "网络运维组",
                        "desc": "网络管理和安全",
                        "order": 2
                    },
                    {
                        "name": "数据库运维组",
                        "desc": "数据库管理和优化",
                        "order": 3
                    }
                ]
            },
            {
                "name": "产品部",
                "desc": "产品设计和管理部门",
                "order": 4,
                "children": [
                    {
                        "name": "产品设计组",
                        "desc": "产品规划和设计",
                        "order": 1
                    },
                    {
                        "name": "用户体验组",
                        "desc": "用户体验研究和优化",
                        "order": 2
                    }
                ]
            },
            {
                "name": "市场部",
                "desc": "市场营销和推广部门",
                "order": 5,
                "children": [
                    {
                        "name": "市场推广组",
                        "desc": "市场推广和品牌建设",
                        "order": 1
                    },
                    {
                        "name": "客户服务组",
                        "desc": "客户服务和支持",
                        "order": 2
                    }
                ]
            }
        ]
    }
]

# 用户初始化数据
INIT_USERS = [
    {
        "username": "admin",
        "alias": "系统管理员",
        "password": "admin123",
        "email": "admin@example.com",
        "phone": "13800138000",
        "is_active": True,
        "is_superuser": True,
        "dept_name": "总公司"
    },
    {
        "username": "manager",
        "alias": "部门经理",
        "password": "manager123",
        "email": "manager@example.com",
        "phone": "13800138001",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "技术部"
    },
    {
        "username": "tester",
        "alias": "测试工程师",
        "password": "tester123",
        "email": "tester@example.com",
        "phone": "13800138002",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "测试部"
    },
    {
        "username": "developer",
        "alias": "开发工程师",
        "password": "dev123",
        "email": "developer@example.com",
        "phone": "13800138003",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "技术部"
    },
    {
        "username": "operator",
        "alias": "运维工程师",
        "password": "ops123",
        "email": "operator@example.com",
        "phone": "13800138004",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "运维部"
    },
    {
        "username": "product",
        "alias": "产品经理",
        "password": "product123",
        "email": "product@example.com",
        "phone": "13800138005",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "产品部"
    },
    {
        "username": "user",
        "alias": "普通用户",
        "password": "user123",
        "email": "user@example.com",
        "phone": "13800138006",
        "is_active": True,
        "is_superuser": False,
        "dept_name": "市场部"
    }
]

# 用户角色关联初始化数据
INIT_USER_ROLES = [
    {
        "username": "admin",
        "role_name": "超级管理员"
    },
    {
        "username": "manager",
        "role_name": "管理员"
    },
    {
        "username": "tester",
        "role_name": "测试工程师"
    },
    {
        "username": "developer",
        "role_name": "开发人员"
    },
    {
        "username": "operator",
        "role_name": "管理员"
    },
    {
        "username": "product",
        "role_name": "管理员"
    },
    {
        "username": "user",
        "role_name": "普通用户"
    }
]

# 角色菜单关联初始化数据
INIT_ROLE_MENUS = [
    {
        "role_name": "超级管理员",
        "all_menus": True
    },
    {
        "role_name": "管理员",
        "menu_names": [
            "首页",
            "数据统计",
            "API测试",
            "项目管理",
            "用例管理",
            "接口信息",
            "关键字管理",
            "素材维护",
            "测试计划",
            "消息配置",
            "企业微信",
            "钉钉",
            "飞书",
            "系统管理",
            "用户管理",
            "角色管理",
            "菜单管理",
            "部门管理",
            "API资源",
            "审计日志",
            "个人中心",
            "系统设置",
            "关于"
        ]
    },
    {
        "role_name": "测试工程师",
        "menu_names": [
            "首页",
            "数据统计",
            "API测试",
            "项目管理",
            "用例管理",
            "接口信息",
            "关键字管理",
            "素材维护",
            "测试计划",
            "消息配置",
            "企业微信",
            "钉钉",
            "飞书",
            "个人中心",
            "关于"
        ]
    },
    {
        "role_name": "开发人员",
        "menu_names": [
            "首页",
            "数据统计",
            "API测试",
            "项目管理",
            "接口信息",
            "测试计划",
            "个人中心",
            "关于"
        ]
    },
    {
        "role_name": "普通用户",
        "menu_names": [
            "首页",
            "数据统计",
            "个人中心",
            "关于"
        ]
    }
]

# 角色API关联初始化数据
INIT_ROLE_APIS = [
    {
        "role_name": "超级管理员",
        "all_apis": True
    },
    {
        "role_name": "管理员",
        "all_apis": True
    },
    {
        "role_name": "测试工程师",
        "api_filter": "api"
    },
    {
        "role_name": "开发人员",
        "api_filter": "project"
    },
    {
        "role_name": "普通用户",
        "api_filter": "dashboard"
    }
]


# ========== 数据库初始化函数 ==========

async def create_tables():
    """
    创建所有数据库表
    """
    from app.db.session import engine, create_database_engine

    # 确保引擎已初始化
    if engine is None:
        await create_database_engine()

    from app.core.logger import logger
    logger.info("正在创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表创建完成")


async def init_roles():
    """
    初始化角色数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal, create_database_engine

    # 确保 AsyncSessionLocal 已初始化
    if AsyncSessionLocal is None:
        await create_database_engine()

    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Role))
        if result.scalars().first():
            logger.info("角色数据已存在，跳过初始化")
            return
        
        logger.info("正在初始化角色数据...")
        
        roles = [
            Role(name=role["name"], desc=role["desc"], created_at=datetime.now(), updated_at=datetime.now())
            for role in INIT_ROLES
        ]
        
        session.add_all(roles)
        await session.commit()
        logger.info(f"角色数据初始化完成，共 {len(roles)} 条")


async def init_menus():
    """
    初始化菜单数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Menu))
        if result.scalars().first():
            logger.info("菜单数据已存在，跳过初始化")
            return
        
        logger.info("正在初始化菜单数据...")
        
        # 建立名称到ID的映射（用于parent_id解析）
        menu_id_map = {}
        menus_to_add = []
        
        # 第一遍：创建所有菜单（不处理parent_id）
        for menu_data in INIT_MENUS:
            menu = Menu(
                name=menu_data["name"],
                menu_type=menu_data.get("menu_type", "menu"),
                icon=menu_data.get("icon", ""),
                path=menu_data.get("path", ""),
                component=menu_data.get("component"),
                order=menu_data.get("order", 0),
                parent_id=0,  # 先设为0，后面再更新
                is_hidden=menu_data.get("is_hidden", False),
                keepalive=menu_data.get("keepalive", True),
                redirect=menu_data.get("redirect"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            menus_to_add.append(menu)
        
        # 批量添加并刷新以获取ID
        session.add_all(menus_to_add)
        await session.flush()
        
        # 建立名称到ID的映射
        for menu in menus_to_add:
            menu_id_map[menu.name] = menu.id
        
        # 第二遍：更新parent_id
        for i, menu_data in enumerate(INIT_MENUS):
            parent_name = menu_data.get("parent_id")
            if parent_name and isinstance(parent_name, str) and parent_name != 0:
                parent_id = menu_id_map.get(parent_name, 0)
                menus_to_add[i].parent_id = parent_id
        
        await session.commit()
        logger.info(f"菜单数据初始化完成，共 {len(menus_to_add)} 条")


async def init_api_resources():
    """
    初始化API资源数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(ApiResource))
        if result.scalars().first():
            logger.info("API资源数据已存在，跳过初始化")
            return
        
        logger.info("正在初始化API资源数据...")
        
        api_resources = [
            ApiResource(
                path=api["path"],
                method=api["method"],
                summary=api["summary"],
                tags=api["tags"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for api in INIT_API_RESOURCES
        ]
        
        session.add_all(api_resources)
        await session.commit()
        logger.info(f"API资源数据初始化完成，共 {len(api_resources)} 条")


async def init_depts():
    """
    初始化部门数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Dept))
        if result.scalars().first():
            logger.info("部门数据已存在，跳过初始化")
            return

        logger.info("正在初始化部门数据...")

        # 建立名称到对象的映射
        dept_map = {}
        all_depts = []

        def collect_all_depts(dept_list, parent_name=None):
            """递归收集所有部门数据"""
            for dept_data in dept_list:
                dept = Dept(
                    name=dept_data["name"],
                    desc=dept_data.get("desc", ""),
                    parent_id=0,  # 暂时设为0，后面更新
                    order=dept_data.get("order", 0),
                    is_deleted=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                all_depts.append(dept)
                dept_map[dept_data["name"]] = {
                    "obj": dept,
                    "parent_name": parent_name
                }

                # 递归处理子部门
                children = dept_data.get("children", [])
                if children:
                    collect_all_depts(children, dept_data["name"])

        # 收集所有部门（包括子部门）
        collect_all_depts(INIT_DEPTS, None)

        # 批量添加并刷新以获取ID
        session.add_all(all_depts)
        await session.flush()

        # 更新parent_id
        for dept_name, dept_info in dept_map.items():
            dept_obj = dept_info["obj"]
            parent_name = dept_info["parent_name"]
            if parent_name and parent_name in dept_map:
                dept_obj.parent_id = dept_map[parent_name]["obj"].id

        await session.commit()

        # 初始化部门闭包表
        logger.info("正在初始化部门闭包表...")
        closures = []

        # 为每个部门插入自身记录（level=0）
        for dept in all_depts:
            closures.append(DeptClosure(ancestor=dept.id, descendant=dept.id, level=0))

        # 为每个非根部门插入父部门关系
        for dept in all_depts:
            if dept.parent_id != 0:
                # 查找所有祖先
                current_dept = dept
                level = 0
                while current_dept.parent_id != 0:
                    level += 1
                    # 查找父部门对象
                    for pd in all_depts:
                        if pd.id == current_dept.parent_id:
                            closures.append(DeptClosure(ancestor=pd.id, descendant=dept.id, level=level))
                            current_dept = pd
                            break

        session.add_all(closures)
        await session.commit()
        logger.info(f"部门数据和闭包表初始化完成，共 {len(all_depts)} 个部门")


async def init_users():
    """
    初始化用户数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.core.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化（检查是否有admin用户）
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalars().first():
            logger.info("用户数据已存在，跳过初始化")
            return
        
        logger.info("正在初始化用户数据...")
        
        # 查询所有部门以建立名称映射
        dept_result = await session.execute(select(Dept))
        all_depts = {dept.name: dept.id for dept in dept_result.scalars().all()}
        
        # 创建用户
        users = []
        for user_data in INIT_USERS:
            username = user_data["username"]
            password = user_data.get("password", "admin123")
            dept_name = user_data.get("dept_name")
            
            # 获取部门ID
            dept_id = all_depts.get(dept_name)
            if not dept_id:
                # 如果找不到指定部门，使用第一个部门
                dept_result = await session.execute(select(Dept).limit(1))
                first_dept = dept_result.scalars().first()
                dept_id = first_dept.id if first_dept else None
            
            user = User(
                username=username,
                alias=user_data.get("alias", username),
                password=get_password_hash(password),
                email=user_data.get("email", f"{username}@example.com"),
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
                dept_id=dept_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            users.append(user)
        
        session.add_all(users)
        await session.commit()
        logger.info(f"用户数据初始化完成，共 {len(users)} 个用户")


async def init_user_roles():
    """
    初始化用户角色关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(UserRole))
        if result.scalars().first():
            logger.info("用户角色关联已存在，跳过初始化")
            return
        
        logger.info("正在初始化用户角色关联...")
        
        # 建立名称到ID的映射
        user_result = await session.execute(select(User))
        user_map = {user.username: user.id for user in user_result.scalars().all()}
        
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        # 创建关联
        user_roles = []
        for ur_data in INIT_USER_ROLES:
            username = ur_data["username"]
            role_name = ur_data["role_name"]
            
            user_id = user_map.get(username)
            role_id = role_map.get(role_name)
            
            if user_id and role_id:
                user_roles.append(
                    UserRole(user_id=user_id, role_id=role_id, created_at=datetime.now())
                )
        
        session.add_all(user_roles)
        await session.commit()
        logger.info(f"用户角色关联初始化完成，共 {len(user_roles)} 条")


async def init_role_menus():
    """
    初始化角色菜单关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(RoleMenu))
        if result.scalars().first():
            logger.info("角色菜单关联已存在，跳过初始化")
            return
        
        logger.info("正在初始化角色菜单关联...")
        
        # 建立名称到ID的映射
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        menu_result = await session.execute(select(Menu))
        menu_map = {menu.name: menu.id for menu in menu_result.scalars().all()}
        
        # 创建关联
        role_menus = []
        for rm_data in INIT_ROLE_MENUS:
            role_name = rm_data["role_name"]
            role_id = role_map.get(role_name)
            
            if not role_id:
                continue
            
            all_menus_flag = rm_data.get("all_menus", False)
            
            if all_menus_flag:
                # 角色拥有所有菜单权限
                for menu_id in menu_map.values():
                    role_menus.append(
                        RoleMenu(role_id=role_id, menu_id=menu_id, created_at=datetime.now())
                    )
            else:
                # 角色拥有指定菜单
                menu_names = rm_data.get("menu_names", [])
                for menu_name in menu_names:
                    menu_id = menu_map.get(menu_name)
                    if menu_id:
                        role_menus.append(
                            RoleMenu(role_id=role_id, menu_id=menu_id, created_at=datetime.now())
                        )
        
        session.add_all(role_menus)
        await session.commit()
        logger.info(f"角色菜单关联初始化完成，共 {len(role_menus)} 条")


async def init_role_apis():
    """
    初始化角色API关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(RoleApi))
        if result.scalars().first():
            logger.info("角色API关联已存在，跳过初始化")
            return
        
        logger.info("正在初始化角色API关联...")
        
        # 建立名称到ID的映射
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        api_result = await session.execute(select(ApiResource))
        api_map = {api.path: api.id for api in api_result.scalars().all()}
        
        # 创建关联
        role_apis = []
        for ra_data in INIT_ROLE_APIS:
            role_name = ra_data["role_name"]
            role_id = role_map.get(role_name)
            
            if not role_id:
                continue
            
            all_apis_flag = ra_data.get("all_apis", False)
            
            if all_apis_flag:
                # 角色拥有所有API权限
                for api_id in api_map.values():
                    role_apis.append(
                        RoleApi(role_id=role_id, api_id=api_id, created_at=datetime.now())
                    )
            else:
                # 角色拥有指定API权限
                api_filter = ra_data.get("api_filter", "")
                if api_filter:
                    for api_path, api_id in api_map.items():
                        if api_filter in api_path.lower():
                            role_apis.append(
                                RoleApi(role_id=role_id, api_id=api_id, created_at=datetime.now())
                            )
        
        session.add_all(role_apis)
        await session.commit()
        logger.info(f"角色API关联初始化完成，共 {len(role_apis)} 条")


async def init_database():
    """
    初始化数据库（创建表和初始化数据）
    这是应用启动时调用的主函数
    """
    logger.info("开始初始化数据库...")
    
    try:
        # 1. 创建所有表
        await create_tables()
        
        # 2. 初始化基础数据
        await init_roles()
        await init_menus()
        await init_api_resources()
        await init_depts()
        
        # 3. 初始化用户数据
        await init_users()
        
        # 4. 初始化关联数据
        await init_user_roles()
        await init_role_menus()
        await init_role_apis()
        
        logger.info("数据库初始化完成！")
        
        # 显示登录信息
        logger.info("默认登录账号:")
        for user_data in INIT_USERS:
            password = user_data.get("password", "admin123")
            alias = user_data.get("alias", user_data["username"])
            logger.info(f"{alias}: {user_data['username']} / {password}")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


async def reset_database():
    """
    重置数据库（删除所有表并重新创建）
    警告：此操作会删除所有数据！
    """
    from sqlalchemy import text
    from app.db.session import engine, create_database_engine

    # 确保引擎已初始化
    if engine is None:
        await create_database_engine()

    logger.warning("警告：正在重置数据库，所有数据将被删除！")

    async with engine.begin() as conn:
        # 删除所有表
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("数据库表已删除")
        
        # 重新创建表
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表已重新创建")
    
    # 重新初始化数据
    await init_database()
