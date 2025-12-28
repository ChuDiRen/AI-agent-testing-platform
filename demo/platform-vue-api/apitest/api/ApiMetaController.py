import os
from flask import Blueprint, request, redirect
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiMetaModel import ApiMeta  # 替换为你的ApiMeta模型类
from datetime import datetime

# 模块信息
module_name = "ApiMeta"  # 模块名称
module_model = ApiMeta
module_route = Blueprint(f"route_{module_name}", __name__)

module_route.route(f"/{module_name}/queryAll", methods=["GET"])
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

            # 添加mate_name搜索条件
            mate_name = request.json.get("mate_name", "")
            if len(mate_name) > 0:
                filter_list.append(module_model.mate_name.like(f'%{mate_name}%'))
            # 添加object_url搜索条件
            object_url = request.json.get("object_url", "")
            if len(object_url) > 0:
                filter_list.append(module_model.object_url.like(f'%{object_url}%'))
            # 添加file_type搜索条件
            file_type = request.json.get("file_type", "")
            if len(file_type) > 0:
                filter_list.append(module_model.file_type.like(f'%{file_type}%'))
            # 添加页面筛选条件
            project_id = request.json.get("project_id", 0)
            if type(project_id) is not str and project_id > 0:
                filter_list.append(module_model.project_id == project_id)

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


# @module_route.route(f"/{module_name}/insert", methods=["POST"])
# def insert():
#     """ 新增数据 """
#     try:
#         with application.app_context():
#             request.json["id"] = None  # ID自增长
#             data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
#             database.session.add(data)
#             # 获取新增后的ID并返回
#             database.session.flush()
#             data_id = data.id
#             database.session.commit()
#         return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        # 获取上传的文件
        file = request.files.get("file")
        if not file:
            return respModel.error_resp(msg="未接收到文件")

        # 获取minio对象
        minio_client = application.extensions["minio_utils"]

        # 使用上传文件的原名作为存储文件名
        file_name = file.filename

        # 上传文件到 minio
        minio_client.upload_file(
            "apitest",  # 不同的素材有不同桶名
            file_name,
            file_data=file.read(),
        )

        # 构造文件元数据
        file_metadata = {
            "project_id":request.form.get("project_id", 0),
            "mate_name": file.filename,
            "object_url": f"/apitest/{file_name}",
            "file_type": file.content_type,
            "create_time": datetime.now()
        }

        with application.app_context():
            # 将文件元数据存入数据库
            data = module_model(**file_metadata)
            database.session.add(data)
            database.session.flush()
            data_id = data.id
            database.session.commit()

        return respModel.ok_resp(msg="文件上传成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"文件上传失败:{e}")

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

@module_route.route(f'/{module_name}/downloadFile',methods=["GET"])
def downloadFile():
    try:
        minio_client_url = application.config["MINIO_CLIENT_URL"]
        data_id = int(request.args.get("id"))
        with application.app_context():
            data = module_model.query.filter_by(id=data_id).first()
            # 获取data中的object_url
            object_url = data.object_url
            if not object_url:
                return respModel.error_resp(msg="获取下载地址失败，文件不存在")
            return respModel.ok_resp(msg="获取到下载地址", dic_t={"downloadUrl":f"{minio_client_url}{object_url}"})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
