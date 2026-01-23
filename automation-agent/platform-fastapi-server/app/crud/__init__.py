"""CRUD 操作模块"""

# 导入通用 CRUD 基类
from app.crud.base import CRUDBase

# 导入 RBAC 相关 CRUD
from app.crud.user import user
from app.crud.role import role
from app.crud.menu import menu
from app.crud.api_resource import api_resource
from app.crud.dept import dept
from app.crud.audit_log import audit_log
from app.crud.permission import permission

# 导入原有的 API 测试相关 CRUD
from app.crud.api_project import api_project_crud as api_project
# from app.crud.api_info import api_info_crud as api_info  # 文件不存在
from app.crud.api_meta import api_meta_crud as api_meta
from app.crud.api_info_case import api_info_case_crud as api_info_case
from app.crud.api_collection_info import api_collection_info_crud as api_collection_info
from app.crud.api_history import api_history_crud as api_history
from app.crud.api_db_base import api_db_base_crud as api_db_base
from app.crud.api_keyword import api_keyword_crud as api_keyword
from app.crud.api_operation_type import api_operation_type_crud as api_operation_type
from app.crud.robot_config import robot_config_crud as robot_config


__all__ = [
    "CRUDBase",
    # RBAC 相关
    "user",
    "role",
    "menu",
    "api_resource",
    "dept",
    "audit_log",
    "permission",
    # API 测试相关
    "api_project",
    # "api_info",  # 文件不存在
    "api_meta",
    "api_info_case",
    "api_collection_info",
    "api_history",
    "api_db_base",
    "api_keyword",
    "api_operation_type",
    "robot_config",
]
