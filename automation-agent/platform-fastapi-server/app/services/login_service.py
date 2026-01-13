"""
登录服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user
from app.core.security import create_access_token
from app.core.exceptions import UnauthorizedException


class LoginService:
    """登录服务"""
    
    @staticmethod
    async def authenticate(
        db: AsyncSession,
        username: str,
        password: str
    ) -> tuple:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
        
        Returns:
            tuple: (用户对象, Token)
        
        Raises:
            UnauthorizedException: 认证失败
        """
        # 查询用户
        db_user = await user.get_by_username(db, username)
        if not db_user:
            raise UnauthorizedException("用户名不存在")
        
        # 验证密码
        if not db_user.check_password(password):
            raise UnauthorizedException("密码错误")
        
        # 生成 Token
        access_token = create_access_token(
            data={"username": username, "password": password}
        )
        
        return db_user, access_token


# 创建全局实例
login_service = LoginService()
