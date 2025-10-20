# -*- coding: utf-8 -*-
"""数据库初始化数据脚本"""

from sqlmodel import Session, select
from core.database import engine
from sysmanage.model.user import User
from sysmanage.model.role import Role
from sysmanage.model.menu import Menu
from sysmanage.model.dept import Dept
from sysmanage.model.user_role import UserRole
from sysmanage.model.role_menu import RoleMenu
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
    """创建初始菜单数据"""
    try:
        with Session(engine) as session:
            initial_menus = [
                # 系统管理
                {"menu_id": 1, "parent_id": 0, "menu_name": "系统管理", "path": "/system", "component": "Layout", "perms": "", "icon": "el-icon-setting", "type": "0", "order_num": 1},
                {"menu_id": 2, "parent_id": 1, "menu_name": "用户管理", "path": "/system/user", "component": "system/user/index", "perms": "system:user:view", "icon": "el-icon-user", "type": "0", "order_num": 1},
                {"menu_id": 3, "parent_id": 1, "menu_name": "角色管理", "path": "/system/role", "component": "system/role/index", "perms": "system:role:view", "icon": "el-icon-s-custom", "type": "0", "order_num": 2},
                {"menu_id": 4, "parent_id": 1, "menu_name": "菜单管理", "path": "/system/menu", "component": "system/menu/index", "perms": "system:menu:view", "icon": "el-icon-menu", "type": "0", "order_num": 3},
                {"menu_id": 5, "parent_id": 1, "menu_name": "部门管理", "path": "/system/dept", "component": "system/dept/index", "perms": "system:dept:view", "icon": "el-icon-office-building", "type": "0", "order_num": 4},
                
                # 用户管理按钮
                {"menu_id": 10, "parent_id": 2, "menu_name": "新增用户", "path": "", "component": "", "perms": "system:user:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 11, "parent_id": 2, "menu_name": "编辑用户", "path": "", "component": "", "perms": "system:user:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 12, "parent_id": 2, "menu_name": "删除用户", "path": "", "component": "", "perms": "system:user:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 13, "parent_id": 2, "menu_name": "分配角色", "path": "", "component": "", "perms": "system:user:role", "icon": "", "type": "1", "order_num": 4},
                
                # 角色管理按钮
                {"menu_id": 20, "parent_id": 3, "menu_name": "新增角色", "path": "", "component": "", "perms": "system:role:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 21, "parent_id": 3, "menu_name": "编辑角色", "path": "", "component": "", "perms": "system:role:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 22, "parent_id": 3, "menu_name": "删除角色", "path": "", "component": "", "perms": "system:role:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 23, "parent_id": 3, "menu_name": "分配权限", "path": "", "component": "", "perms": "system:role:menu", "icon": "", "type": "1", "order_num": 4},
                
                # 菜单管理按钮
                {"menu_id": 30, "parent_id": 4, "menu_name": "新增菜单", "path": "", "component": "", "perms": "system:menu:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 31, "parent_id": 4, "menu_name": "编辑菜单", "path": "", "component": "", "perms": "system:menu:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 32, "parent_id": 4, "menu_name": "删除菜单", "path": "", "component": "", "perms": "system:menu:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 部门管理按钮
                {"menu_id": 40, "parent_id": 5, "menu_name": "新增部门", "path": "", "component": "", "perms": "system:dept:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 41, "parent_id": 5, "menu_name": "编辑部门", "path": "", "component": "", "perms": "system:dept:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 42, "parent_id": 5, "menu_name": "删除部门", "path": "", "component": "", "perms": "system:dept:delete", "icon": "", "type": "1", "order_num": 3},
                
                # API测试
                {"menu_id": 100, "parent_id": 0, "menu_name": "API自动化", "path": "/apitest", "component": "Layout", "perms": "", "icon": "el-icon-promotion", "type": "0", "order_num": 2},
                {"menu_id": 101, "parent_id": 100, "menu_name": "项目管理", "path": "/apitest/project", "component": "apitest/project/index", "perms": "apitest:project:view", "icon": "el-icon-tickets", "type": "0", "order_num": 1},
                {"menu_id": 102, "parent_id": 100, "menu_name": "关键字方法管理", "path": "/apitest/keyword", "component": "apitest/keyword/index", "perms": "apitest:keyword:view", "icon": "el-icon-key", "type": "0", "order_num": 2},
                {"menu_id": 103, "parent_id": 100, "menu_name": "素材维护管理", "path": "/apitest/mate", "component": "apitest/mate/index", "perms": "apitest:mate:view", "icon": "el-icon-document", "type": "0", "order_num": 3},
                
                # 项目管理按·钮权限
                {"menu_id": 110, "parent_id": 101, "menu_name": "新增项目", "path": "", "component": "", "perms": "apitest:project:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 111, "parent_id": 101, "menu_name": "编辑项目", "path": "", "component": "", "perms": "apitest:project:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 112, "parent_id": 101, "menu_name": "删除项目", "path": "", "component": "", "perms": "apitest:project:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 关键字方法管理按钮权限
                {"menu_id": 120, "parent_id": 102, "menu_name": "新增关键字", "path": "", "component": "", "perms": "apitest:keyword:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 121, "parent_id": 102, "menu_name": "编辑关键字", "path": "", "component": "", "perms": "apitest:keyword:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 122, "parent_id": 102, "menu_name": "删除关键字", "path": "", "component": "", "perms": "apitest:keyword:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 素材维护管理按钮权限
                {"menu_id": 130, "parent_id": 103, "menu_name": "新增素材", "path": "", "component": "", "perms": "apitest:mate:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 131, "parent_id": 103, "menu_name": "编辑素材", "path": "", "component": "", "perms": "apitest:mate:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 132, "parent_id": 103, "menu_name": "删除素材", "path": "", "component": "", "perms": "apitest:mate:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 接口信息管理
                {"menu_id": 140, "parent_id": 100, "menu_name": "接口信息管理", "path": "/apitest/apiinfo", "component": "apitest/apiinfo/index", "perms": "apitest:apiinfo:view", "icon": "el-icon-monitor", "type": "0", "order_num": 4},
                {"menu_id": 141, "parent_id": 100, "menu_name": "接口分组管理", "path": "/apitest/apigroup", "component": "apitest/apigroup/index", "perms": "apitest:apigroup:view", "icon": "el-icon-folder", "type": "0", "order_num": 5},
                {"menu_id": 142, "parent_id": 100, "menu_name": "测试历史记录", "path": "/apitest/testhistory", "component": "apitest/testhistory/index", "perms": "apitest:testhistory:view", "icon": "el-icon-document-copy", "type": "0", "order_num": 6},
                
                # 接口信息管理按钮权限
                {"menu_id": 150, "parent_id": 140, "menu_name": "新增接口", "path": "", "component": "", "perms": "apitest:apiinfo:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 151, "parent_id": 140, "menu_name": "编辑接口", "path": "", "component": "", "perms": "apitest:apiinfo:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 152, "parent_id": 140, "menu_name": "删除接口", "path": "", "component": "", "perms": "apitest:apiinfo:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 153, "parent_id": 140, "menu_name": "测试执行", "path": "", "component": "", "perms": "apitest:apiinfo:test", "icon": "", "type": "1", "order_num": 4},
                {"menu_id": 154, "parent_id": 140, "menu_name": "查看详情", "path": "", "component": "", "perms": "apitest:apiinfo:detail", "icon": "", "type": "1", "order_num": 5},
                
                # 接口分组管理按钮权限
                {"menu_id": 160, "parent_id": 141, "menu_name": "新增分组", "path": "", "component": "", "perms": "apitest:apigroup:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 161, "parent_id": 141, "menu_name": "编辑分组", "path": "", "component": "", "perms": "apitest:apigroup:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 162, "parent_id": 141, "menu_name": "删除分组", "path": "", "component": "", "perms": "apitest:apigroup:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 测试历史记录按钮权限
                {"menu_id": 170, "parent_id": 142, "menu_name": "查看报告", "path": "", "component": "", "perms": "apitest:testhistory:report", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 171, "parent_id": 142, "menu_name": "删除记录", "path": "", "component": "", "perms": "apitest:testhistory:delete", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 172, "parent_id": 142, "menu_name": "重新执行", "path": "", "component": "", "perms": "apitest:testhistory:rerun", "icon": "", "type": "1", "order_num": 3},
                
                # AI配置管理（新增）
                {"menu_id": 200, "parent_id": 0, "menu_name": "AI配置", "path": "/ai-config", "component": "Layout", "perms": "", "icon": "el-icon-setting", "type": "0", "order_num": 3},
                {"menu_id": 201, "parent_id": 200, "menu_name": "AI模型管理", "path": "/ai-config/models", "component": "sysmanage/aimodel/index", "perms": "ai:model:view", "icon": "el-icon-cpu", "type": "0", "order_num": 1},
                {"menu_id": 202, "parent_id": 200, "menu_name": "提示词模板管理", "path": "/ai-config/prompts", "component": "sysmanage/prompt/index", "perms": "ai:prompt:view", "icon": "el-icon-edit", "type": "0", "order_num": 2},
                {"menu_id": 180, "parent_id": 200, "menu_name": "AI测试助手", "path": "/ai-config/ai-chat", "component": "apitest/testcase/AiChatInterface", "perms": "ai:chat:view", "icon": "el-icon-chat-dot-round", "type": "0", "order_num": 3},
                {"menu_id": 181, "parent_id": 200, "menu_name": "测试用例管理", "path": "/ai-config/testcase", "component": "apitest/testcase/index", "perms": "ai:testcase:view", "icon": "el-icon-tickets", "type": "0", "order_num": 4},
                
                # AI模型管理按钮权限
                {"menu_id": 210, "parent_id": 201, "menu_name": "新增模型", "path": "", "component": "", "perms": "ai:model:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 211, "parent_id": 201, "menu_name": "编辑模型", "path": "", "component": "", "perms": "ai:model:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 212, "parent_id": 201, "menu_name": "删除模型", "path": "", "component": "", "perms": "ai:model:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 213, "parent_id": 201, "menu_name": "启用禁用", "path": "", "component": "", "perms": "ai:model:toggle", "icon": "", "type": "1", "order_num": 4},
                {"menu_id": 214, "parent_id": 201, "menu_name": "测试连接", "path": "", "component": "", "perms": "ai:model:test", "icon": "", "type": "1", "order_num": 5},
                
                # 提示词模板管理按钮权限
                {"menu_id": 220, "parent_id": 202, "menu_name": "新增模板", "path": "", "component": "", "perms": "ai:prompt:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 221, "parent_id": 202, "menu_name": "编辑模板", "path": "", "component": "", "perms": "ai:prompt:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 222, "parent_id": 202, "menu_name": "删除模板", "path": "", "component": "", "perms": "ai:prompt:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 223, "parent_id": 202, "menu_name": "激活停用", "path": "", "component": "", "perms": "ai:prompt:toggle", "icon": "", "type": "1", "order_num": 4},
            ]

            for menu_data in initial_menus:
                # 将menu_id映射到id字段，确保使用指定的主键ID
                menu_id = menu_data.pop("menu_id")
                existing = session.get(Menu, menu_id)
                if not existing:
                    menu = Menu(id=menu_id, **menu_data, create_time=datetime.now(), modify_time=datetime.now())
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
            all_menu_ids = [menu.id for menu in all_menus]  # 修复：使用menu.id而不是menu.menu_id
            
            # 超级管理员拥有所有权限
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
            
            # 普通用户只有查看权限
            basic_menu_ids = [100, 101, 102, 103] # API测试相关菜单
            for menu_id in basic_menu_ids:
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

def init_all_data():
    """初始化所有数据"""
    try:
        logger.info("开始初始化RBAC数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过RBAC初始化")
            # 但仍然尝试初始化AI数据（如果未初始化）
            from core.init_ai_data import init_all_ai_data
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
        from core.init_ai_data import init_all_ai_data
        with Session(engine) as session:
            init_all_ai_data(session)
        
        logger.info("RBAC数据初始化完成！")
        logger.info("=" * 60)
        logger.info("默认登录账号:")
        logger.info("admin / admin123 (超级管理员)")
        logger.info("")
        logger.info("RBAC功能清单:")
        logger.info("✓ 4个部门 (总公司、技术部、产品部、运营部)")
        logger.info("✓ 3个角色 (超级管理员、管理员、普通用户)")
        logger.info("✓ 完整菜单权限体系 (系统管理 + API测试 + AI配置)")
        logger.info("✓ 用户-角色-菜单权限关联")
        logger.info("✓ 10个AI模型（需配置API Key）")
        logger.info("✓ 4个提示词模板（API/Web/App/通用）")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_all_data()
