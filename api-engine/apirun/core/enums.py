"""
枚举类型定义
用于定义API自动化测试引擎中的常量
"""
from enum import Enum


class CaseType(str, Enum):
    """测试用例类型枚举"""
    YAML = "yaml"
    EXCEL = "excel"
    PYTEST = "pytest"


class HttpMethod(str, Enum):
    """HTTP 请求方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AssertOperator(str, Enum):
    """断言操作符枚举"""
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


__all__ = ["CaseType", "HttpMethod", "AssertOperator"]

