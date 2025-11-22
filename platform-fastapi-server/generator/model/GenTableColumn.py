# -*- coding: utf-8 -*-
"""代码生成器-表字段配置模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class GenTableColumn(SQLModel, table=True): # 代码生成器表字段配置
    __tablename__ = "gen_table_column"
    
    id: Optional[int] = Field(default=None, primary_key=True) # 主键ID
    table_id: int = Field(index=True) # 归属表ID(关联gen_table.id)
    column_name: str = Field(max_length=200) # 列名称
    column_comment: Optional[str] = Field(default=None, max_length=500) # 列描述
    column_type: str = Field(max_length=100) # 列类型(如:varchar(50))
    column_length: Optional[int] = Field(default=None) # 列长度
    python_type: Optional[str] = Field(default=None, max_length=50) # Python类型(如:str)
    python_field: Optional[str] = Field(default=None, max_length=200) # Python属性名(驼峰命名)
    is_pk: str = Field(default='0', max_length=1) # 是否主键(0:否 1:是)
    is_increment: str = Field(default='0', max_length=1) # 是否自增(0:否 1:是)
    is_required: str = Field(default='0', max_length=1) # 是否必填(0:否 1:是)
    is_insert: str = Field(default='1', max_length=1) # 是否为插入字段(0:否 1:是)
    is_edit: str = Field(default='1', max_length=1) # 是否编辑字段(0:否 1:是)
    is_list: str = Field(default='1', max_length=1) # 是否列表字段(0:否 1:是)
    is_query: str = Field(default='0', max_length=1) # 是否查询字段(0:否 1:是)
    query_type: Optional[str] = Field(default='EQ', max_length=20) # 查询方式(EQ等于/NE不等于/LIKE模糊)
    html_type: Optional[str] = Field(default='input', max_length=20) # 显示类型(input文本框/textarea文本域/select下拉框)
    dict_type: Optional[str] = Field(default=None, max_length=200) # 字典类型
    sort: int = Field(default=0) # 排序
    create_by: Optional[str] = Field(default=None, max_length=64) # 创建者
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    update_by: Optional[str] = Field(default=None, max_length=64) # 更新者
    update_time: Optional[datetime] = Field(default_factory=datetime.now) # 更新时间
