# Copyright (c) 2025 左岚. All rights reserved.
"""
用户服务测试
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.service.user_service import UserService
from app.repository.user_repository import UserRepository
from app.entity.user import User
from app.dto.user_dto import UserCreateDTO, UserUpdateDTO
from app.core.security import get_password_hash, verify_password
from app.utils.exceptions import ValidationError, NotFoundError


class TestUserService:
    """用户服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_user_repo(self):
        """模拟用户仓库"""
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def user_service(self, mock_db, mock_user_repo):
        """用户服务实例"""
        service = UserService(mock_db)
        service.user_repo = mock_user_repo
        return service
    
    @pytest.fixture
    def sample_user(self):
        """示例用户"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False
        )
    
    @pytest.fixture
    def user_create_dto(self):
        """用户创建DTO"""
        return UserCreateDTO(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            real_name="New User"
        )
    
    def test_create_user_success(self, user_service, mock_user_repo, user_create_dto):
        """测试成功创建用户"""
        # 准备
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None
        
        created_user = User(
            id=1,
            username=user_create_dto.username,
            email=user_create_dto.email,
            hashed_password=get_password_hash(user_create_dto.password),
            is_active=True
        )
        mock_user_repo.create.return_value = created_user
        
        # 执行
        result = user_service.create_user(user_create_dto)
        
        # 验证
        assert result.username == user_create_dto.username
        assert result.email == user_create_dto.email
        assert result.is_active is True
        mock_user_repo.create.assert_called_once()
    
    def test_create_user_username_exists(self, user_service, mock_user_repo, user_create_dto, sample_user):
        """测试用户名已存在的情况"""
        # 准备
        mock_user_repo.get_by_username.return_value = sample_user
        
        # 执行和验证
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(user_create_dto)
        
        assert "用户名已存在" in str(exc_info.value)
        mock_user_repo.create.assert_not_called()
    
    def test_create_user_email_exists(self, user_service, mock_user_repo, user_create_dto, sample_user):
        """测试邮箱已存在的情况"""
        # 准备
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = sample_user
        
        # 执行和验证
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(user_create_dto)
        
        assert "邮箱已存在" in str(exc_info.value)
        mock_user_repo.create.assert_not_called()
    
    def test_get_user_by_id_success(self, user_service, mock_user_repo, sample_user):
        """测试通过ID获取用户成功"""
        # 准备
        mock_user_repo.get_by_id.return_value = sample_user
        
        # 执行
        result = user_service.get_user_by_id(1)
        
        # 验证
        assert result == sample_user
        mock_user_repo.get_by_id.assert_called_once_with(1)
    
    def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        """测试用户不存在的情况"""
        # 准备
        mock_user_repo.get_by_id.return_value = None
        
        # 执行和验证
        with pytest.raises(NotFoundError) as exc_info:
            user_service.get_user_by_id(999)
        
        assert "用户不存在" in str(exc_info.value)
    
    def test_update_user_success(self, user_service, mock_user_repo, sample_user):
        """测试更新用户成功"""
        # 准备
        update_dto = UserUpdateDTO(
            real_name="Updated Name",
            email="updated@example.com"
        )
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.update.return_value = sample_user
        
        # 执行
        result = user_service.update_user(1, update_dto)
        
        # 验证
        assert result == sample_user
        mock_user_repo.update.assert_called_once()
    
    def test_update_user_email_conflict(self, user_service, mock_user_repo, sample_user):
        """测试更新用户邮箱冲突"""
        # 准备
        update_dto = UserUpdateDTO(email="conflict@example.com")
        other_user = User(id=2, username="other", email="conflict@example.com")
        
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.get_by_email.return_value = other_user
        
        # 执行和验证
        with pytest.raises(ValidationError) as exc_info:
            user_service.update_user(1, update_dto)
        
        assert "邮箱已被其他用户使用" in str(exc_info.value)
    
    def test_delete_user_success(self, user_service, mock_user_repo, sample_user):
        """测试删除用户成功"""
        # 准备
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.delete.return_value = True
        
        # 执行
        result = user_service.delete_user(1)
        
        # 验证
        assert result is True
        mock_user_repo.delete.assert_called_once_with(1)
    
    def test_authenticate_user_success(self, user_service, mock_user_repo, sample_user):
        """测试用户认证成功"""
        # 准备
        mock_user_repo.get_by_username.return_value = sample_user
        
        # 执行
        with patch('app.service.user_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            result = user_service.authenticate_user("testuser", "password123")
        
        # 验证
        assert result == sample_user
        mock_verify.assert_called_once_with("password123", sample_user.hashed_password)
    
    def test_authenticate_user_wrong_password(self, user_service, mock_user_repo, sample_user):
        """测试密码错误"""
        # 准备
        mock_user_repo.get_by_username.return_value = sample_user
        
        # 执行
        with patch('app.service.user_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            result = user_service.authenticate_user("testuser", "wrongpassword")
        
        # 验证
        assert result is None
    
    def test_authenticate_user_not_found(self, user_service, mock_user_repo):
        """测试用户不存在"""
        # 准备
        mock_user_repo.get_by_username.return_value = None
        
        # 执行
        result = user_service.authenticate_user("nonexistent", "password")
        
        # 验证
        assert result is None
    
    def test_change_password_success(self, user_service, mock_user_repo, sample_user):
        """测试修改密码成功"""
        # 准备
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.update.return_value = sample_user
        
        # 执行
        with patch('app.service.user_service.verify_password') as mock_verify, \
             patch('app.service.user_service.get_password_hash') as mock_hash:
            mock_verify.return_value = True
            mock_hash.return_value = "new_hashed_password"
            
            result = user_service.change_password(1, "password123", "newpassword")
        
        # 验证
        assert result is True
        mock_hash.assert_called_once_with("newpassword")
        mock_user_repo.update.assert_called_once()
    
    def test_change_password_wrong_old_password(self, user_service, mock_user_repo, sample_user):
        """测试旧密码错误"""
        # 准备
        mock_user_repo.get_by_id.return_value = sample_user
        
        # 执行
        with patch('app.service.user_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            with pytest.raises(ValidationError) as exc_info:
                user_service.change_password(1, "wrongpassword", "newpassword")
        
        # 验证
        assert "当前密码错误" in str(exc_info.value)
        mock_user_repo.update.assert_not_called()
    
    def test_get_users_with_pagination(self, user_service, mock_user_repo):
        """测试分页获取用户列表"""
        # 准备
        users = [User(id=i, username=f"user{i}") for i in range(1, 6)]
        mock_user_repo.get_list.return_value = (users, 5)
        
        # 执行
        result, total = user_service.get_users(page=1, page_size=10)
        
        # 验证
        assert len(result) == 5
        assert total == 5
        mock_user_repo.get_list.assert_called_once_with(
            skip=0, limit=10, filters=None, order_by=None
        )
    
    def test_search_users(self, user_service, mock_user_repo):
        """测试搜索用户"""
        # 准备
        users = [User(id=1, username="testuser", email="test@example.com")]
        mock_user_repo.search.return_value = (users, 1)
        
        # 执行
        result, total = user_service.search_users("test", page=1, page_size=10)
        
        # 验证
        assert len(result) == 1
        assert total == 1
        assert result[0].username == "testuser"
        mock_user_repo.search.assert_called_once()
    
    def test_activate_user(self, user_service, mock_user_repo, sample_user):
        """测试激活用户"""
        # 准备
        sample_user.is_active = False
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.update.return_value = sample_user
        
        # 执行
        result = user_service.activate_user(1)
        
        # 验证
        assert result.is_active is True
        mock_user_repo.update.assert_called_once()
    
    def test_deactivate_user(self, user_service, mock_user_repo, sample_user):
        """测试禁用用户"""
        # 准备
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.update.return_value = sample_user
        
        # 执行
        result = user_service.deactivate_user(1)
        
        # 验证
        assert result.is_active is False
        mock_user_repo.update.assert_called_once()
    
    def test_get_user_statistics(self, user_service, mock_user_repo):
        """测试获取用户统计信息"""
        # 准备
        mock_user_repo.get_statistics.return_value = {
            "total_users": 100,
            "active_users": 80,
            "inactive_users": 20,
            "new_users_today": 5
        }
        
        # 执行
        result = user_service.get_user_statistics()
        
        # 验证
        assert result["total_users"] == 100
        assert result["active_users"] == 80
        assert result["inactive_users"] == 20
        assert result["new_users_today"] == 5
        mock_user_repo.get_statistics.assert_called_once()
