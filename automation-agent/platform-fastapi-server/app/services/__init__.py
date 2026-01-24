"""
业务服务模块
"""

# 导入通用 CRUD 基类
from app.services.base import CRUDBase

# 导入 RBAC 相关服务
from app.services.user import user
from app.services.role import role
from app.services.menu import menu
from app.services.api_resource import api_resource
from app.services.dept import dept
from app.services.audit_log import audit_log
from app.services.permission import permission

# 导入原有的 API 测试相关服务
from app.services.api_project import api_project_crud as api_project
from app.services.api_meta import api_meta_crud as api_meta
from app.services.api_info_case import api_info_case_crud as api_info_case
from app.services.api_collection_info import api_collection_info_crud as api_collection_info
from app.services.api_history import api_history_crud as api_history
from app.services.api_db_base import api_db_base_crud as api_db_base
from app.services.api_keyword import api_keyword_crud as api_keyword
from app.services.api_operation_type import api_operation_type_crud as api_operation_type
from app.services.robot_config import robot_config_crud as robot_config
from app.services.login_service import login_service
from app.services.minio_service import file_upload_service as minio_service
from app.services.rabbitmq_consumer import rabbitmq_manager as rabbitmq_consumer
from app.services.test_execution_service import test_execution_service


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
    "api_meta",
    "api_info_case",
    "api_collection_info",
    "api_history",
    "api_db_base",
    "api_keyword",
    "api_operation_type",
    "robot_config",
    # 其他服务
    "login_service",
    "minio_service",
    "rabbitmq_consumer",
    "test_execution_service",
]
