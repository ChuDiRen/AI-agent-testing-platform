from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from ..model.WebReportModel import WebReportStatus, WebReportFormat


class WebReportQuery(BaseModel):
    """Web报告查询参数"""
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    execution_id: Optional[str] = Field(default=None, description='执行ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    status: Optional[str] = Field(default=None, description='报告状态')
    format: Optional[str] = Field(default=None, description='报告格式')
    start_date: Optional[datetime] = Field(default=None, description='开始日期')
    end_date: Optional[datetime] = Field(default=None, description='结束日期')
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in WebReportStatus]:
            raise ValueError('报告状态无效')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        if v is not None and v not in [fmt.value for fmt in WebReportFormat]:
            raise ValueError('报告格式无效')
        return v
    
    class Config:
        """Schema配置"""
        json_schema_extra = {
            "example": {
                "page": 1,
                "pageSize": 10,
                "project_id": 1,
                "status": "completed",
                "format": "html"
            }
        }


class WebReportCreate(BaseModel):
    """创建Web报告"""
    execution_id: str = Field(..., description='执行ID')
    project_id: int = Field(..., description='项目ID')
    project_name: str = Field(..., max_length=200, description='项目名称')
    report_name: str = Field(..., max_length=200, description='报告名称')
    format: WebReportFormat = Field(..., description='报告格式')
    summary_data: Optional[Dict[str, Any]] = Field(default=None, description='摘要数据')
    detail_data: Optional[Dict[str, Any]] = Field(default=None, description='详细数据')
    chart_data: Optional[Dict[str, Any]] = Field(default=None, description='图表数据')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    
    class Config:
        """Schema配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "execution_id": "exec_20260106_001",
                "project_id": 1,
                "project_name": "商城系统 Web 测试",
                "report_name": "商城系统 Web 测试报告",
                "format": "html",
                "summary_data": {
                    "total": 15,
                    "passed": 13,
                    "failed": 2,
                    "pass_rate": 86.7
                }
            }
        }


class WebReportUpdate(BaseModel):
    """更新Web报告"""
    id: str = Field(..., description='报告ID')
    status: Optional[WebReportStatus] = Field(default=None, description='报告状态')
    file_path: Optional[str] = Field(default=None, description='报告文件路径')
    file_size: Optional[int] = Field(default=None, description='文件大小')
    download_url: Optional[str] = Field(default=None, description='下载链接')
    view_url: Optional[str] = Field(default=None, description='查看链接')
    allure_url: Optional[str] = Field(default=None, description='Allure报告链接')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    expire_time: Optional[datetime] = Field(default=None, description='过期时间')
    
    class Config:
        """Schema配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "report_20260106_001",
                "status": "completed",
                "file_path": "/reports/web/report_20260106_001.html",
                "allure_url": "/allure-report/exec_20260106_001/index.html"
            }
        }


class WebReportResponse(BaseModel):
    """Web报告响应数据"""
    id: str
    execution_id: str
    project_id: int
    project_name: str
    report_name: str
    status: str
    format: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    view_url: Optional[str] = None
    allure_url: Optional[str] = None
    summary_data: Optional[Dict[str, Any]] = None
    detail_data: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    generate_time: datetime
    expire_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_time: datetime
    
    class Config:
        from_attributes = True


class WebReportTemplateResponse(BaseModel):
    """Web报告模板响应"""
    id: int
    name: str
    description: Optional[str] = None
    template_type: str
    template_content: str
    css_styles: Optional[str] = None
    js_scripts: Optional[str] = None
    is_default: bool
    is_active: bool
    create_time: datetime
    update_time: datetime
    create_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class WebReportGenerateRequest(BaseModel):
    """生成报告请求"""
    execution_id: str = Field(..., description='执行ID')
    format: WebReportFormat = Field(..., description='报告格式')
    template_id: Optional[int] = Field(default=None, description='模板ID')
    custom_name: Optional[str] = Field(default=None, max_length=200, description='自定义报告名称')
    include_screenshots: bool = Field(default=True, description='是否包含截图')
    include_steps: bool = Field(default=True, description='是否包含步骤详情')
    
    class Config:
        """Schema配置"""
        use_enum_values = True


class WebReportDownloadRequest(BaseModel):
    """下载报告请求"""
    report_id: str = Field(..., description='报告ID')
    format: Optional[WebReportFormat] = Field(default=None, description='下载格式')
    include_attachments: bool = Field(default=False, description='是否包含附件')
    
    class Config:
        """Schema配置"""
        use_enum_values = True


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[str] = Field(..., description='报告ID列表')


class WebReportStatistics(BaseModel):
    """报告统计信息"""
    total_reports: int = Field(description='总报告数')
    completed_reports: int = Field(description='已完成报告数')
    generating_reports: int = Field(description='生成中报告数')
    failed_reports: int = Field(description='失败报告数')
    format_stats: Dict[str, int] = Field(description='格式统计')
    avg_file_size: float = Field(description='平均文件大小(KB)')
    latest_report: Optional[WebReportResponse] = Field(default=None, description='最新报告')
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reports": 25,
                "completed_reports": 20,
                "generating_reports": 3,
                "failed_reports": 2,
                "format_stats": {
                    "html": 15,
                    "pdf": 8,
                    "allure": 2
                },
                "avg_file_size": 1024.5
            }
        }
