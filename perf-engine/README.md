# Perf Engine - 基于 Locust 的性能测试引擎

基于 Locust 的性能测试引擎，采用关键字驱动设计，支持 YAML 格式编写性能测试用例。

## 特性

- 🚀 **Locust 引擎**：基于 Locust，支持高并发和分布式测试
- 📝 **YAML 用例**：使用 YAML 编写测试场景，简单直观
- ⏱️ **性能专用关键字**：思考时间、事务控制、响应时间检查
- 📊 **HTML 报告**：自动生成可视化性能报告
- 🔄 **变量支持**：支持参数化和变量替换

## 快速开始

### 安装

```bash
cd perf-engine
pip install -e .
```

### 运行测试

```bash
perf-engine --cases=examples/example-locust-cases --host=https://httpbin.org --users=10 --run-time=30s
```

## YAML 用例示例

```yaml
name: API负载测试
desc: 测试 API 性能

steps:
  - 获取数据:
      关键字: get
      url: /api/users
      name: 获取用户列表

  - 用户思考:
      关键字: think_time
      min: 1
      max: 3

  - 提交数据:
      关键字: post
      url: /api/data
      name: 提交数据
      json:
        user: "{{username}}"

  - 验证响应:
      关键字: check_status
      expected: 200

  - 检查响应时间:
      关键字: check_response_time
      max_ms: 2000
```

## 关键字说明

### HTTP 请求

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `get` | GET 请求 | url, name, params, headers |
| `post` | POST 请求 | url, name, json, data, headers |
| `put` | PUT 请求 | url, name, json, data, headers |
| `delete` | DELETE 请求 | url, name, headers |

### 思考时间

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `think_time` | 模拟用户思考 | seconds, min, max |
| `constant_pacing` | 固定间隔 | seconds |

### 响应验证

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `check_status` | 检查状态码 | expected |
| `check_response_time` | 检查响应时间 | max_ms |
| `check_contains` | 检查包含文本 | text |
| `validate_json` | 验证 JSON | path, expected |

### 事务控制

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `start_transaction` | 开始事务 | name |
| `end_transaction` | 结束事务 | success |

### 数据操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `set_var` | 设置变量 | name, value |
| `extract_json` | 提取 JSON | path, var |
| `log` | 打印日志 | message |

## 命令行参数

```
--cases PATH        YAML 用例目录
--host URL          目标主机
--users NUM         并发用户数 (默认: 10)
--spawn-rate NUM    用户生成速率 (默认: 1)
--run-time TIME     运行时长 (默认: 60s)
--headless          无界面模式 (默认: true)
```

## License

MIT License
