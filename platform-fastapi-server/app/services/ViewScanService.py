# -*- coding: utf-8 -*-
"""
视图扫描服务
扫描前端 views 目录，自动同步菜单数据到数据库

工作流程：
1. 扫描前端 views 目录结构
2. 识别模块（system、generator）和子模块（users、role、table）
3. 识别视图文件（*List.vue、*Form.vue）
4. 自动生成菜单数据（目录菜单 M、页面菜单 C）
5. List 页面显示，Form 页面隐藏
6. 自动为管理员角色分配权限
"""
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from sqlmodel import Session, select

from app.models.MenuModel import Menu
from app.models.RoleMenuModel import RoleMenu
from app.logger.logger import get_logger

logger = get_logger(__name__)


class ViewScanService:
    """视图扫描服务 - 自动同步前端视图到菜单数据库"""
    
    # 需要排除的目录和文件
    EXCLUDE_DIRS = {'home', 'login'}
    EXCLUDE_FILES = {'403.vue', '404.vue', '500.vue'}
    
    # 模块配置：模块名 -> (显示名称, 图标, 排序)
    MODULE_CONFIG = {
        'statistics': ('主页信息', 'DataAnalysis', 0),
        'system': ('系统管理', 'Setting', 1),
        'generator': ('代码生成', 'Document', 2),
    }
    
    # 子模块配置：子模块名 -> (显示名称, 图标, 权限前缀)
    SUB_MODULE_CONFIG = {
        'users': ('用户', 'User', 'user'),
        'role': ('角色', 'UserFilled', 'role'),
        'menu': ('菜单', 'Menu', 'menu'),
        'dept': ('部门', 'OfficeBuilding', 'dept'),
        'table': ('表配置', 'Grid', 'table'),
        'code': ('代码生成', 'EditPen', 'code'),
        'history': ('生成历史', 'Tickets', 'history'),
    }
    
    def __init__(self, views_path: str):
        """
        初始化视图扫描服务
        
        Args:
            views_path: 前端 views 目录的绝对路径
        """
        self.views_path = Path(views_path)
        if not self.views_path.exists():
            raise ValueError(f"Views 目录不存在: {views_path}")
    
    def scan_views(self) -> Dict[str, Any]:
        """
        扫描 views 目录，返回视图结构
        
        Returns:
            {
                'modules': [
                    {
                        'name': 'system',
                        'display_name': '系统管理',
                        'icon': 'Setting',
                        'order': 1,
                        'sub_modules': [
                            {
                                'name': 'users',
                                'display_name': '用户',
                                'views': [
                                    {'name': 'userList', 'type': 'list', 'component': 'system/users/userList'},
                                    {'name': 'userForm', 'type': 'form', 'component': 'system/users/userForm'},
                                ]
                            }
                        ]
                    }
                ],
                'root_views': [
                    {'name': 'statistics', 'component': 'statistics/statistics', 'display_name': '主页信息'}
                ]
            }
        """
        result = {
            'modules': [],
            'root_views': []
        }
        
        for item in self.views_path.iterdir():
            if not item.is_dir():
                continue
            
            if item.name in self.EXCLUDE_DIRS:
                continue
            
            module = self._scan_module(item)
            if module:
                if module.get('sub_modules'):
                    result['modules'].append(module)
                elif module.get('views'):
                    # 没有子模块，直接是视图文件（如 statistics）
                    for view in module['views']:
                        result['root_views'].append({
                            **view,
                            'module_name': module['name'],
                            'display_name': module['display_name'],
                            'icon': module['icon'],
                            'order': module['order']
                        })
        
        # 按 order 排序模块
        result['modules'].sort(key=lambda x: x.get('order', 99))
        result['root_views'].sort(key=lambda x: x.get('order', 99))
        
        return result
    
    def _scan_module(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """扫描单个模块目录"""
        module_name = module_path.name
        config = self.MODULE_CONFIG.get(module_name, (module_name.title(), 'Folder', 99))
        
        module = {
            'name': module_name,
            'display_name': config[0],
            'icon': config[1],
            'order': config[2],
            'sub_modules': [],
            'views': []
        }
        
        for item in module_path.iterdir():
            if item.is_dir():
                # 子模块目录
                sub_module = self._scan_sub_module(item, module_name)
                if sub_module:
                    module['sub_modules'].append(sub_module)
            elif item.is_file() and item.suffix == '.vue':
                # 直接在模块下的视图文件
                if item.name not in self.EXCLUDE_FILES:
                    view = self._parse_view_file(item, module_name)
                    if view:
                        module['views'].append(view)
        
        # 子模块按名称排序
        module['sub_modules'].sort(key=lambda x: x.get('order', 99))
        
        return module if (module['sub_modules'] or module['views']) else None
    
    def _scan_sub_module(self, sub_module_path: Path, parent_module: str) -> Optional[Dict[str, Any]]:
        """扫描子模块目录"""
        sub_module_name = sub_module_path.name
        config = self.SUB_MODULE_CONFIG.get(sub_module_name, (sub_module_name.title(), None, sub_module_name))
        
        sub_module = {
            'name': sub_module_name,
            'display_name': config[0],
            'icon': config[1],
            'perm_prefix': config[2],
            'order': list(self.SUB_MODULE_CONFIG.keys()).index(sub_module_name) if sub_module_name in self.SUB_MODULE_CONFIG else 99,
            'views': []
        }
        
        for item in sub_module_path.iterdir():
            if item.is_file() and item.suffix == '.vue':
                if item.name not in self.EXCLUDE_FILES:
                    view = self._parse_view_file(item, parent_module, sub_module_name)
                    if view:
                        sub_module['views'].append(view)
        
        # 视图按类型排序：list 在前，form 在后
        sub_module['views'].sort(key=lambda x: (0 if x['type'] == 'list' else 1, x['name']))
        
        return sub_module if sub_module['views'] else None
    
    def _parse_view_file(self, file_path: Path, module: str, sub_module: str = None) -> Optional[Dict[str, Any]]:
        """解析视图文件"""
        name = file_path.stem  # 不含扩展名的文件名
        
        # 判断视图类型
        view_type = 'page'
        name_lower = name.lower()
        if name_lower.endswith('list'):
            view_type = 'list'
        elif name_lower.endswith('form'):
            view_type = 'form'
        
        # 构建组件路径
        if sub_module:
            component = f"{module}/{sub_module}/{name}"
        else:
            component = f"{module}/{name}"
        
        return {
            'name': name,
            'type': view_type,
            'component': component,
            'module': module,
            'sub_module': sub_module
        }
    
    def sync_to_database(self, session: Session, admin_role_id: int = 1) -> Dict[str, Any]:
        """
        将扫描结果同步到数据库
        
        Args:
            session: 数据库会话
            admin_role_id: 管理员角色ID，用于分配权限
            
        Returns:
            同步结果统计
        """
        scan_result = self.scan_views()
        
        stats = {
            'scanned_modules': 0,
            'scanned_views': 0,
            'added_menus': 0,
            'added_permissions': 0,
            'details': []
        }
        
        # 获取当前数据库中的最大菜单ID
        statement = select(Menu).order_by(Menu.id.desc())
        max_menu = session.exec(statement).first()
        next_id = (max_menu.id + 1) if max_menu else 1
        
        # 获取已存在的菜单（按 component 索引）
        existing_menus = {}
        all_menus = session.exec(select(Menu)).all()
        for menu in all_menus:
            if menu.component:
                existing_menus[menu.component] = menu
        
        # 1. 处理根视图（如 statistics）
        for view in scan_result['root_views']:
            stats['scanned_views'] += 1
            if view['component'] not in existing_menus:
                next_id = self._create_root_view_menu(
                    session, view, next_id, admin_role_id, stats
                )
        
        # 2. 处理模块
        for module in scan_result['modules']:
            stats['scanned_modules'] += 1
            module_name = module['name']
            
            # 创建或获取模块目录菜单
            module_menu_id = self._find_or_create_module_menu(
                session, module, existing_menus, next_id, stats
            )
            if module_menu_id >= next_id:
                next_id = module_menu_id + 1
            
            # 处理子模块
            sub_order = 1
            for sub_module in module['sub_modules']:
                # 找到 List 页面作为子模块的主菜单
                list_view = None
                form_views = []
                
                for view in sub_module['views']:
                    stats['scanned_views'] += 1
                    if view['type'] == 'list':
                        list_view = view
                    elif view['type'] == 'form':
                        form_views.append(view)
                    else:
                        # 其他类型页面
                        form_views.append(view)
                
                # 创建 List 页面菜单（作为子模块主菜单）
                list_menu_id = None
                if list_view and list_view['component'] not in existing_menus:
                    list_menu_id, next_id = self._create_list_menu(
                        session, list_view, sub_module, module,
                        module_menu_id, next_id, sub_order, admin_role_id, stats
                    )
                elif list_view:
                    list_menu_id = existing_menus[list_view['component']].id
                
                # 创建 Form 页面菜单（隐藏，挂在 List 下面）
                for form_view in form_views:
                    if form_view['component'] not in existing_menus:
                        next_id = self._create_form_menu(
                            session, form_view, sub_module, module,
                            list_menu_id or module_menu_id, next_id, admin_role_id, stats
                        )
                
                sub_order += 1
        
        session.commit()
        logger.info(f"视图同步完成: 添加 {stats['added_menus']} 个菜单, {stats['added_permissions']} 条权限")
        return stats
    
    def _create_root_view_menu(
        self, session: Session, view: Dict, next_id: int,
        admin_role_id: int, stats: Dict
    ) -> int:
        """创建根视图菜单（如主页信息）"""
        menu = Menu(
            id=next_id,
            parent_id=0,
            menu_name=view['display_name'],
            path=f"/{view['name']}",
            component=view['component'],
            perms=None,
            icon=view['icon'],
            menu_type='C',
            visible='0',
            status='0',
            is_cache='0',
            is_frame='1',
            order_num=view['order'],
            remark=f"{view['display_name']}页面",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        session.add(menu)
        self._add_role_menu_permission(session, admin_role_id, next_id, stats)
        stats['added_menus'] += 1
        stats['details'].append(f"添加根菜单: {view['display_name']}")
        logger.info(f"创建根菜单: {view['display_name']} (ID: {next_id})")
        
        return next_id + 1
    
    def _find_or_create_module_menu(
        self, session: Session, module: Dict,
        existing_menus: Dict, next_id: int, stats: Dict
    ) -> int:
        """查找或创建模块目录菜单"""
        module_path = f"/{module['name']}"
        
        # 检查是否已存在（通过 path 查找）
        statement = select(Menu).where(Menu.path == module_path, Menu.menu_type == 'M')
        existing = session.exec(statement).first()
        if existing:
            return existing.id
        
        # 创建模块目录菜单
        menu = Menu(
            id=next_id,
            parent_id=0,
            menu_name=module['display_name'],
            path=module_path,
            component=None,
            perms=None,
            icon=module['icon'],
            menu_type='M',  # 目录类型
            visible='0',
            status='0',
            is_cache='0',
            is_frame='1',
            order_num=module['order'],
            remark=f"{module['display_name']}模块",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        session.add(menu)
        stats['added_menus'] += 1
        stats['details'].append(f"添加模块目录: {module['display_name']}")
        logger.info(f"创建模块目录菜单: {module['display_name']} (ID: {next_id})")
        
        return next_id
    
    def _create_list_menu(
        self, session: Session, view: Dict, sub_module: Dict, module: Dict,
        parent_id: int, next_id: int, order_num: int,
        admin_role_id: int, stats: Dict
    ) -> Tuple[int, int]:
        """创建 List 页面菜单"""
        display_name = f"{sub_module['display_name']}管理"
        perm_prefix = f"{module['name']}:{sub_module['perm_prefix']}"
        
        menu = Menu(
            id=next_id,
            parent_id=parent_id,
            menu_name=display_name,
            path=f"/{module['name']}/{sub_module['name']}",
            component=view['component'],
            perms=f"{perm_prefix}:list",
            icon=sub_module['icon'],
            menu_type='C',
            visible='0',
            status='0',
            is_cache='0',
            is_frame='1',
            order_num=order_num,
            remark=f"{display_name}页面",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        session.add(menu)
        self._add_role_menu_permission(session, admin_role_id, next_id, stats)
        stats['added_menus'] += 1
        stats['details'].append(f"添加列表菜单: {display_name}")
        logger.info(f"创建列表菜单: {display_name} (ID: {next_id})")
        
        return next_id, next_id + 1
    
    def _create_form_menu(
        self, session: Session, view: Dict, sub_module: Dict, module: Dict,
        parent_id: int, next_id: int, admin_role_id: int, stats: Dict
    ) -> int:
        """创建 Form 页面菜单（隐藏）"""
        display_name = f"{sub_module['display_name']}表单"
        perm_prefix = f"{module['name']}:{sub_module['perm_prefix']}"
        
        menu = Menu(
            id=next_id,
            parent_id=parent_id,
            menu_name=display_name,
            path=f"/{view['name']}",
            component=view['component'],
            perms=f"{perm_prefix}:query",
            icon=None,
            menu_type='C',
            visible='1',  # 隐藏
            status='0',
            is_cache='0',
            is_frame='1',
            order_num=99,
            remark=f"{display_name}页面",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        session.add(menu)
        self._add_role_menu_permission(session, admin_role_id, next_id, stats)
        stats['added_menus'] += 1
        stats['details'].append(f"添加表单菜单(隐藏): {display_name}")
        logger.info(f"创建表单菜单(隐藏): {display_name} (ID: {next_id})")
        
        return next_id + 1
    
    def _add_role_menu_permission(self, session: Session, role_id: int, menu_id: int, stats: Dict):
        """为角色添加菜单权限"""
        statement = select(RoleMenu).where(
            RoleMenu.role_id == role_id,
            RoleMenu.menu_id == menu_id
        )
        existing = session.exec(statement).first()
        
        if not existing:
            role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
            session.add(role_menu)
            stats['added_permissions'] += 1
