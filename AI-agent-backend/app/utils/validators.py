"""
数据验证工具
提供通用的数据验证功能
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, validator
from app.utils.exceptions import ValidationException


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        if not email or len(email) > 254:  # RFC 5321 限制
            return False

        # 检查基本格式
        if email.count('@') != 1:
            return False

        local, domain = email.split('@')

        # 检查本地部分
        if not local or len(local) > 64 or local.startswith('.') or local.endswith('.'):
            return False

        # 检查连续的点
        if '..' in local:
            return False

        # 检查域名部分
        if not domain or len(domain) > 253 or domain.startswith('.') or domain.endswith('.'):
            return False

        # 检查域名格式
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            return False

        # 检查本地部分格式
        local_pattern = r'^[a-zA-Z0-9._+-]+$'
        return bool(re.match(local_pattern, local))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return False
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """验证密码强度"""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["issues"].append("密码长度至少8位")
            result["valid"] = False
        else:
            result["score"] += 1
            
        if not re.search(r'[a-z]', password):
            result["issues"].append("密码需包含小写字母")
        else:
            result["score"] += 1
            
        if not re.search(r'[A-Z]', password):
            result["issues"].append("密码需包含大写字母")
        else:
            result["score"] += 1
            
        if not re.search(r'\d', password):
            result["issues"].append("密码需包含数字")
        else:
            result["score"] += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["issues"].append("密码需包含特殊字符")
        else:
            result["score"] += 1
            
        if result["issues"]:
            result["valid"] = False
            
        return result
    
    @staticmethod
    def validate_json_config(config: Dict[str, Any], required_fields: List[str] = None) -> bool:
        """验证JSON配置格式"""
        if not isinstance(config, dict):
            raise ValidationException("配置必须是有效的JSON对象")
            
        if required_fields:
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise ValidationException(f"缺少必需字段: {', '.join(missing_fields)}")
                
        return True
    
    @staticmethod
    def validate_agent_config(config: Dict[str, Any]) -> bool:
        """验证AI代理配置"""
        required_fields = ["model_name", "temperature", "max_tokens"]
        DataValidator.validate_json_config(config, required_fields)
        
        # 验证温度值
        temperature = config.get("temperature")
        if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
            raise ValidationException("temperature必须在0-2之间")
            
        # 验证最大令牌数
        max_tokens = config.get("max_tokens")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValidationException("max_tokens必须是正整数")
            
        return True
    
    @staticmethod
    def validate_test_case_steps(steps: List[Dict[str, Any]]) -> bool:
        """验证测试用例步骤"""
        if not isinstance(steps, list) or not steps:
            raise ValidationException("测试步骤不能为空")
            
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValidationException(f"第{i+1}步必须是对象格式")
                
            required_fields = ["action", "expected"]
            missing_fields = [field for field in required_fields if not step.get(field)]
            if missing_fields:
                raise ValidationException(f"第{i+1}步缺少字段: {', '.join(missing_fields)}")
                
        return True


class BusinessValidator:
    """业务逻辑验证器"""
    
    @staticmethod
    def validate_agent_name_uniqueness(name: str, existing_names: List[str]) -> bool:
        """验证代理名称唯一性"""
        if name in existing_names:
            raise ValidationException(f"代理名称 '{name}' 已存在")
        return True
    
    @staticmethod
    def validate_model_availability(model_id: int, available_models: List[int]) -> bool:
        """验证模型可用性"""
        if model_id not in available_models:
            raise ValidationException(f"模型 {model_id} 不可用或不存在")
        return True
    
    @staticmethod
    def validate_user_permissions(user_id: int, required_permissions: List[str], user_permissions: List[str]) -> bool:
        """验证用户权限"""
        missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
        if missing_permissions:
            raise ValidationException(f"用户缺少权限: {', '.join(missing_permissions)}")
        return True


# 导出验证器
__all__ = ["DataValidator", "BusinessValidator"]
