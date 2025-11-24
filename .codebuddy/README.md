# CodeBuddy 配置使用指南

## 📁 目录结构
```
.codebuddy/
├── agents/              # AI 角色代理
│   ├── backend-architect-python.md
│   ├── backend-architect-go.md
│   ├── frontend-developer.md
│   ├── code-reviewer.md
│   ├── debugger.md
│   ├── data-scientist.md
│   ├── test-automator-python.md
│   └── test-automator-go.md
├── commands/            # 快捷命令
│   ├── code-review-python.md
│   ├── code-review-go.md
│   ├── generate-api-doc-python.md
│   ├── generate-api-doc-go.md
│   ├── generate-tests-python.md
│   └── generate-tests-go.md
└── skills/              # 技能扩展
    └── webapp-testing/  # Playwright Web 测试
```

## 🚀 如何使用

### 方式一: Cursor Chat 直接调用
在 Cursor 的 Chat 窗口中使用 `@` 符号:

```
@backend-architect-python 设计一个用户管理的 API
@frontend-developer 创建一个数据表格组件
@code-reviewer 审查 platform-fastapi-server/app/routes/test.py
@test-automator-python 为 agent-backend/services/agent_service.py 生成测试
```

### 方式二: 使用 Commands
直接在 Chat 中输入命令触发词:

```
/code-review-python platform-fastapi-server/app/routes/
/generate-tests-python agent-backend/services/
/generate-api-doc-python api-engine/
```

### 方式三: 在消息中提及角色
```
请以后端架构师的角度审查这个 API 设计
作为前端开发专家，帮我优化这个 Vue 组件
```

## 📋 Agents 说明

### 🏗️ backend-architect-python
**用途**: 后端系统架构和 API 设计
**触发**: `@backend-architect-python` 或提及"架构师"、"API 设计"
**输出**: 
- API 端点定义
- 服务架构图
- 数据库架构
- 技术推荐清单

### 🎨 frontend-developer
**用途**: React/Vue 组件开发
**触发**: `@frontend-developer` 或提及"前端"、"组件"
**专长**: React 19、Vue 3、TypeScript、性能优化、可访问性

### 🔍 code-reviewer
**用途**: 代码质量审查
**触发**: `@code-reviewer` 或提及"代码审查"、"review"
**检查**: 安全性、性能、架构、测试覆盖率

### 🐛 debugger
**用途**: 问题诊断和调试
**触发**: `@debugger` 或提及"调试"、"bug"

### 🧪 test-automator-python
**用途**: 生成测试用例
**触发**: `@test-automator-python` 或提及"测试"、"test"
**要求**: 覆盖率 ≥80%

## 📝 Commands 说明

### `/code-review-python [路径]`
执行全面代码审查:
- 架构与设计审查
- 安全漏洞扫描
- 性能分析
- 测试覆盖率检查

### `/generate-tests-python [路径]`
生成测试套件:
- 单元测试
- 集成测试
- 边界用例
- Mock 实现

### `/generate-api-doc-python [路径]`
生成 API 文档:
- OpenAPI 规范
- 请求/响应示例
- 错误码说明

## 🛠️ Skills 说明

### webapp-testing
**用途**: Playwright Web 应用测试
**使用**: 
```python
# 使用辅助脚本启动服务器
python .codebuddy/skills/webapp-testing/scripts/with_server.py --help

# 单服务器
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py

# 多服务器
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test.py
```

## 🎯 最佳实践

### 1. 明确指定 Agent
❌ 不好: "帮我看看这个代码"
✅ 好的: "@code-reviewer 审查 platform-fastapi-server/app/routes/test.py"

### 2. 提供上下文
❌ 不好: "生成测试"
✅ 好的: "@test-automator-python 为 agent-backend/services/agent_service.py 生成测试，需要包含异步测试和 Mock"

### 3. 指定文件路径
❌ 不好: "审查后端代码"
✅ 好的: "/code-review-python platform-fastapi-server/app/routes/"

### 4. 分阶段使用
```
第一步: @backend-architect-python 设计 API
第二步: 实现代码
第三步: @test-automator-python 生成测试
第四步: @code-reviewer 审查代码
```

## 🔧 故障排查

### 问题: Agent 没有响应
**解决**:
1. 确保使用 `@agent-name` 格式
2. 检查 agent 名称是否正确
3. 重启 Cursor 编辑器

### 问题: Commands 不生效
**解决**:
1. 确保使用 `/command-name` 格式
2. 提供必要的参数
3. 检查 .codebuddy 目录权限

### 问题: 规则没有应用
**解决**:
1. 确保 `.cursorrules` 文件存在于项目根目录
2. 重新加载 Cursor 工作区
3. 检查 Cursor 设置中是否启用了项目规则

## 📚 参考资料

- [Cursor Documentation](https://docs.cursor.com)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
