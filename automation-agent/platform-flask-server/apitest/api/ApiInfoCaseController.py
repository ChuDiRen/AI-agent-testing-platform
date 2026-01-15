from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiInfoCaseModel import ApiInfoCase  # 请替换为你的模型类
from datetime import datetime

# 模块信息
module_name = "ApiInfoCase"  # 模块名称
module_model = ApiInfoCase  # 修改为相应的模型类
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


#
# 导入对应的需要用到的模块
import json, os, subprocess, uuid, yaml
from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
from apitest.model.ApiKeyWordModel import ApiKeyWord
from apitest.model.ApiDbBaseModel import ApiDbBase
from apitest.model.ApiInfoModel import ApiInfo


@module_route.route(f"/{module_name}/debugTest", methods=["POST"])
def debugTest():
    #  TODO 1：创建执行目录，用来存放测试用例和配置文件
    cases_dir = application.config['CASES_ROOT_DIR']
    # 该次执行唯一ID
    execute_uuid = uuid.uuid4().__str__()
    # 1.0 创建 该次执行对应的文件夹
    run_tmp_dir = os.path.join(cases_dir, execute_uuid)
    os.makedirs(run_tmp_dir, exist_ok=True)

    try:
        data_id = int(request.json["id"])
        with application.app_context():
            # 数据库查询,接收前端传递过来的 ApiInfo
            api_case_info = module_model.query.filter_by(id=data_id).first()
            # 数据库查询,用来接收当前 ApiInfo的测试步骤
            api_steps = ApiInfoCaseStep.query.order_by(ApiInfoCaseStep.run_order.asc()).filter_by(
                api_case_info_id=data_id).all()

            # 数据库查询, 附带当前项目的数据库信息
            filter_list = []
            filter_list.append(ApiDbBase.project_id == api_case_info.project_id)  # 当前项目
            filter_list.append(ApiDbBase.is_enabled == "1")  # 是启动的状态
            db_infos = ApiDbBase.query.filter(*filter_list).all()

        # 第一步： 组装 context.yaml 对应的信息
        test_case_config = {"_database": {}}

        # 0. 调试变量， 如果存在调试参数，则添加到 context 中
        if api_case_info.param_data:
            for d in json.loads(api_case_info.param_data):
                test_case_config.update({d["key"]: d["value"]})

        # 1. 加载项目数据库配置信息保存到 context.yaml
        for db_info in db_infos:
            test_case_config["_database"].update({db_info.ref_name: eval(db_info.db_info)})

        test_case_config.update()

        # 生成yaml文件夹
        test_case_filename = f"context.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
        generate_yaml(test_case_config, test_case_yaml_file)

        # 填充测试用例信息
        test_case_data = {
            "desc": api_case_info.case_name,
            "steps": [],  # 测试步骤
        }

        # 如果存在 前置脚本，则添加
        if api_case_info.pre_request:
            test_case_data["pre_script"] = []
            test_case_data["pre_script"].insert(0, api_case_info.pre_request)
        # 如果存在 后置脚本，则添加
        if api_case_info.post_request:
            test_case_data["post_script"] = []
            test_case_data["post_script"].insert(0, api_case_info.post_request)
        # 遍历添加对应的用例步骤
        case_file_name = uuid.uuid4()
        test_case_filename = f"{1}_{case_file_name}.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)

        all_case_steps = []

        #    把当前的用例拼接进去
        all_case_steps.extend(api_steps)

        # 遍历添加对应的测试步骤
        for api_step in all_case_steps:
            with application.app_context():
                # 获取对应的数据进行拼接
                apiKeyData = ApiKeyWord.query.filter_by(id=api_step.key_word_id).first()
                stepData = {api_step.step_desc: {
                    "关键字": apiKeyData.keyword_fun_name
                }}
                #  如果是：send_request 关键字则必须获取当前的用例id，把当前接口的信息直接拼写进来
                if apiKeyData.keyword_fun_name.startswith("send_request"):
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

        # 文件生成后生成完毕后
        report_root_dir = application.config['REPORT_ROOT_DIR']  # 测试报告目录
        key_words_dir = application.config['KEY_WORDS_DIR']  # 关键字目录

        os.makedirs(report_root_dir, exist_ok=True)  # 创建目录

        report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")  # 测试数据保存目录
        report_html_path = os.path.join(report_root_dir, execute_uuid)  # 测试html报告

        # 1. 执行测试
        remote_command = f"huace-apirun --cases={run_tmp_dir} --keyDir={key_words_dir} -sv --capture=tee-sys --alluredir={report_data_path} "
        subprocess.check_output(remote_command, shell=True, universal_newlines=True, encoding="utf-8")
        # 2. 生成html测试报告
        os.system(f"allure generate {report_data_path} -c -o {report_html_path}")  # 等于你在命令行里面执行 allure
        print("当前的报告路径", report_html_path + "/index.html")
        # 3. 删除一些临时文件，保留html测试报告即可
        # shutil.rmtree(run_tmp_dir)  # 测试套件临时yaml文件 collection_dir
        # shutil.rmtree(report_data_path)  # 测试工具执行后的测试结果数据

        return respModel.ok_resp_text(msg="执行完毕，请查看测试报告", data={
            "report_id": execute_uuid
        })
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"执行出现错误：{e}")



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
        requests_datas = parse_request_data(api_info.request_form_datas)
        if len(requests_datas.items()) > 0:
            steps_info.update({"data": requests_datas})

    # 3. 仅在 www_form_datas 不为空时添加
    if api_info.request_www_form_datas:
        requests_datas = parse_request_data(api_info.request_www_form_datas)
        if len(requests_datas.items()) > 0:
            steps_info.update({"data": requests_datas})

    # 4. 仅在 request_files 不为空时添加 ,注意，它是列表格式
    if api_info.request_files:
        request_files = parse_request_data(api_info.request_files)
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


