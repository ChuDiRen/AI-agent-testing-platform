"""
用户Repository
处理用户相关的数据库操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.entity.user import User
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    用户Repository类
    提供用户特定的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化用户Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或None
        """
        try:
            user = self.db.query(User).filter(
                and_(
                    User.username == username.lower(),
                    User.is_deleted == 0
                )
            ).first()
            
            if user:
                logger.debug(f"Found user with username: {username}")
            else:
                logger.debug(f"No user found with username: {username}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {str(e)}")
            raise

    def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或None
        """
        try:
            user = self.db.query(User).filter(
                and_(
                    User.email == email.lower(),
                    User.is_deleted == 0
                )
            ).first()
            
            if user:
                logger.debug(f"Found user with email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise

    def get_by_phone(self, phone: str) -> Optional[User]:
        """
        根据手机号获取用户
        
        Args:
            phone: 手机号
            
        Returns:
            用户对象或None
        """
        try:
            user = self.db.query(User).filter(
                and_(
                    User.phone == phone,
                    User.is_deleted == 0
                )
            ).first()
            
            if user:
                logger.debug(f"Found user with phone: {phone}")
            else:
                logger.debug(f"No user found with phone: {phone}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by phone {phone}: {str(e)}")
            raise

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        根据用户名或邮箱获取用户
        
        Args:
            identifier: 用户名或邮箱
            
        Returns:
            用户对象或None
        """
        try:
            identifier = identifier.lower()
            user = self.db.query(User).filter(
                and_(
                    or_(
                        User.username == identifier,
                        User.email == identifier
                    ),
                    User.is_deleted == 0
                )
            ).first()
            
            if user:
                logger.debug(f"Found user with identifier: {identifier}")
            else:
                logger.debug(f"No user found with identifier: {identifier}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by identifier {identifier}: {str(e)}")
            raise

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
            users = self.db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} active users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            raise

    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        获取已验证用户列表
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            已验证用户列表
        """
        try:
            users = self.db.query(User).filter(
                and_(
                    User.is_verified == True,
                    User.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} verified users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting verified users: {str(e)}")
            raise

    def get_superusers(self) -> List[User]:
        """
        获取超级用户列表
        
        Returns:
            超级用户列表
        """
        try:
            users = self.db.query(User).filter(
                and_(
                    User.is_superuser == True,
                    User.is_deleted == 0
                )
            ).all()
            
            logger.debug(f"Retrieved {len(users)} superusers")
            return users
            
        except Exception as e:
            logger.error(f"Error getting superusers: {str(e)}")
            raise

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
            keyword = f"%{keyword}%"
            users = self.db.query(User).filter(
                and_(
                    or_(
                        User.username.like(keyword),
                        User.email.like(keyword),
                        User.full_name.like(keyword),
                        User.phone.like(keyword)
                    ),
                    User.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(users)} users matching keyword: {keyword}")
            return users
            
        except Exception as e:
            logger.error(f"Error searching users with keyword {keyword}: {str(e)}")
            raise

    def username_exists(self, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        检查用户名是否已存在
        
        Args:
            username: 用户名
            exclude_user_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        try:
            query = self.db.query(User).filter(
                and_(
                    User.username == username.lower(),
                    User.is_deleted == 0
                )
            )
            
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
                
            exists = query.first() is not None
            
            logger.debug(f"Username '{username}' exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking username existence {username}: {str(e)}")
            raise

    def email_exists(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        检查邮箱是否已存在
        
        Args:
            email: 邮箱地址
            exclude_user_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        try:
            query = self.db.query(User).filter(
                and_(
                    User.email == email.lower(),
                    User.is_deleted == 0
                )
            )
            
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
                
            exists = query.first() is not None
            
            logger.debug(f"Email '{email}' exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            raise

    def phone_exists(self, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        检查手机号是否已存在
        
        Args:
            phone: 手机号
            exclude_user_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        try:
            query = self.db.query(User).filter(
                and_(
                    User.phone == phone,
                    User.is_deleted == 0
                )
            )
            
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
                
            exists = query.first() is not None
            
            logger.debug(f"Phone '{phone}' exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking phone existence {phone}: {str(e)}")
            raise
