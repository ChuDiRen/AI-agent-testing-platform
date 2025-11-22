"""
Swagger导入相关的Schema定义
支持OpenAPI 2.0和3.0规范
"""
from typing import Optional, Dict, Any

from pydantic import BaseModel


class SwaggerImportRequest(BaseModel):
    """Swagger导入请求"""
    project_id: int  # 项目ID
    swagger_url: Optional[str] = None  # Swagger JSON URL
    swagger_json: Optional[Dict[str, Any]] = None  # Swagger JSON内容
    override_existing: bool = False  # 是否覆盖已存在的接口
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "swagger_url": "https://petstore.swagger.io/v2/swagger.json",
                "override_existing": False
            }
        }


class SwaggerImportResponse(BaseModel):
    """Swagger导入响应"""
    total_apis: int  # 总接口数
    imported_apis: int  # 成功导入数
    skipped_apis: int  # 跳过数
    failed_apis: int  # 失败数
    details: list[str] = []  # 详细信息
