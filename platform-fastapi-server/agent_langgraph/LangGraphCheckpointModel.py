"""
LangGraph Checkpoint数据库模型
用于存储LangGraph的对话状态和检查点
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text


class LangGraphCheckpoint(SQLModel, table=True):
    """LangGraph检查点表"""
    __tablename__ = "langgraph_checkpoint"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 线程标识符，对应LangGraph的thread_id
    thread_id: str = Field(index=True)
    
    # 检查点ID，用于标识特定的检查点
    checkpoint_id: str = Field(index=True)
    
    # 父检查点ID，用于构建检查点链
    parent_checkpoint_id: Optional[str] = Field(default=None, index=True)
    
    # 检查点数据，使用JSON格式存储
    checkpoint_data: str = Field(sa_column=Column(Text))
    
    # 元数据，使用JSON格式存储
    checkpoint_metadata: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # 检查点创建时间
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 检查点配置信息
    config_data: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # 是否已被提交
    is_pending: bool = Field(default=True)
    
    class Config:
        table_name = "langgraph_checkpoint"


class LangGraphCheckpointWrite(SQLModel, table=True):
    """LangGraph检查点写入记录表，用于原子操作"""
    __tablename__ = "langgraph_checkpoint_write"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 线程ID
    thread_id: str = Field(index=True)
    
    # 检查点ID
    checkpoint_id: str = Field(index=True)
    
    # 检查点数据
    checkpoint_data: str = Field(sa_column=Column(Text))
    
    # 元数据
    checkpoint_metadata: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # 创建时间
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 任务ID，用于并发控制
    task_id: str = Field(index=True)
    
    # 是否已完成
    completed: bool = Field(default=False)
    
    class Config:
        table_name = "langgraph_checkpoint_write"