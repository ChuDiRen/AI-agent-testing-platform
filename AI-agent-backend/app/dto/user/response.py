"""
用户响应DTO
定义用户相关的响应数据结构
"""

from datetime import datetime
from typing import Optional, List

from pydantic import Field

from app.dto.base import BaseResponse, PaginatedResponse


class UserResponse(BaseResponse):
    """
    用户响应DTO
    """
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱地址")
    phone: Optional[str] = Field(description="手机号")
    full_name: Optional[str] = Field(description="全名")
    avatar: Optional[str] = Field(description="头像URL")
    bio: Optional[str] = Field(description="个人简介")
    is_active: bool = Field(description="是否激活")
    is_verified: bool = Field(description="是否已验证")
    is_superuser: bool = Field(description="是否超级用户")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    last_login_at: Optional[datetime] = Field(description="最后登录时间")
    
    @classmethod
    def from_entity(cls, user) -> "UserResponse":
        """
        从用户实体创建响应对象
        
        Args:
            user: 用户实体对象
            
        Returns:
            用户响应对象
        """
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            avatar=user.avatar,
            bio=user.bio,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )


class UserProfileResponse(BaseResponse):
    """
    用户个人资料响应DTO
    """
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱地址")
    phone: Optional[str] = Field(description="手机号")
    full_name: Optional[str] = Field(description="全名")
    avatar: Optional[str] = Field(description="头像URL")
    bio: Optional[str] = Field(description="个人简介")
    is_verified: bool = Field(description="是否已验证")
    created_at: datetime = Field(description="创建时间")
    last_login_at: Optional[datetime] = Field(description="最后登录时间")
    
    @classmethod
    def from_entity(cls, user) -> "UserProfileResponse":
        """
        从用户实体创建个人资料响应对象
        
        Args:
            user: 用户实体对象
            
        Returns:
            用户个人资料响应对象
        """
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            avatar=user.avatar,
            bio=user.bio,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )


class UserLoginResponse(BaseResponse):
    """
    用户登录响应DTO
    """
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="令牌过期时间（秒）")
    user: UserProfileResponse = Field(description="用户信息")
    
    @classmethod
    def create(cls, tokens: dict, user, expires_in: int) -> "UserLoginResponse":
        """
        创建登录响应对象
        
        Args:
            tokens: 令牌字典
            user: 用户实体对象
            expires_in: 过期时间
            
        Returns:
            登录响应对象
        """
        return cls(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=expires_in,
            user=UserProfileResponse.from_entity(user)
        )


class UserListResponse(PaginatedResponse):
    """
    用户列表响应DTO
    """
    items: List[UserResponse] = Field(description="用户列表")
    
    @classmethod
    def from_entities(cls, users: List, page: int, page_size: int, total: int) -> "UserListResponse":
        """
        从用户实体列表创建响应对象
        
        Args:
            users: 用户实体列表
            page: 当前页码
            page_size: 每页大小
            total: 总记录数
            
        Returns:
            用户列表响应对象
        """
        user_responses = [UserResponse.from_entity(user) for user in users]
        return cls.create(user_responses, page, page_size, total)


class UserStatsResponse(BaseResponse):
    """
    用户统计响应DTO
    """
    total_users: int = Field(description="总用户数")
    active_users: int = Field(description="活跃用户数")
    verified_users: int = Field(description="已验证用户数")
    superusers: int = Field(description="超级用户数")
    new_users_today: int = Field(description="今日新增用户数")
    new_users_this_week: int = Field(description="本周新增用户数")
    new_users_this_month: int = Field(description="本月新增用户数")


class UserTokenResponse(BaseResponse):
    """
    用户令牌响应DTO
    """
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="令牌过期时间（秒）")


class UserBulkOperationResponse(BaseResponse):
    """
    用户批量操作响应DTO
    """
    total: int = Field(description="总操作数量")
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    failed_user_ids: List[int] = Field(default_factory=list, description="失败的用户ID列表")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.success_count / self.total if self.total > 0 else 0.0


class UserSimpleResponse(BaseResponse):
    """
    用户简单响应DTO（用于下拉选择等场景）
    """
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    full_name: Optional[str] = Field(description="全名")
    avatar: Optional[str] = Field(description="头像URL")
    is_active: bool = Field(description="是否激活")
    
    @classmethod
    def from_entity(cls, user) -> "UserSimpleResponse":
        """
        从用户实体创建简单响应对象
        
        Args:
            user: 用户实体对象
            
        Returns:
            用户简单响应对象
        """
        return cls(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar=user.avatar,
            is_active=user.is_active
        )


class UserActivityResponse(BaseResponse):
    """
    用户活动响应DTO
    """
    user_id: int = Field(description="用户ID")
    activity_type: str = Field(description="活动类型")
    activity_description: str = Field(description="活动描述")
    ip_address: Optional[str] = Field(description="IP地址")
    user_agent: Optional[str] = Field(description="用户代理")
    created_at: datetime = Field(description="活动时间")


class UserPermissionResponse(BaseResponse):
    """
    用户权限响应DTO
    """
    user_id: int = Field(description="用户ID")
    permissions: List[str] = Field(description="权限列表")
    roles: List[str] = Field(description="角色列表")
    is_superuser: bool = Field(description="是否超级用户")


# 导出所有响应DTO
__all__ = [
    "UserResponse",
    "UserProfileResponse",
    "UserLoginResponse",
    "UserListResponse",
    "UserStatsResponse",
    "UserTokenResponse",
    "UserBulkOperationResponse",
    "UserSimpleResponse",
    "UserActivityResponse",
    "UserPermissionResponse",
]
