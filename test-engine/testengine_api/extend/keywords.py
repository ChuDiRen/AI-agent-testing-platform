import mimetypes
from importlib.metadata import files

import allure

from ..core.globalContext import g_context  # 相对导入: apirun内部模块
import httpx  # 使用 httpx 替代 requests
import asyncio  # 异步支持
from ..utils.async_client import AsyncClientManager, run_async  # 异步客户端管理器
import jsonpath
import re
import time
import os
import json
import logging
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import urlencode

# 配置日志
logger = logging.getLogger(__name__)

class Keywords:
    request = None

    # def __init__(self, request: requests):
    #     self.request = requests.Session()

    @allure.step(">>>>>>参数数据：")
    def send_request(self, **kwargs):
        # 剔除不需要的字段，例如 EXVALUE
        kwargs.pop("关键字", None)  # 如果存在 关键字 字段则删除，否则不操作

        files = kwargs.get("files", [])

        if files:
            files = self.process_upload_files(files)
            kwargs.update(files=files)

        #  先初始化请求数据，避免接口请求不通过，前端没有请求数据显示
        params = kwargs.get("params")
        url_with_params = kwargs.get("url", "")
        if params:
            url_with_params = f'{url_with_params}?{urlencode(params)}'

        request_data = {
            "url": unquote(url_with_params),
            "method": kwargs.get("method", ""),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data", "") or kwargs.get("json", "") or kwargs.get("files", ""),
            "response": kwargs.get("response", "")
        }

        # 定义异步请求函数
        async def _async_request():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.request(**kwargs)  # 执行异步请求
            return response

        try:
            #  执行异步请求(复用 AsyncClient 连接池)
            logger.info(f"📤 发送请求 | {kwargs.get('method', 'GET')} {kwargs.get('url', '')}")

            response = run_async(_async_request())
            self.request = response  # 保存 response 对象供后续使用

            g_context().set_dict("current_response", response)  # 默认设置成全局变量-- 对象

            #  组装请求数据到全局变量，从response进行获取。方便平台进行显示, 可能请求出错，所以结合请求数据进行填写
            request_data = {
                "url": unquote(str(response.url)),  # httpx.URL 需要转字符串
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": str(response.request.content), # httpx 使用 content 而非 body
                "response": response.text
            }
            g_context().set_dict("current_response_data", request_data)  # 默认设置成全局变量

            # 记录响应日志
            logger.info(f"📥 收到响应 | 状态码: {response.status_code} | 响应大小: {len(response.content)} bytes")

        except Exception as e:
            request_data.update({"response":str(e)})
            logger.error(f"❌ 请求异常 | {kwargs.get('method', 'GET')} {kwargs.get('url', '')} | 错误: {str(e)}")
            raise e
        finally:
            print("-----------current_response_data------------")
            print(request_data)  # 一定要打印，后续是利用它进行前端的显示
            print("----------end current_response_data-------------")


    @allure.step(">>>>>>参数数据：")
    def send_request_and_download(self, **kwargs):
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

        # 定义异步请求函数
        async def _async_request():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.request(**kwargs)  # 执行异步请求
            return response

        try:
            #  执行异步请求(复用 AsyncClient 连接池)
            response = run_async(_async_request())
            self.request = response  # 保存 response 对象供后续使用

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
                "url": unquote(str(response.url)),  # httpx.URL 需要转字符串
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": str(response.request.content),  # httpx 使用 content
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
        处理上传文件，返回 httpx 支持的 files 列表格式
        :param file_list: 文件列表，格式如 [{'file': 'path_or_url'}, {'avatar': 'path2'}]
        :return: 处理后的 files 列表
        """

        import os
        from urllib.parse import urlparse

        processed_files = []
        download_dir = r'/img'  # 本地保存路径

        # 创建目录（如果不存在）
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # 定义异步下载函数
        async def _download_file(url):
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.get(url)
            response.raise_for_status()
            return response

        for item in file_list:
            for field_name, file_path in item.items():
                # 判断是否是 URL
                if file_path.startswith(('http://', 'https://')):
                    try:
                        # 使用异步 httpx 下载文件
                        response = run_async(_download_file(file_path))

                        # 提取文件名（从URL）
                        parsed_url = urlparse(file_path)
                        filename = os.path.basename(parsed_url.path)
                        if not filename:
                            filename = 'downloaded_file'

                        local_path = os.path.join(download_dir, filename)

                        # 写入本地文件
                        with open(local_path, 'wb') as f:
                            f.write(response.content)  # httpx 直接使用 content

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

        # 定义异步请求函数
        async def _async_post():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.post(**request_data)
            return response

        response = run_async(_async_post())  # 执行异步请求(复用连接池)
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

        # 定义异步请求函数
        async def _async_post():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.post(**request_data)
            return response

        response = run_async(_async_post())  # 执行异步请求(复用连接池)
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

        # 定义异步请求函数
        async def _async_post():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.post(**request_data)
            return response

        response = run_async(_async_post())  # 执行异步请求(复用连接池)
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

        # 定义异步请求函数
        async def _async_get():
            client = await AsyncClientManager.get_client()  # 获取复用的异步客户端
            response = await client.get(**request_data)
            return response

        response = run_async(_async_get())  # 执行异步请求(复用连接池)
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


