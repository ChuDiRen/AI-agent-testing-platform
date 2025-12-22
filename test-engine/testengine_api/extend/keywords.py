"""
API 测试关键字模块
基于 httpx 异步客户端实现
"""
import hashlib
import json
import logging
import mimetypes
import os
import random
import re
import string
import time
import urllib.parse
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse, urlencode, parse_qs

import allure
import jsonpath

from ..core.globalContext import g_context
from ..utils.async_client import AsyncClientManager

logger = logging.getLogger(__name__)


class Keywords:
    """
    API 测试关键字类
    
    功能:
    - HTTP 请求: send_request, request_get, request_post_json 等
    - 数据提取: extract_json, extract_regex, extract_mysql
    - 断言: assert_status_code, assert_json, assert_contains 等
    - 工具: generate_random_string, md5_encrypt, base64_encode 等
    """
    
    def __init__(self):
        self.last_response = None
    
    def _clean_url(self, url: str) -> str:
        """清理 URL"""
        return url.strip() if url and isinstance(url, str) else url
    
    def _encode_headers(self, headers: Dict) -> Dict:
        """处理 headers，确保值为字符串且 ASCII 兼容"""
        if not headers:
            return headers
        
        encoded = {}
        for key, value in headers.items():
            if not isinstance(value, str):
                value = str(value)
            value = value.strip()
            
            try:
                value.encode('ascii')
                encoded[key] = value
            except UnicodeEncodeError:
                encoded[key] = urllib.parse.quote(value, safe='')
                logger.warning(f"Header '{key}' 包含非ASCII字符，已URL编码")
        
        return encoded

    @allure.step("HTTP 请求")
    async def send_request(self, **kwargs) -> None:
        """
        统一 HTTP 请求关键字
        
        参数:
            method: 请求方法 (GET/POST/PUT/DELETE/PATCH)
            url: 请求地址
            headers: 请求头
            params: URL 参数
            data: 表单数据
            json: JSON 数据
            files: 上传文件
            download: 是否下载响应
            timeout: 超时时间
        """
        kwargs.pop("关键字", None)
        download = kwargs.pop("download", False)
        
        # 清理 URL
        if "url" in kwargs:
            kwargs["url"] = self._clean_url(kwargs["url"])
        
        # 编码 headers
        if "headers" in kwargs:
            kwargs["headers"] = self._encode_headers(kwargs["headers"])
        
        # 处理文件上传
        if kwargs.get("files"):
            kwargs["files"] = await self._process_upload_files(kwargs["files"])
        
        # 构建请求数据（用于日志）
        params_val = kwargs.get("params") or {}
        params_str = urlencode(params_val) if params_val else ""
        url_with_params = f'{kwargs.get("url", "")}?{params_str}' if params_str else kwargs.get("url", "")
        
        request_data = {
            "url": unquote(url_with_params),
            "method": kwargs.get("method", "GET"),
            "headers": kwargs.get("headers", ""),
            "body": kwargs.get("data") or kwargs.get("json") or kwargs.get("files") or "",
            "response": ""
        }

        client = None
        try:
            client = await AsyncClientManager.get_client()
            response = await client.request(**kwargs)
            self.last_response = response
            
            g_context().set_dict("current_response", response)
            g_context().set_dict("status_code", str(response.status_code))

            # 解析响应数据
            parsed_url = urlparse(str(response.url))
            url_params = parse_qs(parsed_url.query)
            params_dict = {k: v[0] if len(v) == 1 else v for k, v in url_params.items()}
            
            request_data = {
                "url": unquote(str(response.url)),
                "method": response.request.method,
                "headers": dict(response.request.headers),
                "params": params_dict,
                "body": str(response.request.content) if response.request.content else "",
                "response": response.text,
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            }
            
            if download:
                file_path = self._save_response_content(response)
                request_data["download_path"] = file_path
                g_context().set_dict("current_response_file_path", file_path)
                
            g_context().set_dict("current_response_data", request_data)
            logger.debug(f"请求成功: {response.status_code} {kwargs.get('url', '')}")

        except Exception as e:
            request_data["response"] = str(e)
            logger.error(f"请求失败: {kwargs.get('method', 'GET')} {kwargs.get('url', '')} - {e}")
            raise
        finally:
            if client:
                await client.aclose()
            print("-----------request_data------------")
            print(request_data)
            print("-----------end request_data--------")


    def _get_temp_dir(self, subdir: str = "") -> str:
        """获取临时目录路径"""
        import tempfile
        base_dir = g_context().get_dict("_temp_dir") or tempfile.gettempdir()
        if subdir:
            return os.path.join(base_dir, subdir)
        return base_dir

    def _save_response_content(self, response, download_dir: str = None) -> str:
        """保存响应内容到文件"""
        if download_dir is None:
            download_dir = self._get_temp_dir("downloads")
        os.makedirs(download_dir, exist_ok=True)
        
        content_type = response.headers.get("Content-Type", "")
        timestamp = int(time.time())

        if "application/json" in content_type:
            file_path = os.path.join(download_dir, f"response_{timestamp}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(response.json(), ensure_ascii=False, indent=2))
        elif "application/octet-stream" in content_type:
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition and "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('";')
            else:
                filename = f"file_{timestamp}.bin"
            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
        else:
            file_path = os.path.join(download_dir, f"response_{timestamp}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        
        return file_path

    async def _process_upload_files(self, file_list: List) -> List:
        """处理上传文件，支持 URL 自动下载"""
        processed_files = []
        download_dir = self._get_temp_dir("uploads")
        os.makedirs(download_dir, exist_ok=True)

        for item in file_list:
            for field_name, file_path in item.items():
                if file_path.startswith(('http://', 'https://')):
                    try:
                        client = await AsyncClientManager.get_client()
                        response = await client.get(file_path)
                        response.raise_for_status()

                        parsed_url = urlparse(file_path)
                        filename = os.path.basename(parsed_url.path) or 'downloaded_file'
                        local_path = os.path.join(download_dir, filename)
                        
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        file_path = local_path
                    except Exception as e:
                        raise RuntimeError(f"文件下载失败: {file_path}, 错误: {e}")

                file_name = os.path.basename(file_path)
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                processed_files.append((field_name, (file_name, open(file_path, 'rb'), mime_type)))

        return processed_files


    # ==================== 数据提取关键字 ====================

    @allure.step("提取 JSON 数据")
    def extract_json(self, **kwargs) -> Any:
        """
        从响应中提取 JSON 数据
        
        参数:
            expression: JSONPath 表达式
            index: 下标（默认 0）
            var_name: 存储的变量名（必填）
        """
        var_name = kwargs.get("var_name")
        if not var_name:
            raise ValueError("extract_json 缺少必填参数 var_name")
        
        expression = kwargs.get("expression")
        index = int(kwargs.get("index", 0) or 0)
        
        try:
            response = g_context().get_dict("current_response").json()
        except Exception as e:
            raise ValueError(f"响应不是有效的 JSON 格式: {e}")
        
        result = jsonpath.jsonpath(response, expression)
        if not result:
            raise ValueError(f"JSONPath '{expression}' 未找到匹配数据")
        
        value = result[index]
        g_context().set_dict(var_name, value)
        print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("提取正则数据")
    def extract_regex(self, **kwargs) -> Any:
        """
        从响应中提取正则匹配数据
        
        参数:
            expression: 正则表达式
            index: 下标（默认 0）
            var_name: 存储的变量名
        """
        expression = kwargs.get("expression")
        index = int(kwargs.get("index", 0) or 0)
        var_name = kwargs.get("var_name")
        
        response = g_context().get_dict("current_response").text
        result = re.findall(expression, response)
        
        if not result:
            raise ValueError(f"正则 '{expression}' 未找到匹配数据")
        
        value = result[index]
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("提取响应头")
    def extract_header(self, **kwargs) -> str:
        """
        提取响应头
        
        参数:
            header_name: 响应头名称
            var_name: 存储的变量名
        """
        header_name = kwargs.get("header_name")
        var_name = kwargs.get("var_name")
        
        response = g_context().get_dict("current_response")
        value = response.headers.get(header_name, "")
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("提取 Cookie")
    def extract_cookie(self, **kwargs) -> str:
        """
        提取 Cookie
        
        参数:
            cookie_name: Cookie 名称
            var_name: 存储的变量名
        """
        cookie_name = kwargs.get("cookie_name")
        var_name = kwargs.get("var_name")
        
        response = g_context().get_dict("current_response")
        value = response.cookies.get(cookie_name, "")
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("数据库查询")
    def extract_mysql(self, **kwargs) -> Dict:
        """
        执行 MySQL 查询并提取数据
        
        参数:
            db_name: 数据库名称
            sql: SQL 查询语句
            var_names: 变量名列表（可选）
        """
        import pymysql
        from pymysql import cursors
        
        db_name = kwargs.get("db_name")
        sql = kwargs.get("sql")
        var_names = kwargs.get("var_names", [])
        
        # 获取数据库配置
        db_config = g_context().get_dict("_database")[db_name]
        config = {"cursorclass": cursors.DictCursor}
        config.update(db_config)

        con = pymysql.connect(**config)
        cur = con.cursor()
        cur.execute(sql)
        rs = cur.fetchall()
        cur.close()
        con.close()
        
        print(f"数据库查询结果: {rs}")
        
        # 处理变量名
        if isinstance(var_names, str):
            var_names = [var_names.strip()]
        elif not isinstance(var_names, list):
            var_names = list(var_names) if var_names else []
        
        result = {}
        if not var_names:
            # 使用原始字段名
            for i, item in enumerate(rs, start=1):
                for key, value in item.items():
                    result[f"{key}_{i}"] = value
        else:
            # 使用自定义变量名
            field_length = len(rs[0]) if rs else 0
            if len(var_names) != field_length:
                raise ValueError(f"var_names 长度({len(var_names)})与字段数({field_length})不一致")
            
            for idx, item in enumerate(rs, start=1):
                for col_idx, key in enumerate(item):
                    result[f"{var_names[col_idx]}_{idx}"] = item[key]
        
        g_context().set_by_dict(result)
        return result

    # ==================== 断言关键字 ====================

    @allure.step("断言状态码")
    def assert_status_code(self, **kwargs) -> None:
        """
        断言响应状态码
        
        参数:
            expected_code: 期望的状态码
        """
        expected = int(kwargs.get("expected_code", 200))
        response = g_context().get_dict("current_response")
        actual = response.status_code
        
        assert actual == expected, f"状态码断言失败: 期望 {expected}, 实际 {actual}"
        print(f"断言成功: 状态码 = {actual}")

    @allure.step("断言响应时间")
    def assert_response_time(self, **kwargs) -> None:
        """
        断言响应时间
        
        参数:
            max_time: 最大响应时间（秒）
        """
        max_time = float(kwargs.get("max_time", 5))
        response = g_context().get_dict("current_response")
        actual = response.elapsed.total_seconds()
        
        assert actual <= max_time, f"响应时间断言失败: 期望 <= {max_time}s, 实际 {actual:.3f}s"
        print(f"断言成功: 响应时间 = {actual:.3f}s")

    @allure.step("断言包含文本")
    def assert_contains(self, **kwargs) -> None:
        """
        断言响应包含指定文本
        
        参数:
            expected_text: 期望包含的文本
        """
        expected = kwargs.get("expected_text", "")
        response = g_context().get_dict("current_response")
        
        assert expected in response.text, f"文本断言失败: 响应不包含 '{expected}'"
        print(f"断言成功: 响应包含 '{expected}'")

    @allure.step("JSON 断言")
    def assert_json(self, **kwargs) -> None:
        """
        JSON 断言
        
        参数:
            json_path: JSONPath 表达式
            expected: 期望值
            operator: 操作符（==, !=, >, <, >=, <=, in, not in）
        """
        json_path = kwargs.get("json_path")
        expected = kwargs.get("expected")
        operator = kwargs.get("operator", "==")
        
        if not json_path:
            raise ValueError("assert_json 缺少必填参数 json_path")
        
        response = g_context().get_dict("current_response")
        try:
            response_json = response.json()
        except Exception as e:
            raise ValueError(f"响应不是有效的 JSON: {e}")
        
        result = jsonpath.jsonpath(response_json, json_path)
        if not result:
            raise ValueError(f"JSONPath '{json_path}' 未找到匹配数据")
        
        actual = result[0]
        
        # 处理期望值引号
        if isinstance(expected, str) and expected.startswith('"') and expected.endswith('"'):
            expected = expected[1:-1]
        
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
        
        op_func = operators.get(operator)
        if not op_func:
            raise ValueError(f"不支持的操作符: {operator}")
        
        assert op_func(actual, expected), f"JSON 断言失败: {json_path} => {actual} {operator} {expected}"
        print(f"JSON 断言成功: {json_path} => {actual} {operator} {expected}")

    @allure.step("数值比较断言")
    def assert_compare(self, **kwargs) -> None:
        """
        数值比较断言
        
        参数:
            value: 实际值
            expected: 期望值
            operator: 操作符（>, <, ==, >=, <=, !=）
        """
        value = kwargs.get("value")
        expected = kwargs.get("expected")
        operator = kwargs.get("operator", "==")
        message = kwargs.get("message")
        
        operators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }
        
        if operator not in operators:
            raise ValueError(f"不支持的操作符: {operator}")
        
        if not operators[operator](value, expected):
            error_msg = message or f"{value} {operator} {expected} 失败"
            raise AssertionError(error_msg)
        
        print(f"断言成功: {value} {operator} {expected}")

    @allure.step("文件 MD5 断言")
    def assert_file_md5(self, **kwargs) -> None:
        """
        断言响应文件 MD5 值
        
        参数:
            expected_md5: 期望的 MD5 值
        """
        expected_md5 = kwargs.get("expected_md5")
        response = g_context().get_dict("current_response")
        
        if response.status_code != 200:
            raise AssertionError(f"请求失败，状态码: {response.status_code}")
        
        actual_md5 = hashlib.md5(response.content).hexdigest()
        
        assert expected_md5 == actual_md5, f"MD5 不匹配: 期望 {expected_md5}, 实际 {actual_md5}"
        print(f"MD5 断言成功: {actual_md5}")

    @allure.step("JSON 深度对比")
    def assert_json_deep(self, **kwargs) -> None:
        """
        JSON 深度对比断言
        
        参数:
            json1: 第一个 JSON 对象
            json2: 第二个 JSON 对象
            exclude_fields: 需要排除的字段
            ignore_order: 是否忽略列表顺序
        """
        try:
            from deepdiff import DeepDiff
        except ImportError:
            json1 = kwargs.get("json1")
            json2 = kwargs.get("json2")
            if json1 != json2:
                raise AssertionError(f"JSON 对比失败:\n期望: {json2}\n实际: {json1}")
            return

        json1 = kwargs.get("json1")
        json2 = kwargs.get("json2")
        exclude_fields = kwargs.get("exclude_fields")
        ignore_order = kwargs.get("ignore_order", False)
        
        exclude_list = []
        if exclude_fields:
            if isinstance(exclude_fields, (set, list)):
                exclude_list = [f"root['{f}']" for f in exclude_fields]
            elif isinstance(exclude_fields, str):
                exclude_list = [f"root['{f.strip()}']" for f in exclude_fields.strip('{}').split(',') if f.strip()]
        
        diff_params = {'ignore_order': ignore_order}
        if exclude_list:
            diff_params['exclude_paths'] = exclude_list
        
        diff = DeepDiff(json1, json2, **diff_params)
        
        if diff:
            raise AssertionError(f"JSON 对比失败: {diff}")
        print("JSON 深度对比成功")

    # ==================== 工具关键字 ====================

    @allure.step("生成随机字符串")
    def generate_random_string(self, **kwargs) -> str:
        """
        生成随机字符串
        
        参数:
            length: 字符串长度（默认 10）
            var_name: 存储的变量名
        """
        length = int(kwargs.get("length", 10))
        var_name = kwargs.get("var_name")
        
        chars = string.ascii_letters + string.digits
        value = ''.join(random.choices(chars, k=length))
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("生成随机数字")
    def generate_random_number(self, **kwargs) -> int:
        """
        生成随机数字
        
        参数:
            min_value: 最小值
            max_value: 最大值
            var_name: 存储的变量名
        """
        min_val = int(kwargs.get("min_value", 0))
        max_val = int(kwargs.get("max_value", 100))
        var_name = kwargs.get("var_name")
        
        value = random.randint(min_val, max_val)
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("获取时间戳")
    def get_timestamp(self, **kwargs) -> int:
        """
        获取当前时间戳
        
        参数:
            var_name: 存储的变量名
        """
        var_name = kwargs.get("var_name")
        value = int(time.time())
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("格式化时间")
    def format_datetime(self, **kwargs) -> str:
        """
        格式化当前时间
        
        参数:
            format: 时间格式（默认 %Y-%m-%d %H:%M:%S）
            var_name: 存储的变量名
        """
        fmt = kwargs.get("format", "%Y-%m-%d %H:%M:%S")
        var_name = kwargs.get("var_name")
        
        value = time.strftime(fmt)
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("MD5 加密")
    def md5_encrypt(self, **kwargs) -> str:
        """
        MD5 加密
        
        参数:
            text: 要加密的文本
            var_name: 存储的变量名
        """
        text = kwargs.get("text", "")
        var_name = kwargs.get("var_name")
        
        value = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("Base64 编码")
    def base64_encode(self, **kwargs) -> str:
        """
        Base64 编码
        
        参数:
            text: 要编码的文本
            var_name: 存储的变量名
        """
        import base64
        text = kwargs.get("text", "")
        var_name = kwargs.get("var_name")
        
        value = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("Base64 解码")
    def base64_decode(self, **kwargs) -> str:
        """
        Base64 解码
        
        参数:
            encoded_text: 要解码的文本
            var_name: 存储的变量名
        """
        import base64
        encoded_text = kwargs.get("encoded_text", "")
        var_name = kwargs.get("var_name")
        
        value = base64.b64decode(encoded_text).decode('utf-8')
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("AES 加密")
    def aes_encrypt(self, **kwargs) -> str:
        """
        AES 加密
        
        参数:
            data: 要加密的数据
            key: AES 密钥（默认 16 字节）
            var_name: 存储的变量名
        """
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import base64
        except ImportError:
            raise ImportError("请安装 pycryptodome: pip install pycryptodome")
        
        data = kwargs.get("data", "")
        var_name = kwargs.get("var_name")
        key = kwargs.get("key", "1234567890123456").encode('utf-8')
        
        if len(key) not in [16, 24, 32]:
            key = (key + b'0' * 16)[:16]
        
        cipher = AES.new(key, AES.MODE_ECB)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        value = base64.b64encode(encrypted).decode('utf-8')
        
        if var_name:
            g_context().set_dict(var_name, value)
            print(f"已保存变量: {var_name} = {value}")
        return value

    @allure.step("等待")
    def wait_time(self, **kwargs) -> None:
        """
        等待指定时间
        
        参数:
            seconds: 等待时间（秒）
        """
        seconds = float(kwargs.get("seconds", 1))
        time.sleep(seconds)
        print(f"已等待 {seconds} 秒")

    # ==================== WebSocket 关键字 ====================

    @allure.step("WebSocket 连接")
    async def ws_connect(self, **kwargs) -> None:
        """
        建立 WebSocket 连接
        
        参数:
            url: WebSocket 地址 (ws:// 或 wss://)
            headers: 请求头（可选）
            timeout: 连接超时（秒，默认 30）
        """
        try:
            import websockets
        except ImportError:
            raise ImportError("请安装 websockets: pip install websockets")
        
        url = kwargs.get("url")
        headers = kwargs.get("headers")
        timeout = float(kwargs.get("timeout", 30))
        
        if not url:
            raise ValueError("ws_connect 缺少必填参数 url")
        
        extra_headers = headers if headers else {}
        
        ws = await websockets.connect(
            url,
            extra_headers=extra_headers,
            open_timeout=timeout
        )
        
        g_context().set_dict("ws_connection", ws)
        g_context().set_dict("ws_url", url)
        print(f"WebSocket 已连接: {url}")

    @allure.step("WebSocket 发送消息")
    async def ws_send(self, **kwargs) -> None:
        """
        发送 WebSocket 消息
        
        参数:
            message: 要发送的消息（字符串或 JSON 对象）
        """
        ws = g_context().get_dict("ws_connection")
        if not ws:
            raise RuntimeError("WebSocket 未连接，请先调用 ws_connect")
        
        message = kwargs.get("message", "")
        
        # 如果是字典，转为 JSON 字符串
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False)
        
        await ws.send(message)
        print(f"WebSocket 已发送: {message[:100]}...")

    @allure.step("WebSocket 接收消息")
    async def ws_receive(self, **kwargs) -> str:
        """
        接收 WebSocket 消息
        
        参数:
            timeout: 接收超时（秒，默认 30）
            var_name: 存储的变量名（可选）
        """
        import asyncio
        
        ws = g_context().get_dict("ws_connection")
        if not ws:
            raise RuntimeError("WebSocket 未连接，请先调用 ws_connect")
        
        timeout = float(kwargs.get("timeout", 30))
        var_name = kwargs.get("var_name")
        
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"WebSocket 接收超时: {timeout}s")
        
        g_context().set_dict("ws_last_message", message)
        
        if var_name:
            g_context().set_dict(var_name, message)
            print(f"WebSocket 消息已保存到变量: {var_name}")
        
        print(f"WebSocket 已接收: {message[:100]}...")
        return message

    @allure.step("WebSocket 关闭连接")
    async def ws_close(self, **kwargs) -> None:
        """关闭 WebSocket 连接"""
        ws = g_context().get_dict("ws_connection")
        if ws:
            await ws.close()
            g_context().set_dict("ws_connection", None)
            print("WebSocket 已关闭")

    @allure.step("WebSocket 断言消息")
    def ws_assert_message(self, **kwargs) -> None:
        """
        断言 WebSocket 消息
        
        参数:
            expected: 期望值
            operator: 操作符（==, contains, json_path）
            json_path: JSONPath 表达式（当 operator 为 json_path 时）
        """
        message = g_context().get_dict("ws_last_message")
        if not message:
            raise RuntimeError("没有收到 WebSocket 消息")
        
        expected = kwargs.get("expected")
        operator = kwargs.get("operator", "==")
        json_path_expr = kwargs.get("json_path")
        
        if operator == "==":
            assert message == expected, f"WebSocket 断言失败: '{message}' != '{expected}'"
        elif operator == "contains":
            assert expected in message, f"WebSocket 断言失败: 消息不包含 '{expected}'"
        elif operator == "json_path":
            try:
                data = json.loads(message)
                result = jsonpath.jsonpath(data, json_path_expr)
                if not result:
                    raise ValueError(f"JSONPath '{json_path_expr}' 未找到匹配数据")
                actual = result[0]
                assert actual == expected, f"WebSocket JSON 断言失败: {actual} != {expected}"
            except json.JSONDecodeError:
                raise ValueError("WebSocket 消息不是有效的 JSON")
        else:
            raise ValueError(f"不支持的操作符: {operator}")
        
        print(f"WebSocket 断言成功")

    # ==================== HTTP 快捷方法 ====================

    @allure.step("GET 请求")
    async def request_get(self, **kwargs) -> None:
        """
        GET 请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
        """
        kwargs["method"] = "GET"
        await self.send_request(**kwargs)

    @allure.step("POST JSON 请求")
    async def request_post_json(self, **kwargs) -> None:
        """
        POST JSON 请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
            json: JSON 数据
        """
        kwargs["method"] = "POST"
        await self.send_request(**kwargs)

    @allure.step("POST 表单请求")
    async def request_post_form(self, **kwargs) -> None:
        """
        POST 表单请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
            data: 表单数据
        """
        kwargs["method"] = "POST"
        await self.send_request(**kwargs)

    @allure.step("POST 文件上传")
    async def request_post_file(self, **kwargs) -> None:
        """
        POST 文件上传快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
            data: 表单数据
            files: 上传文件
        """
        kwargs["method"] = "POST"
        await self.send_request(**kwargs)

    @allure.step("PUT 请求")
    async def request_put(self, **kwargs) -> None:
        """
        PUT 请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
            json: JSON 数据
        """
        kwargs["method"] = "PUT"
        await self.send_request(**kwargs)

    @allure.step("DELETE 请求")
    async def request_delete(self, **kwargs) -> None:
        """
        DELETE 请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
        """
        kwargs["method"] = "DELETE"
        await self.send_request(**kwargs)

    @allure.step("PATCH 请求")
    async def request_patch(self, **kwargs) -> None:
        """
        PATCH 请求快捷方法
        
        参数:
            url: 请求地址
            params: URL 参数
            headers: 请求头
            json: JSON 数据
        """
        kwargs["method"] = "PATCH"
        await self.send_request(**kwargs)




