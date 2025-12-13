"""
用例解析器模块
支持多种格式的性能测试用例解析
"""

from .CaseParser import case_parser
from .yaml_parser import PerfCaseParser

__all__ = ["case_parser", "PerfCaseParser"]
