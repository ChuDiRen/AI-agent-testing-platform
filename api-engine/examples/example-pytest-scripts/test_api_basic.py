"""
API Engine 基础测试示例
演示如何使用原生 pytest 编写 API 测试
"""
import allure
import pytest


@allure.feature("用户管理")
@allure.story("用户登录")
def test_login_api(api_keywords):
    """测试登录接口"""
    with allure.step("发送登录请求"):
        api_keywords.send_request(
            关键字="send_request",
            method="POST",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/user/login", "application": "app"},
            data={
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
        )
    
    with allure.step("验证响应状态码"):
        # 通过 api_keywords.request 访问最后的 session 对象
        assert api_keywords.request is not None


@allure.feature("API测试")
@allure.story("基础请求")
def test_get_request(api_keywords):
    """测试 GET 请求"""
    with allure.step("发送 GET 请求"):
        api_keywords.send_request(
            关键字="send_request",
            method="GET",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/index/init"}
        )


@allure.feature("API测试")
@allure.story("POST请求")
def test_post_request(api_keywords):
    """测试 POST 请求"""
    with allure.step("发送 POST 请求"):
        api_keywords.send_request(
            关键字="send_request",
            method="POST",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/user/login"},
            json={
                "accounts": "testuser",
                "pwd": "testpass",
                "type": "username"
            }
        )


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_smoke_api(api_keywords):
    """冒烟测试 - 验证 API 基本可用性"""
    with allure.step("验证接口可访问"):
        api_keywords.send_request(
            关键字="send_request",
            method="GET",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/index/init"}
        )

