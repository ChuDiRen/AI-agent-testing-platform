# Copyright (c) 2025 左岚. All rights reserved.
"""
安全相关功能测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)
from app.core.config import settings


class TestSecurity:
    """安全功能测试类"""
    
    def test_password_hashing(self):
        """测试密码哈希"""
        password = "testpassword123"
        
        # 测试密码哈希
        hashed = get_password_hash(password)
        
        # 验证哈希不为空且不等于原密码
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # bcrypt哈希长度通常很长
        
        # 测试密码验证
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_access_token_creation_and_verification(self):
        """测试访问令牌创建和验证"""
        data = {"sub": "123", "username": "testuser"}
        
        # 创建令牌
        token = create_access_token(data)
        
        # 验证令牌不为空
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 10
        
        # 验证令牌
        payload = verify_token(token)
        
        # 检查载荷
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_refresh_token_creation_and_verification(self):
        """测试刷新令牌创建和验证"""
        data = {"sub": "123", "username": "testuser"}
        
        # 创建刷新令牌
        token = create_refresh_token(data)
        
        # 验证令牌不为空
        assert token is not None
        assert isinstance(token, str)
        
        # 验证令牌
        payload = verify_token(token)
        
        # 检查载荷
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_token_expiration(self):
        """测试令牌过期"""
        data = {"sub": "123"}
        
        # 创建过期的令牌（负数分钟）
        with patch.object(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            token = create_access_token(data)
            
            # 验证过期令牌应该失败
            with pytest.raises(Exception):  # JWT过期会抛出异常
                verify_token(token)
    
    def test_invalid_token(self):
        """测试无效令牌"""
        # 测试空令牌
        with pytest.raises(Exception):
            verify_token("")
        
        # 测试无效格式令牌
        with pytest.raises(Exception):
            verify_token("invalid.token.format")
        
        # 测试伪造令牌
        with pytest.raises(Exception):
            verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature")
    
    def test_token_with_custom_expiry(self):
        """测试自定义过期时间的令牌"""
        data = {"sub": "123"}
        expires_delta = timedelta(hours=1)
        
        # 创建自定义过期时间的令牌
        token = create_access_token(data, expires_delta=expires_delta)
        
        # 验证令牌
        payload = verify_token(token)
        
        # 检查过期时间
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + expires_delta
        
        # 允许几秒的误差
        assert abs((exp_datetime - expected_exp).total_seconds()) < 5
    
    def test_token_payload_integrity(self):
        """测试令牌载荷完整性"""
        data = {
            "sub": "123",
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["user", "admin"],
            "permissions": ["read", "write"]
        }
        
        # 创建令牌
        token = create_access_token(data)
        
        # 验证令牌
        payload = verify_token(token)
        
        # 检查所有数据都正确保存
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert payload["roles"] == ["user", "admin"]
        assert payload["permissions"] == ["read", "write"]
    
    def test_password_hash_uniqueness(self):
        """测试密码哈希的唯一性"""
        password = "samepassword"
        
        # 同一密码多次哈希应该产生不同结果（因为盐值）
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        
        # 但都应该能验证原密码
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_empty_password_handling(self):
        """测试空密码处理"""
        # 空密码应该能被哈希
        empty_hash = get_password_hash("")
        assert empty_hash is not None
        assert verify_password("", empty_hash) is True
        
        # 空字符串不应该匹配非空密码哈希
        normal_hash = get_password_hash("normalpassword")
        assert verify_password("", normal_hash) is False
    
    def test_long_password_handling(self):
        """测试长密码处理"""
        # 测试很长的密码
        long_password = "a" * 1000
        long_hash = get_password_hash(long_password)
        
        assert long_hash is not None
        assert verify_password(long_password, long_hash) is True
        assert verify_password(long_password[:-1], long_hash) is False
    
    def test_special_characters_in_password(self):
        """测试密码中的特殊字符"""
        special_password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
        special_hash = get_password_hash(special_password)
        
        assert special_hash is not None
        assert verify_password(special_password, special_hash) is True
    
    def test_unicode_password_handling(self):
        """测试Unicode密码处理"""
        unicode_password = "密码123🔒"
        unicode_hash = get_password_hash(unicode_password)
        
        assert unicode_hash is not None
        assert verify_password(unicode_password, unicode_hash) is True
        assert verify_password("密码123", unicode_hash) is False
