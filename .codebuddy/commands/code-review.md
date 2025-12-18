---
name: code-review
description: 代码审查。自动识别技术栈（Python/Go/JavaScript），审查代码的质量、安全性和可维护性。
---

# 代码审查命令

## 使用方式

```
/code-review [文件或目录路径]
```

## 技术栈自动识别

启动时自动检测并应用对应审查规范：
- **Python**: 检测 `*.py` → PEP 8、Type Hints、Docstrings
- **Go**: 检测 `*.go` → Effective Go、golint、并发安全
- **JavaScript/TypeScript**: 检测 `*.js/*.ts` → ESLint、TypeScript 规范

## 通用审查清单

### 代码质量
- [ ] 代码简单易读
- [ ] 函数和变量命名良好
- [ ] 没有重复代码（DRY 原则）
- [ ] 函数长度合理
- [ ] 职责单一（SRP）

### 错误处理
- [ ] 适当的异常/错误处理
- [ ] 错误信息清晰
- [ ] 自定义错误类型

### 安全性
- [ ] 没有暴露的秘密或 API 密钥
- [ ] 实现了输入验证
- [ ] SQL 注入防护
- [ ] XSS 防护

### 性能
- [ ] 避免 N+1 查询
- [ ] 避免不必要的循环/内存分配
- [ ] 考虑并发安全

## 语言特定检查

### Python
- [ ] 遵循 PEP 8 风格
- [ ] 类型注解（Type Hints）
- [ ] 文档字符串（Docstrings）
- [ ] 合理使用生成器

### Go
- [ ] 正确处理 error 返回值
- [ ] 错误信息包含上下文（`fmt.Errorf("xxx: %w", err)`）
- [ ] 通过 golint/golangci-lint
- [ ] goroutine 泄漏检查

### JavaScript/TypeScript
- [ ] 通过 ESLint 检查
- [ ] 正确的类型定义
- [ ] 避免 any 类型滥用
- [ ] Promise 正确处理

## 示例

```
/code-review app/routes/user.py
/code-review internal/handler/
/code-review src/components/
/code-review .
```

## 输出格式

按优先级组织反馈：
- **关键问题**（必须修复）
- **警告**（应该修复）
- **建议**（考虑改进）

包括如何修复问题的具体示例。
