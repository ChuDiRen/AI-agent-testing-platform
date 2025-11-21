# -*- coding: utf-8 -*-
"""代码生成器表配置Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List

class GenTableQuery(BaseModel): # 查询参数
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    table_name: Optional[str] = Field(default=None, description='表名')
    table_comment: Optional[str] = Field(default=None, description='表描述')

class GenTableCreate(BaseModel): # 创建参数
    table_name: str = Field(description='表名')
    table_comment: Optional[str] = Field(default=None, description='表描述')
    class_name: Optional[str] = Field(default=None, description='实体类名称')
    module_name: Optional[str] = Field(default=None, description='模块名称')
    business_name: Optional[str] = Field(default=None, description='业务名称')
    function_name: Optional[str] = Field(default=None, description='功能名称')
    function_author: str = Field(default='左岚团队', description='作者')
    gen_type: str = Field(default='0', description='生成代码方式')
    gen_path: str = Field(default='/', description='生成路径')

class GenTableUpdate(BaseModel): # 更新参数
    id: int = Field(description='主键ID')
    table_comment: Optional[str] = Field(default=None, description='表描述')
    class_name: Optional[str] = Field(default=None, description='实体类名称')
    module_name: Optional[str] = Field(default=None, description='模块名称')
    business_name: Optional[str] = Field(default=None, description='业务名称')
    function_name: Optional[str] = Field(default=None, description='功能名称')
    function_author: Optional[str] = Field(default=None, description='作者')
    gen_type: Optional[str] = Field(default=None, description='生成代码方式')
    gen_path: Optional[str] = Field(default=None, description='生成路径')

class GenTableImport(BaseModel): # 导入表参数
    table_names: List[str] = Field(description='表名列表')
