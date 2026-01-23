"""
权限控制器
提供用户权限查询API
"""

from flask import Blueprint, request, g
from core.resp_model import respModel
from app import application, database
from core.PermissionMiddleware import PermissionMiddleware
from login.model.UserModel import User

# 模块信息
module_name = "permission"
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/user", methods=["GET"])
def get_user_permissions():
    """获取当前用户权限"""
    try:
        # 获取当前用户
        username = getattr(g, 'username', None)
        if not username:
            return respModel.error_resp("用户未登录"), 401
        
        # 获取用户权限
        permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 转换Set为list以便JSON序列化
        result = {
            "menus": list(permissions.get('menus', set())),
            "apis": list(permissions.get('apis', set())),
            "roles": permissions.get('roles', [])
        }
        
        return respModel.ok_resp(obj=result, msg="获取权限成功")
        
    except Exception as e:
        print(f"[权限API] 获取用户权限失败: {e}")
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.route(f"/{module_name}/check", methods=["POST"])
def check_permission():
    """检查用户是否有指定权限"""
    try:
        # 获取当前用户
        username = getattr(g, 'username', None)
        if not username:
            return respModel.error_resp("用户未登录"), 401
        
        # 获取请求数据
        json_data = request.get_json(silent=True)
        if not json_data:
            return respModel.error_resp("请求数据格式错误")
        
        permission = json_data.get("permission")
        if not permission:
            return respModel.error_resp("缺少权限参数")
        
        # 获取用户权限
        user_permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 检查权限
        has_permission = PermissionMiddleware.check_permission(permission, user_permissions)
        
        return respModel.ok_resp(obj={
            "has_permission": has_permission,
            "permission": permission,
            "user_roles": user_permissions.get('roles', [])
        }, msg="权限检查完成")
        
    except Exception as e:
        print(f"[权限API] 权限检查失败: {e}")
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.route(f"/{module_name}/menu", methods=["GET"])
def get_user_menu_permissions():
    """获取用户菜单权限"""
    try:
        # 获取当前用户
        username = getattr(g, 'username', None)
        if not username:
            return respModel.error_resp("用户未登录"), 401
        
        # 获取用户权限
        permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 只返回菜单权限
        result = {
            "menus": list(permissions.get('menus', set())),
            "roles": permissions.get('roles', [])
        }
        
        return respModel.ok_resp(obj=result, msg="获取菜单权限成功")
        
    except Exception as e:
        print(f"[权限API] 获取菜单权限失败: {e}")
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.route(f"/{module_name}/api", methods=["GET"])
def get_user_api_permissions():
    """获取用户API权限"""
    try:
        # 获取当前用户
        username = getattr(g, 'username', None)
        if not username:
            return respModel.error_resp("用户未登录"), 401
        
        # 获取用户权限
        permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 只返回API权限
        result = {
            "apis": list(permissions.get('apis', set())),
            "roles": permissions.get('roles', [])
        }
        
        return respModel.ok_resp(obj=result, msg="获取API权限成功")
        
    except Exception as e:
        print(f"[权限API] 获取API权限失败: {e}")
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.route(f"/{module_name}/refresh", methods=["POST"])
def refresh_user_permissions():
    """刷新用户权限缓存"""
    try:
        # 获取当前用户
        username = getattr(g, 'username', None)
        if not username:
            return respModel.error_resp("用户未登录"), 401
        
        # 清除缓存并重新获取权限
        from core.PermissionMiddleware import PermissionMiddleware
        permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 转换Set为list以便JSON序列化
        result = {
            "menus": list(permissions.get('menus', set())),
            "apis": list(permissions.get('apis', set())),
            "roles": permissions.get('roles', [])
        }
        
        return respModel.ok_resp(obj=result, msg="权限刷新成功")
        
    except Exception as e:
        print(f"[权限API] 刷新权限失败: {e}")
        return respModel.error_resp(f"服务器错误: {e}")
