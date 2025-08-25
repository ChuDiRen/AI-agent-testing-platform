# Copyright (c) 2025 左岚. All rights reserved.
"""
部门DTO
定义部门相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class DepartmentIdRequest(BaseModel):
    """
    部门ID请求DTO
    """
    dept_id: int = Field(..., description="部门ID")

    class Config:
        json_schema_extra = {
            "example": {
                "dept_id": 1
            }
        }


class DepartmentListRequest(BaseModel):
    """
    部门列表请求DTO
    """
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    dept_name: Optional[str] = Field(None, description="部门名称筛选")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "dept_name": "开发部"
            }
        }


class DepartmentDeleteRequest(BaseModel):
    """
    删除部门请求DTO
    """
    dept_id: int = Field(..., description="部门ID")

    class Config:
        json_schema_extra = {
            "example": {
                "dept_id": 1
            }
        }


class DepartmentCreateRequest(BaseModel):
    """
    创建部门请求DTO
    """
    parent_id: int = Field(..., description="上级部门ID，0表示顶级部门")
    dept_name: str = Field(..., min_length=1, max_length=100, description="部门名称")
    order_num: Optional[float] = Field(None, description="排序号")

    class Config:
        json_schema_extra = {
            "example": {
                "parent_id": 0,
                "dept_name": "开发部",
                "order_num": 1
            }
        }


class DepartmentUpdateRequest(BaseModel):
    """
    更新部门请求DTO
    """
    dept_id: int = Field(..., description="部门ID")
    dept_name: Optional[str] = Field(None, min_length=1, max_length=100, description="部门名称")
    order_num: Optional[float] = Field(None, description="排序号")

    class Config:
        json_schema_extra = {
            "example": {
                "dept_id": 1,
                "dept_name": "技术开发部",
                "order_num": 1
            }
        }


class DepartmentResponse(BaseModel):
    """
    部门响应DTO
    """
    dept_id: int = Field(..., description="部门ID")
    parent_id: int = Field(..., description="上级部门ID")
    dept_name: str = Field(..., description="部门名称")
    order_num: Optional[float] = Field(None, description="排序号")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "dept_id": 1,
                "parent_id": 0,
                "dept_name": "开发部",
                "order_num": 1,
                "create_time": "2025-01-01T00:00:00",
                "modify_time": "2025-01-01T00:00:00"
            }
        }


class DepartmentTreeNode(BaseModel):
    """
    部门树节点DTO
    """
    dept_id: int = Field(..., description="部门ID")
    parent_id: int = Field(..., description="上级部门ID")
    dept_name: str = Field(..., description="部门名称")
    order_num: Optional[float] = Field(None, description="排序号")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")
    children: List['DepartmentTreeNode'] = Field(default=[], description="子部门列表")

    class Config:
        from_attributes = True


class DepartmentTreeResponse(BaseModel):
    """
    部门树响应DTO
    """
    tree: List[DepartmentTreeNode] = Field(..., description="部门树")

    class Config:
        json_schema_extra = {
            "example": {
                "tree": [
                    {
                        "dept_id": 1,
                        "parent_id": 0,
                        "dept_name": "开发部",
                        "order_num": 1,
                        "create_time": "2025-01-01T00:00:00",
                        "modify_time": "2025-01-01T00:00:00",
                        "children": [
                            {
                                "dept_id": 2,
                                "parent_id": 1,
                                "dept_name": "前端组",
                                "order_num": 1,
                                "create_time": "2025-01-01T00:00:00",
                                "modify_time": "2025-01-01T00:00:00",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }


class DepartmentListResponse(BaseModel):
    """
    部门列表响应DTO
    """
    departments: List[DepartmentResponse] = Field(..., description="部门列表")

    class Config:
        json_schema_extra = {
            "example": {
                "departments": [
                    {
                        "dept_id": 1,
                        "parent_id": 0,
                        "dept_name": "开发部",
                        "order_num": 1,
                        "create_time": "2025-01-01T00:00:00",
                        "modify_time": "2025-01-01T00:00:00"
                    }
                ]
            }
        }


class DepartmentStatusResponse(BaseModel):
    """
    部门状态响应DTO
    """
    dept_id: int = Field(..., description="部门ID")
    dept_name: str = Field(..., description="部门名称")
    has_children: bool = Field(..., description="是否有子部门")
    has_users: bool = Field(..., description="是否有用户")
    can_delete: bool = Field(..., description="是否可以删除")

    class Config:
        json_schema_extra = {
            "example": {
                "dept_id": 1,
                "dept_name": "开发部",
                "has_children": True,
                "has_users": False,
                "can_delete": False
            }
        }


# 更新前向引用
DepartmentTreeNode.model_rebuild()
