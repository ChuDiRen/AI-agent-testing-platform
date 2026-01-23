from flask import Blueprint, request, jsonify, g
from app import database, application
from login.model.UserModel import User
from sysmanage.model.RoleModel import Role
from sysmanage.model.MenuModel import Menu
from sysmanage.model.ApiModel import Api

# TODO 0: 导入生成token的jwt
from core.JwtUtil import JwtUtils
from core.resp_model import respModel
from datetime import datetime


# 用途：定义一个独立的“路由容器”，后续可将所有路由挂载到主应用。
# route_login：唯一名称（用于内部标识）。
# __name__：当前模块的名称（用于定位资源文件路径）。
module_route = Blueprint("route_login", __name__)

# @module_route.route("/login", methods=["POST"])
# def login():
#     with application.app_context():
#         data = request.get_json()
#         username = data.get("username")
#         password = data.get("password")
#         user = User.query.filter_by(username=username, password=password).first()
#     if user:
#         # TODO 1: 如果有用户，那么就生成对应的token
#         token = JwtUtils.create_token(username=username, password=password)
#         return respModel().ok_resp(obj=user, msg="登录成功", dic_t={"token": token})
#     else:
#         # 步骤3：如果未查询到用户，则返回登录失败
#         return respModel().error_resp("登录失败，用户名或密码错误")


@module_route.route("/login", methods=["POST"])
def login():
    with application.app_context():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        # 步骤2：参数校验（非空判断）
        if not username or not password:
            return respModel().error_resp(msg="用户名或密码不能为空")

        # 步骤3：查询数据库中的用户
        user = User.query.filter_by(username=username).first()  # 按用户名查询
        if not user:
            return respModel().error_resp(msg="用户名不存在")

        # 步骤4：验证密码
        if not user.check_password(password):
            return respModel().error_resp(msg="密码错误")

        # 步骤5：验证通过，生成 access token 和 refresh token
        access_token = JwtUtils.create_token(username=username, password=password)
        refresh_token = JwtUtils.create_refresh_token(username=username)
        
        return respModel().ok_resp(
            obj=user, 
            msg="登录成功", 
            dic_t={
                "token": access_token,
                "refreshToken": refresh_token
            }
        )


@module_route.route("/refresh", methods=["POST"])
def refresh_token():
    """
    刷新 token 接口
    前端传入 refreshToken，返回新的 token 和 refreshToken
    """
    with application.app_context():
        data = request.get_json()
        refresh_token = data.get("refreshToken")
        
        if not refresh_token:
            return respModel().error_resp(msg="refreshToken 不能为空"), 401
        
        # 使用 refresh token 生成新的 token
        new_access_token, new_refresh_token = JwtUtils.refresh_access_token(refresh_token)
        
        if not new_access_token or not new_refresh_token:
            return respModel().error_resp(msg="refreshToken 已过期，请重新登录"), 401
        
        return respModel().ok_resp(
            msg="token 刷新成功",
            dic_t={
                "token": new_access_token,
                "refreshToken": new_refresh_token
            }
        )


@module_route.route("/userinfo", methods=["GET"])
def get_userinfo():
    """
    获取当前登录用户信息
    需要在请求头中携带 token
    """
    try:
        token = request.headers.get("token")
        if not token:
            return respModel().error_resp(msg="未提供token"), 401
        
        # 验证token并获取用户信息
        payload = JwtUtils.verify_token(token)
        if not payload:
            return respModel().error_resp(msg="token无效或已过期"), 401
        
        username = payload.get("username")
        with application.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            database.session.commit()
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "alias": user.alias,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                "dept_id": user.dept_id,
                "avatar": "https://avatars.githubusercontent.com/u/54677442?v=4"
            }
            
            return respModel().ok_resp(obj=user_data, msg="获取成功")
    except Exception as e:
        print(e)
        return respModel().error_resp(msg=f"获取用户信息失败：{e}"), 500


