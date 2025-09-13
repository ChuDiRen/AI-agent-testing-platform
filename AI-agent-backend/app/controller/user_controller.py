# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC用户Controller
处理用户相关的HTTP请求
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.core.logger import get_logger
from app.core.security import create_access_token, create_token_pair, refresh_access_token, verify_token, create_refresh_token
from app.db.session import get_db
from app.dto.base import ApiResponse, Success, Fail, SuccessExtra
from app.dto.user_dto import (
    UserCreateRequest,
    UserUpdateRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    UserResponse,
    UserListResponse,
    UserRoleAssignRequest,
    UserRoleResponse,
    LoginRequest,
    LoginResponse,
    UserIdRequest,
    UserListRequest,
    UserDeleteRequest,
    UserExportRequest,
    UserImportResponse
)
from app.entity.user import User
from app.middleware.auth import get_current_user
from app.service.user_service import RBACUserService
from app.service.department_service import DepartmentService  # 引入部门服务  # 注释
from app.utils.log_decorators import log_operation, log_user_action
from app.core.token_blacklist import add_to_blacklist, is_blacklisted
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/create-user", response_model=ApiResponse[UserResponse], summary="创建用户")
@log_operation(
    operation_type="CREATE",
    resource_type="USER",
    operation_desc="创建用户",
    include_request=True
)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新用户
    
    - **username**: 用户名（必填，3-50个字符）
    - **password**: 密码（必填，6-20个字符）
    - **email**: 邮箱（可选）
    - **mobile**: 手机号（可选）
    - **dept_id**: 部门ID（可选）
    - **ssex**: 性别，'0'男 '1'女 '2'保密（可选）
    - **avatar**: 头像（可选）
    - **description**: 描述（可选）
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.create_user(
            username=request.username,
            password=request.password,
            email=request.email,
            mobile=request.mobile,
            dept_id=request.dept_id,
            ssex=request.ssex,
            avatar=request.avatar,
            description=request.description
        )
        
        # 转换为字典格式
        user_dict = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "dept_id": user.dept_id,
            "status": user.status,
            "ssex": user.ssex,
            "avatar": user.avatar,
            "description": user.description,
            "create_time": user.create_time.isoformat() if user.create_time else None,
            "modify_time": user.modify_time.isoformat() if user.modify_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
        }

        logger.info(f"User created successfully: {user.username}")
        return Success(code=200, msg="用户创建成功", data=user_dict)
        
    except ValueError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="用户登录")
