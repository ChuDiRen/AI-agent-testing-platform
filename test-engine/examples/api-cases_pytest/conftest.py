# -*- coding: utf-8 -*-
"""
@Time ： 2025/03/29
@Author ：楚地仁人
@File ：conftest.py
@IDE ：PyCharm
"""
import os

import pytest
import pytest_asyncio
from testengine_api.core.globalContext import g_context
from testengine_api.extend.keywords import Keywords
from testengine_api.utils.VarRender import refresh

# 共用常量
# 支持通过环境变量BASE_URL配置，默认为petstore
BASE_URL = os.getenv("BASE_URL", "https://petstore.swagger.io/v2")
# Shop-XO API地址（用于某些测试用例）
SHOP_XO_BASE_URL = "http://shop-xo.hctestedu.com"

# 共用工具类实例
keyWords = Keywords()


# 获取API基础URL的函数
def get_base_url():
    return BASE_URL


# Fixture: 提供基础URL
# 这个fixture会根据测试用例的需要返回合适的base_url
@pytest.fixture
def base_url(request):
    """
    提供基础URL的fixture
    
    根据测试模块名称返回不同的base_url：
    - 如果测试模块是 test_api_basic、test_api_advanced 或 test_DS，返回SHOP_XO_BASE_URL
    - 否则返回BASE_URL（默认petstore）
    """
    # 检查测试函数所在模块的名称
    module_name = request.module.__name__
    
    # 如果测试模块是shop-xo相关的，返回shop-xo的base_url
    if any(keyword in module_name for keyword in ['test_api_basic', 'test_api_advanced', 'test_DS']):
        return SHOP_XO_BASE_URL
    
    # 否则返回默认的petstore URL
    return BASE_URL


# Fixture: 用于模拟API响应（使用pytest-mock）
@pytest.fixture
def mock_response():
    """创建一个简单的mock响应对象"""
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self._json_data = {}
        
        def json(self):
            return self._json_data
    
    return MockResponse()


# Fixture: API客户端 (异步)
@pytest_asyncio.fixture(scope="function")
async def api_client():
    """提供httpx异步客户端"""
    import httpx
    async with httpx.AsyncClient() as client:
        yield client




# Fixture: 创建一个新宠物并返回其ID
@pytest_asyncio.fixture(scope="function")
async def pet_id():
    """
    创建一个新宠物并返回其ID
    根据 Swagger 规范，使用完整的 Pet 对象结构
    """
    import random
    # 使用随机ID避免测试之间的冲突
    pet_id_value = random.randint(10000, 99999)
    
    url = f"{BASE_URL}/pet"
    payload = {
        "id": pet_id_value,
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
    response = await keyWords.request_post_row(url=url, json=payload)
    assert response.status_code == 200, f"创建宠物失败: {response.status_code}"
    
    # 验证创建结果
    result = response.json()
    assert result.get('id') == pet_id_value, f"返回的宠物ID应该匹配: {pet_id_value}"
    
    return result['id']


# 辅助函数：处理请求数据中的变量
def process_request_data(request_data):
    """
    处理请求数据，替换其中的变量
    
    Args:
        request_data: 请求数据字典
        
    Returns:
        处理后的请求数据
    """
    return eval(refresh(request_data, g_context().show_dict()))
