# 安全模式模板库

本文件包含安全检查规则和修复模式，供安全相关插件引用。

## OWASP Top 10 检查清单

| 类别 | 检查项 | 严重级别 |
|------|--------|----------|
| **A01 访问控制** | 越权访问、IDOR | 🔴 严重 |
| **A02 加密失败** | 明文密码、弱加密 | 🔴 严重 |
| **A03 注入** | SQL/XSS/命令注入 | 🔴 严重 |
| **A04 不安全设计** | 业务逻辑漏洞 | 🟠 高危 |
| **A05 配置错误** | 默认凭据、调试模式 | 🟠 高危 |
| **A06 组件漏洞** | 已知CVE | 🟠 高危 |
| **A07 认证失败** | 弱密码、会话固定 | 🔴 严重 |
| **A08 数据完整性** | 不安全反序列化 | 🟠 高危 |
| **A09 日志监控** | 敏感信息泄露 | 🟡 中危 |
| **A10 SSRF** | 服务端请求伪造 | 🟠 高危 |

---

## 漏洞模式与修复

### SQL 注入

❌ **危险代码**
```python
# 字符串拼接
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# format 格式化
query = "SELECT * FROM users WHERE name = '{}'".format(name)
```

✅ **安全代码**
```python
# 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SQLModel ORM
statement = select(User).where(User.id == user_id)
result = session.exec(statement).first()
```

---

### XSS 跨站脚本

❌ **危险代码**
```vue
<!-- v-html 直接渲染用户输入 -->
<div v-html="userInput"></div>

<!-- 动态属性拼接 -->
<a :href="'javascript:' + userInput">链接</a>
```

✅ **安全代码**
```vue
<!-- 文本插值自动转义 -->
<div>{{ userInput }}</div>

<!-- 使用 DOMPurify 净化 -->
<script setup>
import DOMPurify from 'dompurify'
const safeHtml = computed(() => DOMPurify.sanitize(userInput.value))
</script>
<div v-html="safeHtml"></div>
```

---

### 认证授权

❌ **危险代码**
```python
# 硬编码凭据
password = "admin123"
api_key = "sk-xxxx"

# 弱密码校验
if len(password) >= 6:
    pass
```

✅ **安全代码**
```python
# 环境变量
import os
api_key = os.getenv("API_KEY")

# 强密码校验
import re
def validate_password(password: str) -> bool:
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*]", password):
        return False
    return True
```

---

### 敏感数据保护

❌ **危险代码**
```python
# 日志泄露
logger.info(f"User login: {username}, password: {password}")

# 响应泄露
return {"user": user, "password": user.password}
```

✅ **安全代码**
```python
# 脱敏日志
logger.info(f"User login: {username}")

# 响应过滤
return {"user": user.dict(exclude={"password", "id_card"})}

# Pydantic 模型排除
class UserResponse(BaseModel):
    class Config:
        fields = {'password': {'exclude': True}}
```

---

## 检测正则表达式

```python
SECURITY_PATTERNS = {
    "sql_injection": [
        r'execute\s*\(\s*f["\']',
        r'\.format\s*\([^)]*\)\s*\)',
        r'\+\s*["\'].*SELECT|INSERT|UPDATE|DELETE',
    ],
    "xss": [
        r'v-html\s*=\s*["\'][^"\']*user',
        r'innerHTML\s*=',
        r'document\.write\s*\(',
    ],
    "hardcoded_secrets": [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
    ],
    "sensitive_logging": [
        r'log.*password',
        r'print.*token',
        r'logger.*secret',
    ],
}
```

---

## 输出报告格式

```
╔══════════════════════════════════════════════════════════════════╗
║                    🔒 安全审计报告                                ║
╠══════════════════════════════════════════════════════════════════╣
║  📊 扫描统计                                                      ║
║  ─────────────────────────────────────────────────────────────   ║
║  文件: 25    漏洞: 8    严重: 2    高危: 3    中危: 3             ║
╠══════════════════════════════════════════════════════════════════╣
║  🔴 严重漏洞 (2)                                                  ║
║  ─────────────────────────────────────────────────────────────   ║
║  [A03] userService.py:45 - SQL 注入                              ║
║        代码: f"SELECT * FROM users WHERE id = {user_id}"         ║
║        修复: 使用参数化查询                                       ║
║                                                                  ║
║  [A02] config.py:12 - 硬编码密码                                  ║
║        代码: password = "admin123"                               ║
║        修复: 使用环境变量                                         ║
╠══════════════════════════════════════════════════════════════════╣
║  🟠 高危漏洞 (3)                                                  ║
║  ─────────────────────────────────────────────────────────────   ║
║  [A03] UserList.vue:28 - XSS 风险                                ║
║  [A07] auth.py:15 - 弱密码策略                                    ║
║  [A05] settings.py:8 - DEBUG 模式开启                            ║
╚══════════════════════════════════════════════════════════════════╝
```
