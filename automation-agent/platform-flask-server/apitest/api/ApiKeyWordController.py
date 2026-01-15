import os
from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiKeyWordModel import ApiKeyWord  # 请替换为你的ApiModule模型类
from datetime import datetime

# 模块信息
module_name = "ApiKeyWord"  # 模块名称
module_model = ApiKeyWord
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
            # 添加关键字描述搜索条件
            name = request.json.get("name", "")
            if len(name) > 0:
                filter_list.append(module_model.name.like(f'%{name}%'))
            # 添加操作类型进行查询
            operation_type_id = request.json.get("operation_type_id", 0)
            if type(operation_type_id) is not str and operation_type_id > 0:
                filter_list.append(module_model.operation_type_id == operation_type_id)
            # 添加页面筛选条件
            page_id = request.json.get("page_id", 0)
            if type(page_id) is not str and page_id > 0:
                filter_list.append(module_model.page_id == page_id)
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


#  修改新增接口，当keyword_fun_name 在数据库存在则不能添加
@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with application.app_context():
            # 确定关键字唯一
            request.json["id"] = None  # ID自增长
            keyword_fun_name = request.json["keyword_fun_name"]  # 关键字名获取

            # 进行查询确定是否有关键字数据
            data = module_model.query.filter_by(keyword_fun_name=keyword_fun_name).first()

            if data:
                # 如果有数据则提示用户：关键字重复
                return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")
            else:
                data = module_model(**request.json,
                                    create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))
                database.session.add(data)
                # 获取新增后的ID并返回
                database.session.flush()
                data_id = data.id
                database.session.commit()
                return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

# @module_route.route(f"/{module_name}/update", methods=["PUT"])
# def update():
#     """ 修改数据 """
#     try:
#         with application.app_context():
#             module_model.query.filter_by(id=request.json["id"]).update(request.json)
#             database.session.commit()
#         return respModel.ok_resp(msg="修改成功")
#     except Exception as e:
#         print(e)
#         return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

#  更新接口，当keyword_fun_name 在数据库存在则不能修改为它
@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with application.app_context():
            keyword_fun_name = request.json["keyword_fun_name"]  # 关键字名获取
            keyword_id = request.json["id"]  # id获取,更新的是当前的数据、查询的也是这个数据，则过滤
            # 进行查询确定是否有关键字数据
            data = module_model.query.filter_by(keyword_fun_name=keyword_fun_name).first()

            if data and (data.id != keyword_id):
                # 如果有数据则提示用户：关键字重复
                return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")
            else:
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

#  扩展接口： 生成关键字文件
@module_route.route(f"/{module_name}/keywordFile", methods=["POST"])
def keywordFile():
    try:
        with application.app_context():
            file_name = request.json["keyword_fun_name"]  # 方法名
            keyword_value = request.json["keyword_value"]  # 方法体

            key_words_dir = application.config['KEY_WORDS_DIR'] # 关键字目录
            os.makedirs(key_words_dir, exist_ok=True) # 如果没有则创建
            with open(f'{key_words_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
                f.write(keyword_value)

        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

# 扩展方法： 查询所有关键字数据
# 生成对应的联级数据
from apitest.model.ApiOperationTypeModel import OperationType
@module_route.route(f"/{module_name}/queryAllKeyWordList", methods=["GET"])
def queryAllKeyWordList():
    with application.app_context():
        all_datas = []

        allOperationType = OperationType.query.all()
        for data in allOperationType:
            #  初始数据
            apidata = {"id": "", "value": "", "label": "", "children": []}
            # 设置父类
            apidata["id"] = data.id
            apidata["value"] = data.ex_fun_name
            apidata["label"] = data.operation_type_name

            # 搜索当前操作方法的对应的关键字方法并且设置为子类
            apiKeydata = module_model.query.filter(module_model.operation_type_id == data.id).all()
            for data in apiKeydata:
                i = {}
                i["id"] = data.id
                i["value"] = data.keyword_fun_name
                i["label"] = data.name
                i["keyword_desc"] = data.keyword_desc
                apidata["children"].append(i)

            #  把对应的数据加入到到所有数据中。
            all_datas.append(apidata)
        print("打印看看拼接后的数据：", all_datas)
    # 注意这里的返回数据，不能用之前的响应，因为这个是我们拼接的数据，没有特殊的数据，直接返回就好了。
    return respModel().ok_resp_listdata(lst=all_datas, msg="查询成功")