# 扩展：上传文件解析接口
from xmindparser import xmind_to_dict
@module_route.route(f"/{module_name}/uploadFile", methods=["POST"])
def upload_file():
    """ 上传 XMind 文件并解析 """
    try:
        # 获取 project_id 参数，确定测试用例要上传的项目ID
        project_id = request.form.get("project_id")
        if not project_id:
            return respModel.error_resp("缺少 project_id 参数")

        # 获取上传的文件
        file = request.files.get("file")
        if not file or not file.filename.endswith(".xmind"):
            return respModel.error_resp("请上传有效的 XMind 文件")

        # 保存文件到临时目录
        import tempfile
        temp_dir = tempfile.mkdtemp()
        # 退出 with 块后自动删除临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            # 解析 XMind 文件
            xmind_data = xmind_to_dict(file_path)

        # 提取根节点下的第一层节点
        root_topic = xmind_data[0]["topic"]
        for child in root_topic["topics"]:
            case_name = child["title"]

            # 查找 desc 节点并获取其子节点的内容作为 case_desc
            case_desc = ""
            if "topics" in child:
                for topic in child["topics"]:
                    if topic["title"].lower() == "desc" and "topics" in topic and topic["topics"]:
                        case_desc = topic["topics"][0]["title"]
                        break

            # 保存到 APIcaseInfo 表
            with application.app_context():
                api_case_info = module_model(
                    case_name=case_name,
                    case_desc=case_desc,
                    project_id=project_id,
                    create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                )
                database.session.add(api_case_info)
                database.session.flush()  # 获取自增的 ID
                api_case_info_id = api_case_info.id
                database.session.commit()

            # 查找 steps 节点并提取其子节点作为步骤
            if "topics" in child:
                for topic in child["topics"]:
                    if topic["title"].lower() == "steps" and "topics" in topic:
                        for step in topic["topics"]:
                            step_desc = step["title"]
                            # 保存到 ApiInfoCaseStep 表
                            with application.app_context():
                                api_info_step = ApiInfoCaseStep(
                                    step_desc=step_desc,
                                    api_case_info_id=api_case_info_id,
                                    key_word_id=-1,  # 固定的key
                                    ref_variable="{}",  # 一定要给一个空字典
                                    create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
                                )
                                database.session.add(api_info_step)
                                database.session.commit()
        # 删除临时文件
        # import shutil
        # shutil.rmtree(temp_dir)

        return respModel.ok_resp(msg="文件导入数据并解析成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


