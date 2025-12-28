from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo  # 修改导入的模型类
from datetime import datetime


module_name = "ApiCollectionInfo"  # 模块名称
module_model = ApiCollectionInfo
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 分页查询
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        with application.app_context():
            filter_list = []
            # ====筛选条件(如果有筛选条件，在这里拓展 - filter)
            # 添加名称模糊搜索条件
            collection_name = request.json.get("collection_name", "")
            if len(collection_name) > 0:
                filter_list.append(module_model.collection_name.like(f'%{collection_name}%'))
            # 添加 项目筛选条件
            project_id = request.json.get("project_id", 0)
            if type(project_id) is not str and project_id > 0:
                filter_list.append(module_model.project_id == project_id)
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
    """ 删除数据  删除的同时，需要处理掉中间表"""
    try:
        with application.app_context():
            module_model.query.filter_by(id=request.args.get("id")).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

# 扩展接口 - 执行用例接口
# 这里开始远程调用逻辑，生成两个文件夹,文件夹名字用UUID为后缀
import json, os, subprocess, uuid, yaml
# 模块信息,依次导入的包
from apitest.model.ApiDbBaseModel import ApiDbBase
from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiInfoCaseModel import ApiInfoCase
from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
from apitest.model.ApiKeyWordModel import ApiKeyWord

