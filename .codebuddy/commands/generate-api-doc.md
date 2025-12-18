---
name: generate-api-doc
description: API 文档生成。调用 api-documentation Skill，从后端代码生成标准化 API 文档。
---

# API 文档生成命令

## 使用方式

```
/generate-api-doc [文件或目录路径]
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API 文档生成流程                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户输入 → 调用 api-documentation skill                                     │
│       │                                                                     │
│       ├── 1. 技术栈识别                                                      │
│       │       ├── FastAPI: @app.get/post 装饰器                             │
│       │       ├── Flask: @app.route 装饰器                                  │
│       │       ├── Gin: gin.Context                                         │
│       │       └── Echo: echo.Context                                       │
│       │                                                                     │
│       ├── 2. 接口信息提取                                                    │
│       │       ├── URL 路径和请求方式                                         │
│       │       ├── 请求参数（Query/Body/Path）                                │
│       │       ├── 响应结构                                                   │
│       │       └── 错误码                                                     │
│       │                                                                     │
│       └── 3. 文档生成                                                        │
│               └── 输出到 doc/api/ 目录                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 调用 Skill

**Skill：** `api-documentation`

该 Skill 提供：
- 完整的文档格式标准
- 多技术栈解析规则
- 请求/响应模板
- 错误码规范

## 示例

```bash
# 单个文件
/generate-api-doc app/routes/user.py

# 整个目录
/generate-api-doc app/api/
/generate-api-doc internal/handler/
/generate-api-doc controllers/
```

## 输出

- 文档保存到 `doc/api/` 目录
- 命名规则：`{模块名}-api.md`
- 示例：`user-api.md`、`order-api.md`
