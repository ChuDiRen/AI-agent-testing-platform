# Copyright (c) 2025 左岚. All rights reserved.
"""
内置关键字管理器
"""
from typing import Dict, List, Any


class BuiltinKeywords:
    """内置关键字管理器"""

    @staticmethod
    def get_builtin_keywords() -> List[Dict[str, Any]]:
        """获取所有内置关键字"""
        return [
            {
                "name": "send_request",
                "display_name": "发送HTTP请求",
                "description": "发送HTTP请求并获取响应",
                "category": "HTTP请求",
                "params": [
                    {
                        "name": "url",
                        "type": "string",
                        "required": True,
                        "description": "请求URL"
                    },
                    {
                        "name": "method",
                        "type": "select",
                        "required": True,
                        "description": "HTTP方法",
                        "options": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
                    },
                    {
                        "name": "headers",
                        "type": "json",
                        "required": False,
                        "description": "请求头"
                    },
                    {
                        "name": "params",
                        "type": "json",
                        "required": False,
                        "description": "URL参数"
                    },
                    {
                        "name": "data",
                        "type": "text",
                        "required": False,
                        "description": "请求体数据"
                    },
                    {
                        "name": "json",
                        "type": "json",
                        "required": False,
                        "description": "JSON格式请求体"
                    },
                    {
                        "name": "files",
                        "type": "json",
                        "required": False,
                        "description": "上传文件"
                    },
                    {
                        "name": "timeout",
                        "type": "number",
                        "required": False,
                        "description": "超时时间(秒)"
                    }
                ],
                "example": """
- send_request:
    url: https://api.example.com/users
    method: POST
    headers:
      Content-Type: application/json
      Authorization: Bearer ${token}
    json:
      name: John Doe
      email: john@example.com
    timeout: 30
"""
            },
            {
                "name": "assert_status_code",
                "display_name": "断言状态码",
                "description": "断言响应状态码",
                "category": "断言",
                "params": [
                    {
                        "name": "EXPECTED",
                        "type": "number",
                        "required": True,
                        "description": "期望的状态码"
                    }
                ],
                "example": """
- assert_status_code:
    EXPECTED: 200
"""
            },
            {
                "name": "assert_response_contains",
                "display_name": "断言响应内容",
                "description": "断言响应内容包含指定文本",
                "category": "断言",
                "params": [
                    {
                        "name": "EXPECTED",
                        "type": "string",
                        "required": True,
                        "description": "期望包含的文本"
                    }
                ],
                "example": """
- assert_response_contains:
    EXPECTED: "success"
"""
            },
            {
                "name": "assert_json_path_exists",
                "display_name": "断言JSON路径",
                "description": "断言JSON响应中指定路径存在",
                "category": "断言",
                "params": [
                    {
                        "name": "JSON_PATH",
                        "type": "string",
                        "required": True,
                        "description": "JSON路径表达式"
                    }
                ],
                "example": """
- assert_json_path_exists:
    JSON_PATH: "$.data.user.id"
"""
            },
            {
                "name": "ex_jsonData",
                "display_name": "提取JSON数据",
                "description": "从JSON响应中提取数据并存储为变量",
                "category": "数据提取",
                "params": [
                    {
                        "name": "EXVALUE",
                        "type": "string",
                        "required": True,
                        "description": "JSON路径表达式"
                    },
                    {
                        "name": "INDEX",
                        "type": "number",
                        "required": False,
                        "description": "结果索引(默认0)"
                    },
                    {
                        "name": "VARNAME",
                        "type": "string",
                        "required": True,
                        "description": "变量名"
                    }
                ],
                "example": """
- ex_jsonData:
    EXVALUE: "$.data.token"
    VARNAME: access_token
"""
            },
            {
                "name": "ex_reData",
                "display_name": "提取正则数据",
                "description": "从响应文本中提取正则匹配数据",
                "category": "数据提取",
                "params": [
                    {
                        "name": "EXVALUE",
                        "type": "string",
                        "required": True,
                        "description": "正则表达式"
                    },
                    {
                        "name": "INDEX",
                        "type": "number",
                        "required": False,
                        "description": "结果索引(默认0)"
                    },
                    {
                        "name": "VARNAME",
                        "type": "string",
                        "required": True,
                        "description": "变量名"
                    }
                ],
                "example": """
- ex_reData:
    EXVALUE: "token=([a-f0-9]+)"
    VARNAME: token
"""
            },
            {
                "name": "set_variable",
                "display_name": "设置变量",
                "description": "设置变量到全局上下文",
                "category": "变量操作",
                "params": [
                    {
                        "name": "VAR_NAME",
                        "type": "string",
                        "required": True,
                        "description": "变量名"
                    },
                    {
                        "name": "VAR_VALUE",
                        "type": "text",
                        "required": True,
                        "description": "变量值"
                    }
                ],
                "example": """
- set_variable:
    VAR_NAME: username
    VAR_VALUE: testuser
"""
            },
            {
                "name": "sleep",
                "display_name": "等待",
                "description": "等待指定秒数",
                "category": "控制流程",
                "params": [
                    {
                        "name": "SECONDS",
                        "type": "number",
                        "required": True,
                        "description": "等待秒数"
                    }
                ],
                "example": """
- sleep:
    SECONDS: 2
"""
            },
            {
                "name": "log_message",
                "display_name": "输出日志",
                "description": "输出日志消息",
                "category": "调试",
                "params": [
                    {
                        "name": "MESSAGE",
                        "type": "string",
                        "required": True,
                        "description": "日志消息"
                    },
                    {
                        "name": "LEVEL",
                        "type": "select",
                        "required": False,
                        "description": "日志级别",
                        "options": ["INFO", "SUCCESS", "WARNING", "ERROR"]
                    }
                ],
                "example": """
- log_message:
    MESSAGE: "测试步骤执行成功"
    LEVEL: "SUCCESS"
"""
            }
        ]

    @staticmethod
    def get_keywords_by_category() -> Dict[str, List[Dict[str, Any]]]:
        """按分类获取关键字"""
        keywords = BuiltinKeywords.get_builtin_keywords()
        categories = {}

        for keyword in keywords:
            category = keyword.get("category", "其他")
            if category not in categories:
                categories[category] = []
            categories[category].append(keyword)

        return categories

    @staticmethod
    def get_keyword_by_name(name: str) -> Dict[str, Any]:
        """根据名称获取关键字"""
        keywords = BuiltinKeywords.get_builtin_keywords()
        for keyword in keywords:
            if keyword.get("name") == name:
                return keyword
        return {}

    @staticmethod
    def get_keyword_names() -> List[str]:
        """获取所有关键字名称"""
        keywords = BuiltinKeywords.get_builtin_keywords()
        return [keyword.get("name") for keyword in keywords]