from pathlib import Path
from typing import Any

from .ExcelCaseParser import excel_case_parser
from .YamlCaseParser import yaml_case_parser
from ..core.exceptions import ParserError


def case_parser(case_type: str, case_dir: Path) -> dict[str, list[Any]]:
    config_path = case_dir.resolve()

    match case_type:
        case "yaml":
            return yaml_case_parser(config_path)
        case "excel":
            return excel_case_parser(config_path)
        case _:
            raise ParserError(f"不支持的用例类型: {case_type}")