@module_route.route("/usermenu", methods=["GET"])
def get_user_menu():
    """
    获取当前用户的菜单列表
    需要在请求头中携带 token
    """
    try:
        token = request.headers.get("token")
        if not token:
            return respModel().error_resp(msg="未提供token"), 401
        
        # 验证token并获取用户信息
        payload = JwtUtils.verify_token(token)
        if not payload:
            return respModel().error_resp(msg="token无效或已过期"), 401
        
        username = payload.get("username")
        with application.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 获取用户菜单
            menus = []
            if user.is_superuser:
                # 超级管理员获取所有菜单
                menus = Menu.query.all()
            else:
                # 普通用户通过角色获取菜单
                roles = user.roles.all() if hasattr(user, 'roles') else []
                menu_set = set()
                for role in roles:
                    role_menus = role.menus.all() if hasattr(role, 'menus') else []
                    for menu in role_menus:
                        menu_set.add(menu.id)
                menus = Menu.query.filter(Menu.id.in_(menu_set)).all() if menu_set else []
            
            # 构建菜单树
            parent_menus = [m for m in menus if m.parent_id == 0]
            result = []
            for parent_menu in parent_menus:
                parent_dict = {
                    "id": parent_menu.id,
                    "name": parent_menu.name,
                    "menu_type": parent_menu.menu_type,
                    "icon": parent_menu.icon,
                    "path": parent_menu.path,
                    "order": parent_menu.order,
                    "parent_id": parent_menu.parent_id,
                    "is_hidden": parent_menu.is_hidden,
                    "component": parent_menu.component,
                    "keepalive": parent_menu.keepalive,
                    "redirect": parent_menu.redirect,
                    "children": []
                }
                
                # 添加子菜单
                for menu in menus:
                    if menu.parent_id == parent_menu.id:
                        child_dict = {
                            "id": menu.id,
                            "name": menu.name,
                            "menu_type": menu.menu_type,
                            "icon": menu.icon,
                            "path": menu.path,
                            "order": menu.order,
                            "parent_id": menu.parent_id,
                            "is_hidden": menu.is_hidden,
                            "component": menu.component,
                            "keepalive": menu.keepalive,
                            "redirect": menu.redirect
                        }
                        parent_dict["children"].append(child_dict)
                
                result.append(parent_dict)
            
            return respModel().ok_resp(obj=result, msg="获取成功")
    except Exception as e:
        print(e)
        return respModel().error_resp(msg=f"获取用户菜单失败：{e}"), 500


@module_route.route("/userapi", methods=["GET"])
def get_user_api():
    """
    获取当前用户的API权限列表
    需要在请求头中携带 token
    """
    try:
        token = request.headers.get("token")
        if not token:
            return respModel().error_resp(msg="未提供token"), 401
        
        # 验证token并获取用户信息
        payload = JwtUtils.verify_token(token)
        if not payload:
            return respModel().error_resp(msg="token无效或已过期"), 401
        
        username = payload.get("username")
        with application.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 获取用户API权限
            apis = []
            if user.is_superuser:
                # 超级管理员获取所有API
                api_objs = Api.query.all()
                apis = [api.method.lower() + api.path for api in api_objs]
            else:
                # 普通用户通过角色获取API
                roles = user.roles.all() if hasattr(user, 'roles') else []
                api_set = set()
                for role in roles:
                    role_apis = role.apis.all() if hasattr(role, 'apis') else []
                    for api in role_apis:
                        api_set.add(api.method.lower() + api.path)
                apis = list(api_set)
            
            return respModel().ok_resp(obj=apis, msg="获取成功")
    except Exception as e:
        print(e)
        return respModel().error_resp(msg=f"获取用户API权限失败：{e}"), 500


@module_route.route("/updatePassword", methods=["POST"])
def update_password():
    """
    修改当前用户密码
    需要在请求头中携带 token
    """
    try:
        token = request.headers.get("token")
        if not token:
            return respModel().error_resp(msg="未提供token"), 401
        
        # 验证token并获取用户信息
        payload = JwtUtils.verify_token(token)
        if not payload:
            return respModel().error_resp(msg="token无效或已过期"), 401
        
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        
        if not old_password or not new_password:
            return respModel().error_resp(msg="旧密码和新密码不能为空")
        
        username = payload.get("username")
        with application.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 验证旧密码
            if not user.check_password(old_password):
                return respModel().error_resp(msg="旧密码验证错误！")
            
            # 设置新密码
            user.password = user.set_password(new_password)
            database.session.commit()
            
            return respModel().ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel().error_resp(msg=f"修改密码失败：{e}"), 500


@module_route.route("/permission/user", methods=["GET"])
def get_user_permissions():
    """
    获取当前用户的权限信息
    返回菜单权限、API权限和角色信息
    """
    try:
        token = request.headers.get("token")
        if not token:
            return respModel().error_resp(msg="未提供token"), 401
        
        # 验证token并获取用户信息
        payload = JwtUtils.verify_token(token)
        if not payload:
            return respModel().error_resp(msg="token无效或已过期"), 401
        
        username = payload.get("username")
        
        # 导入权限中间件
        from core.PermissionMiddleware import PermissionMiddleware
        
        # 获取用户权限
        permissions = PermissionMiddleware.get_user_permissions(username)
        
        # 将 set 转换为 list，以便 JSON 序列化
        result = {
            "menus": list(permissions.get('menus', set())),
            "apis": list(permissions.get('apis', set())),
            "roles": permissions.get('roles', []),
            "is_superuser": permissions.get('is_superuser', False)
        }
        
        return respModel().ok_resp(obj=result, msg="获取成功")
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        return respModel().error_resp(msg=f"获取用户权限失败：{e}"), 500
