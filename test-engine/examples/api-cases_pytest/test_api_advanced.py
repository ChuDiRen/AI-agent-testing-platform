"""
API 高级测试示例
演示高级测试技巧和最佳实践
"""
import json
from typing import Dict, Any

import allure
import pytest
import requests


@allure.feature("接口关联测试")
@allure.story("数据依赖场景")
class TestAPIChaining:
    """演示接口之间的数据关联"""
    
    @allure.title("测试登录后查询用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_and_get_user_info(self, base_url: str, api_session: requests.Session):
        """
        测试场景：登录后使用 token 查询用户信息
        演示接口间的数据传递
        """
        # 步骤1: 登录获取 token
        with allure.step("步骤1: 用户登录获取 Token"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            response = api_session.post(login_url, json=login_data)
            assert response.status_code == 200
            
            login_result = response.json()
            assert login_result.get("code") == 0, f"登录失败: {login_result.get('msg')}"
            
            token = login_result.get("data", {}).get("token", "")
            assert token, "Token 不能为空"
            
            allure.attach(token, "获取到的 Token", allure.attachment_type.TEXT)
        
        # 步骤2: 使用 token 查询用户信息
        with allure.step("步骤2: 使用 Token 查询用户信息"):
            user_info_url = f"{base_url}/index.php?s=/api/user/index"
            headers = {"token": token}
            
            response = api_session.get(user_info_url, headers=headers)
            allure.attach(response.text, "用户信息响应", allure.attachment_type.JSON)
            
            assert response.status_code == 200
            user_result = response.json()
            assert user_result.get("code") == 0, f"查询用户信息失败: {user_result.get('msg')}"
            
            # 验证用户信息
            user_data = user_result.get("data", {})
            assert user_data.get("username") == "hami", "用户名不匹配"
    
    @allure.title("测试创建订单流程")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.slow
    def test_create_order_workflow(self, api_client, base_url: str):
        """
        测试场景：完整的创建订单流程
        1. 查询商品列表
        2. 选择商品
        3. 加入购物车
        4. 创建订单
        """
        # 步骤1: 查询商品列表
        with allure.step("步骤1: 查询商品列表"):
            response = api_client.get("/index.php?s=/api/goods/index")
            assert response.status_code == 200
            
            goods_result = response.json()
            assert goods_result.get("code") == 0
            
            goods_list = goods_result.get("data", {}).get("data", [])
            assert len(goods_list) > 0, "商品列表为空"
            
            # 选择第一个商品
            selected_goods = goods_list[0]
            goods_id = selected_goods.get("id")
            
            allure.attach(
                json.dumps(selected_goods, ensure_ascii=False, indent=2),
                "选中的商品",
                allure.attachment_type.JSON
            )
        
        # 步骤2: 查询商品详情
        with allure.step("步骤2: 查询商品详情"):
            response = api_client.get(
                "/index.php?s=/api/goods/detail",
                params={"id": goods_id}
            )
            assert response.status_code == 200
            
            detail_result = response.json()
            assert detail_result.get("code") == 0
            
            allure.attach(
                response.text,
                "商品详情",
                allure.attachment_type.JSON
            )
        
        # 注意：实际的加入购物车和创建订单接口需要根据实际 API 调整
        # 这里仅作为示例演示流程


@allure.feature("性能测试")
@allure.story("响应时间验证")
class TestPerformance:
    """API 性能测试示例"""
    
    @allure.title("测试接口响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_time(self, base_url: str):
        """
        测试场景：验证 API 响应时间
        要求：响应时间 < 2 秒
        """
        import time
        
        with allure.step("发送请求并记录响应时间"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            start_time = time.time()
            response = requests.post(login_url, json=login_data)
            end_time = time.time()
            
            response_time = end_time - start_time
            allure.attach(
                f"{response_time:.3f} 秒",
                "响应时间",
                allure.attachment_type.TEXT
            )
        
        with allure.step("验证响应时间"):
            assert response.status_code == 200
            assert response_time < 2.0, f"响应时间过长: {response_time:.3f}秒"
    
    @allure.title("测试并发请求")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    def test_concurrent_requests(self, base_url: str):
        """
        测试场景：并发请求测试
        使用多线程模拟并发
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def send_request(index: int) -> Dict[str, Any]:
            """发送单个请求"""
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            response = requests.post(login_url, json=login_data)
            return {
                "index": index,
                "status_code": response.status_code,
                "success": response.json().get("code") == 0
            }
        
        with allure.step("发送10个并发请求"):
            concurrent_count = 10
            results = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(send_request, i) for i in range(concurrent_count)]
                
                for future in as_completed(futures):
                    results.append(future.result())
        
        with allure.step("验证并发请求结果"):
            success_count = sum(1 for r in results if r["success"])
            allure.attach(
                f"成功: {success_count}/{concurrent_count}",
                "并发测试结果",
                allure.attachment_type.TEXT
            )
            
            # 至少80%的请求应该成功
            success_rate = success_count / concurrent_count
            assert success_rate >= 0.8, f"成功率过低: {success_rate * 100:.1f}%"


@allure.feature("错误处理测试")
@allure.story("异常场景验证")
class TestErrorHandling:
    """API 错误处理测试"""
    
    @allure.title("测试无效的 HTTP 方法")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_http_method(self, base_url: str):
        """
        测试场景：使用错误的 HTTP 方法
        """
        with allure.step("使用 GET 方法调用需要 POST 的接口"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            response = requests.get(login_url)  # 应该使用 POST
            
            allure.attach(response.text, "响应数据", allure.attachment_type.TEXT)
        
        with allure.step("验证返回错误"):
            # 应该返回方法不允许或业务错误
            assert response.status_code in [405, 200]  # 405: Method Not Allowed
    
    @allure.title("测试无效的 JSON 格式")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_json_format(self, base_url: str):
        """
        测试场景：发送无效的 JSON 格式
        """
        with allure.step("发送无效的 JSON 数据"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"Content-Type": "application/json"}
            invalid_json = "{invalid json}"
            
            response = requests.post(login_url, data=invalid_json, headers=headers)
            allure.attach(response.text, "响应数据", allure.attachment_type.TEXT)
        
        with allure.step("验证返回错误"):
            # 应该返回 400 错误或业务错误
            assert response.status_code in [400, 200]
    
    @allure.title("测试超长字符串输入")
    @allure.severity(allure.severity_level.MINOR)
    def test_extremely_long_input(self, base_url: str):
        """
        测试场景：输入超长字符串
        验证 API 的输入长度限制
        """
        with allure.step("准备超长字符串"):
            long_string = "a" * 10000  # 10000个字符
            login_url = f"{base_url}/index.php?s=/api/user/login"
            login_data = {
                "accounts": long_string,
                "pwd": "123456",
                "type": "username"
            }
        
        with allure.step("发送请求"):
            response = requests.post(login_url, json=login_data)
            allure.attach(
                f"状态码: {response.status_code}",
                "响应状态",
                allure.attachment_type.TEXT
            )
        
        with allure.step("验证处理结果"):
            # API 应该能正常处理，返回业务错误或输入验证错误
            assert response.status_code in [200, 400, 413]  # 413: Payload Too Large


@allure.feature("数据验证")
@allure.story("响应数据结构验证")
class TestDataValidation:
    """API 响应数据验证"""
    
    @allure.title("测试响应数据结构完整性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_response_data_structure(self, api_client):
        """
        测试场景：验证 API 响应数据结构
        确保所有必需字段都存在
        """
        with allure.step("查询商品列表"):
            response = api_client.get("/index.php?s=/api/goods/index")
            assert response.status_code == 200
            
            result = response.json()
            allure.attach(
                json.dumps(result, ensure_ascii=False, indent=2),
                "响应数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证响应结构"):
            # 验证顶层结构
            assert "code" in result, "缺少 code 字段"
            assert "msg" in result, "缺少 msg 字段"
            assert "data" in result, "缺少 data 字段"
            
            # 验证 code 为 0 表示成功
            assert result["code"] == 0, f"接口返回错误: {result.get('msg')}"
            
            # 验证 data 结构（根据实际 API 调整）
            data = result["data"]
            if isinstance(data, dict):
                assert "data" in data or "list" in data, "data 字段结构不符合预期"


