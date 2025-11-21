# -*- coding: utf-8 -*-
"""代码生成器-表配置模型"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class GenTable(SQLModel, table=True): # 代码生成器表配置
    __tablename__ = "gen_table"
    
    id: Optional[int] = Field(default=None, primary_key=True) # 主键ID
    table_name: str = Field(max_length=200, index=True) # 表名
    table_comment: Optional[str] = Field(default=None, max_length=500) # 表描述
    class_name: Optional[str] = Field(default=None, max_length=100) # 实体类名称
    module_name: Optional[str] = Field(default=None, max_length=50) # 模块名称(如:sysmanage)
    business_name: Optional[str] = Field(default=None, max_length=50) # 业务名称(如:user)
    function_name: Optional[str] = Field(default=None, max_length=50) # 功能名称(如:用户管理)
    function_author: Optional[str] = Field(default='左岚团队', max_length=50) # 作者
    gen_type: str = Field(default='0', max_length=1) # 生成代码方式(0:zip压缩包 1:自定义路径)
    gen_path: Optional[str] = Field(default='/', max_length=200) # 生成路径(不填默认项目路径)
    
    # 树表相关配置
    tpl_category: str = Field(default='crud', max_length=50) # 模板类型: crud, tree
    tree_code: Optional[str] = Field(default=None, max_length=50) # 树编码字段(id)
    tree_parent_code: Optional[str] = Field(default=None, max_length=50) # 树父编码字段(parent_id)
    tree_name: Optional[str] = Field(default=None, max_length=50) # 树名称字段(name)
    
    options: Optional[str] = Field(default=None, max_length=1000) # 其他生成选项(JSON格式)
    remark: Optional[str] = Field(default=None, max_length=500) # 备注
    create_by: Optional[str] = Field(default=None, max_length=64) # 创建者
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    update_by: Optional[str] = Field(default=None, max_length=64) # 更新者
    update_time: Optional[datetime] = Field(default_factory=datetime.now) # 更新时间
