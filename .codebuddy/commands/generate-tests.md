---
name: generate-tests
description: 测试生成。根据测试类型自动调用对应 Skill：单元测试、API 接口测试、E2E 端到端测试。
---

# 测试生成命令

## 使用方式

```
/generate-tests [类型] [目标路径]
```

**类型参数：**
- `unit` - 单元测试（默认）
- `api` - API 接口自动化测试
- `e2e` - E2E 端到端测试

## 测试类型决策

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           测试类型自动选择                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户输入 → 是否指定测试类型？                                                │
│       │                                                                     │
│       ├── 指定 unit ──→ 单元测试流程                                         │
│       │                                                                     │
│       ├── 指定 api ──→ 调用 api-testing skill                               │
│       │                                                                     │
│       ├── 指定 e2e ──→ 调用 webapp-testing skill                            │
│       │                                                                     │
│       └── 未指定 ──→ 分析目标代码类型                                         │
│               │                                                             │
│               ├── API 路由/控制器 ──→ 建议 api 测试                          │
│               │                                                             │
│               ├── 前端页面/组件 ──→ 建议 e2e 测试                             │
│               │                                                             │
│               └── 业务逻辑/工具函数 ──→ 单元测试                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 单元测试（unit）

**技术栈自动识别：**
- **Python**: `pytest`、`@pytest.mark.parametrize`、mock
- **Go**: `go test`、表驱动测试、testify
- **JavaScript/TypeScript**: `Jest`、`Vitest`

**执行流程：**
1. 分析目标代码：识别函数、类、方法
2. 生成测试用例：正向、边界、异常
3. 输出测试文件

**测试清单：**
- [ ] 正常情况（Happy Path）
- [ ] 边界条件
- [ ] 异常情况
- [ ] Mock 外部依赖
- [ ] 参数化/表驱动测试

**覆盖率目标：**
- 行覆盖率 >= 80%
- 分支覆盖率 >= 70%

**输出位置：**
- Python: `tests/test_<原文件名>.py`
- Go: `<原文件名>_test.go`（同目录）
- JS/TS: `__tests__/<原文件名>.test.ts`

---

## API 接口测试（api）

**调用 Skill：** `api-testing`

**适用场景：**
- RESTful API 接口测试
- 后端服务端点验证
- 接口契约测试

**执行流程：**
1. 检查是否有 OpenAPI/Swagger 文档
2. 分析接口定义（路径、方法、参数）
3. 生成测试用例（正向、异常、参数化）
4. 使用 `pytest + httpx` 编写测试脚本

**可用辅助脚本：**
- `scripts/api_client.py` - API 客户端封装
- `scripts/with_backend.py` - 后端服务生命周期管理

**示例命令：**
```bash
/generate-tests api app/api/user.py
/generate-tests api platform-fastapi-server/app/api/
```

**输出位置：** `tests/api/test_<模块名>.py`

---

## E2E 端到端测试（e2e）

**调用 Skill：** `webapp-testing`

**适用场景：**
- 前端页面功能验证
- 用户交互流程测试
- 跨浏览器兼容性测试

**执行流程：**
1. 分析目标页面/组件
2. 识别关键用户流程
3. 使用 `Playwright` 编写测试脚本
4. 添加截图和日志捕获

**可用辅助脚本：**
- `scripts/with_server.py` - 服务器生命周期管理（支持多服务器）

**示例命令：**
```bash
/generate-tests e2e src/views/login.vue
/generate-tests e2e platform-vue-web/src/views/
```

**输出位置：** `tests/e2e/test_<页面名>.py`

---

## 示例

### 单元测试
```
/generate-tests unit services/user_service.py
/generate-tests unit pkg/service/
```

### API 接口测试
```
/generate-tests api app/api/user.py
/generate-tests api --openapi http://localhost:5000/openapi.json
```

### E2E 测试
```
/generate-tests e2e src/views/login.vue
/generate-tests e2e --url http://localhost:5173
```

---

## 语言特定模板

### Python 单元测试 (pytest)
```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    @pytest.fixture
    def service(self):
        return UserService()
    
    def test_create_user_success(self, service):
        # Arrange
        user_data = {"name": "张三"}
        # Act
        result = service.create_user(user_data)
        # Assert
        assert result.name == "张三"
    
    @pytest.mark.parametrize("input,expected", [
        ("valid@email.com", True),
        ("invalid", False),
    ])
    def test_validate_email(self, service, input, expected):
        assert service.validate_email(input) == expected
```

### Go 单元测试 (go test)
```go
func TestCreateUser(t *testing.T) {
    tests := []struct {
        name    string
        input   UserInput
        want    *User
        wantErr bool
    }{
        {"success", UserInput{Name: "张三"}, &User{Name: "张三"}, false},
        {"empty name", UserInput{}, nil, true},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := CreateUser(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("error = %v, wantErr %v", err, tt.wantErr)
            }
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("got = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### JavaScript/TypeScript 单元测试 (Jest)
```typescript
describe('UserService', () => {
  let service: UserService;
  
  beforeEach(() => {
    service = new UserService();
  });
  
  it('should create user successfully', async () => {
    const result = await service.createUser({ name: '张三' });
    expect(result.name).toBe('张三');
  });
  
  it.each([
    ['valid@email.com', true],
    ['invalid', false],
  ])('validateEmail(%s) should return %s', (input, expected) => {
    expect(service.validateEmail(input)).toBe(expected);
  });
});
```

---

## 协作 Skills

| 测试类型 | 调用 Skill | 说明 |
|---------|-----------|------|
| `api` | `api-testing` | pytest + httpx API 测试 |
| `e2e` | `webapp-testing` | Playwright Web 测试 |
