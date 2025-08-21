"""
测试基类
提供通用的测试功能和工具
"""

import pytest
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class BaseTestCase:
    """
    测试基类
    提供通用的测试方法和断言
    """
    
    def assert_response_success(self, response, expected_status: int = 200):
        """
        断言响应成功
        
        Args:
            response: HTTP响应
            expected_status: 期望的状态码
        """
        assert response.status_code == expected_status
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert data.get("success") is True
    
    def assert_response_error(self, response, expected_status: int = 400):
        """
        断言响应错误
        
        Args:
            response: HTTP响应
            expected_status: 期望的状态码
        """
        assert response.status_code == expected_status
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert data.get("success") is False
    
    def assert_validation_error(self, response):
        """
        断言验证错误
        
        Args:
            response: HTTP响应
        """
        self.assert_response_error(response, 422)
    
    def assert_authentication_error(self, response):
        """
        断言认证错误
        
        Args:
            response: HTTP响应
        """
        self.assert_response_error(response, 401)
    
    def assert_authorization_error(self, response):
        """
        断言授权错误
        
        Args:
            response: HTTP响应
        """
        self.assert_response_error(response, 403)
    
    def assert_not_found_error(self, response):
        """
        断言资源不存在错误
        
        Args:
            response: HTTP响应
        """
        self.assert_response_error(response, 404)
    
    def assert_response_data(self, response, expected_data: Dict[str, Any]):
        """
        断言响应数据
        
        Args:
            response: HTTP响应
            expected_data: 期望的数据
        """
        self.assert_response_success(response)
        
        data = response.json()
        response_data = data.get("data", {})
        
        for key, value in expected_data.items():
            assert key in response_data
            assert response_data[key] == value
    
    def assert_response_contains(self, response, *keys):
        """
        断言响应包含指定键
        
        Args:
            response: HTTP响应
            *keys: 期望包含的键
        """
        self.assert_response_success(response)
        
        data = response.json()
        response_data = data.get("data", {})
        
        for key in keys:
            assert key in response_data
    
    def assert_pagination_response(self, response, expected_total: Optional[int] = None):
        """
        断言分页响应
        
        Args:
            response: HTTP响应
            expected_total: 期望的总数
        """
        self.assert_response_success(response)
        
        data = response.json()
        response_data = data.get("data", {})
        
        # 检查分页结构
        assert "items" in response_data
        assert "pagination" in response_data
        
        pagination = response_data["pagination"]
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination
        
        if expected_total is not None:
            assert pagination["total"] == expected_total
    
    def create_test_request_data(self, base_data: Dict[str, Any], 
                                overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建测试请求数据
        
        Args:
            base_data: 基础数据
            overrides: 覆盖数据
            
        Returns:
            测试请求数据
        """
        data = base_data.copy()
        if overrides:
            data.update(overrides)
        return data
    
    def make_authenticated_request(self, client: TestClient, method: str, url: str,
                                  auth_headers: Dict[str, str], **kwargs):
        """
        发送认证请求
        
        Args:
            client: 测试客户端
            method: HTTP方法
            url: 请求URL
            auth_headers: 认证头
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应
        """
        headers = kwargs.pop("headers", {})
        headers.update(auth_headers)
        
        return client.request(method, url, headers=headers, **kwargs)
    
    def assert_entity_created(self, db: Session, entity_class, **filters):
        """
        断言实体已创建
        
        Args:
            db: 数据库会话
            entity_class: 实体类
            **filters: 过滤条件
        """
        entity = db.query(entity_class).filter_by(**filters).first()
        assert entity is not None
        return entity
    
    def assert_entity_not_exists(self, db: Session, entity_class, **filters):
        """
        断言实体不存在
        
        Args:
            db: 数据库会话
            entity_class: 实体类
            **filters: 过滤条件
        """
        entity = db.query(entity_class).filter_by(**filters).first()
        assert entity is None
    
    def assert_entity_count(self, db: Session, entity_class, expected_count: int, **filters):
        """
        断言实体数量
        
        Args:
            db: 数据库会话
            entity_class: 实体类
            expected_count: 期望数量
            **filters: 过滤条件
        """
        count = db.query(entity_class).filter_by(**filters).count()
        assert count == expected_count
    
    def create_test_entity(self, db: Session, entity_class, **data):
        """
        创建测试实体
        
        Args:
            db: 数据库会话
            entity_class: 实体类
            **data: 实体数据
            
        Returns:
            创建的实体
        """
        entity = entity_class(**data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    def cleanup_test_data(self, db: Session, entity_class, **filters):
        """
        清理测试数据
        
        Args:
            db: 数据库会话
            entity_class: 实体类
            **filters: 过滤条件
        """
        entities = db.query(entity_class).filter_by(**filters).all()
        for entity in entities:
            db.delete(entity)
        db.commit()


class AsyncTestCase(BaseTestCase):
    """
    异步测试基类
    """
    
    @pytest.mark.asyncio
    async def async_assert_response_success(self, response, expected_status: int = 200):
        """
        异步断言响应成功
        """
        self.assert_response_success(response, expected_status)
    
    @pytest.mark.asyncio
    async def async_assert_response_error(self, response, expected_status: int = 400):
        """
        异步断言响应错误
        """
        self.assert_response_error(response, expected_status)


class MockTestCase(BaseTestCase):
    """
    模拟测试基类
    提供模拟对象的创建和管理
    """
    
    def create_mock_user(self, **overrides):
        """
        创建模拟用户
        
        Args:
            **overrides: 覆盖属性
            
        Returns:
            模拟用户对象
        """
        from unittest.mock import Mock
        
        default_attrs = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_verified": True,
            "is_superuser": False
        }
        
        default_attrs.update(overrides)
        
        mock_user = Mock()
        for attr, value in default_attrs.items():
            setattr(mock_user, attr, value)
        
        return mock_user
    
    def create_mock_repository(self, entity_class):
        """
        创建模拟Repository
        
        Args:
            entity_class: 实体类
            
        Returns:
            模拟Repository对象
        """
        from unittest.mock import Mock
        
        mock_repo = Mock()
        mock_repo.model = entity_class
        
        return mock_repo
    
    def create_mock_service(self, repository):
        """
        创建模拟Service
        
        Args:
            repository: Repository对象
            
        Returns:
            模拟Service对象
        """
        from unittest.mock import Mock
        
        mock_service = Mock()
        mock_service.repository = repository
        
        return mock_service


# 导出测试基类
__all__ = ["BaseTestCase", "AsyncTestCase", "MockTestCase"]
