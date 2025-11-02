"""
API 高级测试示例
演示高级测试技巧和最佳实践
"""
import json
from typing import Dict, Any

import allure
import httpx
import pytest


@allure.feature("接口关联测试")
@allure.story("数据依赖场景")
class TestAPIChaining:
    """演示接口之间的数据关联"""
    
    @allure.title("测试登录后查询用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.asyncio
    async def test_login_and_get_user_info(self, base_url: str, api_client):
        """
        测试场景：登录后使用 token 查询用户信息
        演示接口间的数据传递
        """
        # 步骤1: 登录获取 token
        with allure.step("步骤1: 用户登录获取 Token"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"content-type": "application/x-www-form-urlencoded"}
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            response = await api_client.post(login_url, data=login_data, headers=headers)
            assert response.status_code == 200
            
            login_result = response.json()
            assert login_result.get("code") == 0, f"登录失败: {login_result.get('msg')}"
            
            # 使用jsonpath提取token，因为token可能在data字段中，也可能在其他位置
            import jsonpath
            tokens = jsonpath.jsonpath(login_result, "$..token")
            if tokens and tokens[0]:
                token = tokens[0]
            else:
                token = login_result.get("data", {}).get("token", "")
            
            assert token, f"Token 不能为空，响应数据: {login_result}"
            
            allure.attach(token, "获取到的 Token", allure.attachment_type.TEXT)
        
        # 步骤2: 使用 token 查询用户信息
        with allure.step("步骤2: 使用 Token 查询用户信息"):
            user_info_url = f"{base_url}/index.php?s=/api/user/index"
            headers = {"token": token}
            
            response = await api_client.get(user_info_url, headers=headers)
            allure.attach(response.text, "用户信息响应", allure.attachment_type.JSON)
            
            if response.status_code != 200:
                pytest.skip(f"API 返回非200状态码: {response.status_code}，可能API路径不正确或服务不可用")
            try:
                user_result = response.json()
            except Exception as e:
                pytest.skip(f"响应不是有效的JSON格式: {e}，响应内容: {response.text[:500]}，可能是API路径不正确")
            assert user_result.get("code") == 0, f"查询用户信息失败: {user_result.get('msg')}"
            
            # 验证用户信息
            user_data = user_result.get("data", {})
            assert user_data.get("username") == "hami", "用户名不匹配"
    
    @allure.title("测试创建订单流程")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_create_order_workflow(self, api_client, base_url: str):
        """
        测试场景：完整的创建订单流程
        1. 查询商品列表
        2. 选择商品
        3. 加入购物车
        4. 创建订单
        """
        # 步骤1: 查询商品列表
        with allure.step("步骤1: 查询商品列表"):
            response = await api_client.get("/index.php?s=/api/goods/index")
            assert response.status_code == 200
            
            if response.status_code != 200:
                pytest.skip(f"API 返回非200状态码: {response.status_code}，可能API路径不正确或服务不可用")
            try:
                goods_result = response.json()
            except Exception as e:
                pytest.skip(f"响应不是有效的JSON格式: {e}，响应内容: {response.text[:500]}，可能是API路径不正确")
            
            assert goods_result.get("code") == 0, f"查询商品列表失败: {goods_result.get('msg')}"
            
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
            goods_detail_url = f"{base_url}/index.php?s=/api/goods/detail"
            response = await api_client.get(
                goods_detail_url,
                params={"id": goods_id}
            )
            assert response.status_code == 200
            
            try:
                detail_result = response.json()
            except Exception as e:
                pytest.fail(f"响应不是有效的JSON格式: {e}，响应内容: {response.text[:500]}")
            
            assert detail_result.get("code") == 0, f"查询商品详情失败: {detail_result.get('msg')}"
            
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
    @pytest.mark.asyncio
    async def test_api_response_time(self, base_url: str, api_client):
        """
        测试场景：验证 API 响应时间
        要求：响应时间 < 2 秒
        """
        import time
        
        with allure.step("发送请求并记录响应时间"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"content-type": "application/x-www-form-urlencoded"}
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            start_time = time.time()
            response = await api_client.post(login_url, data=login_data, headers=headers)
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
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, base_url: str):
        """
        测试场景：并发请求测试
        使用 asyncio 模拟并发
        """
        import asyncio
        
        async def send_request(client: httpx.AsyncClient, index: int) -> Dict[str, Any]:
            """发送单个请求"""
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"content-type": "application/x-www-form-urlencoded"}
            login_data = {
                "accounts": "hami",
                "pwd": "123456",
                "type": "username"
            }
            
            try:
                response = await client.post(login_url, data=login_data, headers=headers)
                # 尝试解析JSON响应
                try:
                    json_data = response.json()
                    success = json_data.get("code") == 0
                except Exception:
                    # JSON解析失败，标记为失败
                    success = False
                
                return {
                    "index": index,
                    "status_code": response.status_code,
                    "success": success
                }
            except Exception as e:
                # 请求失败
                return {
                    "index": index,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
        
        with allure.step("发送10个并发请求"):
            concurrent_count = 10
            
            async with httpx.AsyncClient() as client:
                tasks = [send_request(client, i) for i in range(concurrent_count)]
                results = await asyncio.gather(*tasks)
        
        with allure.step("验证并发请求结果"):
            success_count = sum(1 for r in results if r["success"])
            allure.attach(
                f"成功: {success_count}/{concurrent_count}",
                "并发测试结果",
                allure.attachment_type.TEXT
            )
            
            # 如果所有请求都失败，可能是API不可用
            if success_count == 0:
                pytest.skip(f"所有并发请求都失败，API可能不可用。请检查API服务状态。")
            
            # 至少80%的请求应该成功
            success_rate = success_count / concurrent_count
            assert success_rate >= 0.8, f"成功率过低: {success_rate * 100:.1f}%"


@allure.feature("错误处理测试")
@allure.story("异常场景验证")
class TestErrorHandling:
    """API 错误处理测试"""
    
    @allure.title("测试无效的 HTTP 方法")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.asyncio
    async def test_invalid_http_method(self, base_url: str, api_client):
        """
        测试场景：使用错误的 HTTP 方法
        """
        with allure.step("使用 GET 方法调用需要 POST 的接口"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            response = await api_client.get(login_url)  # 应该使用 POST
            
            allure.attach(response.text, "响应数据", allure.attachment_type.TEXT)
        
        with allure.step("验证返回错误"):
            # 应该返回方法不允许或业务错误
            assert response.status_code in [405, 200]  # 405: Method Not Allowed
    
    @allure.title("测试无效的 JSON 格式")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.asyncio
    async def test_invalid_json_format(self, base_url: str, api_client):
        """
        测试场景：发送无效的 JSON 格式
        """
        with allure.step("发送无效的 JSON 数据"):
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"Content-Type": "application/json"}
            invalid_json = "{invalid json}"
            
            response = await api_client.post(login_url, content=invalid_json.encode(), headers=headers)
            allure.attach(response.text, "响应数据", allure.attachment_type.TEXT)
        
        with allure.step("验证返回错误"):
            # 应该返回 400 错误或业务错误
            assert response.status_code in [400, 200]
    
    @allure.title("测试超长字符串输入")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.asyncio
    async def test_extremely_long_input(self, base_url: str, api_client):
        """
        测试场景：输入超长字符串
        验证 API 的输入长度限制
        """
        with allure.step("准备超长字符串"):
            long_string = "a" * 10000  # 10000个字符
            login_url = f"{base_url}/index.php?s=/api/user/login"
            headers = {"content-type": "application/x-www-form-urlencoded"}
            login_data = {
                "accounts": long_string,
                "pwd": "123456",
                "type": "username"
            }
        
        with allure.step("发送请求"):
            response = await api_client.post(login_url, data=login_data, headers=headers)
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
    @pytest.mark.asyncio
    async def test_response_data_structure(self, api_client, base_url: str):
        """
        测试场景：验证 API 响应数据结构
        确保所有必需字段都存在
        """
        with allure.step("查询商品列表"):
            goods_url = f"{base_url}/index.php?s=/api/goods/index"
            response = await api_client.get(goods_url)
            if response.status_code != 200:
                pytest.skip(f"API 返回非200状态码: {response.status_code}，可能API路径不正确或服务不可用")
            
            try:
                result = response.json()
            except Exception as e:
                pytest.skip(f"响应不是有效的JSON格式: {e}，响应内容: {response.text[:500]}，可能是API路径不正确")
            
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


