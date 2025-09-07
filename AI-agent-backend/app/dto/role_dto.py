# Copyright (c) 2025 左岚. All rights reserved.
"""
角色DTO
定义角色相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class RoleIdRequest(BaseModel):
    """
    角色ID请求DTO
    """
    role_id: int = Field(..., description="角色ID")

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 1
            }
        }


class RoleBatchDeleteRequest(BaseModel):
    """
    批量删除角色请求DTO
    """
    role_ids: List[int] = Field(..., min_items=1, description="角色ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "role_ids": [1, 2, 3]
            }
        }


class RoleListRequest(BaseModel):
    """
    角色列表请求DTO
    """
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    keyword: Optional[str] = Field(None, description="关键词搜索")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "keyword": "管理员"
            }
        }


class RoleCreateRequest(BaseModel):
    """
    创建角色请求DTO
    """
    role_name: str = Field(..., min_length=1, max_length=10, description="角色名称")
    remark: Optional[str] = Field(None, max_length=100, description="角色描述")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "管理员",
                "remark": "系统管理员角色"
            }
        }


class RoleUpdateRequest(BaseModel):
    """
    更新角色请求DTO
    """
    role_id: int = Field(..., description="角色ID")
    role_name: Optional[str] = Field(None, min_length=1, max_length=10, description="角色名称")
    remark: Optional[str] = Field(None, max_length=100, description="角色描述")

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 1,
                "role_name": "管理员",
                "remark": "系统管理员角色"
            }
        }


class RoleDeleteRequest(BaseModel):
    """
    删除角色请求DTO
    """
    role_id: int = Field(..., description="角色ID")

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 1
            }
        }


class RoleCopyRequest(BaseModel):
    """
    复制角色请求DTO
    """
    role_name: str = Field(..., min_length=1, max_length=10, description="新角色名称")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "新角色名称"
            }
        }


class RoleMenuAssignRequest(BaseModel):
    """
    角色菜单分配请求DTO
    """
    role_id: int = Field(..., description="角色ID")
    menu_ids: List[int] = Field(..., description="菜单ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 1,
                "menu_ids": [1, 2, 3, 4, 5]
            }
        }


class RoleUpdateRequestOld(BaseModel):
    """
    更新角色请求DTO（旧版本）
    """
    role_name: Optional[str] = Field(None, min_length=1, max_length=10, description="角色名称")
    remark: Optional[str] = Field(None, max_length=100, description="角色描述")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "超级管理员",
                "remark": "拥有所有权限的管理员"
            }
        }


class RoleResponse(BaseModel):
    """
    角色响应DTO
    """
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    remark: Optional[str] = Field(None, description="角色描述")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "role_id": 1,
                "role_name": "管理员",
                "remark": "系统管理员角色",
                "create_time": "2025-01-01T00:00:00",
                "modify_time": "2025-01-01T00:00:00"
            }
        }


class RoleListResponse(BaseModel):
    """
    角色列表响应DTO
    """
    roles: List[RoleResponse] = Field(..., description="角色列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "roles": [
                    {
                        "role_id": 1,
                        "role_name": "管理员",
                        "remark": "系统管理员角色",
                        "create_time": "2025-01-01T00:00:00",
                        "modify_time": "2025-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10,
                "pages": 1
            }
        }




class RolePermissionResponse(BaseModel):
    """
    角色权限响应DTO
    """
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    permissions: List[str] = Field(..., description="权限标识列表")
    menu_ids: List[int] = Field(..., description="菜单ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 1,
                "role_name": "管理员",
                "permissions": ["user:view", "user:add", "user:update", "user:delete"],
                "menu_ids": [1, 2, 3, 4, 5]
            }
        }
