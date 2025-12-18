---
name: generate-tests
description: 测试生成。自动识别技术栈（pytest/go test/Jest），为代码生成单元测试和集成测试。
---

# 测试生成命令

## 使用方式

```
/generate-tests [文件或目录路径]
```

## 技术栈自动识别

启动时自动检测并使用对应测试框架：
- **Python**: `pytest`、`@pytest.mark.parametrize`、mock
- **Go**: `go test`、表驱动测试、testify
- **JavaScript/TypeScript**: `Jest`、`Vitest`

## 执行流程

1. **分析目标代码**：识别函数、类、方法
2. **确定测试策略**：
   - 单元测试：独立函数和方法
   - 集成测试：API 端点、数据库操作
3. **生成测试代码**：使用对应框架

## 测试清单

- [ ] 正常情况（Happy Path）
- [ ] 边界条件
- [ ] 异常情况
- [ ] Mock 外部依赖
- [ ] 参数化/表驱动测试

## 覆盖率目标

- 行覆盖率 >= 80%
- 分支覆盖率 >= 70%

## 语言特定模板

### Python (pytest)
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

### Go (go test)
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

### JavaScript/TypeScript (Jest)
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

## 示例

```
/generate-tests services/user_service.py
/generate-tests pkg/service/
/generate-tests src/services/
```

## 输出

- Python: `tests/test_<原文件名>.py`
- Go: `<原文件名>_test.go`（同目录）
- JS/TS: `__tests__/<原文件名>.test.ts`
