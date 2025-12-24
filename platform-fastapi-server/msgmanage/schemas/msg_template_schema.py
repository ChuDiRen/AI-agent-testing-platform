"""
消息模板 Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TemplateVariable(BaseModel):
    """模板变量定义"""
    name: str = Field(..., description="变量名")
    desc: str = Field(..., description="变量描述")
    default_value: Optional[str] = Field(None, description="默认值")


class MsgTemplateInsert(BaseModel):
    """新增消息模板"""
    template_code: str = Field(..., description="模板编码（唯一标识）")
    template_name: str = Field(..., description="模板名称")
    template_type: str = Field(..., description="模板类型：verify-验证码, notify-通知, marketing-营销")
    channel_type: str = Field(..., description="渠道类型：system-站内消息, email-邮件, sms-短信")
    title: Optional[str] = Field("", description="消息标题")
    content: str = Field(..., description="模板内容")
    variables: List[TemplateVariable] = Field(default_factory=list, description="变量列表")
    example_params: Dict[str, Any] = Field(default_factory=dict, description="示例参数")
    status: int = Field(1, description="状态：0-禁用, 1-启用")
    remark: Optional[str] = Field("", description="备注")


class MsgTemplateUpdate(BaseModel):
    """更新消息模板"""
    id: int = Field(..., description="模板ID")
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    channel_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    example_params: Optional[Dict[str, Any]] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class MsgTemplateQuery(BaseModel):
    """查询消息模板"""
    template_code: Optional[str] = None
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    channel_type: Optional[str] = None
    status: Optional[int] = None
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")


class MsgTemplateResponse(BaseModel):
    """消息模板响应"""
    id: int
    template_code: str
    template_name: str
    template_type: str
    channel_type: str
    title: Optional[str] = ""
    content: str
    variables: List[TemplateVariable] = []
    example_params: Dict[str, Any] = {}
    status: int
    remark: Optional[str] = ""
    created_by: Optional[str] = ""
    created_time: datetime
    updated_time: Optional[datetime] = None


class TemplatePreviewRequest(BaseModel):
    """模板预览请求"""
    template_code: str = Field(..., description="模板编码")
    params: Dict[str, Any] = Field(..., description="替换参数")


class TemplatePreviewResponse(BaseModel):
    """模板预览响应"""
    title: str = Field(..., description="替换后的标题")
    content: str = Field(..., description="替换后的内容")
