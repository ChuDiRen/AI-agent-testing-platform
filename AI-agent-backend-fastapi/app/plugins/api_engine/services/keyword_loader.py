# Copyright (c) 2025 左岚. All rights reserved.
"""
关键字加载服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import inspect
import yaml
from pathlib import Path

from ..models.keyword import ApiEngineKeyword


class KeywordLoader:
    """关键字加载器"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._builtin_keywords = None
        self._params_config = None  # 缓存参数配置
    
    def _load_params_config(self) -> Dict[str, List[str]]:
        """加载关键字参数配置(从 keywords.yaml)"""
        if self._params_config is None:
            try:
                yaml_path = Path(__file__).parent.parent / "engine" / "extend" / "keywords.yaml"
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    self._params_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"加载参数配置失败: {str(e)}")
                self._params_config = {}
        return self._params_config

    async def load_builtin_keywords(self) -> List[Dict[str, Any]]:
        """加载内置关键字"""
        if self._builtin_keywords is None:
            try:
                from ..engine.extend.keywords import Keywords
                self._builtin_keywords = self._parse_keywords_class(Keywords)
            except Exception as e:
                print(f"加载内置关键字失败: {str(e)}")
                self._builtin_keywords = []

        return self._builtin_keywords
    
    async def load_custom_keywords(self) -> List[ApiEngineKeyword]:
        """加载自定义关键字"""
        result = await self.db.execute(
            select(ApiEngineKeyword).where(
                ApiEngineKeyword.is_builtin == False
            )
        )
        return list(result.scalars().all())
    
    async def load_all_keywords(self) -> List[Dict[str, Any]]:
        """加载所有关键字(内置+自定义)"""
        builtin = await self.load_builtin_keywords()
        custom = await self.load_custom_keywords()
        
        # 转换自定义关键字格式
        custom_keywords = [
            {
                "name": kw.name,
                "description": kw.description,
                "parameters": kw.parameters or [],
                "is_builtin": False
            }
            for kw in custom
        ]
        
        return builtin + custom_keywords
    
    def _parse_keywords_class(self, keywords_class) -> List[Dict[str, Any]]:
        """解析Keywords类,提取所有关键字方法"""
        keywords = []
        params_config = self._load_params_config()  # 加载 YAML 配置

        for name, method in inspect.getmembers(keywords_class, predicate=inspect.isfunction):
            # 跳过私有方法和特殊方法
            if name.startswith('_'):
                continue

            # 优先从 YAML 配置中获取参数列表
            params = []
            if name in params_config:
                yaml_params = params_config[name]
                # 处理两种格式: 字符串(逗号分隔) 或 列表
                if isinstance(yaml_params, str):
                    param_names = [p.strip() for p in yaml_params.split(',')]
                elif isinstance(yaml_params, list):
                    param_names = yaml_params
                else:
                    param_names = []

                for param_item in param_names:
                    # 处理带注释的参数: "EXVALUE  # JSON表达式"
                    if isinstance(param_item, str):
                        param_name = param_item.split('#')[0].strip()
                        param_desc = param_item.split('#')[1].strip() if '#' in param_item else f"参数: {param_name}"
                    else:
                        param_name = str(param_item)
                        param_desc = f"参数: {param_name}"

                    params.append({
                        "name": param_name,
                        "type": "string",
                        "required": True,
                        "description": param_desc
                    })

            # 获取文档字符串作为描述
            doc = inspect.getdoc(method) or f"关键字: {name}"

            keywords.append({
                "name": name,
                "description": doc,
                "parameters": params,
                "is_builtin": True
            })

        return keywords

    def _parse_params_from_docstring(self, docstring: str) -> List[Dict[str, Any]]:
        """从文档字符串中解析参数信息"""
        params = []
        lines = docstring.split('\n')

        for line in lines:
            line = line.strip()
            # 匹配格式: "参数名: 描述" 或 "参数名 (类型): 描述"
            if ':' in line and not line.startswith('>>>'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    param_part = parts[0].strip()
                    desc_part = parts[1].strip()

                    # 提取参数名 (可能包含类型信息)
                    param_name = param_part
                    param_type = "string"
                    required = True

                    # 处理 "参数名 (类型)" 格式
                    if '(' in param_name and ')' in param_name:
                        param_name = param_name.split('(')[0].strip()
                        type_info = param_part.split('(')[1].split(')')[0].strip()
                        param_type = type_info.lower() if type_info else "string"

                    # 检查是否为可选参数
                    if '非必填' in desc_part or 'optional' in desc_part.lower() or '可选' in desc_part:
                        required = False

                    params.append({
                        "name": param_name,
                        "type": param_type,
                        "required": required,
                        "description": desc_part
                    })

        return params

