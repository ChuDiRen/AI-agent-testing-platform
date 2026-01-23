"""
权限验证中间件
实现基于角色的访问控制 (RBAC)
"""

from functools import wraps
from flask import request, g, abort
from core.resp_model import respModel
import re


class PermissionMiddleware:
    """权限验证中间件类"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        app.config.setdefault('PERMISSIONS', {})
        app.config.setdefault('ROLE_PERMISSIONS', {})
    
    @staticmethod
    def get_current_user():
        """从请求头的token中获取当前用户信息"""
        try:
            token = request.headers.get("token")
            if not token:
                return None
            
            # 验证token并获取用户信息
            from core.JwtUtil import JwtUtils
            payload = JwtUtils.verify_token(token)
            if not payload or payload.get("error"):
                return None
            
            username = payload.get("username")
            if not username:
                return None
            
            from app import application
            from login.model.UserModel import User
            
            with application.app_context():
                user = User.query.filter_by(username=username).first()
                return user
        except Exception as e:
            print(f"[权限中间件] 获取当前用户失败: {e}")
            return None
    
    @staticmethod
    def get_user_permissions(username):
        """获取用户权限列表"""
        try:
            from app import application, database
            from login.model.UserModel import User
            from sysmanage.model.UserRoleModel import UserRole
            from sysmanage.model.RoleModel import Role
            from sysmanage.model.RoleMenuModel import RoleMenu
            from sysmanage.model.RoleApiModel import RoleApi
            from sysmanage.model.MenuModel import Menu
            from sysmanage.model.ApiModel import Api
            
            with application.app_context():
                # 获取用户
                user = User.query.filter_by(username=username).first()
                if not user:
                    return {'menus': set(), 'apis': set(), 'roles': [], 'is_superuser': False}
                
                # 获取用户角色
                user_roles = database.session.query(Role).join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == user.id).all()
                
                permissions = {
                    'menus': set(),
                    'apis': set(),
                    'roles': [role.name for role in user_roles],
                    'is_superuser': user.is_superuser
                }
                
                # 超级管理员拥有所有权限
                if user.is_superuser:
                    return permissions
                
                # 获取角色对应的菜单权限
                for role in user_roles:
                    role_menus = database.session.query(Menu).join(RoleMenu, Menu.id == RoleMenu.menu_id).filter(RoleMenu.role_id == role.id).all()
                    permissions['menus'].update([menu.path for menu in role_menus])
                    
                    # 获取角色对应的API权限
                    role_apis = database.session.query(Api).join(RoleApi, Api.id == RoleApi.api_id).filter(RoleApi.role_id == role.id).all()
                    # 同时存储 path 和 path:method 两种格式
                    for api in role_apis:
                        permissions['apis'].add(api.path)
                        permissions['apis'].add(f"{api.path}:{api.method}")
                
                return permissions
        except Exception as e:
            print(f"[权限中间件] 获取用户权限失败: {e}")
            import traceback
            traceback.print_exc()
            return {'menus': set(), 'apis': set(), 'roles': [], 'is_superuser': False}
    
    @staticmethod
    def check_permission(required_permission, user_permissions):
        """检查用户是否有指定权限"""
        if not required_permission:
            return True
        
        # 检查是否为超级管理员
        if '超级管理员' in user_permissions.get('roles', []):
            return True
        
        # 检查菜单权限
        if required_permission.startswith('/'):
            return required_permission in user_permissions.get('menus', set())
        
        # 检查API权限
        return required_permission in user_permissions.get('apis', set())


def permission_required(permission=None):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 获取当前用户
                username = getattr(g, 'username', None)
                if not username:
                    return respModel.error_resp("用户未登录"), 401
                
                # 获取用户权限
                user_permissions = PermissionMiddleware.get_user_permissions(username)
                
                # 检查权限
                if not PermissionMiddleware.check_permission(permission, user_permissions):
                    print(f"[权限验证] 用户 {username} 尝试访问需要权限 {permission} 的资源被拒绝")
                    return respModel.error_resp("权限不足"), 403
                
                print(f"[权限验证] 用户 {username} 权限验证通过")
                return f(*args, **kwargs)
                
            except Exception as e:
                print(f"[权限验证] 权限检查失败: {e}")
                return respModel.error_resp("权限验证失败"), 500
        
        return decorated_function
    return decorator


def api_permission_required():
    """API权限验证装饰器 - 自动根据请求路径检查权限"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 从 token 获取当前用户
                user = PermissionMiddleware.get_current_user()
                if not user:
                    return respModel.error_resp("用户未登录或token无效"), 401
                
                username = user.username
                
                # 获取用户权限
                user_permissions = PermissionMiddleware.get_user_permissions(username)
                
                # 获取当前请求路径
                current_path = request.path
                method = request.method
                
                # 构建权限标识
                permission_key = f"{current_path}:{method}"
                
                # 检查是否为超级管理员
                if user_permissions.get('is_superuser') or '超级管理员' in user_permissions.get('roles', []):
                    print(f"[API权限验证] 超级管理员 {username} 访问 {permission_key} 通过")
                    # 将用户信息存储到 g 对象中，供后续使用
                    g.current_user = user
                    g.username = username
                    return f(*args, **kwargs)
                
                # 检查API权限
                apis = user_permissions.get('apis', set())
                if permission_key not in apis and current_path not in apis:
                    print(f"[API权限验证] 用户 {username} 尝试访问 {permission_key} 被拒绝")
                    print(f"[API权限验证] 用户拥有的API权限: {apis}")
                    return respModel.error_resp("权限不足"), 403
                
                print(f"[API权限验证] 用户 {username} 访问 {permission_key} 通过")
                # 将用户信息存储到 g 对象中，供后续使用
                g.current_user = user
                g.username = username
                return f(*args, **kwargs)
                
            except Exception as e:
                print(f"[API权限验证] 权限检查失败: {e}")
                import traceback
                traceback.print_exc()
                return respModel.error_resp("权限验证失败"), 500
        
        return decorated_function
    return decorator


# 扩展User模型，添加根据用户名获取ID的方法
def get_user_id_by_username(username):
    """根据用户名获取用户ID"""
    try:
        from app import application, database
        from login.model.UserModel import User
        
        with application.app_context():
            user = User.query.filter_by(username=username).first()
            return user.id if user else None
    except Exception as e:
        print(f"[权限中间件] 获取用户ID失败: {e}")
        return None

# 将方法添加到User模型
try:
    from login.model.UserModel import User
    User.get_user_id_by_username = staticmethod(get_user_id_by_username)
except ImportError:
    pass
