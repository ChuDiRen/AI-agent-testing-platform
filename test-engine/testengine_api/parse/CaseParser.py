# 用例解析器， 根据你传过来的参数，选择不同的解析器
import os
from typing import List, Dict

from .ExcelCaseParser import excel_case_parser  # 相对导入: 同级模块
from .YamlCaseParser import yaml_case_parser  # 相对导入: 同级模块


def case_parser(case_type: str, case_dir: str) -> Dict[str, List]:
    """
    用例解析器工厂函数
    
    :param case_type: 用例类型 (yaml/excel)
    :param case_dir: 用例所在文件夹
    :return: 返回 {"case_infos": [], "case_names": []}
    """
    config_path = os.path.abspath(case_dir)
    print(f"用例读取中... 路径: {config_path}")
    
    # 使用 match-case 语句（Python 3.10+）
    match case_type.lower():
        case 'yaml':
            return yaml_case_parser(config_path)
        case 'excel':
            return excel_case_parser(config_path)
        case _:
            print(f"警告: 不支持的用例类型 '{case_type}'")
            return {"case_infos": [], "case_names": []}


def test_yaml_case_parser():
    # 单元测试 ，检查 yaml_case_parser 方法的正确性
    data = case_parser("yaml", "../../examples")
    print(data)