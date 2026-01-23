"""Schema 模块"""

# 导入 RBAC 相关 Schema
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleDetailResponse,
    RoleAssignMenus,
    RoleAssignApis,
)
from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuResponse,
)
from app.schemas.api_resource import (
    ApiResourceCreate,
    ApiResourceUpdate,
    ApiResourceResponse,
    ApiRefreshRequest,
)
from app.schemas.dept import (
    DeptCreate,
    DeptUpdate,
    DeptResponse,
)
from app.schemas.audit_log import (
    AuditLogResponse,
)
from app.schemas.user_ext import (
    UserCreateExt,
    UserUpdateExt,
    UserResponseExt,
    UserChangePassword,
    UserResetPassword,
    UserAssignRoles,
)
from app.schemas.permission import (
    UserInfoResponse,
    MenuNode,
    UserMenusResponse,
    UserApisResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
)

# 导入原有的 Schema
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
)
from app.schemas.api_project import ApiProjectCreate, ApiProjectUpdate, ApiProjectResponse
from app.schemas.api_info import ApiInfoCreate, ApiInfoUpdate, ApiInfoResponse
from app.schemas.api_meta import ApiMetaCreate, ApiMetaUpdate, ApiMetaResponse
from app.schemas.api_info_case import (
    ApiInfoCaseCreate,
    ApiInfoCaseUpdate,
    ApiInfoCaseResponse,
)
from app.schemas.api_info_case_step import (
    ApiInfoCaseStepCreate,
    ApiInfoCaseStepUpdate,
    ApiInfoCaseStepResponse,
)
from app.schemas.api_collection_info import (
    ApiCollectionInfoCreate,
    ApiCollectionInfoUpdate,
    ApiCollectionInfoResponse,
)
from app.schemas.api_history import ApiHistoryCreate, ApiHistoryUpdate, ApiHistoryResponse
from app.schemas.api_db_base import ApiDbBaseCreate, ApiDbBaseUpdate, ApiDbBaseResponse
from app.schemas.api_keyword import ApiKeyWordCreate, ApiKeyWordUpdate, ApiKeyWordResponse
from app.schemas.api_operation_type import (
    ApiOperationTypeCreate,
    ApiOperationTypeUpdate,
    ApiOperationTypeResponse,
)
from app.schemas.robot_config import RobotConfigCreate, RobotConfigUpdate, RobotConfigResponse


__all__ = [
    # RBAC 相关
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleDetailResponse",
    "RoleAssignMenus",
    "RoleAssignApis",
    "MenuCreate",
    "MenuUpdate",
    "MenuResponse",
    "ApiResourceCreate",
    "ApiResourceUpdate",
    "ApiResourceResponse",
    "ApiRefreshRequest",
    "DeptCreate",
    "DeptUpdate",
    "DeptResponse",
    "AuditLogResponse",
    "UserCreateExt",
    "UserUpdateExt",
    "UserResponseExt",
    "UserChangePassword",
    "UserResetPassword",
    "UserAssignRoles",
    "UserInfoResponse",
    "MenuNode",
    "UserMenusResponse",
    "UserApisResponse",
    "PermissionCheckRequest",
    "PermissionCheckResponse",
    # 原有 Schema
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "ApiProjectCreate",
    "ApiProjectUpdate",
    "ApiProjectResponse",
    "ApiInfoCreate",
    "ApiInfoUpdate",
    "ApiInfoResponse",
    "ApiMetaCreate",
    "ApiMetaUpdate",
    "ApiMetaResponse",
    "ApiInfoCaseCreate",
    "ApiInfoCaseUpdate",
    "ApiInfoCaseResponse",
    "ApiInfoCaseStepCreate",
    "ApiInfoCaseStepUpdate",
    "ApiInfoCaseStepResponse",
    "ApiCollectionInfoCreate",
    "ApiCollectionInfoUpdate",
    "ApiCollectionInfoResponse",
    "ApiHistoryCreate",
    "ApiHistoryUpdate",
    "ApiHistoryResponse",
    "ApiDbBaseCreate",
    "ApiDbBaseUpdate",
    "ApiDbBaseResponse",
    "ApiKeyWordCreate",
    "ApiKeyWordUpdate",
    "ApiKeyWordResponse",
    "ApiOperationTypeCreate",
    "ApiOperationTypeUpdate",
    "ApiOperationTypeResponse",
    "RobotConfigCreate",
    "RobotConfigUpdate",
    "RobotConfigResponse",
]
