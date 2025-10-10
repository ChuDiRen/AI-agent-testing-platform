import mimetypes
from importlib.metadata import files

import allure
# 注: selenium 导入已移除,因为实际未使用且导入路径错误

from ..core.globalContext import g_context  # 修改为相对导入
import requests
import jsonpath
import re
import time
import os
import json
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import urlencode

class Keywords:
    request = None

    # def __init__(self, request: requests):
    #     self.request = requests.Session()

    @allure.step(">>>>>>参数数据：")
    def send_request(self, **kwargs):
        self.request = requests.Session()
        # 剔除不需要的字段，例如 关键字
        kwargs.pop("关键字", None)  # 如果存在 关键字 字段则删除，否则不操作

        files = kwargs.get("files", [])

        if files:
            files = self.process_upload_files(files)
            kwargs.update(files=files)

        #  先初始化请求数据，避免接口请求不通过，前端没有请求数据显示
        request_data = {
            "url": unquote(f'{kwargs.get("url", "")}?{urlencode(kwargs.get("params", ""))}'),
            "method": kwargs.get("method", ""),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data", "") or kwargs.get("json", "") or kwargs.get("files", ""),
            "response": kwargs.get("response", "")
        }

        try:
            #  可能报错
            response = self.request.request(**kwargs)

            g_context().set_dict("current_response", response)  # 默认设置成全局变量-- 对象

            #  组装请求数据到全局变量，从response进行获取。方便平台进行显示, 可能请求出错，所以结合请求数据进行填写
            request_data = {
                "url": unquote(response.url),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": str(response.request.body) if response.request.body else "", # 避免返回的是二进制数据 接口端报错。
                "response": response.text,
                "status_code": response.status_code,
                "elapsed": str(response.elapsed.total_seconds()) + "s"
            }
            g_context().set_dict("current_response_data", request_data)  # 默认设置成全局变量

            # 设置常用的响应数据到全局变量，方便后续断言使用
            g_context().set_dict("response_status_code", response.status_code)
            g_context().set_dict("response_text", response.text)
            g_context().set_dict("response_json", response.json() if response.headers.get('content-type', '').startswith('application/json') else None)

        except Exception as e:
            request_data.update({"response":str(e), "status_code": 0})
            g_context().set_dict("current_response_data", request_data)
            raise e
        finally:
            print("-----------current_response_data------------")
            print(request_data)  # 一定要打印，后续是利用它进行前端的显示
            print("----------end current_response_data-------------")


    @allure.step(">>>>>>参数数据：")
    def send_request_and_download(self, **kwargs):
        self.request = requests.Session()
        # 剔除不需要的字段，例如 EXVALUE
        kwargs.pop("关键字", None)  # 如果存在 关键字 字段则删除，否则不操作

        files = kwargs.get("files", [])

        if files:
            files = self.process_upload_files(files)
            kwargs.update(files=files)

        #  先初始化请求数据，避免接口请求不通过，前端没有请求数据显示
        request_data = {
            "url": unquote(f'{kwargs.get("url", "")}?{urlencode(kwargs.get("params", ""))}'),
            "method": kwargs.get("method", ""),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data", "") or kwargs.get("json", "") or kwargs.get("files", ""),
            "response": kwargs.get("response", ""),
            "current_response_file_path": ""
        }

        try:
            #  可能报错
            response = self.request.request(**kwargs)

            g_context().set_dict("current_response", response)  # 默认设置成全局变量-- 对象

            # 进行上传文件，固定命名：response_时间.文件扩展名
            # 判断response.text的格式，如果是文件，则下载到本地，并返回下载后的文件路径
            # 如果是json，则返回 json，则下载到本地，并返回下载后的文件路径
            # 调用对应的方法，并且返回对应的路径
            file_path = self.save_response_content(response)

            print("-----------------------")
            print(response.text)
            print("-----------------------")

            #  组装请求数据到全局变量，从response进行获取。方便平台进行显示, 可能请求出错，所以结合请求数据进行填写
            request_data = {
                "url": unquote(response.url),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": response.request.body,
                "response": response.text,
                "current_response_file_path":file_path
            }
            g_context().set_dict("current_response_data", request_data)  # 默认设置成全局变量

        except Exception as e:
            request_data.update({"response":str(e)})
            raise e
        finally:
            print("-----------current_response_data------------")
            print(request_data)  # 一定要打印，后续是利用它进行前端的显示
            print("----------end current_response_data-------------")



    # @allure.step(">>>>>>参数数据：")
    # def send_request_and_download(self, **kwargs):
    #     self.request = requests.Session()
    #     # 剔除不需要的字段，例如 EXVALUE
    #     kwargs.pop("关键字", None)  # 如果存在 关键字 字段则删除，否则不操作
    #
    #     files = kwargs.get("files", [])
    #
    #     if files:
    #         files = self.process_upload_files(files)
    #         kwargs.update(files=files)
    #
    #     response = self.request.request(**kwargs)
    #     g_context().set_dict("current_response", response)  # 默认设置成全局变量
    #
    #     # 进行上传文件，固定命名：response_时间.文件扩展名
    #     # 判断response.text的格式，如果是文件，则下载到本地，并返回下载后的文件路径
    #     # 如果是json，则返回 json，则下载到本地，并返回下载后的文件路径
    #     # 调用对应的方法，并且返回对应的路径
    #     file_path = self.save_response_content(response)
    #
    #     g_context().set_dict("current_response_file_path", file_path)  # 默认设置成全局变量
    #     print("-----------------------")
    #     print(response.text)
    #     print("-----------------------")
    #     print("-----------------------")
    #     print(g_context().show_dict())  # 一定要，不然影响测试平台；需要提取这个地址的字段进行下载
    #     print("-----------------------")

    # def process_upload_files(self, file_list):
    #     """
    #     处理上传文件，返回 requests 支持的 files 列表格式
    #     :param file_list: 文件列表，格式如 [{'file': 'path'}, {'avatar': 'path2'}]
    #     :return: 处理后的 files 列表
    #     """
    #     processed_files = []
    #     for item in file_list:
    #         for field_name, file_path in item.items():
    #             import os
    #             file_name = os.path.basename(file_path)
    #             mime_type, _ = mimetypes.guess_type(file_path)
    #             if not mime_type:
    #                 mime_type = 'application/octet-stream'
    #             processed_files.append(
    #                 (field_name, (file_name, open(file_path, 'rb'), mime_type))
    #             )
    #     return processed_files


    def save_response_content(self,response, download_dir="/downloads"):
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

        import os
        import requests as req
        from urllib.parse import urlparse

        processed_files = []
        download_dir = r'/img'  # 本地保存路径

        # 创建目录（如果不存在）
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for item in file_list:
            for field_name, file_path in item.items():
                # 判断是否是 URL
                if file_path.startswith(('http://', 'https://')):
                    try:
                        response = req.get(file_path, stream=True)
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


    @allure.step(">>>>>>参数数据：")
    def request_post_form_urlencoded(self, **kwargs):
        """
        发送Post请求
        """
        url = kwargs.get("URL", None)
        params = kwargs.get("PARAMS", None)
        headers = kwargs.get("HEADERS", None)
        data = kwargs.get("DATA", None)

        request_data = {
            "url": url,
            "params": params,
            "headers": headers,
            "data": data,
        }

        response = requests.post(**request_data)
        g_context().set_dict("current_response", response)  # 默认设置成全局变量
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    def request_post_row_json(self, **kwargs):
        """
        发送Post请求
        """
        url = kwargs.get("URL", None)
        params = kwargs.get("PARAMS", None)
        headers = kwargs.get("HEADERS", None)
        data = kwargs.get("DATA", None)

        request_data = {
            "url": url,
            "params": params,
            "headers": headers,
            "json": data,
        }

        response = requests.post(**request_data)
        g_context().set_dict("current_response", response)  # 默认设置成全局变量
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    def request_post_form_data(self, **kwargs):
        """
        发送Post请求
        """
        url = kwargs.get("URL", None)
        params = kwargs.get("PARAMS", None)
        headers = kwargs.get("HEADERS", None)
        data = kwargs.get("DATA", None)
        files = kwargs.get("FILES", None)

        request_data = {
            "url": url,
            "params": params,
            "headers": headers,
            "files": files,
            "data": data,
        }

        response = requests.post(**request_data)
        g_context().set_dict("current_response", response)  # 默认设置成全局变量
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    def request_get(self, **kwargs):
        """
        发送GET请求
        """
        url = kwargs.get("URL", None)
        params = kwargs.get("PARAMS", None)
        headers = kwargs.get("HEADERS", None)

        request_data = {
            "url": url,
            "params": params,
            "headers": headers,
        }
        response = requests.get(**request_data)
        g_context().set_dict("current_response", response)  # 默认设置成全局变量
        print("-----------------------")
        print(response.json())
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
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

    @allure.step(">>>>>>参数数据：")
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

    @allure.step(">>>>>>参数数据：")
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

    @allure.step(">>>>>>参数数据：")
    def assert_text_comparators(self, **kwargs):
        """
        封装断言以进行不同的比较操作。

        参数:
        ACTUAL (Any): 实际值
        EXPECTED (Any): 期望值
        OPERATOR (str): 操作符
        MESSAGE (str, optional): 自定义的错误消息
        """
        from ..services.assertion_service import AssertionService

        actual = kwargs.get("ACTUAL")
        expected = kwargs.get("EXPECTED")
        operator = kwargs.get("OPERATOR", "equals")
        message = kwargs.get("MESSAGE", "")

        # 映射旧的操作符到新的操作符
        operator_mapping = {
            '>': 'greater_than',
            '<': 'less_than',
            '==': 'equals',
            '>=': 'greater_equal',
            '<=': 'less_equal',
            '!=': 'not_equals',
            'contains': 'contains',
            'not_contains': 'not_contains'
        }

        new_operator = operator_mapping.get(operator, operator)

        try:
            result = AssertionService.execute_assertion(new_operator, actual, expected)
            if not result.success:
                error_msg = message if message else result.message
                raise AssertionError(error_msg)
            print(f"✅ 断言成功: {result.message}")
        except Exception as e:
            print(f"❌ 断言失败: {str(e)}")
            raise

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

    @allure.step(">>>>>>参数数据：")
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
            raise AssertionError(f"请求失败，状态码: {response.status_code}")
            print(f"请求失败，状态码: {response.status_code}")
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    def assert_status_code(self, **kwargs):
        """
        断言响应状态码
        """
        expected_status = kwargs.get("EXPECTED", 200)
        actual_status = g_context().get_dict("response_status_code")

        if actual_status != expected_status:
            raise AssertionError(f"状态码断言失败: 期望 {expected_status}, 实际 {actual_status}")

        print(f"✅ 状态码断言成功: {actual_status}")

    @allure.step(">>>>>>参数数据：")
    def assert_response_contains(self, **kwargs):
        """
        断言响应内容包含指定文本
        """
        expected_text = kwargs.get("EXPECTED", "")
        response_text = g_context().get_dict("response_text", "")

        if expected_text not in response_text:
            raise AssertionError(f"响应内容断言失败: 响应中不包含文本 '{expected_text}'")

        print(f"✅ 响应内容断言成功: 包含文本 '{expected_text}'")

    @allure.step(">>>>>>参数数据：")
    def assert_json_path_exists(self, **kwargs):
        """
        断言JSON路径存在
        """
        json_path = kwargs.get("JSON_PATH", "")
        response_json = g_context().get_dict("response_json", {})

        if not response_json:
            raise AssertionError("JSON路径断言失败: 响应不是JSON格式")

        try:
            result = jsonpath.jsonpath(response_json, json_path)
            if not result:
                raise AssertionError(f"JSON路径断言失败: 路径 '{json_path}' 不存在")
            print(f"✅ JSON路径断言成功: 路径 '{json_path}' 存在, 值: {result[0]}")
        except Exception as e:
            raise AssertionError(f"JSON路径断言失败: {str(e)}")

    @allure.step(">>>>>>参数数据：")
    def sleep(self, **kwargs):
        """
        等待指定秒数
        """
        seconds = kwargs.get("SECONDS", 1)
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)

    @allure.step(">>>>>>参数数据：")
    def set_variable(self, **kwargs):
        """
        设置变量到全局上下文
        """
        var_name = kwargs.get("VAR_NAME", "")
        var_value = kwargs.get("VAR_VALUE", "")

        if not var_name:
            raise ValueError("变量名不能为空")

        g_context().set_dict(var_name, var_value)
        print(f"✅ 设置变量: {var_name} = {var_value}")

    @allure.step(">>>>>>参数数据：")
    def log_message(self, **kwargs):
        """
        输出日志消息
        """
        message = kwargs.get("MESSAGE", "")
        level = kwargs.get("LEVEL", "INFO").upper()

        if level == "ERROR":
            print(f"❌ ERROR: {message}")
        elif level == "WARNING":
            print(f"⚠️  WARNING: {message}")
        elif level == "SUCCESS":
            print(f"✅ SUCCESS: {message}")
        else:
            print(f"ℹ️  INFO: {message}")

    @allure.step(">>>>>>参数数据：")
    def assert_response_time(self, **kwargs):
        """
        断言响应时间
        """
        from ..services.assertion_service import AssertionService

        max_time = kwargs.get("MAX_TIME", 5.0)  # 默认最大5秒
        response = g_context().get_dict("current_response")

        if not response:
            raise AssertionError("无法获取响应对象，请先发送请求")

        actual_time = response.elapsed.total_seconds()
        result = AssertionService.assert_less_than(actual_time, max_time)

        if not result.success:
            raise AssertionError(f"响应时间断言失败: {actual_time:.2f}s > {max_time}s")
        print(f"✅ 响应时间断言成功: {actual_time:.2f}s < {max_time}s")

    @allure.step(">>>>>>参数数据：")
    def assert_response_header(self, **kwargs):
        """
        断言响应头
        """
        header_name = kwargs.get("HEADER_NAME", "")
        expected_value = kwargs.get("EXPECTED_VALUE", "")
        operator = kwargs.get("OPERATOR", "equals")

        response = g_context().get_dict("current_response")
        if not response:
            raise AssertionError("无法获取响应对象，请先发送请求")

        actual_value = response.headers.get(header_name)

        if actual_value is None:
            raise AssertionError(f"响应头中不存在: {header_name}")

        from ..services.assertion_service import AssertionService
        result = AssertionService.execute_assertion(operator, actual_value, expected_value)

        if not result.success:
            raise AssertionError(f"响应头断言失败: {header_name} - {result.message}")
        print(f"✅ 响应头断言成功: {header_name} - {result.message}")

    @allure.step(">>>>>>参数数据：")
    def assert_response_schema(self, **kwargs):
        """
        断言响应JSON结构
        """
        expected_schema = kwargs.get("SCHEMA", {})
        response_json = g_context().get_dict("response_json", {})

        if not response_json:
            raise AssertionError("响应不是JSON格式")

        def validate_schema(data: dict, schema: dict, path: str = "") -> list:
            """递归验证JSON结构"""
            errors = []

            for key, expected_type in schema.items():
                current_path = f"{path}.{key}" if path else key

                if key not in data:
                    errors.append(f"缺少字段: {current_path}")
                    continue

                actual_value = data[key]

                # 处理嵌套对象
                if isinstance(expected_type, dict):
                    if not isinstance(actual_value, dict):
                        errors.append(f"字段 {current_path} 应该是对象，实际是 {type(actual_value).__name__}")
                    else:
                        errors.extend(validate_schema(actual_value, expected_type, current_path))
                # 处理数组
                elif isinstance(expected_type, list) and expected_type:
                    expected_item_type = expected_type[0]
                    if not isinstance(actual_value, list):
                        errors.append(f"字段 {current_path} 应该是数组，实际是 {type(actual_value).__name__}")
                    else:
                        for i, item in enumerate(actual_value):
                            item_path = f"{current_path}[{i}]"
                            if isinstance(expected_item_type, dict) and isinstance(item, dict):
                                errors.extend(validate_schema(item, expected_item_type, item_path))
                            elif not isinstance(item, type(expected_item_type)):
                                errors.append(f"数组项 {item_path} 类型错误，期望 {type(expected_item_type).__name__}")
                else:
                    # 处理基本类型
                    expected_type_name = {
                        str: "string",
                        int: "integer",
                        float: "number",
                        bool: "boolean",
                        type(None): "null"
                    }.get(expected_type, str(expected_type))

                    if not isinstance(actual_value, expected_type):
                        errors.append(f"字段 {current_path} 类型错误，期望 {expected_type_name}，实际 {type(actual_value).__name__}")

            return errors

        errors = validate_schema(response_json, expected_schema)
        if errors:
            raise AssertionError(f"JSON结构断言失败:\n" + "\n".join(f"  - {error}" for error in errors))

        print("✅ JSON结构断言成功: 响应结构符合预期")

    @allure.step(">>>>>>参数数据：")
    def assert_database_query(self, **kwargs):
        """
        断言数据库查询结果
        """
        query = kwargs.get("QUERY", "")
        expected_count = kwargs.get("EXPECTED_COUNT", None)
        expected_data = kwargs.get("EXPECTED_DATA", None)

        try:
            import pymysql
            from pymysql import cursors

            # 获取数据库配置
            db_config = g_context().get_dict("_database", {}).get(kwargs.get("DATABASE", "default"))
            if not db_config:
                raise AssertionError("数据库配置不存在")

            config = {"cursorclass": cursors.DictCursor}
            config.update(db_config)

            con = pymysql.connect(**config)
            cur = con.cursor()
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            con.close()

            if expected_count is not None:
                from ..services.assertion_service import AssertionService
                result = AssertionService.assert_equals(len(results), expected_count)
                if not result.success:
                    raise AssertionError(f"数据库查询结果数量断言失败: {result.message}")

            if expected_data is not None:
                if not results:
                    raise AssertionError("数据库查询结果为空，无法进行数据比较")

                # 比较第一条记录
                first_record = results[0]
                for key, expected_value in expected_data.items():
                    actual_value = first_record.get(key)
                    if actual_value != expected_value:
                        raise AssertionError(f"数据库字段 {key} 值不匹配: 期望 {expected_value}, 实际 {actual_value}")

            print(f"✅ 数据库查询断言成功: 查询返回 {len(results)} 条记录")

        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"数据库查询断言失败: {str(e)}")

    @allure.step(">>>>>>参数数据：")
    def assert_file_exists(self, **kwargs):
        """
        断言文件存在
        """
        file_path = kwargs.get("FILE_PATH", "")

        import os
        exists = os.path.exists(file_path)

        if not exists:
            raise AssertionError(f"文件断言失败: 文件不存在 - {file_path}")

        print(f"✅ 文件断言成功: 文件存在 - {file_path}")

    @allure.step(">>>>>>参数数据：")
    def assert_file_size(self, **kwargs):
        """
        断言文件大小
        """
        file_path = kwargs.get("FILE_PATH", "")
        expected_size = kwargs.get("EXPECTED_SIZE", 0)
        operator = kwargs.get("OPERATOR", "equals")

        import os
        if not os.path.exists(file_path):
            raise AssertionError(f"文件大小断言失败: 文件不存在 - {file_path}")

        actual_size = os.path.getsize(file_path)

        from ..services.assertion_service import AssertionService
        result = AssertionService.execute_assertion(operator, actual_size, expected_size)

        if not result.success:
            raise AssertionError(f"文件大小断言失败: {result.message}")

        print(f"✅ 文件大小断言成功: {result.message}")

    @allure.step(">>>>>>参数数据：")
    def soft_assert(self, **kwargs):
        """
        软断言 - 断言失败不会终止测试，只记录结果
        """
        assertion_type = kwargs.get("TYPE", "equals")
        actual = kwargs.get("ACTUAL")
        expected = kwargs.get("EXPECTED")
        message = kwargs.get("MESSAGE", "")

        from ..services.assertion_service import AssertionService

        try:
            result = AssertionService.execute_assertion(assertion_type, actual, expected)

            # 将软断言结果存储到全局变量中
            soft_assert_results = g_context().get_dict("soft_assert_results", [])
            soft_assert_results.append({
                "type": assertion_type,
                "actual": actual,
                "expected": expected,
                "success": result.success,
                "message": result.message,
                "custom_message": message
            })
            g_context().set_dict("soft_assert_results", soft_assert_results)

            if result.success:
                print(f"✅ 软断言成功: {result.message}")
            else:
                print(f"⚠️  软断言失败: {result.message} (测试继续)")

        except Exception as e:
            print(f"⚠️  软断言错误: {str(e)} (测试继续)")

            # 记录错误到软断言结果
            soft_assert_results = g_context().get_dict("soft_assert_results", [])
            soft_assert_results.append({
                "type": assertion_type,
                "actual": actual,
                "expected": expected,
                "success": False,
                "message": str(e),
                "custom_message": message,
                "error": True
            })
            g_context().set_dict("soft_assert_results", soft_assert_results)

    @allure.step(">>>>>>参数数据：")
    def validate_soft_asserts(self, **kwargs):
        """
        验证所有软断言结果，如果有失败的软断言则抛出异常
        """
        allow_failures = kwargs.get("ALLOW_FAILURES", 0)

        soft_assert_results = g_context().get_dict("soft_assert_results", [])

        if not soft_assert_results:
            print("ℹ️  没有软断言结果需要验证")
            return

        failed_asserts = [r for r in soft_assert_results if not r.get("success", True)]
        failure_count = len(failed_asserts)

        print(f"📊 软断言统计: 总计 {len(soft_assert_results)}, 成功 {len(soft_assert_results) - failure_count}, 失败 {failure_count}")

        if failure_count > allow_failures:
            error_messages = [f"  - {r.get('message', '未知错误')}" for r in failed_asserts]
            raise AssertionError(
                f"软断言验证失败: 失败数量 ({failure_count}) 超过允许数量 ({allow_failures})\n" +
                "\n".join(error_messages)
            )
        else:
            print(f"✅ 软断言验证通过: 失败数量 ({failure_count}) 在允许范围内 ({allow_failures})")


