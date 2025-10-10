# Copyright (c) 2025 左岚. All rights reserved.
"""
测试断言服务
提供丰富的断言功能
"""
import re
import json
import jsonpath
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class AssertionOperator(Enum):
    """断言操作符枚举"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"
    IN = "in"
    NOT_IN = "not_in"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    LENGTH_EQUALS = "length_equals"
    LENGTH_GREATER = "length_greater"
    LENGTH_LESS = "length_less"
    JSON_PATH_EXISTS = "json_path_exists"
    JSON_PATH_EQUALS = "json_path_equals"
    JSON_PATH_CONTAINS = "json_path_contains"
    REGEX_MATCH = "regex_match"
    REGEX_NOT_MATCH = "regex_not_match"
    IS_VALID_JSON = "is_valid_json"
    ARRAY_CONTAINS = "array_contains"
    ARRAY_NOT_CONTAINS = "array_not_contains"
    ARRAY_SIZE_EQUALS = "array_size_equals"
    ARRAY_SIZE_GREATER = "array_size_greater"
    ARRAY_SIZE_LESS = "array_size_less"


class AssertionResult:
    """断言结果"""
    def __init__(self, success: bool, actual: Any, expected: Any, message: str = ""):
        self.success = success
        self.actual = actual
        self.expected = expected
        self.message = message
        self.timestamp = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "success": self.success,
            "actual": self.actual,
            "expected": self.expected,
            "message": self.message
        }


class AssertionService:
    """断言服务"""

    @staticmethod
    def assert_equals(actual: Any, expected: Any) -> AssertionResult:
        """断言相等"""
        success = actual == expected
        message = f"断言相等: {actual} == {expected}" if success else f"断言失败: 期望 {expected}, 实际 {actual}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_not_equals(actual: Any, expected: Any) -> AssertionResult:
        """断言不相等"""
        success = actual != expected
        message = f"断言不相等: {actual} != {expected}" if success else f"断言失败: 期望 {actual} != {expected}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_greater_than(actual: Union[int, float], expected: Union[int, float]) -> AssertionResult:
        """断言大于"""
        success = actual > expected
        message = f"断言大于: {actual} > {expected}" if success else f"断言失败: 期望 {actual} > {expected}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_less_than(actual: Union[int, float], expected: Union[int, float]) -> AssertionResult:
        """断言小于"""
        success = actual < expected
        message = f"断言小于: {actual} < {expected}" if success else f"断言失败: 期望 {actual} < {expected}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_greater_equal(actual: Union[int, float], expected: Union[int, float]) -> AssertionResult:
        """断言大于等于"""
        success = actual >= expected
        message = f"断言大于等于: {actual} >= {expected}" if success else f"断言失败: 期望 {actual} >= {expected}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_less_equal(actual: Union[int, float], expected: Union[int, float]) -> AssertionResult:
        """断言小于等于"""
        success = actual <= expected
        message = f"断言小于等于: {actual} <= {expected}" if success else f"断言失败: 期望 {actual} <= {expected}"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_contains(actual: str, expected: str) -> AssertionResult:
        """断言包含"""
        success = expected in actual
        message = f"断言包含: '{actual}' 包含 '{expected}'" if success else f"断言失败: '{actual}' 不包含 '{expected}'"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_not_contains(actual: str, expected: str) -> AssertionResult:
        """断言不包含"""
        success = expected not in actual
        message = f"断言不包含: '{actual}' 不包含 '{expected}'" if success else f"断言失败: '{actual}' 包含 '{expected}'"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_starts_with(actual: str, expected: str) -> AssertionResult:
        """断言以指定字符串开始"""
        success = actual.startswith(expected)
        message = f"断言开始: '{actual}' 以 '{expected}' 开始" if success else f"断言失败: '{actual}' 不以 '{expected}' 开始"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_ends_with(actual: str, expected: str) -> AssertionResult:
        """断言以指定字符串结束"""
        success = actual.endswith(expected)
        message = f"断言结束: '{actual}' 以 '{expected}' 结束" if success else f"断言失败: '{actual}' 不以 '{expected}' 结束"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_matches(actual: str, pattern: str) -> AssertionResult:
        """断言匹配模式"""
        try:
            success = bool(re.match(pattern, actual))
            message = f"断言匹配: '{actual}' 匹配模式 '{pattern}'" if success else f"断言失败: '{actual}' 不匹配模式 '{pattern}'"
            return AssertionResult(success, actual, pattern, message)
        except re.error as e:
            return AssertionResult(False, actual, pattern, f"正则表达式错误: {str(e)}")

    @staticmethod
    def assert_in(actual: Any, expected: List[Any]) -> AssertionResult:
        """断言在列表中"""
        success = actual in expected
        message = f"断言包含: {actual} 在 {expected} 中" if success else f"断言失败: {actual} 不在 {expected} 中"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_not_in(actual: Any, expected: List[Any]) -> AssertionResult:
        """断言不在列表中"""
        success = actual not in expected
        message = f"断言不包含: {actual} 不在 {expected} 中" if success else f"断言失败: {actual} 在 {expected} 中"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_is_empty(actual: Any) -> AssertionResult:
        """断言为空"""
        success = not actual
        message = "断言为空: 值为空" if success else f"断言失败: 期望为空，实际为 {actual}"
        return AssertionResult(success, actual, None, message)

    @staticmethod
    def assert_is_not_empty(actual: Any) -> AssertionResult:
        """断言不为空"""
        success = bool(actual)
        message = f"断言不为空: 值为 {actual}" if success else "断言失败: 期望不为空，实际为空"
        return AssertionResult(success, actual, None, message)

    @staticmethod
    def assert_is_null(actual: Any) -> AssertionResult:
        """断言为None"""
        success = actual is None
        message = "断言为None: 值为None" if success else f"断言失败: 期望为None，实际为 {actual}"
        return AssertionResult(success, actual, None, message)

    @staticmethod
    def assert_is_not_null(actual: Any) -> AssertionResult:
        """断言不为None"""
        success = actual is not None
        message = f"断言不为None: 值为 {actual}" if success else "断言失败: 期望不为None，实际为None"
        return AssertionResult(success, actual, None, message)

    @staticmethod
    def assert_length_equals(actual: Any, expected: int) -> AssertionResult:
        """断言长度相等"""
        try:
            actual_length = len(actual)
            success = actual_length == expected
            message = f"断言长度相等: 长度 {actual_length} == {expected}" if success else f"断言失败: 期望长度 {expected}, 实际长度 {actual_length}"
            return AssertionResult(success, actual_length, expected, message)
        except TypeError:
            return AssertionResult(False, actual, expected, f"断言失败: {actual} 没有长度属性")

    @staticmethod
    def assert_length_greater(actual: Any, expected: int) -> AssertionResult:
        """断言长度大于"""
        try:
            actual_length = len(actual)
            success = actual_length > expected
            message = f"断言长度大于: 长度 {actual_length} > {expected}" if success else f"断言失败: 期望长度 > {expected}, 实际长度 {actual_length}"
            return AssertionResult(success, actual_length, expected, message)
        except TypeError:
            return AssertionResult(False, actual, expected, f"断言失败: {actual} 没有长度属性")

    @staticmethod
    def assert_length_less(actual: Any, expected: int) -> AssertionResult:
        """断言长度小于"""
        try:
            actual_length = len(actual)
            success = actual_length < expected
            message = f"断言长度小于: 长度 {actual_length} < {expected}" if success else f"断言失败: 期望长度 < {expected}, 实际长度 {actual_length}"
            return AssertionResult(success, actual_length, expected, message)
        except TypeError:
            return AssertionResult(False, actual, expected, f"断言失败: {actual} 没有长度属性")

    @staticmethod
    def assert_json_path_exists(data: Dict, json_path: str) -> AssertionResult:
        """断言JSON路径存在"""
        try:
            result = jsonpath.jsonpath(data, json_path)
            success = bool(result)
            message = f"断言JSON路径存在: '{json_path}' 存在" if success else f"断言失败: JSON路径 '{json_path}' 不存在"
            return AssertionResult(success, result[0] if result else None, json_path, message)
        except Exception as e:
            return AssertionResult(False, None, json_path, f"断言失败: JSON路径查询错误: {str(e)}")

    @staticmethod
    def assert_json_path_equals(data: Dict, json_path: str, expected: Any) -> AssertionResult:
        """断言JSON路径值相等"""
        try:
            result = jsonpath.jsonpath(data, json_path)
            if not result:
                return AssertionResult(False, None, expected, f"断言失败: JSON路径 '{json_path}' 不存在")

            actual = result[0] if len(result) == 1 else result
            success = actual == expected
            message = f"断言JSON路径相等: '{json_path}' 值为 {actual} == {expected}" if success else f"断言失败: 期望 {expected}, 实际 {actual}"
            return AssertionResult(success, actual, expected, message)
        except Exception as e:
            return AssertionResult(False, None, expected, f"断言失败: JSON路径查询错误: {str(e)}")

    @staticmethod
    def assert_json_path_contains(data: Dict, json_path: str, expected: Any) -> AssertionResult:
        """断言JSON路径值包含"""
        try:
            result = jsonpath.jsonpath(data, json_path)
            if not result:
                return AssertionResult(False, None, expected, f"断言失败: JSON路径 '{json_path}' 不存在")

            actual = result[0] if len(result) == 1 else result

            # 如果是字符串，检查包含关系
            if isinstance(actual, str):
                success = expected in actual
                message = f"断言JSON路径包含: '{json_path}' 值 '{actual}' 包含 '{expected}'" if success else f"断言失败: '{actual}' 不包含 '{expected}'"
            # 如果是列表，检查元素包含
            elif isinstance(actual, list):
                success = expected in actual
                message = f"断言JSON路径包含: '{json_path}' 列表包含 '{expected}'" if success else f"断言失败: 列表不包含 '{expected}'"
            else:
                return AssertionResult(False, actual, expected, f"断言失败: 不支持对 {type(actual)} 类型进行包含检查")

            return AssertionResult(success, actual, expected, message)
        except Exception as e:
            return AssertionResult(False, None, expected, f"断言失败: JSON路径查询错误: {str(e)}")

    @staticmethod
    def assert_regex_match(actual: str, pattern: str) -> AssertionResult:
        """断言正则匹配"""
        try:
            success = bool(re.search(pattern, actual))
            message = f"断言正则匹配: '{actual}' 匹配 '{pattern}'" if success else f"断言失败: '{actual}' 不匹配 '{pattern}'"
            return AssertionResult(success, actual, pattern, message)
        except re.error as e:
            return AssertionResult(False, actual, pattern, f"断言失败: 正则表达式错误: {str(e)}")

    @staticmethod
    def assert_regex_not_match(actual: str, pattern: str) -> AssertionResult:
        """断言正则不匹配"""
        try:
            success = not re.search(pattern, actual)
            message = f"断言正则不匹配: '{actual}' 不匹配 '{pattern}'" if success else f"断言失败: '{actual}' 匹配 '{pattern}'"
            return AssertionResult(success, actual, pattern, message)
        except re.error as e:
            return AssertionResult(False, actual, pattern, f"断言失败: 正则表达式错误: {str(e)}")

    @staticmethod
    def assert_is_valid_json(actual: str) -> AssertionResult:
        """断言是有效的JSON"""
        try:
            json.loads(actual)
            return AssertionResult(True, actual, "valid JSON", "断言有效JSON: 字符串是有效的JSON")
        except json.JSONDecodeError as e:
            return AssertionResult(False, actual, "valid JSON", f"断言失败: 不是有效的JSON - {str(e)}")

    @staticmethod
    def assert_array_contains(actual: List, expected: Any) -> AssertionResult:
        """断言数组包含元素"""
        success = expected in actual
        message = f"断言数组包含: {expected} 在数组中" if success else f"断言失败: {expected} 不在数组中"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_array_not_contains(actual: List, expected: Any) -> AssertionResult:
        """断言数组不包含元素"""
        success = expected not in actual
        message = f"断言数组不包含: {expected} 不在数组中" if success else f"断言失败: {expected} 在数组中"
        return AssertionResult(success, actual, expected, message)

    @staticmethod
    def assert_array_size_equals(actual: List, expected: int) -> AssertionResult:
        """断言数组大小相等"""
        actual_size = len(actual)
        success = actual_size == expected
        message = f"断言数组大小相等: {actual_size} == {expected}" if success else f"断言失败: 期望大小 {expected}, 实际大小 {actual_size}"
        return AssertionResult(success, actual_size, expected, message)

    @staticmethod
    def assert_array_size_greater(actual: List, expected: int) -> AssertionResult:
        """断言数组大小大于"""
        actual_size = len(actual)
        success = actual_size > expected
        message = f"断言数组大小大于: {actual_size} > {expected}" if success else f"断言失败: 期望大小 > {expected}, 实际大小 {actual_size}"
        return AssertionResult(success, actual_size, expected, message)

    @staticmethod
    def assert_array_size_less(actual: List, expected: int) -> AssertionResult:
        """断言数组大小小于"""
        actual_size = len(actual)
        success = actual_size < expected
        message = f"断言数组大小小于: {actual_size} < {expected}" if success else f"断言失败: 期望大小 < {expected}, 实际大小 {actual_size}"
        return AssertionResult(success, actual_size, expected, message)

    @classmethod
    def execute_assertion(cls, operator: str, actual: Any, expected: Any = None) -> AssertionResult:
        """执行断言"""
        operator_map = {
            AssertionOperator.EQUALS.value: cls.assert_equals,
            AssertionOperator.NOT_EQUALS.value: cls.assert_not_equals,
            AssertionOperator.GREATER_THAN.value: cls.assert_greater_than,
            AssertionOperator.LESS_THAN.value: cls.assert_less_than,
            AssertionOperator.GREATER_EQUAL.value: cls.assert_greater_equal,
            AssertionOperator.LESS_EQUAL.value: cls.assert_less_equal,
            AssertionOperator.CONTAINS.value: cls.assert_contains,
            AssertionOperator.NOT_CONTAINS.value: cls.assert_not_contains,
            AssertionOperator.STARTS_WITH.value: cls.assert_starts_with,
            AssertionOperator.ENDS_WITH.value: cls.assert_ends_with,
            AssertionOperator.MATCHES.value: cls.assert_matches,
            AssertionOperator.IN.value: cls.assert_in,
            AssertionOperator.NOT_IN.value: cls.assert_not_in,
            AssertionOperator.IS_EMPTY.value: cls.assert_is_empty,
            AssertionOperator.IS_NOT_EMPTY.value: cls.assert_is_not_empty,
            AssertionOperator.IS_NULL.value: cls.assert_is_null,
            AssertionOperator.IS_NOT_NULL.value: cls.assert_is_not_null,
            AssertionOperator.LENGTH_EQUALS.value: cls.assert_length_equals,
            AssertionOperator.LENGTH_GREATER.value: cls.assert_length_greater,
            AssertionOperator.LENGTH_LESS.value: cls.assert_length_less,
            AssertionOperator.REGEX_MATCH.value: cls.assert_regex_match,
            AssertionOperator.REGEX_NOT_MATCH.value: cls.assert_regex_not_match,
            AssertionOperator.IS_VALID_JSON.value: cls.assert_is_valid_json,
            AssertionOperator.ARRAY_CONTAINS.value: cls.assert_array_contains,
            AssertionOperator.ARRAY_NOT_CONTAINS.value: cls.assert_array_not_contains,
            AssertionOperator.ARRAY_SIZE_EQUALS.value: cls.assert_array_size_equals,
            AssertionOperator.ARRAY_SIZE_GREATER.value: cls.assert_array_size_greater,
            AssertionOperator.ARRAY_SIZE_LESS.value: cls.assert_array_size_less,
        }

        # 处理JSON相关的断言
        if operator == AssertionOperator.JSON_PATH_EXISTS.value:
            return cls.assert_json_path_exists(expected, actual)
        elif operator == AssertionOperator.JSON_PATH_EQUALS.value:
            return cls.assert_json_path_equals(expected, actual[0] if isinstance(actual, list) else actual)
        elif operator == AssertionOperator.JSON_PATH_CONTAINS.value:
            return cls.assert_json_path_contains(expected, actual[0] if isinstance(actual, list) else actual)

        # 普通断言
        assertion_func = operator_map.get(operator)
        if not assertion_func:
            return AssertionResult(False, actual, expected, f"不支持的断言操作符: {operator}")

        if expected is None and operator not in [
            AssertionOperator.IS_EMPTY.value, AssertionOperator.IS_NOT_EMPTY.value,
            AssertionOperator.IS_NULL.value, AssertionOperator.IS_NOT_NULL.value,
            AssertionOperator.IS_VALID_JSON.value
        ]:
            return AssertionResult(False, actual, expected, f"断言操作符 {operator} 需要期望值")

        return assertion_func(actual, expected)


class AssertionGroup:
    """断言组，支持批量断言"""

    def __init__(self, name: str = ""):
        self.name = name
        self.assertions: List[Dict] = []
        self.results: List[AssertionResult] = []

    def add_assertion(self, operator: str, actual: Any, expected: Any = None, description: str = ""):
        """添加断言"""
        assertion = {
            "operator": operator,
            "actual": actual,
            "expected": expected,
            "description": description
        }
        self.assertions.append(assertion)

    def execute_all(self) -> List[AssertionResult]:
        """执行所有断言"""
        self.results = []
        for assertion in self.assertions:
            result = AssertionService.execute_assertion(
                assertion["operator"],
                assertion["actual"],
                assertion["expected"]
            )
            result.description = assertion.get("description", "")
            self.results.append(result)

        return self.results

    def get_success_count(self) -> int:
        """获取成功的断言数量"""
        return sum(1 for result in self.results if result.success)

    def get_failure_count(self) -> int:
        """获取失败的断言数量"""
        return sum(1 for result in self.results if not result.success)

    def is_all_passed(self) -> bool:
        """是否所有断言都通过"""
        return all(result.success for result in self.results)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "total_assertions": len(self.assertions),
            "success_count": self.get_success_count(),
            "failure_count": self.get_failure_count(),
            "all_passed": self.is_all_passed(),
            "assertions": [
                {
                    "operator": assertion["operator"],
                    "actual": assertion["actual"],
                    "expected": assertion["expected"],
                    "description": assertion.get("description", "")
                }
                for assertion in self.assertions
            ],
            "results": [result.to_dict() for result in self.results]
        }