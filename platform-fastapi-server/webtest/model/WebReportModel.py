from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field


class WebReportStatus(str, Enum):
    """Web报告状态枚举"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class WebReportFormat(str, Enum):
    """Web报告格式枚举"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    ALLURE = "allure"


class WebReport(SQLModel, table=True):
    """Web测试报告表"""
    __tablename__ = "t_web_report"
    
    id: Optional[str] = Field(default=None, primary_key=True, description='报告ID')
    execution_id: str = Field(description='执行ID')
    project_id: int = Field(description='项目ID')
    project_name: str = Field(max_length=200, description='项目名称')
    report_name: str = Field(max_length=200, description='报告名称')
    status: WebReportStatus = Field(description='报告状态')
    format: WebReportFormat = Field(description='报告格式')
    file_path: Optional[str] = Field(default=None, description='报告文件路径')
    file_size: Optional[int] = Field(default=None, description='文件大小(字节)')
    download_url: Optional[str] = Field(default=None, description='下载链接')
    view_url: Optional[str] = Field(default=None, description='查看链接')
    allure_url: Optional[str] = Field(default=None, description='Allure报告链接')
    summary_data: Optional[str] = Field(default=None, description='摘要数据JSON')
    detail_data: Optional[str] = Field(default=None, description='详细数据JSON')
    chart_data: Optional[str] = Field(default=None, description='图表数据JSON')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    generate_time: datetime = Field(default_factory=datetime.now, description='生成时间')
    expire_time: Optional[datetime] = Field(default=None, description='过期时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    
    class Config:
        """模型配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "report_20260106_001",
                "execution_id": "exec_20260106_001",
                "project_id": 1,
                "project_name": "商城系统 Web 测试",
                "report_name": "商城系统 Web 测试报告",
                "status": "completed",
                "format": "html",
                "file_path": "/reports/web/report_20260106_001.html",
                "allure_url": "/allure-report/exec_20260106_001/index.html"
            }
        }


class WebReportTemplate(SQLModel, table=True):
    """Web报告模板表"""
    __tablename__ = "t_web_report_template"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='模板ID')
    name: str = Field(max_length=200, description='模板名称')
    description: Optional[str] = Field(default=None, max_length=500, description='模板描述')
    template_type: WebReportFormat = Field(description='模板类型')
    template_content: str = Field(description='模板内容')
    css_styles: Optional[str] = Field(default=None, description='CSS样式')
    js_scripts: Optional[str] = Field(default=None, description='JavaScript脚本')
    is_default: bool = Field(default=False, description='是否默认模板')
    is_active: bool = Field(default=True, description='是否启用')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    
    class Config:
        """模型配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "标准HTML报告模板",
                "description": "包含统计图表和详细用例信息的标准报告模板",
                "template_type": "html",
                "is_default": True
            }
        }
