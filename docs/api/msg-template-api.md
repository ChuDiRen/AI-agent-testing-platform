# 消息模板管理 API 文档

## 模块概述
提供消息模板的增删改查、预览和渲染功能，支持自定义变量替换 `{{variable}}`。

## 基础路径
```
/api/template
```

## 数据模型

### MsgTemplateInsert（新增模板）
```json
{
  "template_code": "VERIFY_CODE_SMS",      // 模板编码（必填，唯一）
  "template_name": "短信验证码模板",          // 模板名称（必填）
  "template_type": "verify",               // 模板类型（必填）：verify/notify/marketing/warning/system
  "channel_type": "sms",                   // 渠道类型（必填）：system/email/sms/wechat/dingtalk
  "title": "验证码通知",                     // 消息标题（可选）
  "content": "您的验证码是：{{code}}",      // 模板内容（必填）
  "variables": [                           // 变量列表（可选）
    {"name": "code", "desc": "验证码"}
  ],
  "example_params": {                      // 示例参数（可选）
    "code": "123456"
  },
  "status": 1,                             // 状态：0-禁用, 1-启用
  "remark": "短信验证码模板"                // 备注（可选）
}
```

### TemplatePreviewRequest（预览请求）
```json
{
  "template_code": "VERIFY_CODE_SMS",      // 模板编码
  "params": {                              // 替换参数
    "code": "123456"
  }
}
```

---

## API 接口

### 1. 分页查询模板
```
POST /api/template/queryByPage
```

**请求参数**：
```json
{
  "template_code": "VERIFY",              // 模板编码（模糊查询）
  "template_name": "验证码",                // 模板名称（模糊查询）
  "template_type": "verify",               // 模板类型
  "channel_type": "sms",                   // 渠道类型
  "status": 1,                             // 状态
  "page": 1,                               // 页码
  "page_size": 10                          // 每页数量
}
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "template_code": "VERIFY_CODE_SMS",
        "template_name": "短信验证码模板",
        "template_type": "verify",
        "channel_type": "sms",
        "title": "",
        "content": "您的验证码是：{{code}}",
        "variables": [{"name": "code", "desc": "验证码"}],
        "example_params": {"code": "123456"},
        "status": 1,
        "remark": "",
        "created_by": "",
        "created_time": "2025-12-24T10:00:00",
        "updated_time": null
      }
    ],
    "total": 1
  }
}
```

---

### 2. 根据ID查询
```
GET /api/template/queryById?id=1
```

---

### 3. 根据编码查询
```
GET /api/template/queryByCode?template_code=VERIFY_CODE_SMS
```

---

### 4. 新增模板
```
POST /api/template/insert
```

**请求参数**：参见 `MsgTemplateInsert`

**响应**：
```json
{
  "code": 200,
  "msg": "新增成功",
  "data": {
    "id": 1
  }
}
```

---

### 5. 更新模板
```
PUT /api/template/update
```

**请求参数**：
```json
{
  "id": 1,                                // 模板ID（必填）
  "template_name": "短信验证码模板（更新）",   // 其他字段可选
  "content": "新的验证码是：{{code}}"
}
```

---

### 6. 删除模板
```
DELETE /api/template/delete?id=1
```

---

### 7. 预览模板
```
POST /api/template/preview
```

**说明**：使用示例参数或传入参数预览模板效果

**请求参数**：参见 `TemplatePreviewRequest`

**响应**：
```json
{
  "code": 200,
  "msg": "预览成功",
  "data": {
    "title": "验证码通知",
    "content": "您的验证码是：123456"
  }
}
```

---

### 8. 渲染模板
```
POST /api/template/render
```

**说明**：用于实际发送消息时渲染模板

**请求参数**：参见 `TemplatePreviewRequest`

---

### 9. 获取模板类型列表
```
GET /api/template/types
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {"value": "verify", "label": "验证码"},
      {"value": "notify", "label": "通知消息"},
      {"value": "marketing", "label": "营销消息"},
      {"value": "warning", "label": "告警消息"},
      {"value": "system", "label": "系统消息"}
    ],
    "total": 5
  }
}
```

---

### 10. 获取渠道类型列表
```
GET /api/template/channels
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {"value": "system", "label": "站内消息"},
      {"value": "email", "label": "邮件"},
      {"value": "sms", "label": "短信"},
      {"value": "wechat", "label": "微信"},
      {"value": "dingtalk", "label": "钉钉"}
    ],
    "total": 5
  }
}
```

---

## 权限标识

| 操作 | 权限标识 |
|------|---------|
| 查询 | `msgmanage:template:query` |
| 新增 | `msgmanage:template:add` |
| 编辑 | `msgmanage:template:edit` |
| 删除 | `msgmanage:template:delete` |
| 渲染 | `msgmanage:template:render` |

---

## 使用示例

### Python 示例
```python
import httpx

# 新增模板
async def create_template():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5000/api/template/insert",
            json={
                "template_code": "WELCOME_MSG",
                "template_name": "欢迎消息",
                "template_type": "notify",
                "channel_type": "system",
                "title": "欢迎加入",
                "content": "欢迎 {{userName}} 加入平台！",
                "variables": [{"name": "userName", "desc": "用户名"}],
                "example_params": {"userName": "张三"},
                "status": 1
            }
        )
        return response.json()

# 渲染模板
async def render_template():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5000/api/template/render",
            json={
                "template_code": "WELCOME_MSG",
                "params": {"userName": "李四"}
            }
        )
        return response.json()
        # {"title": "欢迎加入", "content": "欢迎 李四 加入平台！"}
```

### curl 示例
```bash
# 新增模板
curl -X POST http://localhost:5000/api/template/insert \
  -H "Content-Type: application/json" \
  -d '{
    "template_code": "VERIFY_CODE_SMS",
    "template_name": "短信验证码",
    "template_type": "verify",
    "channel_type": "sms",
    "content": "验证码：{{code}}，{{expire}}分钟有效",
    "variables": [{"name": "code", "desc": "验证码"}, {"name": "expire", "desc": "有效期"}],
    "example_params": {"code": "123456", "expire": "5"}
  }'

# 渲染模板
curl -X POST http://localhost:5000/api/template/render \
  -H "Content-Type: application/json" \
  -d '{
    "template_code": "VERIFY_CODE_SMS",
    "params": {"code": "654321", "expire": "10"}
  }'
```
