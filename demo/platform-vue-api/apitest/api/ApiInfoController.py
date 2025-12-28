from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from apitest.model.ApiInfoModel import ApiInfo
from datetime import datetime

module_name = "ApiInfo"
module_model = ApiInfo
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        with application.app_context():
            filter_list = []
            # 添加 项目筛选条件
            project_id = request.json.get("project_id", 0)
            if type(project_id) is not str and project_id > 0:
                filter_list.append(module_model.project_id == project_id)
            # 添加 模块筛选条件
            module_id = request.json.get("module_id", 0)
            if type(module_id) is not str and module_id > 0:
                filter_list.append(module_model.module_id == module_id)
            # 添加名称模糊搜索条件
            api_name = request.json.get("api_name", "")
            if len(api_name) > 0:
                filter_list.append(module_model.api_name.like(f'%{api_name}%'))
            # 数据库查询
            datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
            return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    try:
        data_id = int(request.args.get("id"))
        with application.app_context():
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
    try:
        with application.app_context():
            module_model.query.filter_by(id=request.args.get("id")).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


# 扩展接口： 调试执行接口
import uuid, os, json, yaml
import subprocess
@module_route.route(f"/{module_name}/debug", methods=["POST"])
def debug_execute():
    try:
        # TODO 1. 当需要下载的时候，先进行获取标识
        # 如果是True，send_request 要改成send_request_and_download
        download_response = request.json.get("download_response", "")

        # TODO 1: 获取对应的测试用例信息
        with application.app_context():
            data_id = int(request.json["id"])
            api_info = module_model.query.filter_by(id=data_id).first()

        #  TODO 2：创建执行目录，用来存放测试用例和配置文件
        cases_dir = application.config['CASES_ROOT_DIR']
        # 该次执行唯一ID
        execute_uuid = uuid.uuid4().__str__()
        # 1.0 创建 该次执行对应的文件夹
        run_tmp_dir = os.path.join(cases_dir, execute_uuid)
        os.makedirs(run_tmp_dir, exist_ok=True)

        # TODO 3: 获取 Debug变量 数据，生成 context.yaml 文件
        context_data = {}  # 默认为空
        context_yaml_file = os.path.join(run_tmp_dir, "context.yaml")  # 创建 context.yaml 文件
        if api_info.debug_vars and api_info.debug_vars != "null":
            context_data = parse_request_data(api_info.debug_vars)
        with open(context_yaml_file, "w", encoding="utf-8") as context_file:
            yaml.dump(context_data, context_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        # TODO 4: 把数据转变为yaml 保存到 测试套件执行对应的文件夹
        # 1. 填充测试用例信息
        steps_info = {}
        test_case_data = {
            "desc": api_info.api_name,
            "steps": [
                {
                    api_info.api_name: steps_info
                }
            ]
        }

        if download_response is True:
            steps_info.update({
                "关键字": "send_request_and_download",  # 固定的KEY， 对应核心执行器
                "method": api_info.request_method,
                "url": api_info.request_url
            })
        else:
            steps_info.update({
                "关键字": "send_request",  # 固定的KEY， 对应核心执行器
                "method": api_info.request_method,
                "url": api_info.request_url
            })

        # 2. 仅在 params 不为空时添加
        if api_info.request_params:
            requests_params = parse_request_data(api_info.request_params)
            if len(requests_params.items()) > 0:
                steps_info.update({"params": requests_params})

        # 3. 如果存在请求头，则添加请求头
        if api_info.request_headers:
            requests_header = parse_request_data(api_info.request_headers)
            if len(requests_header.items()) > 0:
                steps_info.update({"headers": requests_header})

        # 4. 仅在 data 不为空时添加
        if api_info.request_form_datas:
            requests_datas = parse_request_data(api_info.request_form_datas)
            if len(requests_datas.items()) > 0:
                steps_info.update({"data": requests_datas})

        # 5. 仅在 www_form_datas 不为空时添加
        if api_info.request_www_form_datas:
            requests_datas = parse_request_data(api_info.request_www_form_datas)
            if len(requests_datas.items()) > 0:
                steps_info.update({"data": requests_datas})

        # 6. 仅在 request_files 不为空时添加 ,注意，它是列表格式
        if api_info.request_files:
            request_files = parse_request_data(api_info.request_files)
            request_files = [{key: value} for key, value in request_files.items()]
            if len(request_files) > 0:
                steps_info.update({"files": request_files})

        # 7. 仅在 json_data 不为空时添加
        if api_info.requests_json_data:
            steps_info.update({"json": json.loads(api_info.requests_json_data)})

        # 将测试用例数据写入 YAML 文件，格式为 执行顺序_名称.yaml
        case_file_name = uuid.uuid4()
        test_case_filename = f"1_{case_file_name}.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
        with open(test_case_yaml_file, "w", encoding="utf-8") as test_case_file:
            yaml.dump(test_case_data, test_case_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        # 执行测试
        remote_command = f"huace-apirun --cases={run_tmp_dir} -sv --capture=tee-sys "
        command_output = subprocess.check_output(remote_command, shell=True, text=True, errors='ignore')
        print("=" * 60)
        print("执行结果：", command_output)
        print("=" * 60)

        #  TODO 5: 提取响应数据，进行返回数据。
        command_output=parse_test_output(command_output)
        print("提取出来的响应数据：",command_output)

        #  TODO 6: 确定是否需要上传文件，如果需要则
        if command_output.get("current_response_file_path") is not None:
            file_path = command_output.get("current_response_file_path")
            # 获取 minio_client
            minio_client = application.extensions.get("minio_utils")
            if not minio_client:
                return respModel.error_resp("MinIO客户端未初始化")

            minio_client = application.extensions["minio_utils"]
            minio_client_url = application.config["MINIO_CLIENT_URL"]
            bucket_name = "apitest"  # 替换为你自己的桶名
            file_name = os.path.basename(file_path)  # 对象名（即 MinIO 中保存的路径）

            try:
                # 上传文件到 MinIO
                minio_client.upload_file(
                    bucket_name,
                    file_name,
                    file_path=file_path  # 注意：这里直接传文件路径"":f"{object_url}"
                )

                command_output.update({"current_response_file_path": f"{minio_client_url}/apitest/{file_name}"})
                return respModel.ok_resp(msg="执行结束", dic_t={"output": command_output})
            except Exception as e:
                print(f"MinIO上传失败: {e}")
                return respModel.error_resp(f"文件上传失败: {str(e)}")
        else:
            return respModel.ok_resp(msg="执行结束", dic_t={"output": command_output})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"执行出现错误：{e}")



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


import re
def parse_test_output(output):
    # 处理 Unicode 编码（如果需要）
    result = {
        'test_result': 'UNKNOWN',
        "file_path":""
    }

    # 提取测试结果
    result_pattern = r"========.*?========\n(PASSED|FAILED) \[100%\]"
    result_match = re.search(result_pattern, output)
    result['test_result'] = result_match.group(1) if result_match else "UNKNOWN"

    # 提取请求数据和响应数据
    pattern = r"-+current_response_data-+\n(.*?)\n-+end current_response_data-+"
    match = re.search(pattern, output, re.DOTALL)

    if match:
        content = match.group(1).strip()
        try:
            raw_data = ast.literal_eval(content)
            result.update(raw_data)
        except Exception as e:
            print("解析失败:", e)
    else:
        print("未找到匹配的内容")

    #  提取下载的文件路径
        pattern = r"'current_response_file_path':\s*'([^']+)"
        match = re.search(pattern, output)

        if match:
            file_path = match.group(1)  # 获取匹配到的文件路径
            result.update(file_path)
    return result


import requests
@module_route.route(f"/{module_name}/importSwagger", methods=["POST"])
def import_swagger():
    try:
        # 获取前端传入的参数
        swagger_url = request.json.get("host")
        version = request.json.get("version")
        project_id = request.json.get("project_id")  # 新增：获取 project_id

        if not all([swagger_url, version, project_id]):
            return respModel.error_resp("缺少必要参数：host, version, project_id")

        # 发送 HTTP 请求获取 Swagger JSON 数据
        response = requests.get(swagger_url)
        if response.status_code != 200:
            return respModel.error_resp(f"无法访问 Swagger API: {swagger_url}")

        swagger_data = response.json()

        # 解析 Swagger 数据
        base_path = swagger_data.get("basePath", "")
        paths = swagger_data.get("paths", {})
        host = swagger_data.get("host")

        # 数据库插入逻辑
        inserted_count = 0
        with application.app_context():
            for path, methods in paths.items():
                for method, details in methods.items():
                    # 构造完整 URL
                    # 修改: 确保 request_url 正确拼接，避免多余的斜杠
                    request_url = f"http://{host}/{base_path.rstrip('/')}{path.lstrip('/')}" if base_path else f"http://{host}/{path.lstrip('/')}"

                    # 根据请求方式决定参数存放位置
                    if method.lower() == "post":
                        # POST 请求参数放在 request_form_datas 中
                        request_form_datas = []
                        for param in details.get("parameters", []):
                            request_form_datas.append({
                                "key": param.get("name"),
                                "value": ""  # 参数值置空
                            })
                        request_params = []
                    else:
                        # 其他请求方式参数放在 request_params 中
                        request_params = []
                        for param in details.get("parameters", []):
                            request_params.append({
                                "key": param.get("name"),
                                "value": ""  # 参数值置空
                            })
                        request_form_datas = []

                    # 提取请求头
                    request_headers = []
                    for header in details.get("headers", []):
                        request_headers.append({
                            "key": header.get("name"),
                            "value": ""  # 请求头值置空
                        })

                    # 构造 APIInfo 对象
                    api_info = ApiInfo(
                        api_name=details.get("summary", ""),
                        project_id=project_id,  # 新增：设置 project_id
                        request_method=method.upper(),
                        request_url=request_url,
                        request_params=json.dumps(request_params),
                        request_form_datas=json.dumps(request_form_datas),
                        request_www_form_datas="[]",
                        request_headers=json.dumps(request_headers),
                        debug_vars="[]",
                        requests_json_data="{}",
                        request_files="[]",
                        create_time=datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'),
                    )

                    # 插入数据库
                    database.session.add(api_info)
                    inserted_count += 1
            # 提交事务
            database.session.commit()

        return respModel.ok_resp(msg=f"成功导入 {inserted_count} 条 API 数据")

    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"导入失败：{e}")