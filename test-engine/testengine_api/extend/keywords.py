import json
import logging
import mimetypes
import os
import re
import time
from urllib.parse import unquote, urlparse, urlencode

import allure
import jsonpath

from ..core.globalContext import g_context  # 相对导入
from ..utils.async_client import AsyncClientManager  # 异步客户端管理器

logger = logging.getLogger(__name__) # 配置日志

class Keywords:
    request = None

    def _clean_url(self, url):
        """
        清理 URL，去除前后空格
        """
        if url and isinstance(url, str):
            return url.strip()
        return url
    
    def _encode_headers(self, headers):
        """
        处理 headers 中的值，确保所有值都是字符串类型
        注意：HTTP headers 中不建议使用中文，建议将中文数据放在请求体中
        """
        if not headers:
            return headers
        
        encoded_headers = {}
        for key, value in headers.items():
            # 将所有值转为字符串（处理整数、浮点数等类型）
            if not isinstance(value, str):
                value = str(value)
            
            # 去除前后空格
            value = value.strip()
            
            # 尝试编码为 ASCII（HTTP header 标准）
            try:
                # 测试是否可以用 ASCII 编码
                value.encode('ascii')
                encoded_headers[key] = value
            except UnicodeEncodeError:
                # 如果包含中文等非 ASCII 字符，使用 URL 编码
                import urllib.parse
                encoded_value = urllib.parse.quote(value, safe='')
                encoded_headers[key] = encoded_value
                logger.warning(f"Header '{key}' 包含非ASCII字符，已URL编码: {value} -> {encoded_value}")
        
        return encoded_headers

    @allure.step(">>>>>>参数数据：")
    async def send_request(self, **kwargs): # 改为异步方法
        kwargs.pop("关键字", None) # 剔除不需要的字段
        files = kwargs.get("files", [])

        if files:
            files = await self.process_upload_files(files) # 异步处理文件上传
            kwargs.update(files=files)

        # 初始化请求数据
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

        client = None
        try:
            client = await AsyncClientManager.get_client() # 获取异步客户端
            response = await client.request(**kwargs) # 执行异步请求
            self.request = response
            g_context().set_dict("current_response", response)

            # 组装请求数据
            request_data = {
                "url": unquote(str(response.url)),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": str(response.request.content),
                "response": response.text
            }
            g_context().set_dict("current_response_data", request_data)
            logger.debug(f"请求成功: {response.status_code} {kwargs.get('url', '')}") # 简化日志

        except Exception as e:
            request_data.update({"response": str(e)})
            logger.error(f"请求失败: {kwargs.get('method', 'GET')} {kwargs.get('url', '')} - {str(e)}") # 移除 emoji
            raise e
        finally:
            if client:
                await client.aclose() # 关闭客户端,释放连接回连接池
            print("-----------current_response_data------------")
            print(request_data)
            print("----------end current_response_data-------------")


    @allure.step(">>>>>>参数数据：")
    async def send_request_and_download(self, **kwargs): # 改为异步方法
        kwargs.pop("关键字", None)
        files = kwargs.get("files", [])

        if files:
            files = await self.process_upload_files(files) # 异步处理文件
            kwargs.update(files=files)

        request_data = {
            "url": unquote(f'{kwargs.get("url", "")}?{urlencode(kwargs.get("params", ""))}'),
            "method": kwargs.get("method", ""),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data", "") or kwargs.get("json", "") or kwargs.get("files", ""),
            "response": kwargs.get("response", ""),
            "current_response_file_path": ""
        }

        client = None
        try:
            client = await AsyncClientManager.get_client()
            response = await client.request(**kwargs)
            self.request = response
            g_context().set_dict("current_response", response)

            file_path = self.save_response_content(response) # 保存响应内容
            print("-----------------------")
            print(response.text)
            print("-----------------------")

            request_data = {
                "url": unquote(str(response.url)),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "body": str(response.request.content),
                "response": response.text,
                "current_response_file_path": file_path
            }
            g_context().set_dict("current_response_data", request_data)

        except Exception as e:
            request_data.update({"response": str(e)})
            raise e
        finally:
            if client:
                await client.aclose() # 关闭客户端
            print("-----------current_response_data------------")
            print(request_data)
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


    async def process_upload_files(self, file_list): # 改为异步方法
        """处理上传文件,返回 httpx 支持的 files 列表格式"""
        processed_files = []
        download_dir = r'/img' # 本地保存路径

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for item in file_list:
            for field_name, file_path in item.items():
                if file_path.startswith(('http://', 'https://')): # 判断是否是 URL
                    try:
                        client = await AsyncClientManager.get_client()
                        response = await client.get(file_path) # 异步下载文件
                        response.raise_for_status()

                        parsed_url = urlparse(file_path)
                        filename = os.path.basename(parsed_url.path)
                        if not filename:
                            filename = 'downloaded_file'

                        local_path = os.path.join(download_dir, filename)
                        with open(local_path, 'wb') as f:
                            f.write(response.content)

                        file_path = local_path
                    except Exception as e:
                        raise RuntimeError(f"文件下载失败: {file_path}, 错误: {e}")

                file_name = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                processed_files.append(
                    (field_name, (file_name, open(file_path, 'rb'), mime_type))
                )

        return processed_files


    @allure.step(">>>>>>参数数据：")
    async def request_post_form_urlencoded(self, **kwargs): # 改为异步方法
        """发送Post请求"""
        request_data = {
            "url": self._clean_url(kwargs.get("URL", None)),
            "params": kwargs.get("PARAMS", None),
            "headers": self._encode_headers(kwargs.get("HEADERS", None)),
            "data": kwargs.get("DATA", None),
        }

        client = await AsyncClientManager.get_client()
        response = await client.post(**request_data)
        g_context().set_dict("current_response", response)
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    async def request_post_row_json(self, **kwargs): # 改为异步方法
        """发送Post请求"""
        request_data = {
            "url": self._clean_url(kwargs.get("URL", None)),
            "params": kwargs.get("PARAMS", None),
            "headers": self._encode_headers(kwargs.get("HEADERS", None)),
            "json": kwargs.get("DATA", None),
        }

        client = await AsyncClientManager.get_client()
        response = await client.post(**request_data)
        g_context().set_dict("current_response", response)
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    async def request_post_form_data(self, **kwargs): # 改为异步方法
        """发送Post请求"""
        request_data = {
            "url": self._clean_url(kwargs.get("URL", None)),
            "params": kwargs.get("PARAMS", None),
            "headers": self._encode_headers(kwargs.get("HEADERS", None)),
            "files": kwargs.get("FILES", None),
            "data": kwargs.get("DATA", None),
        }

        client = await AsyncClientManager.get_client()
        response = await client.post(**request_data)
        g_context().set_dict("current_response", response)
        print("-----------------------")
        print(response.text)
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    async def request_get(self, **kwargs): # 改为异步方法
        """发送GET请求"""
        request_data = {
            "url": self._clean_url(kwargs.get("URL", None)),
            "params": kwargs.get("PARAMS", None),
            "headers": self._encode_headers(kwargs.get("HEADERS", None)),
        }

        client = await AsyncClientManager.get_client()
        response = await client.get(**request_data)
        g_context().set_dict("current_response", response)
        print("-----------------------")
        print(response.json())
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    async def request_get_row(self, **kwargs):
        """发送GET请求 - 异步版本"""
        client = await AsyncClientManager.get_client()
        response = await client.get(**kwargs)
        g_context().set_dict("current_response", response)
        return response

    @allure.step(">>>>>>参数数据：")
    async def request_post_row(self, **kwargs):
        """发送POST请求 - 异步版本"""
        client = await AsyncClientManager.get_client()
        response = await client.post(**kwargs)
        g_context().set_dict("current_response", response)
        return response

    @allure.step(">>>>>>参数数据：")
    async def request_put_row(self, **kwargs):
        """发送PUT请求 - 异步版本"""
        client = await AsyncClientManager.get_client()
        response = await client.put(**kwargs)
        g_context().set_dict("current_response", response)
        return response

    @allure.step(">>>>>>参数数据：")
    async def request_delete_row(self, **kwargs):
        """发送DELETE请求 - 异步版本"""
        client = await AsyncClientManager.get_client()
        response = await client.delete(**kwargs)
        g_context().set_dict("current_response", response)
        return response

    @allure.step(">>>>>>参数数据：")
    def ex_jsonData(self, **kwargs):
        """
        提取json数据
        EXVALUE：提取josn的表达式
        INDEX: 非必填，默认为0
        VARNAME：存储的变量名（必填）
        """
        # 检查必填参数
        if "VARNAME" not in kwargs or not kwargs["VARNAME"]:
            raise ValueError(
                "❌ ex_jsonData 缺少必填参数 VARNAME！\n"
                "   请检查 Excel 测试用例中的参数设置：\n"
                "   - 参数_1: EXVALUE (JsonPath表达式)\n"
                "   - 参数_2: INDEX (索引，默认0)\n"
                "   - 参数_3: VARNAME (变量名，必填)\n"
                f"   当前参数: {kwargs}"
            )
        
        # 获取JsonPath的值
        EXPRESSION = kwargs.get("EXVALUE", None)
        # 获取对应的下标，非必填，默认为0
        INDEX = kwargs.get("INDEX", None)
        # 如果 INDEX 为 None 或空字符串，使用默认值 0
        if INDEX is None or INDEX == '':
            INDEX = 0
        else:
            # 转为字符串后判断是否为数字
            INDEX_str = str(INDEX)
            INDEX = int(INDEX_str) if INDEX_str.isdigit() else 0

        # 获取响应数据
        try:
            response = g_context().get_dict("current_response").json()
        except Exception as e:
            print(f"JSON解析失败，响应内容: {g_context().get_dict('current_response').text[:500]}")
            raise ValueError(f"响应不是有效的JSON格式: {str(e)}")
        
        ex_data = jsonpath.jsonpath(response, EXPRESSION)[INDEX]  # 通过JsonPath进行提取
        g_context().set_dict(kwargs["VARNAME"], ex_data)  # 根据变量名设置成全局变量
        print("-----------------------")
        print(f"✅ 已保存变量: {kwargs['VARNAME']} = {ex_data}")
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
        reference_variables：数据库要存储的变量名，支持字符串或列表格式

        如果 reference_variables 为空，则默认使用数据库字段名生成变量。
        如果 reference_variables 有数据，则检查其长度是否与每条记录中的字段数量一致，若一致则生成对应格式的数据；否则抛出错误提示。

        存储到全局变量：{"变量名_下标":数据}
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

        var_names = kwargs.get("reference_variables",  [])
        
        # 处理 reference_variables 的不同格式
        if var_names:
            # 如果是字符串，转换为列表
            if isinstance(var_names, str):
                var_names = [var_names.strip()]
            # 如果是其他可迭代对象，转换为列表
            elif not isinstance(var_names, list):
                var_names = list(var_names)
        
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
                print(f"❌ var_names 的长度({len(var_names)})与每条记录的字段数({field_length})不一致！")
                print(f"   var_names: {var_names}")
                print(f"   查询字段: {list(rs[0].keys()) if rs else []}")
                raise ValueError(f"❌ var_names 的长度与每条记录的字段数不一致，请检查输入！")

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

    @allure.step(">>>>>>JSON断言：")
    def assert_json_comparators(self, **kwargs):
        """
        JSON 断言比较 - 从响应中提取 JSON 数据并与期望值比较
        
        参数:
        JSON_PATH: JSONPath 表达式（如 '$..msg'）
        EXPECTED: 期望的值
        OP_STR: 操作符（如 '==', '!=', '>', '<', '>=', '<=', 'in', 'not in'）
        """
        import jsonpath
        
        # 获取参数
        json_path = kwargs.get("JSON_PATH", None)
        expected = kwargs.get("EXPECTED", None)
        op_str = kwargs.get("OP_STR", "==")
        
        if not json_path:
            raise ValueError("❌ assert_json_comparators 缺少必填参数 JSON_PATH")
        
        # 获取响应数据
        try:
            response = g_context().get_dict("current_response")
            response_json = response.json()
        except Exception as e:
            print(f"JSON解析失败，响应内容: {response.text[:500]}")
            raise ValueError(f"响应不是有效的JSON格式: {str(e)}")
        
        # 使用 JSONPath 提取数据
        try:
            result = jsonpath.jsonpath(response_json, json_path)
            if not result:
                raise ValueError(f"JSONPath '{json_path}' 未找到匹配的数据")
            
            # 取第一个匹配的值
            actual_value = result[0]
        except Exception as e:
            print(f"JSONPath 提取失败: {str(e)}")
            print(f"响应数据: {response_json}")
            raise
        
        # 处理期望值（可能包含引号）
        if isinstance(expected, str):
            # 如果期望值是带引号的字符串（如 '"200"'），尝试解析
            if expected.startswith('"') and expected.endswith('"'):
                expected = expected[1:-1]  # 去除外层引号
        
        # 定义操作符字典
        operators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
            'in': lambda a, b: a in b,
            'not in': lambda a, b: a not in b
        }
        
        # 获取操作符函数
        op_func = operators.get(op_str)
        if not op_func:
            raise ValueError(f"不支持的操作符: {op_str}")
        
        # 执行比较
        try:
            result_bool = op_func(actual_value, expected)
            assert result_bool, f"JSON断言失败: {json_path} => {actual_value} {op_str} {expected}"
            print(f"✅ JSON断言成功: {json_path} => {actual_value} {op_str} {expected}")
            return True
        except AssertionError as e:
            print(f"❌ JSON断言失败: {str(e)}")
            print(f"   JSONPath: {json_path}")
            print(f"   实际值: {actual_value} (类型: {type(actual_value).__name__})")
            print(f"   期望值: {expected} (类型: {type(expected).__name__})")
            print(f"   操作符: {op_str}")
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
    def generate_name_new(self, **kwargs):
        """
        生成随机用户名
        VARNAME：存储的变量名
        """
        import random
        import string
        import time
        
        # 生成随机用户名：user + 时间戳 + 随机字符
        timestamp = str(int(time.time()))[-6:]  # 取时间戳后6位
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        username = f"user{timestamp}{random_str}"
        
        g_context().set_dict(kwargs["VARNAME"], username)
        print(f"生成的用户名: {username}")
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")

    @allure.step(">>>>>>参数数据：")
    def assert_json_DeepDiff(self, **kwargs):
        """
        JSON深度对比断言
        json1: 第一个JSON对象
        json2: 第二个JSON对象
        过滤字段: 需要过滤的字段（可选）- 格式可以是 {city} 或 ['city'] 或 'city'
        忽略顺序: 是否忽略列表顺序（可选，默认False）
        """
        try:
            from deepdiff import DeepDiff
        except ImportError:
            print("警告: deepdiff库未安装，将使用简单对比")
            # 简单对比
            json1 = kwargs.get("json1")
            json2 = kwargs.get("json2")
            if json1 != json2:
                raise AssertionError(f"JSON对比失败:\n期望: {json2}\n实际: {json1}")
            return

        json1 = kwargs.get("json1")
        json2 = kwargs.get("json2")
        exclude_paths = kwargs.get("过滤字段", None)
        ignore_order = kwargs.get("忽略顺序", False)
        
        print(f"调试信息 - exclude_paths类型: {type(exclude_paths)}, 值: {exclude_paths}")
        
        # 处理过滤字段 - 支持多种格式
        exclude_list = []
        if exclude_paths:
            # 情况1: 如果是set类型 {city}
            if isinstance(exclude_paths, set):
                for field in exclude_paths:
                    field = str(field).strip()
                    exclude_list.append(f"root['{field}']")
            # 情况2: 如果是list类型 ['city']
            elif isinstance(exclude_paths, list):
                for field in exclude_paths:
                    field = str(field).strip()
                    exclude_list.append(f"root['{field}']")
            # 情况3: 如果是字符串 "city" 或 "{city}"
            elif isinstance(exclude_paths, str):
                # 去除花括号和空格
                exclude_str = exclude_paths.strip('{}').strip()
                if exclude_str:
                    # 支持逗号分隔的多个字段
                    for field in exclude_str.split(','):
                        field = field.strip()
                        if field:
                            exclude_list.append(f"root['{field}']")
        
        print(f"调试信息 - 最终的exclude_list: {exclude_list}")
        
        # 进行深度对比
        diff_params = {
            'ignore_order': ignore_order,
        }
        if exclude_list:
            diff_params['exclude_paths'] = exclude_list
            
        print(f"调试信息 - DeepDiff参数: {diff_params}")
        diff = DeepDiff(json1, json2, **diff_params)
        
        if diff:
            print(f"❌ JSON对比发现差异: {diff}")
            raise AssertionError(f"JSON对比失败: {diff}")
        else:
            print("✅ JSON对比一致")

    @allure.step(">>>>>>参数数据：")
    def encrypt_aes(self, **kwargs):
        """
        AES加密
        data: 要加密的数据
        VARNAME: 存储加密结果的变量名
        key: AES密钥（可选，默认使用固定密钥）
        mode: 加密模式（可选，默认CBC）
        """
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import base64
        except ImportError:
            raise ImportError("请安装 pycryptodome 库: pip install pycryptodome")
        
        data = kwargs.get("data", "")
        var_name = kwargs.get("VARNAME")
        # 默认密钥（16字节）
        key = kwargs.get("key", "1234567890123456").encode('utf-8')
        if len(key) not in [16, 24, 32]:
            key = (key + b'0' * 16)[:16]  # 填充到16字节
        
        # 创建AES加密器
        cipher = AES.new(key, AES.MODE_ECB)
        
        # 对数据进行填充并加密
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        
        # Base64编码
        encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')
        
        g_context().set_dict(var_name, encrypted_base64)
        print(f"AES加密结果: {encrypted_base64}")
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")


