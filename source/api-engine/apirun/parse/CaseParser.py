# 用例解析器， 根据你传过来的参数，选择不同的解析器
import os

from apirun.parse.YamlCaseParser import yaml_case_parser
from apirun.parse.ExcelCaseParser import excel_case_parser


def case_parser(case_type, case_dir):
    """
    type： 用例类型
    dir: 用例所在文件夹
    return: 返回 {"case_name":[], "cases_info":[]}
    """
    config_path = os.path.abspath(case_dir)
    print("用例读取中...", dir)
    if case_type == 'yaml':
        return yaml_case_parser(config_path)
    if case_type == 'excel':
        return excel_case_parser(config_path)

    return {"case_name": [], "cases_info": []}


def test_yaml_case_parser():
    # 单元测试 ，检查 yaml_case_parser 方法的正确性
    data = case_parser("yaml", "../../examples")
    print(data)