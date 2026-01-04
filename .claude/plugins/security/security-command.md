# /security - 安全扫描

## 描述
扫描代码中的安全漏洞，基于 OWASP Top 10 标准。

## 使用方式
```
/security [目标] [--mode <模式>] [--agent]
```

## 参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `目标` | 文件/目录路径 | 当前目录 |
| `--mode` | `quick`/`full` | `quick` |
| `--agent` | 使用 security-auditor Agent | 否 |

## 检查项

参考 `@templates/security-patterns.md`：

### OWASP Top 10
| 类别 | 检查项 |
|------|--------|
| A01 | 访问控制 - 越权访问、IDOR |
| A02 | 加密失败 - 明文密码、弱加密 |
| A03 | 注入 - SQL/XSS/命令注入 |
| A04 | 不安全设计 - 业务逻辑漏洞 |
| A05 | 配置错误 - 默认凭据、调试模式 |
| A06 | 组件漏洞 - 已知 CVE |
| A07 | 认证失败 - 弱密码、会话固定 |
| A08 | 数据完整性 - 不安全反序列化 |
| A09 | 日志监控 - 敏感信息泄露 |
| A10 | SSRF - 服务端请求伪造 |

## 输出格式

参考 `@templates/security-patterns.md` 中的报告格式。

## 示例
```bash
/security                            # 快速扫描
/security platform-fastapi-server/   # 扫描后端
/security --mode full                # 全面审计
/security --agent                    # 使用 Agent 深度分析
```
