from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class TestTaskQuery(BaseModel):
    """测试任务查询参数"""
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    task_name: Optional[str] = Field(default=None, description='任务名称')
    task_type: Optional[str] = Field(default=None, description='任务类型')
    task_status: Optional[str] = Field(default=None, description='任务状态')


class TestTaskCreate(BaseModel):
    """创建测试任务"""
    project_id: Optional[int] = Field(default=None, description='项目ID')
    task_name: str = Field(..., min_length=1, max_length=255, description='任务名称')
    task_desc: Optional[str] = Field(default=None, description='任务描述')
    task_type: str = Field(default='manual', description='任务类型：manual-手动, scheduled-定时')
    cron_expression: Optional[str] = Field(default=None, description='Cron表达式')
    plan_id: Optional[int] = Field(default=None, description='关联测试计划ID')
    case_ids: Optional[List[int]] = Field(default=None, description='关联用例ID列表')
    executor_code: str = Field(default='api_engine', description='执行引擎代码')
    notify_config: Optional[Dict[str, Any]] = Field(default=None, description='通知配置')
    extra_config: Optional[Dict[str, Any]] = Field(default=None, description='额外配置')


class TestTaskUpdate(BaseModel):
    """更新测试任务"""
    id: int = Field(..., description='任务ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    task_name: Optional[str] = Field(default=None, max_length=255, description='任务名称')
    task_desc: Optional[str] = Field(default=None, description='任务描述')
    task_type: Optional[str] = Field(default=None, description='任务类型')
    cron_expression: Optional[str] = Field(default=None, description='Cron表达式')
    plan_id: Optional[int] = Field(default=None, description='关联测试计划ID')
    case_ids: Optional[List[int]] = Field(default=None, description='关联用例ID列表')
    executor_code: Optional[str] = Field(default=None, description='执行引擎代码')
    task_status: Optional[str] = Field(default=None, description='任务状态')
    notify_config: Optional[Dict[str, Any]] = Field(default=None, description='通知配置')
    extra_config: Optional[Dict[str, Any]] = Field(default=None, description='额外配置')


class TestTaskExecuteRequest(BaseModel):
    """执行测试任务请求"""
    task_id: int = Field(..., description='任务ID')
    trigger_type: str = Field(default='manual', description='触发类型：manual-手动, scheduled-定时, api-接口')
    context_vars: Optional[Dict[str, Any]] = Field(default=None, description='上下文变量')


class TestTaskExecutionQuery(BaseModel):
    """任务执行记录查询参数"""
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    task_id: Optional[int] = Field(default=None, description='任务ID')
    status: Optional[str] = Field(default=None, description='执行状态')
    trigger_type: Optional[str] = Field(default=None, description='触发类型')
