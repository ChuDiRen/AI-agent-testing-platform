"""
接口目录Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class ApiFolderQuery(BaseModel):
    """目录查询参数"""
    project_id: int
    parent_id: Optional[int] = None


class ApiFolderCreate(BaseModel):
    """创建目录"""
    project_id: int
    parent_id: int = 0
    folder_name: str
    folder_desc: Optional[str] = None
    folder_icon: Optional[str] = None
    sort_order: int = 0


class ApiFolderUpdate(BaseModel):
    """更新目录"""
    id: int
    folder_name: Optional[str] = None
    folder_desc: Optional[str] = None
    folder_icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_expanded: Optional[int] = None


class ApiFolderMove(BaseModel):
    """移动目录"""
    id: int
    target_parent_id: int
    target_sort_order: int = 0


class ApiFolderTreeNode(BaseModel):
    """目录树节点"""
    id: int
    project_id: int
    parent_id: int
    folder_name: str
    folder_desc: Optional[str] = None
    folder_icon: Optional[str] = None
    sort_order: int
    is_expanded: int
    node_type: str = "folder"  # folder 或 api
    children: List[Any] = []
    api_count: int = 0


class ApiMoveToFolder(BaseModel):
    """移动接口到目录"""
    api_ids: List[int]
    folder_id: int


class ApiFolderBatchSort(BaseModel):
    """批量排序"""
    items: List[dict]  # [{"id": 1, "sort_order": 0}, ...]
