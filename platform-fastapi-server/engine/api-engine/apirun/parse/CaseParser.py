"""
用例解析器入口
根据用例类型选择对应的解析器
"""
from pathlib import Path
from typing import Any

from .ExcelCaseParser import excel_case_parser
from .YamlCaseParser import yaml_case_parser
from ..core.exceptions import ParserError


def case_parser(case_type: str, case_dir: Path) -> dict[str, list[Any]]:
    """
    用例解析器 - 使用模式匹配选择解析器
    
    :param case_type: 用例类型 (yaml/excel)
    :param case_dir: 用例所在文件夹路径（Path对象）
    :return: 包含用例信息的字典 {"case_infos": [...], "case_names": [...]}
    :raises ParserError: 不支持的用例类型
    """
    config_path = case_dir.resolve()
    print(f"用例读取中... 路径: {config_path}")
    
    # 使用 match-case 模式匹配
    match case_type:
        case 'yaml':
            return yaml_case_parser(config_path)
        case 'excel':
            return excel_case_parser(config_path)
        case _:
            raise ParserError(f"不支持的用例类型: {case_type}")


def test_yaml_case_parser() -> None:
    """单元测试 - 检查 yaml_case_parser 方法的正确性"""
    data = case_parser("yaml", Path("../../examples"))
    print(data)