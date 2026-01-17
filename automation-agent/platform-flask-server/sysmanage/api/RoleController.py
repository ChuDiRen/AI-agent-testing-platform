from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

from sysmanage.model.RoleModel import Role
from sysmanage.model.MenuModel import Menu
from sysmanage.model.ApiModel import Api
from sysmanage.model.UserRoleModel import UserRole

module_name = "role"
module_model = Role
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        page = int(request.json.get("page", 1))
        page_size = int(request.json.get("pageSize", 10))
        with application.app_context():
            filter_list = []
            name = request.json.get("name", "")
            if len(name) > 0:
                filter_list.append(module_model.name.like(f"%{name}%"))

            datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
            return respModel().ok_resp_list(lst=datas, total=total, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        with application.app_context():
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data, msg="查询成功")
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with application.app_context():
            request.json["id"] = None
            if module_model.query.filter_by(name=request.json["name"]).first():
                return respModel.error_resp(msg="角色名称已存在")

            data = module_model(**request.json)
            database.session.add(data)
            database.session.flush()
            data_id = data.id
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with application.app_context():
            role = module_model.query.filter_by(name=request.json["name"]).first()
            if role and role.id != request.json["id"]:
                return respModel.error_resp(msg="角色名称已存在")

            module_model.query.filter_by(id=request.json["id"]).update(request.json)
            database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        with application.app_context():
            module_model.query.filter_by(id=request.args.get("id")).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/queryMenus", methods=["GET"])
def queryMenus():
    """ 查询角色关联的菜单 """
    try:
        role_id = int(request.args.get("id"))
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if role:
                menus = database.session.query(Menu).all()
                role_menu_ids = [m.id for m in role.menus]
                result = []
                for menu in menus:
                    result.append({
                        "id": menu.id,
                        "name": menu.name,
                        "menu_type": menu.menu_type,
                        "path": menu.path,
                        "checked": menu.id in role_menu_ids
                    })
                return respModel().ok_resp(obj=result, msg="查询成功")
        return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/updateMenus", methods=["PUT"])
def updateMenus():
    """ 更新角色菜单关联 """
    try:
        role_id = request.json.get("id")
        menu_ids = request.json.get("menu_ids", [])
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if role:
                role.menus = []
                database.session.flush()
                for menu_id in menu_ids:
                    menu = Menu.query.get(menu_id)
                    if menu:
                        role.menus.append(menu)
                database.session.commit()
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"更新失败：{e}")


@module_route.route(f"/{module_name}/queryApis", methods=["GET"])
def queryApis():
    """ 查询角色关联的API """
    try:
        role_id = int(request.args.get("id"))
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if role:
                apis = database.session.query(Api).all()
                role_api_ids = [a.id for a in role.apis]
                result = []
                for api in apis:
                    result.append({
                        "id": api.id,
                        "path": api.path,
                        "method": api.method,
                        "summary": api.summary,
                        "tags": api.tags,
                        "checked": api.id in role_api_ids
                    })
                return respModel().ok_resp(obj=result, msg="查询成功")
        return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/updateApis", methods=["PUT"])
def updateApis():
    """ 更新角色API关联 """
    try:
        role_id = request.json.get("id")
        api_ids = request.json.get("api_ids", [])
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if role:
                role.apis = []
                database.session.flush()
                for api_id in api_ids:
                    api = Api.query.get(api_id)
                    if api:
                        role.apis.append(api)
                database.session.commit()
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"更新失败：{e}")


@module_route.route(f"/{module_name}/authorized", methods=["GET"])
def get_role_authorized():
    """ 查看角色权限(菜单+API) """
    try:
        role_id = int(request.args.get("id"))
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if not role:
                return respModel.error_resp(msg="角色不存在")
            
            # 获取角色的菜单
            menus = role.menus.all() if hasattr(role, 'menus') else []
            menu_list = [{
                "id": menu.id,
                "name": menu.name,
                "menu_type": menu.menu_type,
                "path": menu.path,
                "icon": menu.icon,
                "order": menu.order,
                "parent_id": menu.parent_id,
                "is_hidden": menu.is_hidden,
                "component": menu.component,
                "keepalive": menu.keepalive,
                "redirect": menu.redirect,
                "created_at": menu.created_at.strftime('%Y-%m-%d %H:%M:%S') if menu.created_at else None,
                "updated_at": menu.updated_at.strftime('%Y-%m-%d %H:%M:%S') if menu.updated_at else None
            } for menu in menus]
            
            # 获取角色的API
            apis = role.apis.all() if hasattr(role, 'apis') else []
            api_list = [{
                "id": api.id,
                "path": api.path,
                "method": api.method,
                "summary": api.summary,
                "tags": api.tags,
                "created_at": api.created_at.strftime('%Y-%m-%d %H:%M:%S') if api.created_at else None,
                "updated_at": api.updated_at.strftime('%Y-%m-%d %H:%M:%S') if api.updated_at else None
            } for api in apis]
            
            result = {
                "id": role.id,
                "name": role.name,
                "desc": role.desc,
                "menus": menu_list,
                "apis": api_list,
                "created_at": role.created_at.strftime('%Y-%m-%d %H:%M:%S') if role.created_at else None,
                "updated_at": role.updated_at.strftime('%Y-%m-%d %H:%M:%S') if role.updated_at else None
            }
            
            return respModel().ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/updateAuthorized", methods=["POST"])
def update_role_authorized():
    """ 更新角色权限(菜单+API) """
    try:
        role_id = request.json.get("id")
        menu_ids = request.json.get("menu_ids", [])
        api_infos = request.json.get("api_infos", [])
        
        with application.app_context():
            role = module_model.query.filter_by(id=role_id).first()
            if not role:
                return respModel.error_resp(msg="角色不存在")
            
            # 更新菜单关联
            role.menus = []
            database.session.flush()
            for menu_id in menu_ids:
                menu = Menu.query.get(menu_id)
                if menu:
                    role.menus.append(menu)
            
            # 更新API关联
            role.apis = []
            database.session.flush()
            for api_info in api_infos:
                # api_infos 可能是ID列表或包含path/method的字典列表
                if isinstance(api_info, dict):
                    path = api_info.get("path")
                    method = api_info.get("method")
                    if path and method:
                        api = Api.query.filter_by(path=path, method=method).first()
                        if api:
                            role.apis.append(api)
                else:
                    # 如果是ID
                    api = Api.query.get(api_info)
                    if api:
                        role.apis.append(api)
            
            database.session.commit()
        
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"更新失败：{e}")
