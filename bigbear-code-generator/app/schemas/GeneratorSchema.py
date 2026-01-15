# -*- coding: utf-8 -*-
"""代码生成器请求Schema"""
from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel): # 生成代码请求
    table_id: int = Field(description='表配置ID')
    gen_type: str = Field(default='0', description='生成方式(0:预览 1:下载 2:生成到路径)')
    gen_path: Optional[str] = Field(default=None, description='生成路径')

class GeneratePreviewRequest(BaseModel): # 预览代码请求
    table_id: int = Field(description='表配置ID')

class GenerateBatchRequest(BaseModel): # 批量生成请求
    table_ids: List[int] = Field(description='表配置ID列表')
    gen_type: str = Field(default='1', description='生成方式(0:预览 1:下载 2:生成到路径)')
    gen_path: Optional[str] = Field(default=None, description='生成路径')
