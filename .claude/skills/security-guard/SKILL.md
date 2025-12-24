# 安全防护技能

## 触发条件
- 关键词：安全、XSS、SQL注入、权限、认证、加密、CSRF、漏洞
- 场景：当用户需要处理安全相关问题时

## 核心规范

### 规范1：认证与授权

#### JWT 认证（本项目）
```python
# core/JwtUtil.py
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"

def create_token(data: dict, expires_delta: timedelta = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """验证 Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionDeniedException("Token 已过期")
    except jwt.JWTError:
        raise PermissionDeniedException("Token 无效")
```

#### 权限校验（本项目）
```python
# core/dependencies.py
from fastapi import Depends, HTTPException, Header

async def get_current_user(authorization: str = Header(...)):
    """获取当前用户"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证头")
    token = authorization[7:]
    payload = verify_token(token)
    return payload

def check_permission(permission: str):
    """权限校验装饰器"""
    async def permission_checker(user = Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="权限不足")
        return user
    return permission_checker
```

### 规范2：SQL 注入防护

```python
# ✅ 正确：使用 SQLModel/SQLAlchemy 参数化查询
from sqlmodel import select

statement = select(User).where(User.name == name)  # 参数化
result = session.exec(statement).all()

# ✅ 正确：使用 text() 绑定参数
from sqlalchemy import text

statement = text("SELECT * FROM user WHERE name = :name")
result = session.execute(statement, {"name": name})

# ❌ 错误：字符串拼接（SQL 注入风险）
statement = f"SELECT * FROM user WHERE name = '{name}'"  # 危险！
```

### 规范3：XSS 防护

```python
# 后端：输出转义
import html

def escape_html(text: str) -> str:
    """HTML 转义"""
    return html.escape(text)

# 存储时转义
data.description = escape_html(request.description)
```

```vue
<!-- 前端：使用 v-text 而非 v-html -->
<template>
  <!-- ✅ 安全：自动转义 -->
  <div>{{ userInput }}</div>
  <div v-text="userInput"></div>
  
  <!-- ❌ 危险：可能执行脚本 -->
  <div v-html="userInput"></div>
</template>
```

### 规范4：敏感数据处理

```python
# 密码加密存储
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 敏感字段脱敏
def mask_phone(phone: str) -> str:
    """手机号脱敏"""
    if len(phone) == 11:
        return phone[:3] + "****" + phone[7:]
    return phone

def mask_id_card(id_card: str) -> str:
    """身份证脱敏"""
    if len(id_card) == 18:
        return id_card[:6] + "********" + id_card[14:]
    return id_card
```

### 规范5：文件上传安全

```python
# 文件类型白名单
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'application/pdf'}

def validate_file(file: UploadFile):
    """验证上传文件"""
    # 检查扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(f"不允许的文件类型: {ext}")
    
    # 检查 MIME 类型
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationException(f"不允许的文件类型: {file.content_type}")
    
    # 检查文件大小
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise ValidationException("文件大小超过限制")
    file.file.seek(0)
    
    return True
```

### 规范6：日志安全

```python
# ❌ 错误：记录敏感信息
logger.info(f"用户登录: {username}, 密码: {password}")

# ✅ 正确：脱敏处理
logger.info(f"用户登录: {username}")

# ❌ 错误：记录完整 Token
logger.info(f"Token: {token}")

# ✅ 正确：只记录部分
logger.info(f"Token: {token[:10]}...")
```

### 规范7：前端安全

```javascript
// Token 存储
// ✅ 推荐：httpOnly Cookie（需后端配合）
// 或者：localStorage（XSS 风险较高时避免）
localStorage.setItem('token', token)

// 请求拦截器添加 Token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 敏感操作二次确认
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除？此操作不可恢复', '警告', {
    type: 'warning'
  })
  // 执行删除
}
```

## 安全检查清单

| 检查项 | 说明 |
|--------|------|
| SQL 注入 | 是否使用参数化查询 |
| XSS | 是否转义用户输入 |
| 认证 | 是否验证 Token |
| 授权 | 是否校验权限 |
| 密码 | 是否加密存储 |
| 文件上传 | 是否验证类型和大小 |
| 日志 | 是否脱敏敏感信息 |

## 禁止事项
- ❌ 明文存储密码
- ❌ SQL 字符串拼接
- ❌ 使用 v-html 渲染用户输入
- ❌ 日志记录敏感信息
- ❌ 不验证文件类型
