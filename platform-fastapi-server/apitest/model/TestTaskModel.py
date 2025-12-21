from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class TestTask(SQLModel, table=True):
    """测试任务表"""
    __tablename__ = "t_test_task"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='任务ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    task_name: str = Field(max_length=255, description='任务名称')
    task_desc: Optional[str] = Field(default=None, description='任务描述')
    task_type: str = Field(default='manual', max_length=20, description='任务类型：manual-手动, scheduled-定时')
    cron_expression: Optional[str] = Field(default=None, max_length=100, description='Cron表达式(定时任务)')
    plan_id: Optional[int] = Field(default=None, description='关联测试计划ID')
    case_ids: Optional[str] = Field(default=None, description='关联用例ID列表JSON')
    executor_code: str = Field(default='api_engine', max_length=50, description='执行引擎代码')
    task_status: str = Field(default='pending', max_length=20, description='任务状态：pending-待执行, running-执行中, completed-已完成, failed-失败, disabled-已禁用')
    last_run_time: Optional[datetime] = Field(default=None, description='上次执行时间')
    next_run_time: Optional[datetime] = Field(default=None, description='下次执行时间')
    run_count: int = Field(default=0, description='执行次数')
    success_count: int = Field(default=0, description='成功次数')
    fail_count: int = Field(default=0, description='失败次数')
    notify_config: Optional[str] = Field(default=None, description='通知配置JSON')
    extra_config: Optional[str] = Field(default=None, description='额外配置JSON')
    create_by: Optional[str] = Field(default=None, max_length=64, description='创建人')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')


class TestTaskExecution(SQLModel, table=True):
    """测试任务执行记录表"""
    __tablename__ = "t_test_task_execution"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='执行记录ID')
    task_id: int = Field(description='任务ID')
    execution_uuid: str = Field(max_length=64, description='执行批次UUID')
    trigger_type: str = Field(default='manual', max_length=20, description='触发类型：manual-手动, scheduled-定时, api-接口')
    status: str = Field(default='running', max_length=20, description='执行状态：running-执行中, completed-已完成, failed-失败, cancelled-已取消')
    total_cases: int = Field(default=0, description='总用例数')
    passed_cases: int = Field(default=0, description='通过用例数')
    failed_cases: int = Field(default=0, description='失败用例数')
    skipped_cases: int = Field(default=0, description='跳过用例数')
    start_time: Optional[datetime] = Field(default_factory=datetime.now, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    duration: Optional[int] = Field(default=None, description='执行耗时(秒)')
    report_path: Optional[str] = Field(default=None, max_length=500, description='报告路径')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
