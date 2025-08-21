"""
用户请求DTO
定义用户相关的请求数据结构
"""

from typing import Optional

from pydantic import Field, validator, EmailStr

from app.dto.base import BaseRequest, SearchRequest


class UserCreateRequest(BaseRequest):
    """
    创建用户请求DTO
    """
    username: str = Field(min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱地址")
    password: str = Field(min_length=8, max_length=128, description="密码")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    full_name: Optional[str] = Field(default=None, max_length=100, description="全名")
    bio: Optional[str] = Field(default=None, max_length=500, description="个人简介")
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        v = v.lower().strip()
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            v = v.strip()
            if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class UserUpdateRequest(BaseRequest):
    """
    更新用户请求DTO
    """
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(default=None, description="邮箱地址")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    full_name: Optional[str] = Field(default=None, max_length=100, description="全名")
    bio: Optional[str] = Field(default=None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_verified: Optional[bool] = Field(default=None, description="是否已验证")
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if v is not None:
            v = v.lower().strip()
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            v = v.strip()
            if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                raise ValueError('Invalid phone number format')
        return v


class UserLoginRequest(BaseRequest):
    """
    用户登录请求DTO
    """
    identifier: str = Field(min_length=3, max_length=100, description="用户名或邮箱")
    password: str = Field(min_length=1, max_length=128, description="密码")
    remember_me: bool = Field(default=False, description="记住我")
    
    @validator('identifier')
    def validate_identifier(cls, v):
        """验证登录标识符"""
        return v.lower().strip()


class UserChangePasswordRequest(BaseRequest):
    """
    修改密码请求DTO
    """
    old_password: str = Field(min_length=1, max_length=128, description="旧密码")
    new_password: str = Field(min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(min_length=8, max_length=128, description="确认新密码")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        """验证密码确认"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """验证新密码强度"""
        # 检查新密码不能与旧密码相同
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('New password must be different from old password')
        
        # 检查密码强度
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class UserSearchRequest(SearchRequest):
    """
    用户搜索请求DTO
    """
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_verified: Optional[bool] = Field(default=None, description="是否已验证")
    is_superuser: Optional[bool] = Field(default=None, description="是否超级用户")


class UserPasswordResetRequest(BaseRequest):
    """
    密码重置请求DTO
    """
    email: EmailStr = Field(description="邮箱地址")


class UserPasswordResetConfirmRequest(BaseRequest):
    """
    确认密码重置请求DTO
    """
    token: str = Field(min_length=1, description="重置令牌")
    new_password: str = Field(min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(min_length=8, max_length=128, description="确认新密码")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        """验证密码确认"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class UserEmailVerificationRequest(BaseRequest):
    """
    邮箱验证请求DTO
    """
    token: str = Field(min_length=1, description="验证令牌")


class UserRefreshTokenRequest(BaseRequest):
    """
    刷新令牌请求DTO
    """
    refresh_token: str = Field(min_length=1, description="刷新令牌")


class UserBulkOperationRequest(BaseRequest):
    """
    用户批量操作请求DTO
    """
    user_ids: list[int] = Field(min_items=1, max_items=100, description="用户ID列表")
    operation: str = Field(description="操作类型: activate, deactivate, verify, delete")
    
    @validator('operation')
    def validate_operation(cls, v):
        """验证操作类型"""
        allowed_operations = ['activate', 'deactivate', 'verify', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v
    
    @validator('user_ids')
    def validate_user_ids(cls, v):
        """验证用户ID列表"""
        # 去重并排序
        return sorted(list(set(v)))


# 导出所有请求DTO
__all__ = [
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserLoginRequest", 
    "UserChangePasswordRequest",
    "UserSearchRequest",
    "UserPasswordResetRequest",
    "UserPasswordResetConfirmRequest",
    "UserEmailVerificationRequest",
    "UserRefreshTokenRequest",
    "UserBulkOperationRequest",
]
