# /api-doc - 生成 API 文档

## 描述
根据后端代码自动生成 API 接口文档。

## 使用方式
```
/api-doc [--module <模块名>] [--format <格式>]
```

## 参数说明
- `--module`: 指定模块，不指定则生成全部
- `--format`: 输出格式，可选：`markdown`、`openapi`、`html`

## 文档内容

### 接口信息
- 接口路径
- 请求方法
- 请求参数（Query、Path、Body）
- 响应格式
- 错误码说明

### 文档模板
```markdown
## 用户管理

### 获取用户列表

**请求**
- 方法: `GET`
- 路径: `/api/users`

**Query 参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |
| keyword | string | 否 | 搜索关键词 |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

**错误码**
| 错误码 | 说明 |
|--------|------|
| 40001 | 参数校验失败 |
| 40101 | 未授权 |
```

## 输出位置
- Markdown: `doc/api/{module}-api.md`
- OpenAPI: `doc/openapi.yaml`
- HTML: `doc/api-doc.html`

## 注意事项
- 需要后端代码有完整的类型注解
- 会读取 docstring 作为接口描述
- 支持从 Pydantic Schema 提取字段信息
