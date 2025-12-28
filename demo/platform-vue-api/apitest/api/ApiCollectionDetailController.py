from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail  # 请替换为你的ApiModule模型类
from datetime import datetime
# 模块信息
module_name = "ApiCollectionDetail"  # 模块名称
module_model = ApiCollectionDetail
module_route = Blueprint(f"route_{module_name}", __name__)


# @module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
# def queryByPage():
#     """ 查询数据(支持模糊搜索) """
#     try:
#         # 分页查询
#         page = int(request.json["page"])
#         page_size = int(request.json["pageSize"])
#         with application.app_context():
#             filter_list = []
#
#             # 增加可以通过collection_info_id进行筛选的条件
#             collection_info_id = request.json.get("collection_info_id", 0)
#             if type(collection_info_id) is not str and collection_info_id > 0:
#                 filter_list.append(module_model.collection_info_id == collection_info_id)
#
#             datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
#             total = module_model.query.filter(*filter_list).count()
#             return respModel().ok_resp_list(lst=datas, total=total)
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 其它模块
from apitest.model.ApiInfoCaseModel import ApiInfoCase  # 请替换为你的ApiModule模型类
@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        with application.app_context():
            filter_list = []
            # 增加可以通过collection_info_id进行筛选的条件
            collection_info_id = request.json.get("collection_info_id", 0)
            if type(collection_info_id) is not str and collection_info_id > 0:
                filter_list.append(module_model.collection_info_id == collection_info_id)

            # 数据库查询- 这个位置需要针对于id进行排序
            datas = module_model.query.order_by(module_model.run_order.asc()).filter(*filter_list).limit(
                page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()

            results = []
            # 遍历所有的关联的测试用例
            for data in datas:
                # 1. 通过用例的编号查询到具体的信息
                api_case_info_id = ApiInfoCase.query.filter_by(id=data.api_case_info_id).first()
                # 2. 把查询到的用例信息(api_case_info_id) 和 当前的(data) 都加到result中
                result = respModel().get_custom_attributes(api_case_info_id)
                result.update(respModel().get_custom_attributes(data))
                # 3. 把所有的数据加到:results中
                results.append(result)

            # 返回了results的值
            return respModel().ok_resp_simple_list(lst=results, total=total)
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
            data = module_model.query.filter_by(id = data_id).first()
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
            request.json["id"] = None # ID自增长
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
