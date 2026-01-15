from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep  # 请替换为你的模型类
from datetime import datetime

# 模块信息
module_name = "ApiInfoCaseStep"  # 模块名称
module_model = ApiInfoCaseStep  # 修改为相应的模型类
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
            # 添加操作类型模糊搜索条件
            case_name = request.json.get("case_name", "")
            if len(case_name) > 0:
                filter_list.append(module_model.case_name.like(f'%{case_name}%'))
            # 添加对应的搜索条件,可以通过项目ID进行筛选
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


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with application.app_context():
            request.json["id"] = None  # ID自增长
            data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


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


# 扩展-- 用于级联回显对应的数据
from apitest.model.ApiOperationTypeModel import OperationType
from apitest.model.ApiKeyWordModel import ApiKeyWord
@module_route.route(f"/{module_name}/queryAllTree", methods=["POST"])
def queryAllTree():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        with application.app_context():
            filter_list = []
            api_case_info_id = request.json.get("api_case_info_id", 0)
            if type(api_case_info_id) is not str and api_case_info_id > 0:
                filter_list.append(module_model.api_case_info_id == api_case_info_id)
            # 需要注意的是，需要在加载数据的时候，为了方便，我们直接通过run_order字段进行升序排列
            datas = module_model.query.order_by(module_model.run_order.asc()).filter(*filter_list).limit(
                page_size).offset((page - 1) * page_size).all()

            all_datas = []
            for data in datas:
                stepData = {"id": data.id,
                            "api_case_info_id": data.api_case_info_id,
                            "key_word_id": data.key_word_id,
                            "value": [],
                            "step_desc": data.step_desc,
                            "ref_variable": data.ref_variable,
                            "run_order": data.run_order
                            }
                # data["value"] = [操作对象的值，关键字的值]

                keyWordData = ApiKeyWord.query.filter(ApiKeyWord.id == data.key_word_id).first()
                OperationTypeData = OperationType.query.filter(
                    OperationType.id == keyWordData.operation_type_id).first()
                stepData["value"] = [OperationTypeData.ex_fun_name, keyWordData.keyword_fun_name]
                all_datas.append(stepData)
            # total = module_model.query.filter(*filter_list).count()
            print("当然的测试步骤数据为", all_datas)
            return respModel().ok_resp_listdata(lst=all_datas, total="查询成功")

    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")