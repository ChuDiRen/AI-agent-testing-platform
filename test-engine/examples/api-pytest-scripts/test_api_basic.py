"""
API 基础测试示例
演示基本的 API 测试用例编写方法
"""
import allure
import pytest
import requests


@allure.feature("用户管理")
@allure.story("用户登录")
class TestUserLogin:
    """用户登录相关测试"""
    
    @allure.title("测试用户名密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_login_success(self, base_url: str):
        """
        测试用例：用户名密码登录成功
        
        步骤：
        1. 发送登录请求
        2. 验证响应状态码
        3. 验证响应数据
        """
        with allure.step("准备登录数据"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            allure.attach(str(login_data), "请求数据", allure.attachment_type.JSON)
        
        with allure.step("发送登录请求"):
            response = requests.post(login_url, json=login_data)
            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"状态码错误: {response.status_code}"
        
        with allure.step("验证响应数据"):
            result = response.json()
            assert result.get("code") == 0, f"返回码错误: {result.get('msg')}"
            assert "data" in result, "响应中缺少 data 字段"
            assert result["data"].get("token"), "Token 不能为空"
    
    @allure.title("测试用户名密码登录失败-密码错误")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, base_url: str):
        """
        测试用例：密码错误登录失败
        """
        with allure.step("准备错误的登录数据"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "wrong_password",
                "type": "username"
            }
        
        with allure.step("发送登录请求"):
            response = requests.post(login_url, json=login_data)
        
        with allure.step("验证登录失败"):
            assert response.status_code == 200
            result = response.json()
            assert result.get("code") != 0, "应该返回错误码"
    
    @allure.title("测试参数缺失登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("missing_field", ["accounts", "pwd", "type"])
    def test_login_missing_params(self, base_url: str, missing_field: str):
        """
        测试用例：参数缺失登录失败
        使用参数化测试多个场景
        """
        with allure.step(f"准备缺少 {missing_field} 的登录数据"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            # 删除指定字段
            del login_data[missing_field]
            allure.attach(str(login_data), "请求数据", allure.attachment_type.JSON)
        
        with allure.step("发送登录请求"):
            response = requests.post(login_url, json=login_data)
            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)
        
        with allure.step("验证登录失败"):
            # 应该返回 4xx 或者业务错误码
            result = response.json()
            assert result.get("code") != 0, "缺少必填参数应该登录失败"


@allure.feature("商品管理")
@allure.story("商品查询")
class TestProductQuery:
    """商品查询相关测试"""
    
    @allure.title("测试商品列表查询")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_list(self, api_client):
        """
        测试用例：查询商品列表
        使用 api_client fixture
        """
        with allure.step("查询商品列表"):
            response = api_client.get("/index.php?s=/api/goods/index")
            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)
        
        with allure.step("验证响应"):
            assert response.status_code == 200
            result = response.json()
            assert result.get("code") == 0, f"查询失败: {result.get('msg')}"
            assert "data" in result, "响应中缺少 data 字段"
    
    @allure.title("测试商品详情查询")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_detail(self, api_client):
        """
        测试用例：查询商品详情
        """
        with allure.step("准备商品ID"):
            goods_id = 1
            allure.attach(str(goods_id), "商品ID", allure.attachment_type.TEXT)
        
        with allure.step("查询商品详情"):
            response = api_client.get(
                "/index.php?s=/api/goods/detail",
                params={"id": goods_id}
            )
            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)
        
        with allure.step("验证响应"):
            assert response.status_code == 200
            result = response.json()
            assert result.get("code") == 0, f"查询失败: {result.get('msg')}"
            
            # 验证返回的商品ID
            if "data" in result and result["data"]:
                assert result["data"].get("id") == goods_id, "返回的商品ID不匹配"


@allure.feature("数据驱动测试")
@allure.story("参数化测试示例")
class TestDataDriven:
    """数据驱动测试示例"""
    
    @allure.title("测试多用户登录-{username}")
    @pytest.mark.parametrize("username,password,expected", [
        ("hami", "123456", True),
        ("testuser1", "wrong_pwd", False),
        ("", "123456", False),
        ("hami", "", False),
    ])
    def test_login_with_multiple_users(
        self, 
        base_url: str, 
        username: str, 
        password: str, 
        expected: bool
    ):
        """
        数据驱动测试：测试多个用户登录场景
        
        :param username: 用户名
        :param password: 密码
        :param expected: 预期是否成功
        """
        with allure.step(f"使用用户名 {username} 登录"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": username,
                "pwd": password,
                "type": "username"
            }
            
            response = requests.post(login_url, json=login_data)
            result = response.json()
            
            allure.attach(str(login_data), "请求数据", allure.attachment_type.JSON)
            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)
        
        with allure.step("验证登录结果"):
            if expected:
                assert result.get("code") == 0, f"预期登录成功，但失败了: {result.get('msg')}"
            else:
                assert result.get("code") != 0, f"预期登录失败，但成功了"

