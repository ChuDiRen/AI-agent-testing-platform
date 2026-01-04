# Security Guard Skill

安全守护技能，提供代码安全检查能力。

## 触发条件
- `/security` 命令
- `/review --mode security` 命令
- 用户请求安全检查

## 检查能力

参考 `@templates/security-patterns.md`：

### 注入攻击检测
- SQL 注入：字符串拼接、format 格式化
- XSS：v-html、innerHTML、document.write
- 命令注入：os.system、subprocess

### 认证授权检测
- 硬编码凭据：password、api_key、secret
- 弱密码策略：长度、复杂度
- 会话管理：固定会话、过期策略

### 敏感数据检测
- 日志泄露：password、token、secret
- 响应泄露：未过滤敏感字段
- 配置泄露：DEBUG 模式、默认凭据

### 检测正则
```python
PATTERNS = {
    "sql_injection": [r'execute\s*\(\s*f["\']', r'\.format\s*\('],
    "xss": [r'v-html\s*=', r'innerHTML\s*='],
    "hardcoded_secrets": [r'password\s*=\s*["\']', r'api_key\s*='],
}
```

## 输出要求

1. 按 OWASP 类别分类
2. 标注严重级别（严重/高危/中危）
3. 提供漏洞代码位置
4. 给出安全修复代码

## 与其他组件协作

- 深度审计 → 调用 `security-auditor` Agent
- 代码审查中 → 被 `code-quality` 插件调用
