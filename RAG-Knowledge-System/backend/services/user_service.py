"""
用户服务
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select

from models.user import User
from models.role import Role
from models.department import Department
from core.security import get_password_hash, verify_password
from core.logger import setup_logger
from core.exceptions import (
    ValidationException,
    BusinessException
)

logger = setup_logger(__name__)


class UserService:
    """用户服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        full_name: Optional[str] = None,
        role_id: Optional[int] = None,
        dept_id: Optional[int] = None
    ) -> User:
        """
        创建用户

        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            full_name: 全名
            role_id: 角色ID
            dept_id: 部门ID

        Returns:
            创建的用户

        Raises:
            ValidationException: 用户名或邮箱已存在
        """
        logger.info(f"创建用户: username={username}, email={email}")

        # 检查用户名是否已存在
        existing_user = self.db.exec(
            select(User).where(User.username == username)
        ).first()

        if existing_user:
            raise ValidationException(
                "用户名已存在",
                field="username"
            )

        # 检查邮箱是否已存在
        existing_email = self.db.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_email:
            raise ValidationException(
                "邮箱已被注册",
                field="email"
            )

        # 密码哈希
        password_hash = get_password_hash(password)

        # 创建用户
        user = User(
            username=username,
            hashed_password=password_hash,
            email=email,
            full_name=full_name,
            role_id=role_id,
            dept_id=dept_id,
            is_active=True,
            is_superuser=False
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"用户创建成功: user_id={user.id}, username={username}")
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户

        Args:
            username: 用户名
            password: 密码

        Returns:
            用户对象或None
        """
        logger.info(f"用户登录: username={username}")

        # 查找用户
        user = self.db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            logger.warning(f"用户不存在: username={username}")
            return None

        # 检查是否激活
        if not user.is_active:
            logger.warning(f"用户未激活: user_id={user.id}")
            return None

        # 验证密码
        if not verify_password(password, user.hashed_password):
            logger.warning(f"密码错误: user_id={user.id}")
            return None

        logger.info(f"用户登录成功: user_id={user.id}")
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """
        获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        return self.db.exec(
            select(User).where(User.id == user_id)
        ).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或None
        """
        return self.db.exec(
            select(User).where(User.username == username)
        ).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            用户对象或None
        """
        return self.db.exec(
            select(User).where(User.email == email)
        ).first()

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role_id: Optional[int] = None,
        dept_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        password: Optional[str] = None
    ) -> User:
        """
        更新用户

        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱
            full_name: 全名
            role_id: 角色ID
            dept_id: 部门ID
            is_active: 是否激活
            password: 密码

        Returns:
            更新后的用户
        """
        user = self.get_user(user_id)

        if not user:
            raise BusinessException("用户不存在")

        # 更新字段
        if username and username != user.username:
            # 检查用户名是否已存在
            existing = self.db.exec(
                select(User).where(User.username == username)
            ).first()
            if existing:
                raise ValidationException("用户名已存在", field="username")
            user.username = username

        if email and email != user.email:
            # 检查邮箱是否已存在
            existing = self.db.exec(
                select(User).where(User.email == email)
            ).first()
            if existing:
                raise ValidationException("邮箱已被注册", field="email")
            user.email = email

        if full_name is not None:
            user.full_name = full_name

        if role_id is not None:
            user.role_id = role_id

        if dept_id is not None:
            user.dept_id = dept_id

        if is_active is not None:
            user.is_active = is_active

        if password:
            user.hashed_password = get_password_hash(password)

        self.db.commit()
        self.db.refresh(user)

        logger.info(f"用户更新成功: user_id={user_id}")
        return user

    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        dept_id: Optional[int] = None,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """
        获取用户列表

        Args:
            skip: 跳过数量
            limit: 返回数量
            keyword: 关键词
            dept_id: 部门ID
            role_id: 角色ID
            is_active: 是否激活

        Returns:
            包含用户列表和总数的字典
        """
        query = select(User)

        # 过滤条件
        if keyword:
            query = query.where(
                User.username.contains(keyword) |
                User.email.contains(keyword) |
                User.full_name.contains(keyword)
            )
        if dept_id:
            query = query.where(User.dept_id == dept_id)
        if role_id:
            query = query.where(User.role_id == role_id)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # 统计总数
        total = len(self.db.exec(query).all())

        # 分页查询
        users = self.db.exec(
            query.order_by(User.id.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        return {
            "items": users,
            "total": total
        }

    def delete_user(self, user_id: int) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        user = self.get_user(user_id)

        if not user:
            return False

        # 不能删除超级管理员
        if user.is_superuser:
            raise BusinessException("不能删除超级管理员")

        self.db.delete(user)
        self.db.commit()

        logger.info(f"用户删除成功: user_id={user_id}")
        return True

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码

        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            是否修改成功
        """
        user = self.get_user(user_id)

        if not user:
            raise BusinessException("用户不存在")

        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            raise ValidationException("旧密码错误", field="old_password")

        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()

        logger.info(f"密码修改成功: user_id={user_id}")
        return True

    def reset_password(
        self,
        user_id: int,
        new_password: str
    ) -> bool:
        """
        重置密码（管理员功能）

        Args:
            user_id: 用户ID
            new_password: 新密码

        Returns:
            是否重置成功
        """
        user = self.get_user(user_id)

        if not user:
            raise BusinessException("用户不存在")

        # 重置密码
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()

        logger.info(f"密码重置成功: user_id={user_id}")
        return True
