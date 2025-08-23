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
    LoginResponse
)
from app.service.rbac_user_service import RBACUserService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/", response_model=ApiResponse[UserResponse], summary="创建用户")
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
            user_id=user.USER_ID,
            username=user.USERNAME,
            email=user.EMAIL,
            mobile=user.MOBILE,
            dept_id=user.DEPT_ID,
            status=user.STATUS,
            ssex=user.SSEX,
            avatar=user.AVATAR,
            description=user.DESCRIPTION,
            create_time=user.CREATE_TIME,
            modify_time=user.MODIFY_TIME,
            last_login_time=user.LAST_LOGIN_TIME
        )
        
        logger.info(f"User created successfully: {user.USERNAME}")
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
async def login(
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
        access_token = create_access_token(data={"sub": str(user.USER_ID)})
        
        # 获取用户权限
        permissions = user_service.get_user_permissions(user.USER_ID)
        
        # 构建用户信息
        user_info = UserResponse(
            user_id=user.USER_ID,
            username=user.USERNAME,
            email=user.EMAIL,
            mobile=user.MOBILE,
            dept_id=user.DEPT_ID,
            status=user.STATUS,
            ssex=user.SSEX,
            avatar=user.AVATAR,
            description=user.DESCRIPTION,
            create_time=user.CREATE_TIME,
            modify_time=user.MODIFY_TIME,
            last_login_time=user.LAST_LOGIN_TIME
        )
        
        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_info=user_info,
            permissions=permissions
        )
        
        logger.info(f"User logged in successfully: {user.USERNAME}")
        return ApiResponse.success_response(data=login_response, message="登录成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.get("/", response_model=ApiResponse[UserListResponse], summary="获取用户列表")
async def get_users(
    db: Session = Depends(get_db)
):
    """
    获取所有用户列表
    """
    try:
        user_service = RBACUserService(db)
        users = user_service.get_all_users()
        
        # 转换为响应格式
        user_responses = [
            UserResponse(
                user_id=user.USER_ID,
                username=user.USERNAME,
                email=user.EMAIL,
                mobile=user.MOBILE,
                dept_id=user.DEPT_ID,
                status=user.STATUS,
                ssex=user.SSEX,
                avatar=user.AVATAR,
                description=user.DESCRIPTION,
                create_time=user.CREATE_TIME,
                modify_time=user.MODIFY_TIME,
                last_login_time=user.LAST_LOGIN_TIME
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


@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取用户详情")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户详情
    
    - **user_id**: 用户ID
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user_response = UserResponse(
            user_id=user.USER_ID,
            username=user.USERNAME,
            email=user.EMAIL,
            mobile=user.MOBILE,
            dept_id=user.DEPT_ID,
            status=user.STATUS,
            ssex=user.SSEX,
            avatar=user.AVATAR,
            description=user.DESCRIPTION,
            create_time=user.CREATE_TIME,
            modify_time=user.MODIFY_TIME,
            last_login_time=user.LAST_LOGIN_TIME
        )
        
        return ApiResponse.success_response(data=user_response, message="获取用户详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败"
        )


@router.put("/{user_id}", response_model=ApiResponse[UserResponse], summary="更新用户")
async def update_user(
    user_id: int,
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
            user_id=user_id,
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
            user_id=user.USER_ID,
            username=user.USERNAME,
            email=user.EMAIL,
            mobile=user.MOBILE,
            dept_id=user.DEPT_ID,
            status=user.STATUS,
            ssex=user.SSEX,
            avatar=user.AVATAR,
            description=user.DESCRIPTION,
            create_time=user.CREATE_TIME,
            modify_time=user.MODIFY_TIME,
            last_login_time=user.LAST_LOGIN_TIME
        )
        
        logger.info(f"User updated successfully: {user_id}")
        return ApiResponse.success_response(data=user_response, message="用户更新成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败"
        )


@router.put("/{user_id}/password", response_model=ApiResponse[bool], summary="修改密码")
async def change_password(
    user_id: int,
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
            user_id=user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误或用户不存在"
            )

        logger.info(f"Password changed successfully for user: {user_id}")
        return ApiResponse.success_response(data=True, message="密码修改成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
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


@router.post("/{user_id}/roles", response_model=ApiResponse[bool], summary="分配角色")
async def assign_roles_to_user(
    user_id: int,
    request: UserRoleAssignRequest,
    db: Session = Depends(get_db)
):
    """
    为用户分配角色

    - **user_id**: 用户ID
    - **role_ids**: 角色ID列表
    """
    try:
        user_service = RBACUserService(db)
        success = user_service.assign_roles_to_user(user_id, request.role_ids)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在或角色不存在"
            )

        logger.info(f"Roles assigned to user successfully: {user_id}")
        return ApiResponse.success_response(data=True, message="角色分配成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning roles to user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配角色失败"
        )


@router.get("/{user_id}/roles", response_model=ApiResponse[UserRoleResponse], summary="获取用户角色")
async def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户的角色列表

    - **user_id**: 用户ID
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        roles = user_service.get_user_roles(user_id)

        # 转换角色信息
        role_data = [
            {
                "role_id": role.ROLE_ID,
                "role_name": role.ROLE_NAME,
                "remark": role.REMARK
            }
            for role in roles
        ]

        user_role_response = UserRoleResponse(
            user_id=user.USER_ID,
            username=user.USERNAME,
            roles=role_data
        )

        return ApiResponse.success_response(data=user_role_response, message="获取用户角色成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user roles for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户角色失败"
        )


@router.get("/{user_id}/permissions", response_model=ApiResponse[list], summary="获取用户权限")
async def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户权限列表

    - **user_id**: 用户ID
    """
    try:
        user_service = RBACUserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        permissions = user_service.get_user_permissions(user_id)
        return ApiResponse.success_response(data=permissions, message="获取用户权限成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user permissions for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户权限失败"
        )
