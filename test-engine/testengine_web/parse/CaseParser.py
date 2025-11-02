"""
测试用例解析器入口
根据用例类型选择对应的解析器
"""
from typing import List, Dict

from .YamlCaseParser import yaml_case_parser  # 相对导入: 同级模块
from .ExcelCaseParser import excel_case_parser  # 相对导入: 同级模块


def case_parser(case_type: str, cases_dir: str) -> Dict[str, List]:
    """
    用例解析器工厂函数
    
    :param case_type: 用例类型 (yaml/excel)
    :param cases_dir: 用例目录
    :return: 解析后的用例数据 {"case_infos": [], "case_names": []}
    """
    # 使用 match-case 语句（Python 3.10+）
    match case_type.lower():
        case 'yaml':
            return yaml_case_parser(cases_dir)
        case 'excel':
            return excel_case_parser(cases_dir)
        case _:
            print(f"警告: 不支持的用例类型 '{case_type}'")
            return {"case_infos": [], "case_names": []}

