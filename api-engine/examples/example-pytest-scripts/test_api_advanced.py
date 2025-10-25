"""
API Engine 高级测试示例
演示 pytest 高级特性：参数化、测试类、fixture 等
"""
import allure
import pytest


# ==================== 测试类 ====================
class TestUserAPI:
    """用户 API 测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_keywords):
        """每个测试前的准备"""
        self.keywords = api_keywords
        self.base_url = "http://shop-xo.hctestedu.com"
        self.api_path = "/index.php"
        yield
        # teardown 代码
    
    @allure.story("用户登录")
    def test_user_login(self):
        """测试用户登录"""
        with allure.step("发送登录请求"):
            self.keywords.send_request(
                关键字="send_request",
                method="POST",
                url=f"{self.base_url}{self.api_path}",
                params={"s": "/api/user/login", "application": "app"},
                data={
                    "accounts": "hami",
                    "pwd": "123456",
                    "type": "username"
                }
            )
    
    @allure.story("用户信息")
    def test_get_user_info(self):
        """测试获取用户信息"""
        with allure.step("获取用户信息"):
            self.keywords.send_request(
                关键字="send_request",
                method="GET",
                url=f"{self.base_url}{self.api_path}",
                params={"s": "/api/user/center"}
            )


# ==================== 参数化测试 ====================
@pytest.mark.parametrize("username,password", [
    ("hami", "123456"),
    ("testuser1", "testpass1"),
    ("testuser2", "testpass2"),
])
@allure.feature("参数化测试")
@allure.story("登录数据驱动")
def test_login_ddt(api_keywords, username, password):
    """数据驱动登录测试"""
    with allure.step(f"测试用户 {username} 登录"):
        api_keywords.send_request(
            关键字="send_request",
            method="POST",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/user/login", "application": "app"},
            data={
                "accounts": username,
                "pwd": password,
                "type": "username"
            }
        )


@pytest.mark.parametrize("api_path,method", [
    ("/api/index/init", "GET"),
    ("/api/goods/index", "GET"),
    ("/api/user/center", "GET"),
])
@allure.feature("参数化测试")
@allure.story("多接口测试")
def test_multiple_apis(api_keywords, api_path, method):
    """测试多个 API 接口"""
    with allure.step(f"测试接口: {api_path}"):
        api_keywords.send_request(
            关键字="send_request",
            method=method,
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": api_path}
        )


# ==================== Fixture 示例 ====================
@pytest.fixture
def login_token(api_keywords):
    """登录并获取 token"""
    with allure.step("执行登录获取 token"):
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
        # 这里可以提取 token
        token = "mock_token_12345"
        yield token


@allure.feature("授权测试")
@allure.story("需要登录的接口")
def test_api_with_auth(api_keywords, login_token):
    """测试需要认证的接口"""
    with allure.step("使用 token 访问受保护接口"):
        api_keywords.send_request(
            关键字="send_request",
            method="GET",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/user/center"},
            headers={"Authorization": f"Bearer {login_token}"}
        )


# ==================== 标记示例 ====================
@pytest.mark.smoke
@allure.severity(allure.severity_level.BLOCKER)
def test_critical_api(api_keywords):
    """关键接口测试"""
    with allure.step("测试关键业务接口"):
        api_keywords.send_request(
            关键字="send_request",
            method="GET",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/index/init"}
        )


@pytest.mark.regression
@allure.severity(allure.severity_level.NORMAL)
def test_regression_api(api_keywords):
    """回归测试"""
    with allure.step("执行回归测试"):
        api_keywords.send_request(
            关键字="send_request",
            method="GET",
            url="http://shop-xo.hctestedu.com/index.php",
            params={"s": "/api/goods/index"}
        )


# ==================== 跳过测试示例 ====================
@pytest.mark.skip(reason="此接口暂未实现")
def test_not_implemented(api_keywords):
    """尚未实现的测试"""
    pass


@pytest.mark.skipif(True, reason="条件跳过示例")
def test_conditional_skip(api_keywords):
    """条件跳过的测试"""
    pass


# ==================== 预期失败示例 ====================
@pytest.mark.xfail(reason="已知缺陷")
def test_known_issue(api_keywords):
    """已知问题的测试"""
    api_keywords.send_request(
        关键字="send_request",
        method="GET",
        url="http://shop-xo.hctestedu.com/api/broken"
    )

