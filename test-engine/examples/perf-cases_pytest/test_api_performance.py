"""
API 性能测试示例 - Pytest 格式
基于 Locust 封装的关键字进行真正的分布式压测

核心特性:
- 使用 Locust 作为压测引擎
- 关键字驱动的 API 设计
- 支持真正的并发用户模拟
- 完整的性能指标统计
"""
import pytest
import allure
from testengine_perf.extend.keywords import (
    PerfKeywords,
    PerfTestResult,
    create_perf_test
)


# ==================== 基础性能测试 ====================

@allure.feature("API 性能测试")
@allure.story("基于 Locust 的关键字驱动测试")
class TestAPIPerformance:
    """
    API 性能测试套件
    使用 PerfKeywords 进行真正的压测
    """
    
    @allure.title("GET 请求性能测试 - 10 并发用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_users_performance(self):
        """
        测试 GET /users 接口性能
        
        场景:
        - 10 个并发用户
        - 每秒生成 2 个用户
        - 运行 30 秒
        """
        # 创建性能测试实例
        perf = create_perf_test()
        
        # 定义用户行为（关键字驱动）
        @perf.task(weight=1)
        def get_users(kw):
            """获取用户列表"""
            kw.get(url="/users", name="GET /users")
            if not kw.check_status(expected=200):
                raise AssertionError(f"状态码错误: {kw.last_response.status_code}")
        
        # 运行压测
        with allure.step("执行 Locust 压测"):
            result = perf.run_test(
                host="https://jsonplaceholder.typicode.com",
                users=10,
                spawn_rate=2,
                run_time=30,
                wait_time_min=1,
                wait_time_max=3
            )
        
        # 记录性能指标
        with allure.step("验证性能指标"):
            allure.attach(
                f"总请求数: {result.total_requests}\n"
                f"失败数: {result.failures}\n"
                f"失败率: {result.failure_rate:.2%}\n"
                f"平均响应时间: {result.avg_response_time:.2f}ms\n"
                f"P95 响应时间: {result.p95_response_time:.2f}ms\n"
                f"P99 响应时间: {result.p99_response_time:.2f}ms\n"
                f"RPS: {result.requests_per_second:.2f}",
                "性能指标",
                allure.attachment_type.TEXT
            )
            
            # 性能断言
            assert result.failure_rate < 0.05, \
                f"失败率 {result.failure_rate:.2%} 超过阈值 5%"
            assert result.avg_response_time < 1000, \
                f"平均响应时间 {result.avg_response_time:.2f}ms 超过阈值 1000ms"
    
    @allure.title("POST 请求性能测试 - 创建用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_users_performance(self):
        """
        测试 POST /users 接口性能
        """
        perf = create_perf_test()
        
        @perf.task(weight=1)
        def create_user(kw):
            """创建用户"""
            import time
            payload = {
                "name": f"User_{int(time.time() * 1000)}",
                "username": "testuser",
                "email": "test@example.com"
            }
            
            kw.post(url="/users", json=payload, name="POST /users")
            if kw.last_response.status_code not in [200, 201]:
                raise AssertionError(f"状态码错误: {kw.last_response.status_code}")
        
        with allure.step("执行 POST 压测"):
            result = perf.run_test(
                host="https://jsonplaceholder.typicode.com",
                users=10,
                spawn_rate=2,
                run_time=30
            )
        
        with allure.step("验证性能指标"):
            allure.attach(str(result.__dict__), "结果详情", allure.attachment_type.JSON)
            
            assert result.failure_rate < 0.05
            assert result.p95_response_time < 1500


@allure.feature("API 性能测试")
@allure.story("混合场景压测")
class TestMixedScenario:
    """
    混合场景压测
    模拟真实用户行为：多种操作混合执行
    """
    
    @allure.title("混合场景 - GET/POST 组合")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mixed_operations(self):
        """
        混合场景测试
        
        场景:
        - GET /users (权重 3)
        - GET /posts (权重 2)
        - POST /posts (权重 1)
        """
        perf = create_perf_test()
        
        @perf.task(weight=3)
        def get_users(kw):
            """获取用户列表 - 高频操作"""
            kw.get(url="/users", name="GET /users")
        
        @perf.task(weight=2)
        def get_posts(kw):
            """获取文章列表 - 中频操作"""
            kw.get(url="/posts", name="GET /posts")
        
        @perf.task(weight=1)
        def create_post(kw):
            """创建文章 - 低频操作"""
            import time
            kw.post(url="/posts", json={
                "title": f"Post_{int(time.time())}",
                "body": "Test content",
                "userId": 1
            }, name="POST /posts")
        
        with allure.step("执行混合场景压测"):
            result = perf.run_test(
                host="https://jsonplaceholder.typicode.com",
                users=20,
                spawn_rate=5,
                run_time=60
            )
        
        with allure.step("分析各接口性能"):
            for stat in result.request_stats:
                allure.attach(
                    f"接口: {stat['name']}\n"
                    f"请求数: {stat['num_requests']}\n"
                    f"失败数: {stat['num_failures']}\n"
                    f"平均响应时间: {stat['avg_response_time']:.2f}ms\n"
                    f"P95: {stat['p95']:.2f}ms",
                    stat['name'],
                    allure.attachment_type.TEXT
                )
        
        # 整体断言
        assert result.failure_rate < 0.1, "整体失败率过高"


@allure.feature("API 性能测试")
@allure.story("压力测试")
class TestStressScenario:
    """
    压力测试场景
    逐步增加负载，测试系统极限
    """
    
    @allure.title("阶梯压测 - 逐步增加用户")
    @allure.severity(allure.severity_level.NORMAL)
    def test_step_load(self):
        """
        阶梯压测
        
        场景:
        - 第一阶段: 10 用户, 30 秒
        - 第二阶段: 30 用户, 30 秒
        - 第三阶段: 50 用户, 30 秒
        """
        results = []
        user_levels = [10, 30, 50]
        
        for users in user_levels:
            with allure.step(f"压测阶段: {users} 并发用户"):
                perf = create_perf_test()
                
                @perf.task(weight=1)
                def get_posts(kw):
                    kw.get(url="/posts/1", name=f"GET /posts/1 ({users} users)")
                
                result = perf.run_test(
                    host="https://jsonplaceholder.typicode.com",
                    users=users,
                    spawn_rate=users // 2,
                    run_time=30
                )
                
                results.append({
                    "users": users,
                    "result": result
                })
                
                allure.attach(
                    f"并发用户: {users}\n"
                    f"RPS: {result.requests_per_second:.2f}\n"
                    f"平均响应时间: {result.avg_response_time:.2f}ms\n"
                    f"失败率: {result.failure_rate:.2%}",
                    f"阶段 {users} 用户",
                    allure.attachment_type.TEXT
                )
        
        # 分析趋势
        with allure.step("分析性能趋势"):
            for r in results:
                # 随着用户增加，允许一定的性能下降
                max_failure_rate = 0.05 + (r["users"] / 100) * 0.05
                assert r["result"].failure_rate < max_failure_rate, \
                    f"{r['users']} 用户时失败率 {r['result'].failure_rate:.2%} 过高"


@allure.feature("API 性能测试")
@allure.story("带登录的场景")
class TestAuthenticatedScenario:
    """
    需要认证的场景测试
    演示 on_start 的使用
    """
    
    @allure.title("带登录的压测场景")
    @allure.severity(allure.severity_level.NORMAL)
    def test_with_login(self):
        """
        带登录的压测
        
        场景:
        - 用户启动时执行登录
        - 然后执行业务操作
        """
        perf = create_perf_test()
        
        # 用户启动时执行登录
        @perf.on_start
        def login(kw):
            """用户登录"""
            # 这里模拟登录，实际场景会保存 token
            kw.post(url="/posts", json={
                "title": "Login simulation",
                "body": "This simulates a login",
                "userId": 1
            }, name="Login")
            # 可以提取 token 并保存到上下文
            # kw.extract_json(path="$.token", var="auth_token")
        
        @perf.task(weight=1)
        def get_profile(kw):
            """获取用户信息（需要登录后）"""
            kw.get(url="/users/1", name="GET /users/1 (authenticated)")
        
        @perf.task(weight=2)
        def get_my_posts(kw):
            """获取我的文章"""
            kw.get(url="/posts?userId=1", name="GET /posts?userId=1")
        
        with allure.step("执行带认证的压测"):
            result = perf.run_test(
                host="https://jsonplaceholder.typicode.com",
                users=10,
                spawn_rate=2,
                run_time=30
            )
        
        assert result.failure_rate < 0.05


@allure.feature("API 性能测试")
@allure.story("关键字验证场景")
class TestKeywordsValidation:
    """
    演示使用关键字进行响应验证
    """
    
    @allure.title("使用关键字验证响应")
    @allure.severity(allure.severity_level.NORMAL)
    def test_with_validation(self):
        """
        使用关键字验证响应
        
        演示:
        - check_status: 验证状态码
        - check_response_time: 验证响应时间
        - check_contains: 验证响应包含文本
        - extract_json: 提取 JSON 数据
        """
        perf = create_perf_test()
        
        @perf.task(weight=1)
        def get_user_with_validation(kw):
            """获取用户并验证响应"""
            # 发送请求
            kw.get(url="/users/1", name="GET /users/1")
            
            # 验证状态码
            kw.check_status(expected=200)
            
            # 验证响应时间
            kw.check_response_time(max_ms=2000)
            
            # 提取数据到上下文
            kw.extract_json(path="$.name", var="user_name")
            
            # 打印日志
            kw.log(message="用户名: {{user_name}}")
        
        @perf.task(weight=1)
        def get_posts_with_transaction(kw):
            """使用事务统计"""
            # 开始事务
            kw.start_transaction(name="获取文章流程")
            
            # 获取文章列表
            kw.get(url="/posts?userId=1", name="GET /posts")
            kw.check_status(expected=200)
            
            # 思考时间
            kw.think_time(min=0.5, max=1)
            
            # 获取第一篇文章详情
            kw.get(url="/posts/1", name="GET /posts/1")
            kw.check_status(expected=200)
            
            # 结束事务
            kw.end_transaction(success=True)
        
        with allure.step("执行带验证的压测"):
            result = perf.run_test(
                host="https://jsonplaceholder.typicode.com",
                users=5,
                spawn_rate=1,
                run_time=30
            )
        
        assert result.failure_rate < 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