@module_route.route(f"/{module_name}/excuteTest", methods=["POST"])
def excuteTest():
    #当前函数绑定事件
    session = database.session

    # TODO : 第一步：正常生成对用的数据
    # 获取配置中指定的 临时文件生成地址
    cases_dir = application.config['CASES_ROOT_DIR']
    # 该次执行唯一ID
    execute_uuid = uuid.uuid4().__str__()
    # 1.0 创建 该次执行对应的文件夹
    run_tmp_dir = os.path.join(cases_dir, execute_uuid)
    os.makedirs(run_tmp_dir, exist_ok=True)

    try:
        # 获取测试计划ID
        data_id = int(request.json["id"])
        with application.app_context():
            # 1. 测试计划信息
            api_collection_info = module_model.query.filter_by(id=data_id).first()

            # 3. 数据库查询, 附带当前项目的数据库信息
            filter_list = []
            filter_list.append(ApiDbBase.project_id == api_collection_info.project_id)  # 当前项目
            filter_list.append(ApiDbBase.is_enabled == "1")  # 是启动的状态
            db_infos = ApiDbBase.query.filter(*filter_list).all()

            # 第一步： 组装 context.yaml 对应的信息
            test_case_config = {"_database": {}}
            # 0. 环境变量， 如果存在，则添加到 context 中
            if api_collection_info.collection_env:
                for d in json.loads(api_collection_info.collection_env):
                    test_case_config.update({d["key"]: d["value"]})

            # 1. 加载项目数据库配置信息保存到 context.yaml
            for db_info in db_infos:
                test_case_config["_database"].update({db_info.ref_name: eval(db_info.db_info)})

            # 生成context.yaml文件夹
            test_case_filename = f"context.yaml"
            test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
            generate_yaml(test_case_config, test_case_yaml_file)

            # 第二步： 生成每一步的测试用例信息
            with application.app_context():
                # 数据库查询,用来接收当前 Collection关联的对应的测试用例
                case_infos = ApiCollectionDetail.query.order_by(ApiCollectionDetail.run_order.asc()).filter_by(
                    collection_info_id=data_id).all()

            # 2.1 遍历每一个用例，生成对应的 yaml 文件
            for case_info in case_infos:
                # 测试用例信息
                case_file_name = uuid.uuid4()

                # 不是数字则给个0， 否则执行会报错
                run_order = case_info.run_order if isinstance(case_info.run_order, (int, float)) else 0

                test_case_filename = f"{run_order}_{case_file_name}.yaml"
                test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)

                with application.app_context():

                    # # 数据库查询 ApiInfoCase
                    api_case_info = ApiInfoCase.query.filter_by(id=case_info.api_case_info_id).first()
                    # 数据库查询,用来接收当前 WebInfo的测试步骤
                    api_steps = ApiInfoCaseStep.query.order_by(ApiInfoCaseStep.run_order.asc()).filter_by(
                        api_case_info_id=api_case_info.id).all()

                # 填充测试用例信息 - 基本格式
                test_case_data = {
                    "desc": api_case_info.case_name,
                    "steps": [],  # 测试步骤
                }

                # 2.1.0 DDT数据驱动信息
                ddt_datas = json.loads(case_info.ddt_param_data)
                if len(ddt_datas) > 0: test_case_data["ddts"] = []  # 如果有数据则填充
                for ddt_data in ddt_datas:
                    d = {}
                    for data in ddt_data:
                        d.update({data["key"]: data["value"]})
                    test_case_data["ddts"].append(d)

                # 2.1.1 前后置脚本信息
                # 如果存在 前置脚本，则添加 -- BUGFIX：之前按照换行符做的分割，会导致脚本运行失败
                if api_case_info.pre_request:
                    test_case_data["pre_script"] = []
                    test_case_data["pre_script"].insert(0, api_case_info.pre_request)
                # 如果存在 后置脚本，则添加
                if api_case_info.post_request:
                    test_case_data["post_script"] = []
                    test_case_data["post_script"].insert(0, api_case_info.post_request)

                # 2.1.2 测试步骤
                all_case_steps = []

                #    把当前的用例的步骤也拼接进去
                all_case_steps.extend(api_steps)

                # 遍历测试步骤，生成 执行器需要的格式数据
                for api_step in all_case_steps:
                    with application.app_context():
                        # 获取对应的数据进行拼接
                        keyWordData = ApiKeyWord.query.filter_by(id=api_step.key_word_id).first()

                        stepData = {api_step.step_desc: {
                            "关键字": keyWordData.keyword_fun_name
                        }}
                        #  判断关键字是否：send_request 关键字开头，如果是：send_request，则需要把接口信息读取出来进行拼接
                        if keyWordData.keyword_fun_name.startswith("send_request"):
                            # 获取当前用例"_接口信息" id：{"_接口信息":1}
                            case_id = json.loads(api_step.ref_variable).get("_接口信息")  # 注意和你的关键字的key一致
                            api_info = ApiInfo.query.filter_by(id=case_id).first()

                            # 把当前的用例写进来 - 调用对应的方法
                            case_steps_data = api_case_generate(api_info)

                        else:
                            # 加载每个步骤中的参数配置，更新到步骤信息中
                            case_steps_data = json.loads(api_step.ref_variable)
                        stepData[api_step.step_desc].update(case_steps_data)
                        test_case_data["steps"].append(stepData)

                generate_yaml(test_case_data, test_case_yaml_file)

        # 文件生成后生成完毕后，
        report_root_dir = application.config['REPORT_ROOT_DIR']  # 测试报告目录

        os.makedirs(report_root_dir, exist_ok=True)
        report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")  # 测试数据保存目录
        report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告

        # TODO 扩展：发送消息
        from core.RabbitMQ_Producer import send_perf_message
        routing_key = "api_queue" # 队列名称, 对应rabbitMQ中的队列名称，比如：api_queue、web_queue、app_queue
        message = {
            "coll_type": "api",  # 对应的类型, 对应api、web、app
            "case_collection_info": json.dumps(respModel().get_custom_attributes(api_collection_info),
                                               ensure_ascii=False),
            "report_data_path": report_data_path,
            "report_html_path": report_html_path,
            "run_tmp_dir": run_tmp_dir,
            "execute_uuid": execute_uuid
        }
        send_perf_message(routing_key=routing_key, message=json.dumps(message))

        # 扩展：保存任务信息，更新状态
        import redis
        from config.dev_settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
        coll_type = "api"
        key = f"task:{coll_type}_{data_id}_{execute_uuid}"
        with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD) as r:
            r.hset(key, "name", api_collection_info.collection_name)
            r.hset(key, "execute_uuid", execute_uuid)
            r.hset(key, "type", coll_type)
            r.hset(key, "status", "等待中")


        return respModel.ok_resp_text(msg="已将本次计划加入执行序列", data={
            "msg": "success"
        })

    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"执行出现错误：{e}")

def api_case_generate(api_info):
    steps_info = {}
    steps_info.update({
        "关键字": "send_request",  # 固定的KEY， 对应核心执行器
        "method": api_info.request_method,
        "url": api_info.request_url
    })

    # 0.仅在 params 不为空时添加
    if api_info.request_params:
        requests_params = parse_request_data(api_info.request_params)
        if len(requests_params.items()) > 0:
            steps_info.update({"params": requests_params})

    # 1. 如果存在请求头，则添加请求头
    if api_info.request_headers:
        requests_header = parse_request_data(api_info.request_headers)
        if len(requests_header.items()) > 0:
            steps_info.update({"headers": requests_header})

    # 2. 仅在 data 不为空时添加
    if api_info.request_form_datas:
        request_form_datas = parse_request_data(api_info.request_form_datas)
        if len(request_form_datas.items()) > 0:
            steps_info.update({"data": request_form_datas})

    # 3. 仅在 www_form_datas 不为空时添加
    if api_info.request_www_form_datas:
        request_www_form_datas = parse_request_data(api_info.request_www_form_datas)
        if len(request_www_form_datas.items()) > 0:
            steps_info.update({"data": request_www_form_datas})

    # 4. 仅在 request_files 不为空时添加 ,注意，它是列表格式
    if api_info.request_files:
        request_files = parse_request_data(api_info.request_files)
        # 转换为列表中的字典:{key:value,key:value,...}转成：[{key:value},{key:value}...]
        request_files = [{key: value} for key, value in request_files.items()]
        if len(request_files) > 0:
            steps_info.update({"files": request_files})

    # 5.仅在 json_data 不为空时添加
    if api_info.requests_json_data:
        steps_info.update({"json": json.loads(api_info.requests_json_data)})

    return steps_info