async def user_login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录认证

    - **username**: 用户名
    - **password**: 密码
    """
    try:
        logger.info(f"Login attempt for user: {request.username}")

        # 步骤1：用户认证
        logger.info("Step 1: User authentication")
        user_service = RBACUserService(db)
        user = user_service.authenticate_user(request.username, request.password)

        if not user:
            logger.warning(f"Authentication failed for user: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        logger.info(f"User authenticated: {user.username}")

        # 步骤2：创建令牌对
        logger.info("Step 2: Creating token pair")
        token_pair = create_token_pair(user_id=user.id)
        logger.info("Token pair created successfully")

        # 步骤3：获取用户权限
        logger.info("Step 3: Getting user permissions")
        permissions = user_service.get_user_permissions(user.id)
        logger.info(f"Retrieved {len(permissions)} permissions")

        # 步骤4：构建用户信息
        logger.info("Step 4: Building user info")
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "dept_id": user.dept_id,
            "status": user.status,
            "ssex": user.ssex,
            "avatar": user.avatar,
            "description": user.description,
            "create_time": user.create_time.isoformat() if user.create_time else None,
            "modify_time": user.modify_time.isoformat() if user.modify_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
        }

        login_data = {
            "access_token": token_pair["access_token"],
            "refresh_token": token_pair.get("refresh_token"),
            "token_type": token_pair.get("token_type", "bearer"),
            "user_info": user_info,
            "permissions": permissions
        }

        logger.info(f"User logged in successfully: {user.username}")
        return Success(code=200, msg="登录成功", data=login_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.post("/refresh-token", summary="刷新访问令牌")
async def refresh_token_endpoint(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    使用refresh_token换取新的access_token。
    请求体：{ "refresh_token": "..." }
    """
    try:
        refresh_token = request.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少refresh_token")

        # 黑名单检查
        if is_blacklisted(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌已失效")

        # 验证并提取用户
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌无效或已过期")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌无效")

        # 作废旧refresh_token
        add_to_blacklist(refresh_token)

        # 颁发新的访问令牌和刷新令牌
        new_access = create_access_token({"sub": user_id_str})  # 使用字符串类型的user_id
        new_refresh = create_refresh_token({"sub": user_id_str})  # 使用字符串类型的user_id

        return Success(code=200, msg="令牌刷新成功", data={
            "access_token": new_access,
            "token_type": "bearer",
            "refresh_token": new_refresh
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="刷新令牌失败")


@router.post("/logout", response_model=ApiResponse[bool], summary="用户退出登录")
async def user_logout(
    body: Optional[dict] = None,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """
    用户退出登录：将access_token与refresh_token（如提供）加入黑名单
    """
    try:
        # 黑名单当前访问令牌
        try:
            if credentials and credentials.credentials:
                add_to_blacklist(credentials.credentials)
        except Exception:
            pass

        # 黑名单刷新令牌
        try:
            refresh_token = (body or {}).get("refresh_token")
            if refresh_token:
                add_to_blacklist(refresh_token)
        except Exception:
            pass

        logger.info("User logged out successfully")
        return Success(code=200, msg="退出登录成功", data=True)

    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="退出登录失败"
        )


@router.post("/get-user-list", response_model=ApiResponse[UserListResponse], summary="获取用户列表")
async def get_user_list(
    request: UserListRequest,
    db: Session = Depends(get_db)
):
    """
    获取用户列表（支持分页和筛选）
    """
    try:
        user_service = RBACUserService(db)

        # 数据库层筛选 + 分页，并预加载部门与角色  # 注释
        paginated_users, total = user_service.query_users(
            page=request.page,
            size=request.size,
            username=request.username,
            dept_id=request.dept_id,
            status=request.status,
            ssex=request.ssex
        )

        # 批量准备部门名称映射，避免重复查询  # 注释
        dept_service = DepartmentService(db)
        dept_ids = {u.dept_id for u in paginated_users if u.dept_id}
        dept_name_map = {}
        if dept_ids:
            for dept in dept_service.get_departments_by_ids(list(dept_ids)):
                dept_name_map[dept.id] = dept.dept_name

        # 批量获取角色映射，避免逐条查询  # 注释
        user_ids = [u.user_id for u in paginated_users]
        roles_map = user_service.get_roles_for_users(user_ids)

        # 转换为响应格式
        user_list = []
        for user in paginated_users:
            # 查询用户角色并转换为精简结构  # 注释
            roles = roles_map.get(user.user_id, [])
            role_data = [
                {"role_id": role.id, "role_name": role.role_name, "remark": role.remark or ""}
                for role in roles
            ]

            user_dict = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "mobile": user.mobile,
                "ssex": user.ssex,
                "avatar": user.avatar,
                "description": user.description,
                "dept_id": user.dept_id,
                "dept_name": dept_name_map.get(user.dept_id),  # 部门名称  # 注释
                "status": user.status,
                "create_time": user.create_time.isoformat() if user.create_time else None,
                "modify_time": user.modify_time.isoformat() if user.modify_time else None,
                "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
                "roles": role_data  # 追加角色数组
            }
            user_list.append(user_dict)

        return SuccessExtra(
            code=200,
            msg="获取用户列表成功",
            data=user_list,
            total=total,
            page=request.page,
            page_size=request.size
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.post("/get-user-info", response_model=ApiResponse[UserResponse], summary="获取用户详情")
async def get_user_info(
    request: UserIdRequest,
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户详情

    - **user_id**: 用户ID（请求体传参）
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(request.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 转换为字典格式
        user_dict = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "dept_id": user.dept_id,
            "status": user.status,
            "ssex": user.ssex,
            "avatar": user.avatar,
            "description": user.description,
            "create_time": user.create_time.isoformat() if user.create_time else None,
            "modify_time": user.modify_time.isoformat() if user.modify_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
        }

        return Success(code=200, msg="获取用户详情成功", data=user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败"
        )


@router.post("/update-user", response_model=ApiResponse[UserResponse], summary="更新用户")
async def update_user(
    request: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新用户信息

    - **user_id**: 用户ID
    - **username**: 新的用户名（可选）
    - **email**: 新的邮箱（可选）
    - **mobile**: 新的手机号（可选）
    - **dept_id**: 新的部门ID（可选）
    - **status**: 新的状态（可选）
    - **ssex**: 新的性别（可选）
    - **avatar**: 新的头像（可选）
    - **description**: 新的描述（可选）
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.update_user(
            user_id=request.user_id,
            username=request.username,
            email=request.email,
            mobile=request.mobile,
            dept_id=request.dept_id,
            status=request.status,
            ssex=request.ssex,
            avatar=request.avatar,
            description=request.description
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 转换为字典格式
        user_dict = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "dept_id": user.dept_id,
            "status": user.status,
            "ssex": user.ssex,
            "avatar": user.avatar,
            "description": user.description,
            "create_time": user.create_time.isoformat() if user.create_time else None,
            "modify_time": user.modify_time.isoformat() if user.modify_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
        }
        return Success(code=200, msg="用户更新成功", data=user_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败"
        )


@router.post("/delete-user", response_model=ApiResponse[bool], summary="删除用户")
async def delete_user(
    request: UserDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    删除用户

    - **user_id**: 用户ID（请求体传参）
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.delete_user(request.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"User deleted successfully: {request.user_id}")
        return Success(code=200, msg="用户删除成功", data=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )


@router.post("/change-password", response_model=ApiResponse[bool], summary="修改密码")
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db)
):
    """
    修改用户密码

    - **user_id**: 用户ID
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.change_password(
            user_id=request.user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误或用户不存在"
            )

        logger.info(f"Password changed successfully for user: {request.user_id}")
        return ApiResponse.success_response(data=True, message="密码修改成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )


@router.post("/reset-password", response_model=ApiResponse[bool], summary="管理员重置密码")
async def reset_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    管理员重置用户密码（无需旧密码）

    - **user_id**: 用户ID
    - **new_password**: 新密码
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.reset_password(
            user_id=request.user_id,
            new_password=request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"Password reset successfully for user: {request.user_id}")
        return ApiResponse.success_response(data=True, message="密码重置成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置密码失败"
        )


@router.put("/{user_id}/lock", response_model=ApiResponse[bool], summary="锁定用户")
async def lock_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    锁定用户

    - **user_id**: 用户ID
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.lock_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"User locked successfully: {user_id}")
        return ApiResponse.success_response(data=True, message="用户锁定成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error locking user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="锁定用户失败"
        )


@router.put("/{user_id}/unlock", response_model=ApiResponse[bool], summary="解锁用户")
async def unlock_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    解锁用户

    - **user_id**: 用户ID
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.unlock_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"User unlocked successfully: {user_id}")
        return ApiResponse.success_response(data=True, message="用户解锁成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解锁用户失败"
        )


@router.post("/assign-user-roles", response_model=ApiResponse[bool], summary="分配角色")
async def assign_user_roles(
    request: UserRoleAssignRequest,
    db: Session = Depends(get_db)
):
    """
    为用户分配角色

    - **user_id**: 用户ID（请求体传参）
    - **role_ids**: 角色ID列表
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.assign_roles_to_user(request.user_id, request.role_ids)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在或角色不存在"
            )

        logger.info(f"Roles assigned to user successfully: {request.user_id}")
        return ApiResponse.success_response(data=True, message="角色分配成功")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配角色失败"
        )


