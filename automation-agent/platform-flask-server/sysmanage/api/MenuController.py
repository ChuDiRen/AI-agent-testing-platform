from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

from sysmanage.model.MenuModel import Menu

module_name = "menu"
module_model = Menu
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

            menu_type = request.json.get("menu_type", "")
            if len(menu_type) > 0:
                filter_list.append(module_model.menu_type == menu_type)

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


@module_route.route(f"/{module_name}/queryTree", methods=["GET"])
def queryTree():
    """ 查询菜单树 """
    try:
        with application.app_context():
            menus = module_model.query.order_by(module_model.order).all()
            result = build_tree(menus, 0)
            return respModel.ok_resp_tree(treeData=result, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


def build_tree(menus, parent_id):
    """ 构建树形结构 """
    result = []
    for menu in menus:
        if menu.parent_id == parent_id:
            children = build_tree(menus, menu.id)
            menu_dict = {
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
                "redirect": menu.redirect
            }
            if children:
                menu_dict["children"] = children
            result.append(menu_dict)
    return result
