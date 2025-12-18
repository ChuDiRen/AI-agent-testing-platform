---
name: generate-api-doc
description: API 文档生成。自动识别技术栈（FastAPI/Flask/Gin/Echo），从后端代码生成标准化 API 文档。
---

# API 文档生成命令

## 使用方式

```
/generate-api-doc [文件或目录路径]
```

## 技术栈自动识别

启动时自动检测并应用对应解析规则：
- **FastAPI**: 检测 `@app.get/post` 装饰器、Pydantic 模型
- **Flask**: 检测 `@app.route` 装饰器
- **Gin**: 检测 `gin.Context`、`c.JSON()` 等
- **Echo**: 检测 `echo.Context`、`c.JSON()` 等

## 执行流程

1. **分析目标代码**：识别路由、控制器、处理函数
2. **提取接口信息**：
   - URL 路径和请求方式
   - 请求参数（Query/Body/Path）
   - 响应结构
   - 错误码
3. **生成文档**：输出到 `doc/api/` 目录

## 文档格式标准

### 基本信息
```markdown
## 接口名称

**功能描述：** 详细描述接口的业务用途
**接口地址：** /api/v1/endpoint
**请求方式：** GET/POST/PUT/DELETE
**Content-Type：** application/json
```

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|-----|------|--------|
| page | int | 否 | 页码 | 1 |
| pageSize | int | 否 | 每页数量 | 20 |

### 响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 错误码说明
| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录 |
| 403 | 无权限 |
| 500 | 服务器错误 |

## 示例

```
/generate-api-doc app/routes/
/generate-api-doc internal/handler/
/generate-api-doc controllers/
```

## 输出

- 文档保存到 `doc/api/` 目录
- 命名规则：`{模块名}-api.md`
- 示例：`user-api.md`、`order-api.md`
