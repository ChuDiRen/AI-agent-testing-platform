---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [文件路径] | [组件名称]
description: 为 Golang/trpc-go 项目生成包含单元测试、集成测试和边界情况覆盖的全面测试套件
---

# 生成测试

为以下目标生成全面的测试套件：$ARGUMENTS

## 当前测试设置

- 测试框架：Go 标准 `testing` 包配合 `testify` 断言库
- 现有测试：!find . -name "*_test.go" | head -10
- 测试覆盖率：!go test -cover ./... 2>/dev/null || echo "运行 go test 检查测试"
- 目标文件：@$ARGUMENTS（如果提供了文件路径）

## 任务

我将分析目标代码并创建完整的测试覆盖，包括：

1. 单元测试：标准函数、方法和工具函数
2. 集成测试：trpc-go handler、interceptor、service 层交互
3. 边界情况和错误处理：context 取消、超时、并发安全、输入验证
4. Mock 实现：为接口依赖生成 mock（使用 `testify/mock` 或 `go-mock`）
5. 测试工具和辅助函数：根据需求创建
6. 性能测试：使用 `go test -bench` 进行基准测试（适用场景）

## 流程

我将遵循以下步骤：

1. 运行 `go test ./...` 检查现有测试，运行 `go test -cover ./...` 查看覆盖率
2. 分析目标文件/组件结构：识别 Go 包结构、trpc-go 组件（services、logic、repository）
3. 识别所有可测试函数、方法和行为：分析函数签名、依赖关系和 trpc-go 组件类型
4. 检查项目中现有的测试模式和实践
5. 创建 `*_test.go` 文件：遵循项目命名规范
6. 实现完整测试用例：使用表驱动测试，包含适当的 setup/teardown
7. 添加必要的 mock 和测试工具：使用 `testify/mock` 或 `go-mock`
8. 验证测试覆盖率 ≥80%，运行 `go test -race` 检测竞态条件

## 测试类型

### 单元测试

- 使用表驱动测试，覆盖正常输入、错误输入、边界值
- 测试结构体方法的行为和状态变更
- 工具函数的全面测试
- 验证错误返回和错误信息

### 集成测试

- **trpc-go Handler 测试**：Request/Response 流程验证、Mock 依赖项（repository、service、client）、错误码和错误处理验证（使用 `errs.Code(err)`）、Context 传递和超时测试
- **Service 层测试**：业务逻辑集成、多依赖项协调、事务处理测试
- **数据库集成测试**：使用 `testcontainers-go` 或内存数据库（如 sqlite in-memory）、数据一致性验证、事务回滚测试

### 边界情况和错误处理

- **Context 取消**：测试 context 取消时的行为
- **超时处理**：验证超时机制的触发
- **并发安全**：使用 `go test -race` 检测竞态条件
- **输入验证**：边界值、nil 值、空值、非法输入
- **错误场景**：网络错误、数据库错误、业务错误

### trpc-go 特定测试

- **Handler 测试**：验证 Request/Response、错误码、Context
- **Interceptor 测试**：context 传递、元数据处理、错误处理
- **Service 测试**：使用 mock client 或 `go-mock`
- **元数据传递**：使用 `trpc.Message(ctx)` 测试元数据

## 测试最佳实践

### 测试结构

- 使用描述性测试名称，清晰表达测试场景（使用中文）
- 遵循 AAA 模式（Arrange、Act、Assert）
- 使用 `t.Run()` 组织子测试
- 使用适当的 setup/teardown（`t.Cleanup()` 或 `defer`）实现测试隔离

### Mock 策略

- 仅 Mock 边界之外的依赖（DB/网络/外部服务）
- 使用 `testify/mock` 或 `go-mock`，结束后 `AssertExpectations()`
- 测试数据用工厂/固定随机种子，必要时 Mock 时间

### 覆盖率目标

- 覆盖率 ≥ 80%（运行 `go test -cover ./...`）
- 聚焦关键业务路径与错误场景
- 覆盖边界值、并发安全（`go test -race`）、超时与 context 取消
- 使用 `go tool cover -html=coverage.out` 可视化未覆盖代码

### 完成检查

- [ ] `go test -v ./...` 测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 使用表驱动测试（适用场景）
- [ ] Mock 验证：`AssertExpectations()`
- [ ] `go test -race` 无竞态条件
