# Copyright (c) 2025 左岚. All rights reserved.
"""
执行记录Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ExecutionResponse(BaseModel):
    """执行记录响应Schema"""
    execution_id: int = Field(..., description="执行记录ID")
    case_id: int = Field(..., description="用例ID")
    task_id: str = Field(..., description="Celery任务ID")
    status: str = Field(..., description="执行状态")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")
    logs: Optional[str] = Field(None, description="执行日志")
    error_message: Optional[str] = Field(None, description="错误信息")
    duration: Optional[float] = Field(None, description="执行时长(秒)")
    steps_total: int = Field(0, description="总步骤数")
    steps_passed: int = Field(0, description="通过步骤数")
    steps_failed: int = Field(0, description="失败步骤数")
    executed_by: int = Field(..., description="执行人ID")
    executed_at: datetime = Field(..., description="执行时间")
    finished_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """执行记录列表响应Schema"""
    total: int = Field(..., description="总数")
    items: List[ExecutionResponse] = Field(..., description="执行记录列表")


class ExecutionStatusResponse(BaseModel):
    """执行状态响应Schema"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度百分比")
    current_step: Optional[str] = Field(None, description="当前步骤")
    message: Optional[str] = Field(None, description="状态消息")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")

