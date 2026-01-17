from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

from sysmanage.model.AuditLogModel import AuditLog

module_name = "auditlog"
module_model = AuditLog
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        page = int(request.json.get("page", 1))
        page_size = int(request.json.get("pageSize", 10))
        with application.app_context():
            filter_list = []
            username = request.json.get("username", "")
            if len(username) > 0:
                filter_list.append(module_model.username.like(f"%{username}%"))

            module = request.json.get("module", "")
            if len(module) > 0:
                filter_list.append(module_model.module.like(f"%{module}%"))

            method = request.json.get("method", "")
            if len(method) > 0:
                filter_list.append(module_model.method == method)

            datas = module_model.query.filter(*filter_list).order_by(module_model.created_at.desc()).limit(page_size).offset((page - 1) * page_size).all()
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


@module_route.route(f"/{module_name}/clear", methods=["POST"])
def clear():
    """ 清空所有日志 """
    try:
        with application.app_context():
            module_model.query.delete()
            database.session.commit()
        return respModel.ok_resp(msg="清空成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"清空失败：{e}")
