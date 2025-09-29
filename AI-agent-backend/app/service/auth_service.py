"""
认证服务 - 兼容vue-fastapi-admin格式
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.entity.user import User
from app.core.security import verify_password
from app.core.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            认证成功返回用户对象，失败返回None
        """
        try:
            # 查询用户
            user = self.db.query(User).filter(
                and_(
                    User.username == username,
                    User.is_deleted == False
                )
            ).first()
            
            if not user:
                logger.warning(f"用户不存在: {username}")
                return None
            
            # 验证密码
            if not verify_password(password, user.password_hash):
                logger.warning(f"密码错误: {username}")
                return None
            
            # 检查用户状态
            if not user.is_active:
                logger.warning(f"用户已禁用: {username}")
                return None
            
            logger.info(f"用户认证成功: {username}")
            return user
            
        except Exception as e:
            logger.error(f"用户认证失败: {username}, 错误: {str(e)}")
            return None
    
    async def verify_token_user(self, user_id: int) -> Optional[User]:
        """
        验证令牌用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        try:
            user = self.db.query(User).filter(
                and_(
                    User.id == user_id,
                    User.is_active == True,
                    User.is_deleted == False
                )
            ).first()
            
            return user
            
        except Exception as e:
            logger.error(f"验证令牌用户失败: {user_id}, 错误: {str(e)}")
            return None
