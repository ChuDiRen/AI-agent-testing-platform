# AI Agent 编排平台后端测试

## 项目结构

```
tests/
├── conftest.py          # 全局 fixtures 和配置
├── pytest.ini          # pytest 配置文件
├── requirements.txt     # 测试依赖
├── api/                 # API 测试模块
│   ├── __init__.py
│   ├── test_auth.py     # 认证授权测试
│   ├── test_agent.py    # Agent管理测试
│   ├── test_workflow.py # Workflow管理测试
│   ├── test_execution.py# Execution管理测试
│   ├── test_tool.py     # Tool管理测试
│   ├── test_billing.py  # 计费统计测试
│   └── test_batch.py    # 批量操作测试
└── README.md           # 说明文档
```

## 测试覆盖范围

### P0级别测试（核心功能）
- **认证授权模块** (test_auth.py): SQL注入防护、认证绕过、敏感信息泄露、空值处理、异常捕获、并发安全
- **Agent管理模块** (test_agent.py): 名称注入、空值处理、事务回滚
- **Workflow管理模块** (test_workflow.py): 空值处理、状态一致性
- **Execution管理模块** (test_execution.py): 空值处理、状态转换、并发执行
- **Tool管理模块** (test_tool.py): 配置注入、空值处理、连接测试异常
- **批量操作模块** (test_batch.py): 空列表处理、部分失败处理、事务一致性
- **计费统计模块** (test_billing.py): 计费数据注入、数值边界、统计数据一致性、并发计费

### P1级别测试（重要功能）
- **性能瓶颈测试**: N+1查询、索引优化、缓存策略、同步阻塞
- **数据库设计测试**: 表结构约束、字段类型、软删除
- **API设计测试**: RESTful规范、响应格式、参数校验、接口文档
- **代码质量测试**: 错误处理、日志记录、职责单一
- **监控日志检查测试**: 错误监控、性能监控、用户行为埋点

### 边界条件和兼容性测试
- **边界条件测试**: 极限值、网络异常、权限边界
- **环境兼容性测试**: 数据库兼容性、跨域、国际化、时区
- **特殊场景测试**: 高并发、数据恢复、内存压力
- **安全增强测试**: 恶意文件上传、会话劫持防护

## 环境要求

1. Python 3.8+
2. 后端服务运行在 `http://localhost:8000`
3. 测试数据库环境（与生产环境隔离）

## 安装依赖

```bash
pip install -r tests/requirements.txt
```

## 运行测试

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行指定模块测试
```bash
# 认证模块测试
pytest tests/api/test_auth.py -v

# Agent管理测试
pytest tests/api/test_agent.py -v

# Workflow管理测试
pytest tests/api/test_workflow.py -v
```

### 运行指定测试类
```bash
pytest tests/api/test_auth.py::TestAuthAPI -v
```

### 运行指定测试方法
```bash
pytest tests/api/test_auth.py::TestAuthAPI::test_sql_injection_login -v
```

### 按标记运行测试
```bash
# 运行安全测试
pytest tests/ -m security -v

# 运行性能测试
pytest tests/ -m performance -v

# 排除慢速测试
pytest tests/ -m "not slow" -v
```

### 生成测试报告

```bash
# 生成HTML报告
pytest tests/ -v --html=report.html --self-contained-html

# 生成覆盖率报告
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# 同时生成HTML和覆盖率报告
pytest tests/ -v --html=report.html --self-contained-html --cov=app --cov-report=html
```

## 配置说明

### 环境变量
- `BASE_URL`: 后端服务地址（默认: http://localhost:8000）
- `TEST_TOKEN`: 测试用的认证token

### pytest.ini 配置
- 自动发现测试文件和测试类
- 启用异步测试支持
- 配置测试标记
- 生成HTML和覆盖率报告

### conftest.py fixtures
- `client`: 基础HTTP客户端
- `auth_client`: 带认证的HTTP客户端
- `test_user_data`: 测试用户数据
- `test_agent_data`: 测试Agent数据
- `test_workflow_data`: 测试Workflow数据
- `test_tool_data`: 测试Tool数据
- `mock_db_session`: 模拟数据库会话
- `mock_logger`: 模拟日志记录器

## 测试数据管理

### 测试数据隔离
- 每个测试用例使用独立的测试数据
- 测试完成后自动清理
- 使用mock避免影响生产数据

### 测试用户
- 用户名: testuser
- 邮箱: test@example.com
- 密码: Test123456

## 注意事项

1. **测试环境**: 确保在测试环境中运行，避免影响生产数据
2. **数据库**: 使用独立的测试数据库
3. **并发测试**: 部分测试使用并发，注意资源消耗
4. **Mock使用**: 大量使用mock来模拟外部依赖
5. **异步测试**: 所有API测试都是异步的，需要使用 `@pytest.mark.asyncio`

## 故障排除

### 常见问题

1. **连接超时**: 检查后端服务是否运行
2. **认证失败**: 检查TEST_TOKEN配置
3. **数据库错误**: 检查测试数据库配置
4. **导入错误**: 确保在正确的目录运行pytest

### 调试技巧

```bash
# 显示详细输出
pytest tests/ -v -s

# 只运行失败的测试
pytest tests/ --lf

# 在第一个失败时停止
pytest tests/ -x

# 显示本地变量
pytest tests/ -v --tb=long
```

## 持续集成

测试配置支持CI/CD集成：

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v --cov=app --cov-report=xml
```

## 扩展测试

### 添加新测试

1. 在对应的测试文件中添加测试方法
2. 使用 `@pytest.mark.asyncio` 装饰器
3. 遵循命名规范 `test_*`
4. 添加适当的断言和清理逻辑

### 添加新模块测试

1. 创建新的测试文件 `test_*.py`
2. 继承测试基类或直接使用pytest
3. 添加相应的fixtures
4. 更新README文档
