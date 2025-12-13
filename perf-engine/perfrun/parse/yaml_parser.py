"""
YAML 用例解析器
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

from ..core.globalContext import g_context
from ..core.exceptions import ParserError
from ..utils.VarRender import refresh

class PerfCaseParser:
    """性能测试用例解析器"""
    
    def __init__(self):
        self.context = {}
    
    def load_cases(self, cases_dir: Path) -> List[Dict[str, Any]]:
        """加载目录下所有用例"""
        cases = []
        
        # 先加载 context.yaml 并存储到全局上下文
        context_file = cases_dir / "context.yaml"
        if context_file.exists():
            self.context = self._load_yaml(context_file) or {}
            # 同步到全局上下文
            g_context().set_by_dict(self.context)
            print(f"  加载全局配置: {context_file}")
        
        # 保存用例目录路径到全局上下文，供 VarRender 文件路径解析使用
        g_context().set_dict("_cases_dir", str(cases_dir.resolve()))
        
        # 加载所有用例文件
        for yaml_file in sorted(cases_dir.glob("*.yaml")):
            if yaml_file.name == "context.yaml":
                continue
            
            case = self._load_yaml(yaml_file)
            if case:
                # 合并全局上下文
                if "context" not in case:
                    case["context"] = {}
                case["context"].update(self.context)
                
                # 设置用例来源
                case["_source_file"] = str(yaml_file)
                
                cases.append(case)
                print(f"  加载用例: {yaml_file.name}")
        
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
