from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

from sysmanage.model.DeptModel import Dept
from sysmanage.model.DeptClosureModel import DeptClosure

module_name = "dept"
module_model = Dept
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
                return respModel.error_resp(msg="部门名称已存在")

            data = module_model(**request.json)
            database.session.add(data)
            database.session.flush()
            data_id = data.id

            parent_id = request.json.get("parent_id", 0)
            if parent_id == 0:
                closure = DeptClosure()
                closure.ancestor = data_id
                closure.descendant = data_id
                closure.level = 0
                database.session.add(closure)
            else:
                parent_closures = DeptClosure.query.filter_by(descendant=parent_id).all()
                for pc in parent_closures:
                    closure = DeptClosure()
                    closure.ancestor = pc.ancestor
                    closure.descendant = data_id
                    closure.level = pc.level + 1
                    database.session.add(closure)

            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with application.app_context():
            dept = module_model.query.filter_by(name=request.json["name"]).first()
            if dept and dept.id != request.json["id"]:
                return respModel.error_resp(msg="部门名称已存在")

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
            data_id = int(request.args.get("id"))
            has_children = Dept.query.filter_by(parent_id=data_id).first()
            if has_children:
                return respModel.error_resp(msg="该部门下存在子部门，无法删除")

            DeptClosure.query.filter_by(descendant=data_id).delete(synchronize_session=False)
            module_model.query.filter_by(id=data_id).delete(synchronize_session=False)
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/queryTree", methods=["GET"])
def queryTree():
    """ 查询部门树 """
    try:
        name = request.args.get("name", "")
        with application.app_context():
            # 查询所有未删除的部门
            query = module_model.query.filter_by(is_deleted=False)
            if name:
                query = query.filter(module_model.name.like(f"%{name}%"))
            depts = query.order_by(module_model.order).all()
            
            # 构建树形结构
            def build_tree(parent_id):
                result = []
                for dept in depts:
                    if dept.parent_id == parent_id:
                        dept_dict = {
                            "id": dept.id,
                            "name": dept.name,
                            "desc": dept.desc,
                            "order": dept.order,
                            "parent_id": dept.parent_id,
                            "children": build_tree(dept.id)
                        }
                        result.append(dept_dict)
                return result
            
            tree = build_tree(0)
            return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
