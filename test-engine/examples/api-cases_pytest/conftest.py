# -*- coding: utf-8 -*-
"""
@Time ： 2025/03/29
@Author ：楚地仁人
@File ：conftest.py
@IDE ：PyCharm
"""
import pytest
from unittest.mock import Mock

from apirun.core.globalContext import g_context
from apirun.extend.KeyWords import KeyWords
from apirun.utils.VarRender import refresh

# 共用常量
BASE_URL = "https://petstore.swagger.io/v2"

# 共用工具类实例
keyWords = KeyWords()


# 获取API基础URL的函数
def get_base_url():
    return BASE_URL


# Fixture: 提供基础URL
@pytest.fixture(scope="module")
def base_url():
    return get_base_url()


# Fixture: 用于模拟API响应
@pytest.fixture
def mock_response():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {}
    return response


# Fixture: 创建一个新宠物并返回其ID
@pytest.fixture
def pet_id():
    url = f"{BASE_URL}/pet"
    payload = {
        "id": 1,
        "name": "Fluffy",
        "category": {
            "id": 1,
            "name": "Dogs"
        },
        "photoUrls": [
            "http://example.com/fluffy.jpg"
        ],
        "tags": [
            {
                "id": 1,
                "name": "cute"
            }
        ],
        "status": "available"
    }
    response = keyWords.request_post_row(url=url, json=payload)
    assert response.status_code == 200
    return response.json()['id']


# 辅助函数：处理请求数据中的变量
def process_request_data(request_data):
    """
    处理请求数据，替换其中的变量
    
    Args:
        request_data: 请求数据字典
        
    Returns:
        处理后的请求数据
    """
    return eval(refresh(request_data, g_context.show_dict()))
