# Perf Engine - 基于 Locust 的性能测试引擎

基于 Locust 的性能测试引擎，采用关键字驱动和数据驱动的设计理念。

## 特性

- 🚀 **Locust 引擎**：基于 Locust，支持高并发和分布式测试
- 📝 **YAML 用例**：使用 YAML 编写测试场景，简单直观
- 🐍 **原生 Locust**：支持使用 Python Locust 脚本编写测试
- ⏱️ **性能专用关键字**：思考时间、事务控制、响应时间检查
- 📊 **HTML 报告**：自动生成可视化性能报告
- 🔄 **变量支持**：支持参数化和变量替换
- 🔧 **易扩展**：支持自定义关键字扩展

## 目录结构

```
perf-engine/
├── README.md                  # 项目说明文档（本文件）
├── requirements.txt           # Python 依赖包配置
├── setup.py                   # 安装配置脚本
├── plugin.yaml                # 插件配置文件
│
├── perfrun/                   # 核心测试引擎代码
│   ├── __init__.py           # 包初始化文件
│   ├── cli.py                # 命令行入口（支持直接运行）
│   ├── plugin_config.py      # 插件配置管理
│   │
│   ├── core/                 # 核心运行器模块
│   │   ├── __init__.py
│   │   ├── locust_runner.py      # Locust 测试执行器
│   │   ├── globalContext.py      # 全局上下文管理
│   │   └── exceptions.py         # 自定义异常类
│   │
│   ├── extend/               # 关键字扩展模块
│   │   ├── __init__.py
│   │   ├── keywords.py           # 关键字实现库
│   │   └── keywords.yaml         # 关键字配置文件
│   │
│   ├── parse/                # 用例解析器模块
│   │   ├── __init__.py
│   │   └── yaml_parser.py        # YAML 用例解析器
│   │
│   └── utils/                # 工具类模块
│       ├── __init__.py
│       └── VarRender.py          # 变量渲染工具
│
├── examples/                 # 示例用例目录
│   └── example-locust-cases/     # YAML 格式用例示例
│       ├── context.yaml              # 全局配置（URL、变量等）
│       └── *.yaml                    # 测试用例文件
│
└── reports/                  # 测试报告目录（运行时自动生成）
    └── report_*.html             # HTML 可视化报告
```

> **注意**:
>
> - `__pycache__/` 等缓存目录已自动忽略
> - `reports/` 目录在首次运行测试后自动创建
> - 所有模块使用相对导入，`cli.py` 使用绝对导入以支持直接运行

## 导入策略说明

- **cli.py**: 作为命令行入口文件,使用**绝对导入**,支持直接运行 `python cli.py`
- **其他模块**: perfrun 内部模块(core/extend/parse/utils)使用**相对导入**,提高模块独立性

## 快速开始

### 1. 安装依赖

```bash
cd perf-engine
pip install -r requirements.txt
```

### 2. 运行示例用例

#### 方式一：运行 YAML 用例

**推荐方式 - 使用命令行**:

```bash
perf-engine --cases=examples/example-locust-cases --host=https://httpbin.org --users=10 --run-time=30s
```

**模块方式运行**:

```bash
cd perf-engine
python -m perfrun.cli --cases=examples/example-locust-cases --host=https://httpbin.org --users=10 --run-time=30s
```

**直接运行 cli.py**:

```bash
cd perfrun
python cli.py --cases=../examples/example-locust-cases --host=https://httpbin.org --users=10 --run-time=30s
```

#### 方式二：运行原生 Locust 脚本

```bash
cd examples
locust -f my_locustfile.py --host=https://httpbin.org
```

### 3. 查看测试报告

测试执行完成后，HTML 报告会自动生成在 `reports/` 目录下：

```bash
# 报告已自动生成，直接用浏览器打开查看
cd perf-engine/reports
# 打开 report_YYYYMMDD_HHMMSS.html
```

**报告位置**：

- HTML 报告：`perf-engine/reports/report_*.html`
- CSV 数据：`perf-engine/reports/locust_*.csv`

## 测试方式对比

### YAML 驱动测试

**适用场景**：

- 测试人员不熟悉编程
- 快速编写简单性能测试用例
- 数据驱动测试

**示例**：

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
```

### 原生 Locust 测试

**适用场景**：

- 开发人员或熟悉 Python 的测试人员
- 需要复杂逻辑的测试场景
- 需要使用 Locust 高级特性

**示例**：

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def load_test(self):
        self.client.get("/api/users")
        
    @task(3)
    def submit_data(self):
        self.client.post("/api/data", json={"user": "test"})
```

## 关键字说明

### HTTP 请求

| 关键字   | 说明        | 参数                         |
| -------- | ----------- | ---------------------------- |
| `get`    | GET 请求    | url, name, params, headers   |
| `post`   | POST 请求   | url, name, json, data, headers |
| `put`    | PUT 请求    | url, name, json, data, headers |
| `delete` | DELETE 请求 | url, name, headers           |

**参数说明**：

- `url`: 请求路径（相对于 host）
- `name`: 请求名称（用于报告分组）
- `params`: URL 参数
- `headers`: 请求头
- `json`: JSON 数据
- `data`: 表单数据

### 思考时间

