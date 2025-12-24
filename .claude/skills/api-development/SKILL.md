# API 开发技能

## 触发条件
- 关键词：API、接口、RESTful、GraphQL、端点、后端接口
- 场景：当用户需要设计或开发 API 接口时

## 核心规范

### 规范1：RESTful 设计原则
- 使用名词而非动词：`/users` 而不是 `/getUsers`
- 使用复数形式：`/users` 而不是 `/user`
- 使用连字符：`/user-profiles` 而不是 `/userProfiles`
- 版本控制：`/api/v1/users`

### 规范2：HTTP 状态码使用
| 状态码 | 含义 | 使用场景 |
|-------|------|---------|
| 200 | OK | 成功获取/更新资源 |
| 201 | Created | 成功创建资源 |
| 204 | No Content | 成功删除资源 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Error | 服务器错误 |

### 规范3：统一响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": 1703404800000
}
```

**错误响应：**
```json
{
  "code": 40001,
  "message": "参数校验失败",
  "errors": [
    { "field": "email", "message": "邮箱格式不正确" }
  ],
  "timestamp": 1703404800000
}
```

### 规范4：请求参数规范
- **Query 参数**：用于筛选、分页、排序
- **Path 参数**：用于资源标识
- **Body 参数**：用于创建/更新数据

```python
# FastAPI 示例
@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: UserStatus = Query(None)
):
    pass
```

### 规范5：认证与授权
- 使用 JWT Token 认证
- Token 放在 Authorization Header
- 格式：`Bearer <token>`

## 禁止事项
- ❌ 在 URL 中传递敏感信息
- ❌ 使用 GET 请求修改数据
- ❌ 返回未脱敏的敏感数据
- ❌ 接口不做权限校验
- ❌ 不记录操作日志

## 检查清单
- [ ] 是否符合 RESTful 规范
- [ ] 是否有参数校验
- [ ] 是否有统一的错误处理
- [ ] 是否有认证授权
- [ ] 是否有接口文档
- [ ] 是否有请求日志
