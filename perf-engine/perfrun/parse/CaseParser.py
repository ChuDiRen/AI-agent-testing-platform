"""
用例解析器入口
根据用例类型选择对应的解析器
"""
from pathlib import Path
from typing import Any, List, Dict

from .yaml_parser import PerfCaseParser
from ..core.exceptions import ParserError


def case_parser(case_type: str, case_dir: Path) -> List[Dict[str, Any]]:
    """
    用例解析器 - 使用模式匹配选择解析器
    
    :param case_type: 用例类型 (yaml/jmx/locustfile 等)
    :param case_dir: 用例所在文件夹路径（Path对象）
    :return: 用例信息列表
    :raises ParserError: 不支持的用例类型
    """
    config_path = case_dir.resolve()
    print(f"用例读取中... 路径: {config_path}")
    
    # 使用 match-case 模式匹配
    match case_type:
        case 'yaml':
            parser = PerfCaseParser()
            return parser.load_cases(config_path)
        case 'jmx':
            # 预留 JMeter 格式支持
            raise ParserError("JMeter 格式暂未支持")
        case 'locustfile':
            # 预留 Locust Python 脚本支持
            raise ParserError("Locustfile 格式暂未支持")
        case _:
            raise ParserError(f"不支持的用例类型: {case_type}")


def test_yaml_case_parser() -> None:
    """单元测试 - 检查 yaml_case_parser 方法的正确性"""
    cases = case_parser("yaml", Path("../../examples/example-locust-cases"))
    print(f"加载了 {len(cases)} 个用例")
    for case in cases:
        print(f"  - {case.get('desc', 'Unknown')}")

