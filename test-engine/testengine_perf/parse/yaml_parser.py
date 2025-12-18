"""
YAML 用例解析器
负责加载和解析 YAML 格式的性能测试用例
"""
import copy
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, TypeAlias

import yaml

from ..core.globalContext import g_context
from ..core.exceptions import ParserError
from ..utils.VarRender import refresh

# 类型别名
CaseDict: TypeAlias = Dict[str, Any]
CaseList: TypeAlias = List[CaseDict]


class PerfCaseParser:
    """性能测试用例解析器"""

    def __init__(self):
        self.context: Dict[str, Any] = {}
    
    def load_cases(self, cases_dir: Path) -> CaseList:
        """
        加载目录下所有测试用例

        :param cases_dir: 用例目录路径（Path对象）
        :return: 用例信息列表
        """
        cases: CaseList = []

        # 先加载 context.yaml 并存储到全局上下文
        self._load_context_from_yaml(cases_dir)

        # 保存用例目录路径到全局上下文，供 VarRender 文件路径解析使用
        g_context().set_dict("_cases_dir", str(cases_dir.resolve()))

        # 一步完成：筛选、排序 YAML 文件（与 api-engine 保持一致）
        sorted_files = sorted(
            [f for f in cases_dir.iterdir()
             if f.suffix == ".yaml" and f.name != "context.yaml" and f.stem.split("_")[0].isdigit()],
            key=lambda f: int(f.stem.split("_")[0])
        )

        # 加载并处理用例文件
        for yaml_file in sorted_files:
            case = self._load_yaml(yaml_file)
            if case:
                # 处理数据驱动测试（DDT）
                cases.extend(self._process_ddt(case, yaml_file))

        return cases

    def _load_context_from_yaml(self, folder_path: Path) -> bool:
        """
        从文件夹中加载 context.yaml 配置文件

        :param folder_path: 文件夹路径（Path对象）
        :return: 加载是否成功
        """
        try:
            yaml_file_path = folder_path / 'context.yaml'

            if not yaml_file_path.exists():
                print(f"  ℹ️  context.yaml 文件不存在: {yaml_file_path}")
                return False

            with yaml_file_path.open('r', encoding='utf-8') as file:
                data = yaml.full_load(file)
                print(f"  📋 加载全局配置: context.yaml")
                if data:
                    self.context = data
                    g_context().set_by_dict(data)
            return True
        except Exception as e:
            print(f"  ⚠️  装载 context.yaml 文件错误: {str(e)}")
            return False

    def _process_ddt(self, caseinfo: CaseDict, yaml_file: Path) -> CaseList:
        """
        处理数据驱动测试（DDT）

        :param caseinfo: 原始用例信息
        :param yaml_file: YAML 文件路径
        :return: 处理后的用例列表
        """
        cases: CaseList = []

        # 使用海象操作符 - 读取 ddts 节点并生成多组测试用例
        if (ddts := caseinfo.get("ddts")) and len(ddts) > 0:
            caseinfo.pop("ddts")
            # 数据驱动测试 - 生成多个用例
            for ddt in ddts:
                new_case = copy.deepcopy(caseinfo)
                # 合并上下文 - 使用 | 操作符
                new_case["context"] = new_case.get("context", {}) | self.context | ddt
                # 生成用例名称
                case_name = f'{caseinfo.get("desc", uuid.uuid4().__str__())}-{ddt.get("desc", uuid.uuid4().__str__())}'
                new_case["_case_name"] = case_name
                new_case["_source_file"] = str(yaml_file)
                cases.append(new_case)
                print(f"    - {case_name}")
        else:
            # 单个用例 - 使用 match 解构获取 desc
            match caseinfo:
                case {"desc": desc}:
                    case_name = desc
                case _:
                    case_name = uuid.uuid4().__str__()

            caseinfo["_case_name"] = case_name
            caseinfo["_source_file"] = str(yaml_file)
            # 合并全局上下文
            caseinfo["context"] = caseinfo.get("context", {}) | self.context
            cases.append(caseinfo)
            print(f"  ✅ {yaml_file.name}: {case_name}")

        return cases
    
    def _load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载单个 YAML 文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ParserError(f"YAML 语法错误 {file_path}: {e}")
        except Exception as e:
            print(f"  ⚠️ 加载失败 {file_path}: {e}")
            return None
    
    def parse_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个用例，处理变量替换（使用 VarRender）"""
        # 合并全局上下文和用例上下文
        context = g_context().show_dict().copy()
        context.update(case.get("context", {}))
        return self._process_variables(case, context)
    
    def _process_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """递归处理变量替换（使用 VarRender.refresh）"""
        if isinstance(data, str):
            # 使用 VarRender 的 refresh 函数进行 Jinja2 模板渲染
            result = refresh(data, context)
            return result if result is not None else data
        elif isinstance(data, dict):
            return {k: self._process_variables(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._process_variables(item, context) for item in data]
        else:
            return data
    
    def _replace_variables(self, text: str, context: Dict[str, Any]) -> str:
        """
        替换字符串中的变量（向后兼容方法）
        推荐使用 VarRender.refresh() 替代
        """
        result = refresh(text, context)
        return result if result is not None else text
