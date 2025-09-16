# Copyright (c) 2025 左岚. All rights reserved.
"""
测试配置文件
"""

import pytest
import sys
import os
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    # 使用内存SQLite数据库进行测试
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    # 清理
    session.rollback()
    session.close()


@pytest.fixture
def mock_user():
    """模拟用户信息"""
    return {
        "user_id": 1,
        "username": "test_user",
        "email": "test@example.com"
    }