@router.post("/get-user-roles", response_model=ApiResponse[UserRoleResponse], summary="获取用户角色")
async def get_user_roles(
    request: UserIdRequest,
    db: Session = Depends(get_db)
):
    """
    获取用户的角色列表

    - **user_id**: 用户ID（请求体传参）
    """
    try:
        logger.info(f"Getting roles for user_id: {request.user_id}")
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(request.user_id)
        logger.info(f"Found user: {user.username if user else 'None'}")

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        roles = user_service.get_user_roles(request.user_id)
        logger.info(f"Found {len(roles)} roles for user {request.user_id}")

        # 转换角色信息
        role_data = [
            {
                "role_id": role.id,
                "role_name": role.role_name,
                "remark": role.remark or ""
            }
            for role in roles
        ]

        user_role_response = UserRoleResponse(
            user_id=user.user_id,
            username=user.username,
            roles=role_data
        )

        return ApiResponse.success_response(data=user_role_response.model_dump(), message="获取用户角色成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user roles for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户角色失败: {str(e)}"
        )


@router.get("/export", summary="导出用户数据")
async def export_users(
    dept_id: Optional[int] = Query(None, description="部门ID筛选"),
    user_status: Optional[str] = Query(None, description="状态筛选"),
    ssex: Optional[str] = Query(None, description="性别筛选"),
    include_roles: bool = Query(True, description="是否包含角色信息"),
    user_ids: Optional[str] = Query(None, description="指定用户ID列表，逗号分隔"),
    db: Session = Depends(get_db)
):
    """
    导出用户数据到Excel文件

    - **dept_id**: 部门ID筛选（可选）
    - **user_status**: 状态筛选：0禁用 1启用（可选）
    - **ssex**: 性别筛选：0男 1女 2保密（可选）
    - **include_roles**: 是否包含角色信息（默认true）
    - **user_ids**: 指定用户ID列表，逗号分隔（可选，如果提供则只导出这些用户）
    """
    try:
        user_service = RBACUserService(db)

        # 解析用户ID列表
        parsed_user_ids = None
        if user_ids:
            try:
                parsed_user_ids = [int(uid.strip()) for uid in user_ids.split(',') if uid.strip()]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户ID格式错误，请使用逗号分隔的数字"
                )

        # 导出用户数据
        excel_data = user_service.export_users_to_excel(
            dept_id=dept_id,
            status=user_status,
            ssex=ssex,
            include_roles=include_roles,
            user_ids=parsed_user_ids
        )

        # 创建文件名
        from datetime import datetime
        import urllib.parse
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 根据导出类型生成不同的文件名
        if parsed_user_ids:
            safe_filename = f"selected_users_{timestamp}.xlsx"
            chinese_filename = f"选中用户_{timestamp}.xlsx"
        else:
            safe_filename = f"users_list_{timestamp}.xlsx"
            chinese_filename = f"用户列表_{timestamp}.xlsx"
        encoded_filename = urllib.parse.quote(chinese_filename.encode('utf-8'))
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导出用户数据失败"
        )