| 关键字           | 说明           | 参数              |
| ---------------- | -------------- | ----------------- |
| `think_time`     | 模拟用户思考   | seconds, min, max |
| `constant_pacing`| 固定间隔       | seconds           |

**参数说明**：

- `seconds`: 固定等待秒数
- `min`: 最小秒数（随机等待）
- `max`: 最大秒数（随机等待）

### 响应验证

| 关键字              | 说明           | 参数          |
| ------------------- | -------------- | ------------- |
| `check_status`      | 检查状态码     | expected      |
| `check_response_time` | 检查响应时间 | max_ms        |
| `check_contains`    | 检查包含文本   | text          |
| `validate_json`     | 验证 JSON      | path, expected |

### 事务控制

| 关键字            | 说明     | 参数    |
| ----------------- | -------- | ------- |
| `start_transaction` | 开始事务 | name    |
| `end_transaction` | 结束事务 | success |

### 数据操作

| 关键字        | 说明         | 参数        |
| ------------- | ------------ | ----------- |
| `set_var`     | 设置变量     | name, value |
| `extract_json`| 提取 JSON    | path, var   |
| `log`         | 打印日志     | message     |

## YAML 用例编写

### 基础用例

```yaml
name: 基础性能测试
desc: 测试用户接口性能

context:
  base_url: https://api.example.com
  username: testuser

steps:
  - 发送GET请求:
      关键字: get
      url: /api/users
      name: 获取用户列表
      headers:
        Authorization: "Bearer {{token}}"

  - 用户思考:
      关键字: think_time
      min: 1
      max: 3

  - 验证状态码:
      关键字: check_status
      expected: 200
```

### 带事务的用例

```yaml
name: 事务性能测试
desc: 测试登录到下单完整流程

steps:
  - 开始登录事务:
      关键字: start_transaction
      name: 用户登录

  - 登录请求:
      关键字: post
      url: /api/login
      name: 登录
      json:
        username: "{{username}}"
        password: "{{password}}"

  - 提取Token:
      关键字: extract_json
      path: $.token
      var: auth_token

  - 结束登录事务:
      关键字: end_transaction
      success: true

  - 用户思考:
      关键字: think_time
      seconds: 2
```

## 配置文件

`context.yaml` 示例：

```yaml
host: https://api.example.com
username: testuser
password: test123
timeout: 30
```

## 命令行参数

| 参数          | 说明                   | 默认值 |
| ------------- | ---------------------- | ------ |
| `--cases`     | YAML 用例目录          | -      |
| `--host`      | 目标主机 URL           | -      |
| `--users`     | 并发用户数             | 10     |
| `--spawn-rate`| 用户生成速率（每秒）   | 1      |
| `--run-time`  | 运行时长（如 60s, 5m） | 60s    |
| `--headless`  | 无界面模式             | true   |
| `--html-report`| 生成 HTML 报告        | true   |
| `--type`      | 用例格式（yaml/script）| yaml   |

## 自定义关键字

```python
class MyPerfKeyword:
    def my_custom_keyword(self, **kwargs):
        # 实现自定义逻辑
        pass
```

## 常见问题

### 1. 为什么 cli.py 使用绝对导入，其他模块使用相对导入？

- **cli.py**: 作为入口文件，需要支持直接运行 `python cli.py`，因此使用绝对导入
- **其他模块**: 内部模块使用相对导入，提高模块独立性和可移植性
- **最佳实践**: 入口文件绝对导入，内部模块相对导入

### 2. 运行 cli.py 时报 ImportError 怎么办？

确保在正确的目录运行:

```bash
cd perfrun
python cli.py --cases=../examples/example-locust-cases --host=https://httpbin.org
```

或使用模块方式:

```bash
cd perf-engine
python -m perfrun.cli --cases=examples/example-locust-cases --host=https://httpbin.org
```

### 3. 如何在 YAML 和 Locust 脚本之间选择？

- **YAML**：适合简单测试、数据驱动、非编程人员
- **Locust 脚本**：适合复杂逻辑、需要编程灵活性、开发人员

### 4. 如何设置不同的并发模式？

```bash
# 固定并发
perf-engine --cases=... --users=100 --spawn-rate=10 --run-time=5m

# 逐步增加
perf-engine --cases=... --users=100 --spawn-rate=1 --run-time=10m
```

### 5. 报告中的指标说明？

- **RPS**: 每秒请求数
- **Avg/Min/Max**: 平均/最小/最大响应时间（毫秒）
- **P50/P90/P95/P99**: 响应时间百分位数
- **Fail Rate**: 失败率

## 与 API Engine 的关系

Perf Engine 与 API Engine 是姊妹项目：

| 特性         | API Engine              | Perf Engine             |
| ------------ | ----------------------- | ----------------------- |
| 测试类型     | 功能测试                | 性能测试                |
| 底层框架     | Pytest + Requests       | Locust                  |
| 并发模型     | 串行执行                | 并发执行                |
| 报告格式     | Allure                  | HTML + CSV              |
| 适用场景     | 接口功能验证            | 负载/压力测试           |

两者共享相似的设计理念：
- 关键字驱动
- 数据驱动
- YAML 用例格式
- 模块化架构

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
