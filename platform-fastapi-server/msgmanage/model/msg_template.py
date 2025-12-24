"""
消息模板 Model
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from datetime import datetime
import json


class MsgTemplate(SQLModel, table=True):
    """消息模板表"""
    __tablename__ = "msg_template"

    id: Optional[int] = Field(default=None, primary_key=True, description="主键ID")
    template_code: str = Field(max_length=50, unique=True, index=True, description="模板编码（唯一标识）")
    template_name: str = Field(max_length=100, description="模板名称")
    template_type: str = Field(max_length=20, description="模板类型：verify-验证码, notify-通知, marketing-营销")
    channel_type: str = Field(max_length=20, description="渠道类型：system-站内消息, email-邮件, sms-短信")
    title: Optional[str] = Field(default="", max_length=200, description="消息标题（站内消息/邮件使用）")
    content: str = Field(description="模板内容，支持{{variable}}变量")
    variables: Optional[str] = Field(default="[]", description="变量列表JSON，例：[{\"name\":\"code\",\"desc\":\"验证码\"}]")
    example_params: Optional[str] = Field(default="{}", description="示例参数JSON，用于预览")
    status: int = Field(default=1, description="状态：0-禁用, 1-启用")
    remark: Optional[str] = Field(default="", max_length=500, description="备注说明")
    created_by: Optional[str] = Field(default="", max_length=50, description="创建人")
    created_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_time: Optional[datetime] = Field(default=None, description="更新时间")

    class Config:
        from_attributes = True


class MsgTemplateQuery(SQLModel):
    """消息模板查询条件"""
    template_code: Optional[str] = None
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    channel_type: Optional[str] = None
    status: Optional[int] = None
