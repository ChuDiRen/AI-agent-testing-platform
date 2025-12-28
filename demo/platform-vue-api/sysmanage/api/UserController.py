from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

# 这里我们引用对应的Model，因为我们登录和管理用的是同一个表，所以我么这个位置直接引用对应Model
from login.model.UserModel import User

# 模块信息
module_name = "user"  # 模块名称
module_model = User
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json.get("page",0))
        page_size = int(request.json.get("pageSize",10))
        with application.app_context():
            filter_list = []
            # ====筛选条件(如果有筛选条件，在这里拓展 - filter)
            # 代码示例：
            # yyyy = request.json["xxxx"]
            # if len(yyyy) > 0 :
            #    filter_list.append(Model.属性.like(f"%{yyyy}%"))
            # =====结束
            username = request.json.get("username","")
            if len(username) > 0 :
               filter_list.append(module_model.username.like(f"%{username}%"))

            # 数据库查询
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
            # 数据库查询
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
            request.json["id"] = None  # ID自增长
            #  获取用户名，如果存在，则不允许新增
            if module_model.query.filter_by(username=request.json["username"]).first():
                return respModel.error_resp(msg="用户名已存在")

            # 密码进行加密处理
            request.json["password"] = module_model().set_password(request.json["password"])
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
            # 修改的用户名不能是数据库存在的用户名
            user = module_model.query.filter_by(username=request.json["username"]).first()
            if user and user.id != request.json["id"]:
                # 同时要确认修改的用户ID
                return respModel.error_resp(msg="用户名已存在")
            # 密码进行加密处理
            request.json["password"] = module_model().set_password(request.json["password"])
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
