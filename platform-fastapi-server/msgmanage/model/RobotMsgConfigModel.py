"""
机器人消息模板配置数据模型
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class RobotMsgConfig(SQLModel, table=True):
    """机器人消息模板配置表"""
    __tablename__ = "t_robot_msg_config"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='模板ID')
    robot_id: int = Field(foreign_key="t_robot_config.id", description='关联的机器人ID')
    msg_type: str = Field(max_length=50, description='消息类型: text/markdown/card')
    template_name: str = Field(max_length=255, description='模板名称')
    template_content: str = Field(description='模板内容（支持变量替换）')
    variables: Optional[str] = Field(default=None, description='模板变量说明（JSON格式）')
    is_enabled: bool = Field(default=True, description='是否启用')
    description: Optional[str] = Field(default=None, max_length=500, description='描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_id": 1,
                "msg_type": "markdown",
                "template_name": "测试完成通知",
                "template_content": "## 测试执行完成\n- 项目: {{project_name}}\n- 结果: {{result}}\n- 耗时: {{duration}}",
                "variables": '{"project_name": "项目名称", "result": "通过/失败", "duration": "执行时长"}',
                "is_enabled": True
            }
        }
