import json
import mimetypes
import os
import re
import time
from urllib.parse import unquote
from urllib.parse import urlencode

import allure
import jsonpath
import requests

from ..core.globalContext import g_context

class Keywords:
    """
    API 测试关键字类
    
    能力:
    - 传统关键字: send_request, ex_jsonData, assert_text_comparators 等
    """
    
    request = None

    @allure.step("参数数据")
    def send_request(self, **kwargs):
        """
        统一的 HTTP 请求关键字
        
        支持的参数:
        - method: 请求方法 (GET, POST, PUT, DELETE 等)
        - url/URL: 请求地址
        - headers/HEADERS: 请求头
        - params/PARAMS: URL 参数
        - data/DATA: 表单数据 (form-urlencoded)
        - json: JSON 数据
        - files/FILES: 上传文件
        - download: 是否下载响应内容到文件 (True/False)
        - timeout: 超时时间
        """
        self.request = requests.Session()
        
        # 剔除不需要的字段
        kwargs.pop("关键字", None)
        download = kwargs.pop("download", False)  # 是否下载响应
        
        # 兼容大写参数名
        url = kwargs.pop("URL", None) or kwargs.get("url")
        if url and "url" not in kwargs:
            kwargs["url"] = url
        
        headers = kwargs.pop("HEADERS", None)
        if headers and "headers" not in kwargs:
            kwargs["headers"] = headers
            
        params = kwargs.pop("PARAMS", None)
        if params and "params" not in kwargs:
            kwargs["params"] = params
            
        data = kwargs.pop("DATA", None)
        if data and "data" not in kwargs:
            kwargs["data"] = data
            
        files_param = kwargs.pop("FILES", None)
        if files_param and "files" not in kwargs:
            kwargs["files"] = files_param

        # 处理文件上传
        files = kwargs.get("files", [])
        if files:
            files = self.process_upload_files(files)
            kwargs["files"] = files

        # 初始化请求数据（用于错误时显示）
        params_val = kwargs.get("params") or {}
        params_str = urlencode(params_val) if params_val else ""
        url_with_params = f'{kwargs.get("url", "")}?{params_str}' if params_str else kwargs.get("url", "")
        request_data = {
            "url": unquote(url_with_params),
            "method": kwargs.get("method", "GET"),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data", "") or kwargs.get("json", "") or kwargs.get("files", ""),
            "response": ""
        }

        try:
            # 禁用 SSL 验证以避免网络环境问题
            kwargs.setdefault("verify", False)
            response = self.request.request(**kwargs)
            g_context().set_dict("current_response", response)
            # 设置 status_code 变量供断言使用
            g_context().set_dict("status_code", str(response.status_code))

            # 解析 URL 参数
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(response.url)
            url_params = parse_qs(parsed_url.query)
            params_dict = {k: v[0] if len(v) == 1 else v for k, v in url_params.items()}
            
            # 组装请求数据
            request_data = {
                "url": unquote(response.url),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "params": params_dict,
                "body": str(response.request.body) if response.request.body else "",
                "response": response.text,
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            }
            
            # 如果需要下载响应内容
            if download:
                file_path = self.save_response_content(response)
                request_data["download_path"] = file_path
                
            g_context().set_dict("current_response_data", request_data)
            
        except Exception as e:
            request_data["response"] = str(e)
            raise e
        finally:
            print("-----------current_response_data------------")
            print(request_data)
            print("----------end current_response_data-------------")


    def save_response_content(self, response, download_dir="/downloads"):
        # 创建下载目录（如果不存在）
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        content_type = response.headers.get("Content-Type", "")
        timestamp = int(time.time())  # 当前时间戳

        if "application/json" in content_type:
            # 处理JSON数据
            file_path = os.path.join(download_dir, f"response_{timestamp}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json_data = response.json()
                f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
            return file_path

        elif "application/octet-stream" in content_type:
            # 处理二进制文件
            # 从Content-Disposition获取文件名（如果有）
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition and "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('";')
            else:
                # 默认文件名
                filename = f"file_{timestamp}.bin"

            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return file_path
        else:
            # 不管是什么生成一个text文件
            print("未知文件类型")
            file_path = os.path.join(download_dir, f"response_{timestamp}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return file_path


    def process_upload_files(self, file_list):
        """
        处理上传文件，返回 requests 支持的 files 列表格式
        :param file_list: 文件列表，格式如 [{'file': 'path_or_url'}, {'avatar': 'path2'}]
        :return: 处理后的 files 列表
        """
        from urllib.parse import urlparse

        processed_files = []
        # 使用临时目录存储下载的文件
        download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        
        # 获取用例目录路径（用于解析相对路径）
        cases_dir = g_context().get_dict("_cases_dir")

        # 创建目录（如果不存在）
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for item in file_list:
            for field_name, file_path in item.items():
                # 判断是否是 URL
                if file_path.startswith(('http://', 'https://')):
                    try:
                        response = requests.get(file_path, stream=True)
                        response.raise_for_status()

                        # 提取文件名（从URL）
                        parsed_url = urlparse(file_path)
                        filename = os.path.basename(parsed_url.path)
                        if not filename:
                            filename = 'downloaded_file'

                        local_path = os.path.join(download_dir, filename)

                        # 写入本地文件
                        with open(local_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)

                        file_path = local_path  # 替换为本地路径
                    except Exception as e:
                        raise RuntimeError(f"文件下载失败: {file_path}, 错误: {e}")
                else:
                    # 本地文件路径处理
                    if not os.path.isabs(file_path):
                        # 相对路径：先尝试相对于用例目录
                        if cases_dir:
                            candidate_path = os.path.join(cases_dir, file_path)
                            if os.path.exists(candidate_path):
                                file_path = candidate_path
                        # 如果用例目录下找不到，保持原路径（可能是相对于当前工作目录）

                # 获取文件名和 MIME 类型
                file_name = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                # 添加到上传结构中
                processed_files.append(
                    (field_name, (file_name, open(file_path, 'rb'), mime_type))
                )

        return processed_files

    @allure.step("参数数据")
    def ex_jsonData(self, **kwargs):
        """
        提取json数据
        EXVALUE：提取josn的表达式
        INDEX: 非必填，默认为0
        VARNAME：存储的变量名
        """
        # 获取JsonPath的值
        EXPRESSION = kwargs.get("EXVALUE", None)
        # 获取对应的下标，非必填，默认为0字符串
        INDEX = str(kwargs.get("INDEX", "0"))
        #  判断INDEX 是不是数字 ，如果是则变成整形，如果不是则为0
        INDEX = int(INDEX) if INDEX.isdigit() else 0

        # 获取响应数据
        response = g_context().get_dict("current_response").json()
        ex_data = jsonpath.jsonpath(response, EXPRESSION)[INDEX]  # 通过JsonPath进行提取
        g_context().set_dict(kwargs["VARNAME"], ex_data)  # 根据变量名设置成全局变量
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")

    # ==================== Python 脚本执行 ====================

    @allure.step("执行Python脚本: {script_path}")
    def run_script(self, **kwargs):
        """
        执行 Python 脚本文件
        
        参数:
            script_path: 脚本文件路径（绝对路径或相对于用例目录的路径）
            function_name: 要调用的函数名（可选，如果不指定则执行整个脚本）
            variable_name: 保存返回值到变量（可选）
            其他参数: 将作为函数参数传递
        """
        from .script.run_script import exec_script_file
        
        script_path = kwargs.pop("script_path", None)
        function_name = kwargs.pop("function_name", None)
        variable_name = kwargs.pop("variable_name", None)
        kwargs.pop("关键字", None)
        
        if not script_path:
            raise ValueError("必须指定 script_path 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行脚本
        result = exec_script_file(
            script_path=script_path,
            context=context,
            caseinfo=None,
            function_name=function_name,
            **kwargs
        )
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"脚本返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("执行Python代码")
    def run_code(self, **kwargs):
        """
        执行 Python 代码片段
        
        参数:
            code: Python 代码字符串
            variable_name: 保存返回值到变量（可选，代码中使用 __result__ = xxx 设置返回值）
        """
        from .script.run_script import exec_script
        
        code = kwargs.get("code", "")
        variable_name = kwargs.get("variable_name")
        
        if not code:
            raise ValueError("必须指定 code 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行代码
        result = exec_script(code, context)
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"代码返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("参数数据")
    def ex_reData(self, **kwargs):
        """
        提取正则数据
        """
        # 获取JsonPath的值
        EXPRESSION = kwargs.get("EXVALUE", None)
        # 获取对应的下标，非必填，默认为0
        INDEX = kwargs.get("INDEX", 0)
        if INDEX is None:
            INDEX = 0
        # 获取响应数据
        response = g_context().get_dict("current_response").text
        # 使用findall方法找到所有匹配的结果，返回一个列表
        ex_data = re.findall(EXPRESSION, response)[INDEX]  # 通过正则表达进行提取
        g_context().set_dict(kwargs["VARNAME"], ex_data)  # 根据变量名设置成全局变量
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")

    # ==================== Python 脚本执行 ====================

    @allure.step("执行Python脚本: {script_path}")
    def run_script(self, **kwargs):
        """
        执行 Python 脚本文件
        
        参数:
            script_path: 脚本文件路径（绝对路径或相对于用例目录的路径）
            function_name: 要调用的函数名（可选，如果不指定则执行整个脚本）
            variable_name: 保存返回值到变量（可选）
            其他参数: 将作为函数参数传递
        """
        from .script.run_script import exec_script_file
        
        script_path = kwargs.pop("script_path", None)
        function_name = kwargs.pop("function_name", None)
        variable_name = kwargs.pop("variable_name", None)
        kwargs.pop("关键字", None)
        
        if not script_path:
            raise ValueError("必须指定 script_path 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行脚本
        result = exec_script_file(
            script_path=script_path,
            context=context,
            caseinfo=None,
            function_name=function_name,
            **kwargs
        )
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"脚本返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("执行Python代码")
    def run_code(self, **kwargs):
        """
        执行 Python 代码片段
        
        参数:
            code: Python 代码字符串
            variable_name: 保存返回值到变量（可选，代码中使用 __result__ = xxx 设置返回值）
        """
        from .script.run_script import exec_script
        
        code = kwargs.get("code", "")
        variable_name = kwargs.get("variable_name")
        
        if not code:
            raise ValueError("必须指定 code 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行代码
        result = exec_script(code, context)
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"代码返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("参数数据")
    def ex_mysqlData(self, **kwargs):
        """
        数据库: 数据库的名称
        SQL：查询的SQL
        引用变量：数据库要存储的变量名，列表格式,默认[]

        如果 引用变量 为空，则默认使用数据库字段名生成变量。
        如果 引用变量  有数据，则检查其长度是否与每条记录中的字段数量一致，若一致则生成对应格式的数据；否则抛出错误提示。

        存储到全局变量：{“变量名_下标”:数据}
        """
        import pymysql
        from pymysql import cursors
        config = {"cursorclass": cursors.DictCursor}
        # 读取全局变量 - 根据选择的数据 读取指定的数据库配置 连接对应的数据库
        db_config = g_context().get_dict("_database")[kwargs["数据库"]]
        config.update(db_config)

        con = pymysql.connect(**config)
        cur = con.cursor()
        cur.execute(kwargs["SQL"])
        rs = cur.fetchall()
        cur.close()
        con.close()
        print("数据库查询结果:", rs)

        var_names = kwargs.get("引用变量",  [])
        result = {}

        if not var_names:
            # var_names 为空，使用原始字段名
            for i, item in enumerate(rs, start=1):
                for key, value in item.items():
                    result[f"{key}_{i}"] = value
        else:
            # var_names 有数据，验证字段数量一致性
            field_length = len(rs[0]) if rs else 0
            if len(var_names) != field_length:
                print("❌ var_names 的长度与每条记录的字段数不一致，请检查输入！")
                raise ValueError("❌ var_names 的长度与每条记录的字段数不一致，请检查输入！")

            for idx, item in enumerate(rs, start=1):
                for col_idx, key in enumerate(item):
                    result[f"{var_names[col_idx]}_{idx}"] = item[key]
        g_context().set_by_dict(result)

    @allure.step("参数数据")
    def assert_text_comparators(self, **kwargs):
        """
        封装断言以进行不同的比较操作。

        参数:
        value (Any): 要比较的值。
        expected (Any): 预期的值。
        op_str (str): 操作符的字符串表示（如 '>', '<', '==' 等）。
        message (str, optional): 自定义的错误消息。

        返回:
        None: 如果断言成功，则不返回任何内容。

        引发:
        AssertionError: 如果断言失败。
        """
        comparators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }

        message = kwargs.get("MESSAGE", None)

        if kwargs["OP_STR"] not in comparators:
            raise ValueError(f"没有该操作方式: {kwargs['OP_STR']}")

        if not comparators[kwargs['OP_STR']](kwargs['VALUE'], kwargs["EXPECTED"]):
            if message:
                raise AssertionError(message)
            else:
                raise AssertionError(f"{kwargs['VALUE']} {kwargs['OP_STR']} {kwargs['EXPECTED']} 失败")

    def get_md5_from_bytes(self,data):
        """
        从字节流中计算 MD5 值
        :param data: bytes 数据
        :return: MD5 字符串
        """
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(data)
        return hash_md5.hexdigest()

    @allure.step("参数数据")
    def assert_files_by_md5_comparators(self, **kwargs):
        """
        value (Any): 要比较的值。
        expected (Any): 预期的值。
        """
        # 获取: 预期的值
        value_md5 = kwargs.get("value", None)
        # 获取：实际数据
        response = g_context().get_dict("current_response")

        if response.status_code == 200:
            # 获取响应的二进制内容
            file_content = response.content

            # 直接计算 MD5
            remote_md5 = self.get_md5_from_bytes(file_content)

            # 如果你还想和本地文件比对
            if value_md5 == remote_md5:
                print(f"✅ 本地与远程文件内容一致（MD5 值均为：{value_md5}）")
            else:
                print(f"❌ 本地与远程文件内容不一致\n"
                      f"    本地文件 MD5：{value_md5}\n"
                      f"    远程文件 MD5：{remote_md5}")
                raise AssertionError(f"❌ 本地与远程文件内容不一致\n"
                      f"    本地文件 MD5：{value_md5}\n"
                      f"    远程文件 MD5：{remote_md5}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            raise AssertionError(f"请求失败，状态码: {response.status_code}")
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")

    # ==================== Python 脚本执行 ====================

    @allure.step("执行Python脚本: {script_path}")
    def run_script(self, **kwargs):
        """
        执行 Python 脚本文件
        
        参数:
            script_path: 脚本文件路径（绝对路径或相对于用例目录的路径）
            function_name: 要调用的函数名（可选，如果不指定则执行整个脚本）
            variable_name: 保存返回值到变量（可选）
            其他参数: 将作为函数参数传递
        """
        from .script.run_script import exec_script_file
        
        script_path = kwargs.pop("script_path", None)
        function_name = kwargs.pop("function_name", None)
        variable_name = kwargs.pop("variable_name", None)
        kwargs.pop("关键字", None)
        
        if not script_path:
            raise ValueError("必须指定 script_path 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行脚本
        result = exec_script_file(
            script_path=script_path,
            context=context,
            caseinfo=None,
            function_name=function_name,
            **kwargs
        )
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"脚本返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("执行Python代码")
    def run_code(self, **kwargs):
        """
        执行 Python 代码片段
        
        参数:
            code: Python 代码字符串
            variable_name: 保存返回值到变量（可选，代码中使用 __result__ = xxx 设置返回值）
        """
        from .script.run_script import exec_script
        
        code = kwargs.get("code", "")
        variable_name = kwargs.get("variable_name")
        
        if not code:
            raise ValueError("必须指定 code 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行代码
        result = exec_script(code, context)
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"代码返回值已保存到变量 {variable_name}: {result}")
        
        return result




