"""
操作日志模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class OperationLog(SQLModel, table=True):
    """操作日志表"""

    __tablename__ = "sys_operation_log"

    id: Optional[int] = Field(default=None, primary_key=True, description="日志ID")
    user_id: Optional[int] = Field(default=None, foreign_key="sys_user.id", index=True, description="用户ID")
    username: Optional[str] = Field(default=None, max_length=50, description="用户名")
    module: str = Field(max_length=50, description="模块")
    operation: str = Field(max_length=50, description="操作类型")
    method: Optional[str] = Field(default=None, max_length=10, description="请求方法")
    url: Optional[str] = Field(default=None, max_length=500, description="请求URL")
    ip: Optional[str] = Field(default=None, max_length=50, description="IP地址")
    location: Optional[str] = Field(default=None, max_length=200, description="地址")
    browser: Optional[str] = Field(default=None, max_length=200, description="浏览器")
    os: Optional[str] = Field(default=None, max_length=200, description="操作系统")
    status: int = Field(default=1, description="状态：1成功 0失败")
    error_msg: Optional[str] = Field(default=None, max_length=500, description="错误信息")
    cost_time: Optional[int] = Field(default=None, description="耗时(毫秒）")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
