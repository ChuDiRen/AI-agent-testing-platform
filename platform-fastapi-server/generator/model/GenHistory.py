# -*- coding: utf-8 -*-
"""代码生成器-生成历史记录模型"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class GenHistory(SQLModel, table=True): # 代码生成历史记录
    __tablename__ = "gen_history"
    
    id: Optional[int] = Field(default=None, primary_key=True) # 主键ID
    table_id: int = Field(index=True) # 表配置ID(关联gen_table.id)
    table_name: str = Field(max_length=200) # 表名
    gen_type: str = Field(default='0', max_length=1) # 生成方式(0:预览 1:下载 2:生成到路径)
    gen_content: Optional[str] = Field(default=None, max_length=10000) # 生成内容(预览时保存)
    gen_path: Optional[str] = Field(default=None, max_length=500) # 生成路径
    file_count: int = Field(default=0) # 生成文件数量
    status: str = Field(default='1', max_length=1) # 生成状态(0:失败 1:成功)
    error_msg: Optional[str] = Field(default=None, max_length=500) # 错误信息
    create_by: Optional[str] = Field(default=None, max_length=64) # 创建者
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