import ast
def parse_request_data(data):
    """
    安全解析请求数据（如 request_form_datas, request_params 等）

    :param data: 原始数据，可能是字符串或 Python 对象.
    :return: 解析后的字典 {key: value}
    """
    if not data:
        return {}

    try:
        # 尝试判断原始数据类型并解析
        if isinstance(data, str):
            try:
                # 先尝试使用 json.loads（更安全、支持 JSON 格式）
                data_list = json.loads(data)
            except json.JSONDecodeError:
                # 若 json 失败，再尝试 ast.literal_eval（兼容旧格式）
                data_list = ast.literal_eval(data)
        else:
            # 如果已经是 dict/list 类型，直接使用
            data_list = data

        # 组装 key-value 结构
        result = {}
        for item in data_list:
            if isinstance(item, dict):
                key = item.get("key")
                value = item.get("value")
                if key and value is not None:
                    result[key] = value
        return result

    except Exception as e:
        print(f"[parse_request_data] 数据解析失败: {e}")
        return {}


#  生成Yaml文件方法
import yaml
def generate_yaml(json_data, url_path):
    if url_path is None:
        raise ValueError("The 'filname' parameter is required.")

    url_path = url_path

    # 检查json_data是否是字典或JSON字符串
    if isinstance(json_data, dict):
        # 已经是字典，直接转换
        with open(url_path, 'w', encoding='utf-8') as file:
            yaml.dump(json_data, file, default_flow_style=False, sort_keys=False, allow_unicode=True)
    elif isinstance(json_data, str):
        try:
            # 尝试将JSON字符串加载为字典
            json_data = json.loads(json_data)
            with open(url_path, 'w', encoding='utf-8') as file:
                yaml.dump(json_data, file, default_flow_style=False, sort_keys=False, allow_unicode=True)
        except json.JSONDecodeError:
            raise ValueError("The provided string is not a valid JSON.")
    else:
        raise ValueError("The 'json_data' parameter must be a dictionary or a JSON string.")


# 扩展接口：复制测试集合计划
from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail

@module_route.route(f"/{module_name}/copyData", methods=["POST"])
def copyData():
    """ 复制的接口 """
    try:
        with application.app_context():
            # todo: 1. 获取当前测试集以及对应关联用例
            data_id = request.json["id"]
            # 数据库查询,接收前端传递过来的 Collection
            collection_info = module_model.query.filter_by(id=data_id).first()
            # 数据库查询,用来接收当前 Collection关联的对应的测试用例
            api_collection_detail = ApiCollectionDetail.query.order_by(ApiCollectionDetail.run_order.asc()).filter_by(collection_info_id=data_id).all()

            # todo：2. 拼接测试集和用例的数据
            coll_data = {"id": None,
                         "project_id": collection_info.project_id,
                         "collection_name": collection_info.collection_name + " copy",
                         "collection_desc":collection_info.collection_desc,
                         "collection_env":collection_info.collection_env,
                         "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                         }
            data = module_model(**coll_data)
            # 获取新增后的ID并返回
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            database.session.commit()

            # todo：3. 拼接用例的数据
            for case in api_collection_detail:
                case_data = {"id":None,
                             "collection_info_id": data_id,# 之前获取的测试集合的id
                             "api_case_info_id": case.api_case_info_id,
                             "ddt_param_data": case.ddt_param_data,
                             "run_order": case.run_order,
                             "create_time": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                            }
                data = ApiCollectionDetail(**case_data)
                # 获取新增后的ID并返回
                database.session.add(data)
                # 获取新增后的ID并返回
                database.session.flush()
                database.session.commit()
            return respModel.ok_resp(msg="复制成功", dic_t={"id": data_id})

    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")