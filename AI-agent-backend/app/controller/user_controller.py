"""
用户Controller
处理用户相关的HTTP请求
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.controller.base import BaseController
from app.service.user_service import UserService
from app.repository.user_repository import UserRepository
from app.dto.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserLoginRequest,
    UserChangePasswordRequest,
    UserSearchRequest,
    UserResponse,
    UserListResponse,
    UserLoginResponse,
    UserProfileResponse
)
from app.dto.base import ApiResponse, PaginationRequest
from app.db.session import get_db
from app.core.security import create_token_pair
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["users"])


class UserController(BaseController):
    """
    用户Controller类
    处理用户相关的HTTP请求
    """

    def __init__(self):
        super().__init__(UserService)

    def get_service(self, db: Session = Depends(get_db)) -> UserService:
        """
        获取用户Service实例
        
        Args:
            db: 数据库会话
            
        Returns:
            用户Service实例
        """
        repository = UserRepository(db)
        return UserService(repository)


# 创建Controller实例
user_controller = UserController()


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(user_controller.get_service)
):
    """
    创建用户
    
    Args:
        request: 创建用户请求
        service: 用户服务
        
    Returns:
        创建结果
    """
    try:
        user_controller.log_request("create_user", request.dict())
        
        # 创建用户
        user = service.create(request.dict())
        
        # 转换为响应对象
        user_response = UserResponse.from_entity(user)
        
        response = user_controller.create_success_response(
            data=user_response,
            message="User created successfully"
        )
        
        user_controller.log_response("create_user", user_response)
        return response
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(user_controller.get_service)
):
    """
    获取用户详情
    
    Args:
        user_id: 用户ID
        service: 用户服务
        
    Returns:
        用户详情
    """
    try:
        user_controller.validate_id(user_id, "User")
        user_controller.log_request("get_user", {"user_id": user_id})
        
        # 获取用户
        user = service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # 转换为响应对象
        user_response = UserResponse.from_entity(user)
        
        response = user_controller.create_success_response(
            data=user_response,
            message="User retrieved successfully"
        )
        
        user_controller.log_response("get_user", user_response)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    service: UserService = Depends(user_controller.get_service)
):
    """
    更新用户
    
    Args:
        user_id: 用户ID
        request: 更新用户请求
        service: 用户服务
        
    Returns:
        更新结果
    """
    try:
        user_controller.validate_id(user_id, "User")
        user_controller.log_request("update_user", {"user_id": user_id, **request.dict()})
        
        # 更新用户
        user = service.update(user_id, request.dict(exclude_unset=True))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # 转换为响应对象
        user_response = UserResponse.from_entity(user)
        
        response = user_controller.create_success_response(
            data=user_response,
            message="User updated successfully"
        )
        
        user_controller.log_response("update_user", user_response)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: int,
    service: UserService = Depends(user_controller.get_service)
):
    """
    删除用户
    
    Args:
        user_id: 用户ID
        service: 用户服务
        
    Returns:
        删除结果
    """
    try:
        user_controller.validate_id(user_id, "User")
        user_controller.log_request("delete_user", {"user_id": user_id})
        
        # 删除用户
        success = service.delete(user_id, soft_delete=True)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        response = user_controller.create_success_response(
            message="User deleted successfully"
        )
        
        user_controller.log_response("delete_user", {"deleted": True})
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise


@router.get("/", response_model=ApiResponse)
async def list_users(
    pagination: PaginationRequest = Depends(),
    service: UserService = Depends(user_controller.get_service)
):
    """
    获取用户列表
    
    Args:
        pagination: 分页参数
        service: 用户服务
        
    Returns:
        用户列表
    """
    try:
        user_controller.validate_pagination(pagination)
        user_controller.log_request("list_users", pagination.dict())
        
        # 获取用户列表
        users = service.get_all(pagination.skip, pagination.limit)
        total = service.count()
        
        # 创建分页响应
        user_list_response = UserListResponse.from_entities(
            users, pagination.page, pagination.page_size, total
        )
        
        response = user_controller.create_success_response(
            data=user_list_response,
            message="Users retrieved successfully"
        )
        
        user_controller.log_response("list_users", {"count": len(users), "total": total})
        return response
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise


@router.post("/login", response_model=ApiResponse)
async def login_user(
    request: UserLoginRequest,
    service: UserService = Depends(user_controller.get_service)
):
    """
    用户登录
    
    Args:
        request: 登录请求
        service: 用户服务
        
    Returns:
        登录结果（包含令牌）
    """
    try:
        user_controller.log_request("login_user", {"identifier": request.identifier})
        
        # 用户认证
        user = service.authenticate_user(request.identifier, request.password)
        
        # 创建令牌
        tokens = create_token_pair(user.id)
        
        # 创建登录响应
        login_response = UserLoginResponse.create(
            tokens=tokens,
            user=user,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        response = user_controller.create_success_response(
            data=login_response,
            message="Login successful"
        )
        
        user_controller.log_response("login_user", {"user_id": user.id})
        return response
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise


@router.post("/{user_id}/change-password", response_model=ApiResponse)
async def change_password(
    user_id: int,
    request: UserChangePasswordRequest,
    service: UserService = Depends(user_controller.get_service)
):
    """
    修改用户密码
    
    Args:
        user_id: 用户ID
        request: 修改密码请求
        service: 用户服务
        
    Returns:
        修改结果
    """
    try:
        user_controller.validate_id(user_id, "User")
        user_controller.log_request("change_password", {"user_id": user_id})
        
        # 修改密码
        success = service.change_password(
            user_id, 
            request.old_password, 
            request.new_password
        )
        
        if success:
            response = user_controller.create_success_response(
                message="Password changed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        user_controller.log_response("change_password", {"success": success})
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        raise


@router.post("/search", response_model=ApiResponse)
async def search_users(
    request: UserSearchRequest,
    service: UserService = Depends(user_controller.get_service)
):
    """
    搜索用户
    
    Args:
        request: 搜索请求
        service: 用户服务
        
    Returns:
        搜索结果
    """
    try:
        user_controller.log_request("search_users", request.dict())
        
        # 搜索用户
        if request.keyword:
            users = service.search_users(request.keyword, request.skip, request.limit)
            total = len(users)  # 简化实现，实际应该查询总数
        else:
            users = service.get_all(request.skip, request.limit)
            total = service.count()
        
        # 创建分页响应
        user_list_response = UserListResponse.from_entities(
            users, request.page, request.page_size, total
        )
        
        response = user_controller.create_success_response(
            data=user_list_response,
            message="Search completed successfully"
        )
        
        user_controller.log_response("search_users", {"count": len(users)})
        return response
        
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise


# 导出路由器
__all__ = ["router", "UserController"]
