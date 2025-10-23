"""
测试用例解析器入口
根据用例类型选择对应的解析器
"""
from .YamlCaseParser import yaml_case_parser  # 相对导入: 同级模块


def case_parser(case_type, cases_dir):
    """
    用例解析器
    
    :param case_type: 用例类型 (yaml/excel/等)
    :param cases_dir: 用例目录
    :return: 解析后的用例数据
    """
    if case_type.lower() == "yaml":
        return yaml_case_parser(cases_dir)
    else:
        raise ValueError(f"不支持的用例类型: {case_type}")

