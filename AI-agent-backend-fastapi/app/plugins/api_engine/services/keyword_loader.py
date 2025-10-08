# Copyright (c) 2025 左岚. All rights reserved.
"""
关键字加载服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import inspect

from ..models.keyword import ApiEngineKeyword


class KeywordLoader:
    """关键字加载器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._builtin_keywords = None
    
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
                "params_schema": kw.params_schema or [],
                "is_builtin": False
            }
            for kw in custom
        ]
        
        return builtin + custom_keywords
    
    def _parse_keywords_class(self, keywords_class) -> List[Dict[str, Any]]:
        """解析Keywords类,提取所有关键字方法"""
        keywords = []
        
        for name, method in inspect.getmembers(keywords_class, predicate=inspect.isfunction):
            # 跳过私有方法和特殊方法
            if name.startswith('_'):
                continue
            
            # 获取方法签名
            sig = inspect.signature(method)
            params = []
            
            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'kwargs']:
                    continue
                
                params.append({
                    "name": param_name,
                    "type": "string",
                    "required": param.default == inspect.Parameter.empty,
                    "description": f"参数: {param_name}"
                })
            
            # 获取文档字符串
            doc = inspect.getdoc(method) or f"关键字: {name}"
            
            keywords.append({
                "name": name,
                "description": doc,
                "params_schema": params,
                "is_builtin": True
            })
        
        return keywords

