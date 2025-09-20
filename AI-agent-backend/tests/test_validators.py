# Copyright (c) 2025 左岚. All rights reserved.
"""
验证器测试
"""

import pytest
from app.utils.validators import DataValidator, BusinessValidator
from app.utils.exceptions import ValidationException


class TestDataValidator:
    """数据验证器测试"""
    
    def test_validate_email_valid(self):
        """测试有效邮箱验证"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            assert DataValidator.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """测试无效邮箱验证"""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in invalid_emails:
            assert DataValidator.validate_email(email) is False
    
    def test_validate_phone_valid(self):
        """测试有效手机号验证"""
        valid_phones = [
            "13812345678",
            "15987654321",
            "18612345678"
        ]
        
        for phone in valid_phones:
            assert DataValidator.validate_phone(phone) is True
    
    def test_validate_phone_invalid(self):
        """测试无效手机号验证"""
        invalid_phones = [
            "",
            "12345678901",  # 不是1开头
            "1381234567",   # 长度不够
            "138123456789", # 长度过长
            "10812345678"   # 第二位不是3-9
        ]
        
        for phone in invalid_phones:
            assert DataValidator.validate_phone(phone) is False
    
    def test_validate_password_strength_strong(self):
        """测试强密码验证"""
        strong_password = "StrongP@ssw0rd123"
        result = DataValidator.validate_password_strength(strong_password)
        
        assert result["valid"] is True
        assert result["score"] == 5
        assert len(result["issues"]) == 0
    
    def test_validate_password_strength_weak(self):
        """测试弱密码验证"""
        weak_password = "123"
        result = DataValidator.validate_password_strength(weak_password)
        
        assert result["valid"] is False
        assert result["score"] < 5
        assert len(result["issues"]) > 0
    
    def test_validate_json_config_valid(self):
        """测试有效JSON配置验证"""
        config = {
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        required_fields = ["model_name", "temperature"]
        
        assert DataValidator.validate_json_config(config, required_fields) is True
    
    def test_validate_json_config_missing_fields(self):
        """测试缺少字段的JSON配置验证"""
        config = {
            "model_name": "gpt-4"
        }
        required_fields = ["model_name", "temperature", "max_tokens"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_json_config(config, required_fields)
        
        assert "缺少必需字段" in str(exc_info.value)
    
    def test_validate_agent_config_valid(self):
        """测试有效代理配置验证"""
        config = {
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        assert DataValidator.validate_agent_config(config) is True
    
    def test_validate_agent_config_invalid_temperature(self):
        """测试无效温度的代理配置验证"""
        config = {
            "model_name": "gpt-4",
            "temperature": 3.0,  # 超出范围
            "max_tokens": 1000
        }
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_agent_config(config)
        
        assert "temperature必须在0-2之间" in str(exc_info.value)
    
    def test_validate_test_case_steps_valid(self):
        """测试有效测试步骤验证"""
        steps = [
            {
                "action": "点击登录按钮",
                "expected": "跳转到登录页面"
            },
            {
                "action": "输入用户名和密码",
                "expected": "显示登录成功消息"
            }
        ]
        
        assert DataValidator.validate_test_case_steps(steps) is True
    
    def test_validate_test_case_steps_empty(self):
        """测试空测试步骤验证"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_test_case_steps([])
        
        assert "测试步骤不能为空" in str(exc_info.value)
    
    def test_validate_test_case_steps_missing_fields(self):
        """测试缺少字段的测试步骤验证"""
        steps = [
            {
                "action": "点击登录按钮"
                # 缺少expected字段
            }
        ]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_test_case_steps(steps)
        
        assert "缺少字段" in str(exc_info.value)


class TestBusinessValidator:
    """业务验证器测试"""
    
    def test_validate_agent_name_uniqueness_valid(self):
        """测试代理名称唯一性验证 - 有效"""
        name = "新代理"
        existing_names = ["代理1", "代理2", "代理3"]
        
        assert BusinessValidator.validate_agent_name_uniqueness(name, existing_names) is True
    
    def test_validate_agent_name_uniqueness_duplicate(self):
        """测试代理名称唯一性验证 - 重复"""
        name = "代理1"
        existing_names = ["代理1", "代理2", "代理3"]
        
        with pytest.raises(ValidationException) as exc_info:
            BusinessValidator.validate_agent_name_uniqueness(name, existing_names)
        
        assert "已存在" in str(exc_info.value)
    
    def test_validate_model_availability_valid(self):
        """测试模型可用性验证 - 有效"""
        model_id = 1
        available_models = [1, 2, 3, 4]
        
        assert BusinessValidator.validate_model_availability(model_id, available_models) is True
    
    def test_validate_model_availability_invalid(self):
        """测试模型可用性验证 - 无效"""
        model_id = 5
        available_models = [1, 2, 3, 4]
        
        with pytest.raises(ValidationException) as exc_info:
            BusinessValidator.validate_model_availability(model_id, available_models)
        
        assert "不可用或不存在" in str(exc_info.value)
    
    def test_validate_user_permissions_valid(self):
        """测试用户权限验证 - 有效"""
        user_id = 1
        required_permissions = ["read", "write"]
        user_permissions = ["read", "write", "delete"]
        
        assert BusinessValidator.validate_user_permissions(
            user_id, required_permissions, user_permissions
        ) is True
    
    def test_validate_user_permissions_insufficient(self):
        """测试用户权限验证 - 权限不足"""
        user_id = 1
        required_permissions = ["read", "write", "delete"]
        user_permissions = ["read", "write"]
        
        with pytest.raises(ValidationException) as exc_info:
            BusinessValidator.validate_user_permissions(
                user_id, required_permissions, user_permissions
            )
        
        assert "缺少权限" in str(exc_info.value)
