# Copyright (c) 2025 左岚. All rights reserved.
"""任务状态Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str = Field(..., description="任务ID")
    state: str = Field(..., description="任务状态")  # PENDING/PROCESSING/SUCCESS/FAILURE
    current: Optional[int] = Field(None, description="当前进度")
    total: Optional[int] = Field(None, description="总进度")
    status: Optional[str] = Field(None, description="状态描述")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")


class TaskSubmitResponse(BaseModel):
    """任务提交响应"""
    task_id: str = Field(..., description="任务ID")
    doc_id: int = Field(..., description="文档ID")
    message: str = Field(..., description="提示信息")


class BatchTaskSubmitResponse(BaseModel):
    """批量任务提交响应"""
    total: int = Field(..., description="总任务数")
    submitted: int = Field(..., description="已提交数")
    failed: int = Field(..., description="失败数")
    task_ids: list[str] = Field(..., description="任务ID列表")

