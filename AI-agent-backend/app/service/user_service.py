"""
用户Service
处理用户相关的业务逻辑
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.entity.user import User
from app.repository.user_repository import UserRepository
from app.service.base import BaseService
from app.core.security import get_password_hash, verify_password
from app.utils.exceptions import (
    ValidationException, 
    BusinessException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserService(BaseService[User, UserRepository]):
    """
    用户Service类
    处理用户相关的业务逻辑
    """

    def __init__(self, repository: UserRepository):
        """
        初始化用户Service
        
        Args:
            repository: 用户Repository实例
        """
        super().__init__(repository)

    def _create_entity_from_data(self, data: Dict[str, Any]) -> User:
        """
        从数据字典创建用户实体对象
        
        Args:
            data: 用户数据字典
            
        Returns:
            用户实体对象
        """
        return User.from_dict(data)

    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        验证创建用户数据
        
        Args:
            data: 用户数据字典
            
        Raises:
            ValidationException: 数据验证异常
        """
        # 检查必需字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                raise ValidationException(f"Field '{field}' is required")
        
        # 验证用户名格式
        username = data['username']
        if len(username) < 3 or len(username) > 50:
            raise ValidationException("Username must be between 3 and 50 characters")
        
        # 验证邮箱格式
        email = data['email']
        if '@' not in email or len(email) > 100:
            raise ValidationException("Invalid email format")
        
        # 验证密码强度
        password = data['password']
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        # 检查用户名是否已存在
        if self.repository.username_exists(username):
            raise UserAlreadyExistsException("username", username)
        
        # 检查邮箱是否已存在
        if self.repository.email_exists(email):
            raise UserAlreadyExistsException("email", email)
        
        # 检查手机号是否已存在（如果提供）
        phone = data.get('phone')
        if phone and self.repository.phone_exists(phone):
            raise UserAlreadyExistsException("phone", phone)

    def _validate_update_data(self, entity_id: int, data: Dict[str, Any]) -> None:
        """
        验证更新用户数据
        
        Args:
            entity_id: 用户ID
            data: 更新数据字典
            
        Raises:
            ValidationException: 数据验证异常
        """
        # 验证用户名（如果要更新）
        username = data.get('username')
        if username:
            if len(username) < 3 or len(username) > 50:
                raise ValidationException("Username must be between 3 and 50 characters")
            if self.repository.username_exists(username, exclude_user_id=entity_id):
                raise UserAlreadyExistsException("username", username)
        
        # 验证邮箱（如果要更新）
        email = data.get('email')
        if email:
            if '@' not in email or len(email) > 100:
                raise ValidationException("Invalid email format")
            if self.repository.email_exists(email, exclude_user_id=entity_id):
                raise UserAlreadyExistsException("email", email)
        
        # 验证手机号（如果要更新）
        phone = data.get('phone')
        if phone and self.repository.phone_exists(phone, exclude_user_id=entity_id):
            raise UserAlreadyExistsException("phone", phone)

    def _before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建用户前的处理
        
        Args:
            data: 用户数据字典
            
        Returns:
            处理后的数据字典
        """
        # 加密密码
        if 'password' in data:
            data['hashed_password'] = get_password_hash(data.pop('password'))
        
        # 设置默认值
        data.setdefault('is_active', True)
        data.setdefault('is_verified', False)
        data.setdefault('is_superuser', False)
        
        return data

    def _before_update(self, entity: User, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户前的处理
        
        Args:
            entity: 现有用户实体
            data: 更新数据字典
            
        Returns:
            处理后的数据字典
        """
        # 如果要更新密码，进行加密
        if 'password' in data:
            data['hashed_password'] = get_password_hash(data.pop('password'))
        
        return data

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            identifier: 用户名或邮箱
            password: 密码
            
        Returns:
            认证成功的用户对象或None
            
        Raises:
            InvalidCredentialsException: 认证失败异常
        """
        try:
            # 根据用户名或邮箱查找用户
            user = self.repository.get_by_username_or_email(identifier)
            
            if not user:
                logger.warning(f"Authentication failed: user not found for identifier '{identifier}'")
                raise InvalidCredentialsException()
            
            # 检查用户是否可以登录
            if not user.can_login():
                logger.warning(f"Authentication failed: user '{identifier}' cannot login")
                raise InvalidCredentialsException()
            
            # 验证密码
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: invalid password for user '{identifier}'")
                raise InvalidCredentialsException()
            
            # 更新最后登录时间
            user.update_last_login()
            self.repository.update(user.id, {'last_login_at': user.last_login_at})
            
            logger.info(f"User '{identifier}' authenticated successfully")
            return user
            
        except InvalidCredentialsException:
            raise
        except Exception as e:
            logger.error(f"Error during user authentication: {str(e)}")
            raise BusinessException("Authentication failed")

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            是否修改成功
            
        Raises:
            UserNotFoundException: 用户不存在异常
            InvalidCredentialsException: 旧密码错误异常
            ValidationException: 新密码验证异常
        """
        try:
            # 获取用户
            user = self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            # 验证旧密码
            if not verify_password(old_password, user.hashed_password):
                raise InvalidCredentialsException()
            
            # 验证新密码
            if len(new_password) < 8:
                raise ValidationException("New password must be at least 8 characters long")
            
            # 更新密码
            new_hashed_password = get_password_hash(new_password)
            user.change_password(new_hashed_password)
            
            self.repository.update(user_id, {
                'hashed_password': user.hashed_password,
                'password_changed_at': user.password_changed_at
            })
            
            logger.info(f"Password changed successfully for user {user_id}")
            return True
            
        except (UserNotFoundException, InvalidCredentialsException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {str(e)}")
            raise BusinessException("Failed to change password")

    def activate_user(self, user_id: int) -> bool:
        """
        激活用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否激活成功
        """
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.activate()
            self.repository.update(user_id, {
                'is_active': user.is_active,
                'updated_at': user.updated_at
            })
            
            logger.info(f"User {user_id} activated successfully")
            return True
            
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {str(e)}")
            raise BusinessException("Failed to activate user")

    def deactivate_user(self, user_id: int) -> bool:
        """
        停用用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否停用成功
        """
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.deactivate()
            self.repository.update(user_id, {
                'is_active': user.is_active,
                'updated_at': user.updated_at
            })
            
            logger.info(f"User {user_id} deactivated successfully")
            return True
            
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            raise BusinessException("Failed to deactivate user")

    def verify_user(self, user_id: int) -> bool:
        """
        验证用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否验证成功
        """
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.verify()
            self.repository.update(user_id, {
                'is_verified': user.is_verified,
                'updated_at': user.updated_at
            })
            
            logger.info(f"User {user_id} verified successfully")
            return True
            
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {str(e)}")
            raise BusinessException("Failed to verify user")

    def search_users(self, keyword: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            匹配的用户列表
        """
        try:
            return self.repository.search_users(keyword, skip, limit)
            
        except Exception as e:
            logger.error(f"Error searching users with keyword '{keyword}': {str(e)}")
            raise BusinessException("Failed to search users")

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        获取活跃用户列表
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            活跃用户列表
        """
        try:
            return self.repository.get_active_users(skip, limit)
            
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            raise BusinessException("Failed to get active users")

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或None
        """
        try:
            return self.repository.get_by_username(username)
            
        except Exception as e:
            logger.error(f"Error getting user by username '{username}': {str(e)}")
            raise BusinessException("Failed to get user")

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或None
        """
        try:
            return self.repository.get_by_email(email)
            
        except Exception as e:
            logger.error(f"Error getting user by email '{email}': {str(e)}")
            raise BusinessException("Failed to get user")