@router.post("/import", response_model=ApiResponse[UserImportResponse], summary="导入用户数据")
async def import_users(
    file: UploadFile = File(..., description="Excel文件"),
    update_existing: bool = Query(False, description="是否更新已存在的用户"),
    db: Session = Depends(get_db)
):
    """
    从Excel文件导入用户数据
    
    - **file**: Excel文件(.xlsx格式)
    - **update_existing**: 是否更新已存在的用户（默认false）
    
    Excel文件格式要求：
    - 第一行为表头：用户ID, 用户名, 邮箱, 手机号, 部门, 性别, 状态, 头像, 描述, 创建时间, 最后登录时间
    - 从第二行开始为数据行
    - 用户名为必填项
    - 性别：男/女/保密
    - 状态：启用/禁用
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持Excel文件格式(.xlsx, .xls)"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        user_service = RBACUserService(db)
        
        # 导入用户数据
        import_result = user_service.import_users_from_excel(
            file_content=file_content,
            update_existing=update_existing
        )
        
        # 构建响应
        response_data = UserImportResponse(
            total_count=import_result["total_count"],
            success_count=import_result["success_count"],
            failed_count=import_result["failed_count"],
            error_messages=import_result["error_messages"]
        )
        
        logger.info(f"User import completed: {import_result['success_count']}/{import_result['total_count']} successful")
        
        return Success(
            code=200,
            msg=f"导入完成！成功：{import_result['success_count']}，失败：{import_result['failed_count']}",
            data=response_data.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入用户数据失败: {str(e)}"
        )


@router.post("/batch-delete", response_model=ApiResponse[bool], summary="批量删除用户")
async def batch_delete_users(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    批量删除用户
    
    - **user_ids**: 用户ID列表
    """
    try:
        user_ids = request.get("user_ids", [])
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID列表不能为空"
            )
        
        user_service = RBACUserService(db)
        
        success_count = 0
        for user_id in user_ids:
            if user_service.delete_user(user_id):
                success_count += 1
        
        logger.info(f"Batch deleted {success_count}/{len(user_ids)} users")
        return Success(
            code=200,
            msg=f"批量删除完成！成功删除 {success_count} 个用户",
            data=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error batch deleting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除用户失败"
        )



