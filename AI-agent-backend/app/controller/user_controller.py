# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC用户Controller
处理用户相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.security import create_access_token
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.user_dto import (
    UserCreateRequest,
    UserUpdateRequest,
    PasswordChangeRequest,
    UserResponse,
    UserListResponse,
    UserRoleAssignRequest,
    UserRoleResponse,
    LoginRequest,
    LoginResponse,
    UserIdRequest,
    UserListRequest,
    UserDeleteRequest
)
from app.entity.user import User
from app.middleware.auth import get_current_user
from app.service.rbac_user_service import RBACUserService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/create-user", response_model=ApiResponse[UserResponse], summary="创建用户")
async def create_user(
    request: UserCreateRequest,
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
        
        # 转换为响应格式
        user_response = UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            dept_id=user.dept_id,
            status=user.status,
            ssex=user.ssex,
            avatar=user.avatar,
            description=user.description,
            create_time=user.create_time,
            modify_time=user.modify_time,
            last_login_time=user.last_login_time
        )
        
        logger.info(f"User created successfully: {user.username}")
        return ApiResponse.success_response(data=user_response, message="用户创建成功")
        
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
    db: Session = Depends(get_db)
):
    """
    用户登录认证
    
    - **username**: 用户名
    - **password**: 密码
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 生成访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})

        # 获取用户权限
        permissions = user_service.get_user_permissions(user.id)

        # 构建用户信息
        user_info = UserResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            dept_id=user.dept_id,
            status=user.status,
            ssex=user.ssex,
            avatar=user.avatar,
            description=user.description,
            create_time=user.create_time,
            modify_time=user.modify_time,
            last_login_time=user.last_login_time
        )
        
        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_info=user_info,
            permissions=permissions
        )
        
        logger.info(f"User logged in successfully: {user.username}")
        return ApiResponse.success_response(data=login_response, message="登录成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.post("/logout", response_model=ApiResponse[bool], summary="用户退出登录")
async def user_logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户退出登录

    Args:
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        退出登录结果
    """
    try:
        # 在实际应用中，这里可以：
        # 1. 将token加入黑名单（如果使用Redis）
        # 2. 记录退出日志
        # 3. 清理用户相关缓存

        logger.info(f"User logged out successfully: {current_user.username}")
        return ApiResponse.success_response(data=True, message="退出登录成功")

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
        users = user_service.get_all_users()
        
        # 转换为响应格式
        user_responses = [
            UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                mobile=user.mobile,
                dept_id=user.dept_id,
                status=user.status,
                ssex=user.ssex,
                avatar=user.avatar,
                description=user.description,
                create_time=user.create_time,
                modify_time=user.modify_time,
                last_login_time=user.last_login_time
            )
            for user in users
        ]
        
        user_list_response = UserListResponse(users=user_responses)
        
        return ApiResponse.success_response(data=user_list_response, message="获取用户列表成功")
        
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
        
        user_response = UserResponse(
            user_id=user.id,  # 修复：使用正确的属性名
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            dept_id=user.dept_id,
            status=user.status,
            ssex=user.ssex,
            avatar=user.avatar,
            description=user.description,
            create_time=user.create_time,
            modify_time=user.modify_time,
            last_login_time=user.last_login_time
        )
        
        return ApiResponse.success_response(data=user_response, message="获取用户详情成功")
        
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
    - **email**: 新的邮箱（可选）
    - **mobile**: 新的手机号（可选）
    - **ssex**: 新的性别（可选）
    - **avatar**: 新的头像（可选）
    - **description**: 新的描述（可选）
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.update_user(
            user_id=request.user_id,
            email=request.email,
            mobile=request.mobile,
            ssex=request.ssex,
            avatar=request.avatar,
            description=request.description
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user_response = UserResponse(
            user_id=user.id,  # 修复：使用正确的属性名
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            dept_id=user.dept_id,
            status=user.status,
            ssex=user.ssex,
            avatar=user.avatar,
            description=user.description,
            create_time=user.create_time,
            modify_time=user.modify_time,
            last_login_time=user.last_login_time
        )
        return ApiResponse.success_response(data=user_response, message="用户更新成功")

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
        success = user_service.delete_user()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"User deleted successfully: {request.user_id}")
        return ApiResponse.success_response(data=True, message="用户删除成功")

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
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(request.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        roles = user_service.get_user_roles(request.user_id)

        # 转换角色信息
        role_data = [
            {
                "role_id": role.id,
                "role_name": role.role_name,
                "remark": role.remark
            }
            for role in roles
        ]

        user_role_response = UserRoleResponse(
            user_id=user.user_id,
            username=user.username,
            roles=role_data
        )

        return ApiResponse.success_response(data=user_role_response, message="获取用户角色成功")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户角色失败"
        )


