# -*- coding: utf-8 -*-
"""
数据库初始化数据脚本

注意：菜单数据从前端静态菜单配置同步到数据库，用于权限控制
"""

import logging
from datetime import datetime

from sqlmodel import Session, select
from app.models.DeptModel import Dept
from app.models.RoleModel import Role
from app.models.UserModel import User
from app.models.UserRoleModel import UserRole
from app.models.MenuModel import Menu
from app.models.RoleMenuModel import RoleMenu

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

def load_static_menu_config():
    """
    读取前端静态菜单配置文件
    使用 Node.js 解析 JavaScript 文件
    """
    try:
        from pathlib import Path
        import json
        import subprocess
        
        # 计算前端静态菜单配置文件路径
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        menu_config_file = project_root / "platform-vue-web" / "src" / "config" / "staticMenus.js"
        
        if not menu_config_file.exists():
            logger.warning(f"静态菜单配置文件不存在: {menu_config_file}")
            return None
        
        # 创建临时 Node.js 脚本来解析 JavaScript
        temp_script = project_root / "platform-fastapi-server" / "temp_parse_menu.js"
        temp_script.write_text(f"""
const fs = require('fs');
const path = require('path');

// 动态导入 ES 模块
(async () => {{
    try {{
        const menuPath = path.resolve('{menu_config_file.as_posix()}');
        const {{ staticMenus }} = await import('file://' + menuPath);
        console.log(JSON.stringify(staticMenus, null, 2));
    }} catch (error) {{
        console.error('Error:', error.message);
        process.exit(1);
    }}
}})();
""", encoding='utf-8')
        
        try:
            # 执行 Node.js 脚本
            result = subprocess.run(
                ['node', str(temp_script)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Node.js 执行失败: {result.stderr}")
                return None
            
            # 解析 JSON 输出
            menus = json.loads(result.stdout)
            logger.info(f"成功加载静态菜单配置，共 {len(menus)} 个顶级菜单")
            return menus
        finally:
            # 清理临时文件
            if temp_script.exists():
                temp_script.unlink()
        
    except FileNotFoundError:
        logger.error("未找到 Node.js，请确保已安装 Node.js")
        return None
    except Exception as e:
        logger.error(f"加载静态菜单配置失败: {e}", exc_info=True)
        return None

def convert_frontend_menu_to_db(menu, parent_id=0, order_num=1, id_counter={'value': 1}):
    """
    将前端菜单配置转换为数据库菜单格式
    
    参数:
        menu: 前端菜单对象
        parent_id: 父菜单ID
        order_num: 排序号
        id_counter: ID计数器（使用字典以支持递归修改）
    
    返回:
        菜单数据字典列表
    """
    menus = []
    
    # 生成当前菜单ID
    current_id = id_counter['value']
    id_counter['value'] += 1
    
    # 判断菜单类型
    has_children = 'child' in menu and menu['child'] and len(menu['child']) > 0
    has_path = 'frontpath' in menu and menu['frontpath'] and menu['frontpath'] != ''
    
    if has_children:
        menu_type = "M"  # 目录
    elif has_path:
        menu_type = "C"  # 菜单
    else:
        menu_type = "F"  # 按钮
    
    # 生成权限标识
    menu_name = menu.get('name', '')
    if has_path and menu.get('frontpath', '').startswith('/'):
        # 从路径生成权限标识，例如 /userList -> system:user:list
        path_parts = menu['frontpath'].strip('/').split('/')
        if len(path_parts) > 0:
            # 修正：使用标准化的权限格式
            # system:user:view 对应 /userList 路由
            if path_parts[-1].lower() == 'userlist':
                perms = "system:user:view"
            elif path_parts[-1].lower() == 'rolelist':
                perms = "system:role:view"
            elif path_parts[-1].lower() == 'menulist':
                perms = "system:menu:view"
            elif path_parts[-1].lower() == 'deptlist':
                perms = "system:dept:view"
            elif path_parts[-1].lower() == 'statistics':
                perms = "system:statistics:view"
            else:
                perms = f"system:{path_parts[-1].lower()}:view"
        else:
            perms = ""
    else:
        perms = ""
    
    # 构建数据库菜单对象
    db_menu = {
        "id": current_id,
        "menu_name": menu_name,
        "parent_id": parent_id,
        "order_num": order_num,
        "path": menu.get('frontpath', ''),
        "component": "",  # 前端已配置，后端不需要
        "menu_type": menu_type,
        "visible": "0",
        "status": "0",
        "icon": menu.get('icon', ''),
        "perms": perms,
        "create_time": datetime.now(),
        "modify_time": datetime.now()
    }
    
    menus.append(db_menu)
    
    # 添加调试日志
    if perms:
        logger.info(f"菜单 '{menu_name}' (ID: {current_id}) 权限: {perms}")
    
    # 递归处理子菜单
    if has_children:
        for idx, child in enumerate(menu['child'], start=1):
            child_menus = convert_frontend_menu_to_db(child, current_id, idx, id_counter)
            menus.extend(child_menus)
    
    return menus

def create_initial_menus():
    """
    根据前端静态菜单配置自动生成数据库菜单数据
    
    优势：
    1. 单一数据源：只需在前端 staticMenus.js 维护菜单
    2. 自动同步：修改前端配置后，重新初始化即可
    3. 减少重复：不需要在后端重复定义菜单结构
    """
    try:
        # 加载前端静态菜单配置
        static_menus = load_static_menu_config()
        
        if not static_menus:
            logger.warning("未能加载静态菜单配置，使用默认菜单")
            static_menus = [
                {
                    "name": "主页",
                    "icon": "HomeFilled",
                    "frontpath": "/Statistics",
                    "child": []
                }
            ]
        
        # 转换为数据库格式
        id_counter = {'value': 1}
        db_menus = []
        for idx, menu in enumerate(static_menus, start=1):
            converted = convert_frontend_menu_to_db(menu, 0, idx, id_counter)
            db_menus.extend(converted)
        
        logger.info(f"转换完成，共生成 {len(db_menus)} 个菜单项")
        
        # 保存到数据库
        with Session(engine) as session:
            for menu_data in db_menus:
                existing = session.get(Menu, menu_data["id"])
                if not existing:
                    menu = Menu(**menu_data)
                    session.add(menu)
                    if menu_data.get('perms'):
                        logger.info(f"创建菜单: {menu_data['menu_name']} (ID: {menu_data['id']}, 类型: {menu_data['menu_type']}, 权限: {menu_data['perms']})")
                    else:
                        logger.info(f"创建菜单: {menu_data['menu_name']} (ID: {menu_data['id']}, 类型: {menu_data['menu_type']})")
            
            session.commit()
            logger.info("初始菜单数据创建完成")
    except Exception as e:
        logger.error(f"创建初始菜单失败: {e}", exc_info=True)
        raise

def create_initial_role_menus():
    """为超级管理员角色分配所有菜单权限"""
    try:
        with Session(engine) as session:
            # 获取所有菜单ID
            statement = select(Menu.id)
            menu_ids = session.exec(statement).all()
            
            logger.info(f"开始为超级管理员分配菜单权限，共找到 {len(menu_ids)} 个菜单")
            
            # 为超级管理员(role_id=1)分配所有菜单
            for menu_id in menu_ids:
                # 检查是否已存在角色菜单关系
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 1,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                
                if not existing:
                    # 检查菜单是否有关联权限
                    menu = session.get(Menu, menu_id)
                    if menu and menu.perms:
                        role_menu = RoleMenu(role_id=1, menu_id=menu_id)
                        session.add(role_menu)
                        logger.info(f"为超级管理员分配菜单权限: {menu.perms} (菜单ID: {menu_id})")
            
            session.commit()
            logger.info(f"为超级管理员分配 {len(menu_ids)} 个菜单权限完成")
    except Exception as e:
        logger.error(f"创建角色菜单关系失败: {e}")
        raise

def init_data():
    """
    初始化所有数据
    
    注意：菜单数据从前端静态配置同步到数据库，用于权限控制
    """
    try:
        logger.info("开始初始化数据库数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过初始化")
            return
        
        # 按顺序创建基础数据
        create_initial_depts()
        create_initial_roles()
        create_initial_users()
        create_initial_user_roles()
        create_initial_menus()       # 根据静态配置创建菜单
        create_initial_role_menus()  # 为管理员分配菜单权限
        
        logger.info("数据库基础数据初始化完成！")
    except Exception as e:
        logger.error(f"数据库数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_data()
