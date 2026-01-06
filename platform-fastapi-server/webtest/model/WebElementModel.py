from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class WebElement(SQLModel, table=True):
    """Web元素表"""
    __tablename__ = "t_web_element"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='元素ID')
    name: str = Field(max_length=100, description='元素名称')
    description: Optional[str] = Field(default=None, max_length=500, description='元素描述')
    project_id: int = Field(description='项目ID')
    module: Optional[str] = Field(default=None, max_length=100, description='所属模块')
    locator_type: str = Field(max_length=20, description='定位器类型：id/name/class/xpath/css/link_text/partial_link_text/tag_name')
    locator_value: str = Field(max_length=500, description='定位器值')
    page_url: Optional[str] = Field(default=None, max_length=500, description='页面URL')
    frame_info: Optional[str] = Field(default=None, max_length=200, description='框架信息')
    wait_strategy: str = Field(default='implicit', max_length=20, description='等待策略：implicit/explicit/fluent')
    wait_timeout: int = Field(default=10, description='等待超时(秒)')
    is_dynamic: bool = Field(default=False, description='是否动态元素')
    backup_locator: Optional[str] = Field(default=None, max_length=500, description='备用定位器')
    status: str = Field(default='active', max_length=20, description='状态：active/inactive')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_by: Optional[int] = Field(default=None, description='更新人ID')
