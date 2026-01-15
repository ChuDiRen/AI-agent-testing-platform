from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from msgmanage.model.RobotConfigModel import RobotConfig  # 导入对应的模型类
from datetime import datetime

# 模块信息
module_name = "RobotConfig"  # 模块名称
module_model = RobotConfig  # 对应的模型类
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryAll", methods=["GET"])
def queryAll():
    with application.app_context():
        datas = module_model.query.all()
        return respModel.ok_resp_list(lst=datas, msg="查询成功")

@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])

        with application.app_context():
            filter_list = []
            if request.json["type"]:
                type = int(request.json["type"])
                filter_list.append(module_model.robot_type == type)

            robot_name = request.json.get("robot_name", "")
            if len(robot_name) > 0:
                filter_list.append(module_model.robot_name.like(f'%{robot_name}%'))
                # ====筛选条件(如果有筛选条件，在这里拓展 - filter)
                # 代码示例：
                # yyyy = request.json["xxxx"]
                # if len(yyyy) > 0 :
                #    filter_list.append(Model.属性.like(f"%{yyyy}%"))
                # =====结束
                # 数据库查询
            datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
            return respModel().ok_resp_list(lst=datas, total=total)
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
        with application.app_context():
            request.json["id"] = None  # ID自增长
            request_data = request.json
            keywords = request_data.get("keywords", "")

            # 验证 keywords 是否为有效的 JSON 格式
            if keywords:
                try:
                    import json
                    json.loads(keywords)
                except ValueError:
                    return respModel.error_resp(msg="keywords 必须是有效的 JSON 格式")

            data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
            database.session.add(data)
            # 获取新增后的ID并返回
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

from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig  # 导入对应的模型类
@module_route.route(f"/{module_name}/queryByPageWithFilter", methods=["POST"])
def queryByPageWithFilter():
    """ 分页查询所有机器人，并根据 coll_id 和 用例类型coll_type 过滤掉已有的机器人 """
    try:
        # 获取分页参数
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        coll_id = int(request.json.get("coll_id", 0))  # 获取 coll_id，默认为 0
        coll_type = request.json.get("coll_type", "")  # 获取 coll_type，默认为 0
        robot_name = request.json.get("robot_name", "")

        with application.app_context():
            filter_list = []
            if request.json.get("type"):
                type = int(request.json["type"])
                filter_list.append(RobotConfig.robot_type == type)

            # 如果 coll_id 不为 0，则查询已有的机器人 ID 列表
            if coll_id > 0:
                existing_robot_ids = [config.robot_id for config in RobotMsgConfig.query.filter_by(coll_id=coll_id,coll_type=coll_type).all()]
                filter_list.append(~RobotConfig.id.in_(existing_robot_ids))

            if len(robot_name) > 0:
                filter_list.append(RobotConfig.robot_name.like(f"%{robot_name}%"))

            # 数据库查询
            datas = RobotConfig.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = RobotConfig.query.filter(*filter_list).count()
            return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
