"""数据模型模块"""
from app.db.base import Base

# 导入所有模型，确保它们被注册到 Base.metadata
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.api_resource import ApiResource
from app.models.dept import Dept
from app.models.dept_closure import DeptClosure
from app.models.audit_log import AuditLog
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu
from app.models.role_api import RoleApi

# 导入原有的API测试相关模型
from app.models.api_project import ApiProject
from app.models.api_info import ApiInfo
from app.models.api_meta import ApiMeta
from app.models.api_info_case import ApiInfoCase
from app.models.api_info_case_step import ApiInfoCaseStep
from app.models.api_collection_info import ApiCollectionInfo
from app.models.api_collection_detail import ApiCollectionDetail
from app.models.api_history import ApiHistory
from app.models.api_db_base import ApiDbBase
from app.models.api_keyword import ApiKeyWord
from app.models.api_operation_type import ApiOperationType
from app.models.robot_config import RobotConfig
from app.models.robot_msg_config import RobotMsgConfig
from app.models.api_test_plan_chart import ApiTestPlanChart


__all__ = [
    "Base",
    # RBAC相关模型
    "User",
    "Role",
    "Menu",
    "ApiResource",
    "Dept",
    "DeptClosure",
    "AuditLog",
    "UserRole",
    "RoleMenu",
    "RoleApi",
    # API测试相关模型
    "ApiProject",
    "ApiInfo",
    "ApiMeta",
    "ApiInfoCase",
    "ApiInfoCaseStep",
    "ApiCollectionInfo",
    "ApiCollectionDetail",
    "ApiHistory",
    "ApiDbBase",
    "ApiKeyWord",
    "ApiOperationType",
    "RobotConfig",
    "RobotMsgConfig",
    "ApiTestPlanChart",
]
