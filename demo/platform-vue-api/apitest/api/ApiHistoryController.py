from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime
from apitest.model.ApiHistoryModel import ApiHistoryModel
from flask import send_from_directory


# 模块信息
module_name = "ApiHistoryModel"  # 模块名称
module_model = ApiHistoryModel  # 请根据您的模型类进行调整
module_route = Blueprint(f"route_{module_name}", __name__)

# 查看报告的接口
@module_route.route('/AppHistory/<path:dir>/<filename>',methods=["GET"])
def uploaded_file(dir, filename):
    report_root_dir = application.config['REPORT_ROOT_DIR']
    return send_from_directory(f"{report_root_dir}/{dir}/", filename)

@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索)-倒叙 """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        with application.app_context():
            filter_list = []
            collection_info_id = request.json.get("collection_info_id", 0)
            if type(collection_info_id) is not str and collection_info_id > 0:
                filter_list.append(module_model.collection_info_id == collection_info_id)
            # 数据库查询
            datas = module_model.query.filter(*filter_list).order_by(module_model.create_time.desc()).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
        if datas:
            return respModel().ok_resp_list(lst=datas, total=total)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        with application.app_context():
            # 数据库查询
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
        with application.app_context():
            database.session.add(data)
            database.session.commit()
        return respModel.ok_resp(msg="添加成功")
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