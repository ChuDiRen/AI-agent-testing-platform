# Perf Engine - 基于 Locust 的性能测试引擎

基于 Locust 的性能测试引擎，采用关键字驱动和数据驱动的设计理念。

## 特性

- 🚀 **Locust 引擎**：基于 Locust，支持高并发和分布式测试
- 📝 **YAML 用例**：使用 YAML 编写测试场景，简单直观
- 🐍 **原生 Locust**：支持使用标准 Locust 脚本编写测试（HttpUser、@task 等）
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
│   ├── example-locust-cases/     # YAML 格式用例示例
│   │   ├── context.yaml              # 全局配置（URL、变量等）
│   │   └── *.yaml                    # 测试用例文件
│   │
│   └── example-locust-scripts/   # 原生 Locust 脚本示例
│       ├── locustfile_basic.py       # 基础性能测试
│       ├── locustfile_login_flow.py  # 登录流程测试
│       └── locustfile_advanced.py    # 高级特性示例
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
cd examples/example-locust-scripts

# 启动 Locust Web UI（默认 http://localhost:8089）
locust -f locustfile_basic.py --host=https://httpbin.org

# 无界面模式运行
locust -f locustfile_basic.py --host=https://httpbin.org --headless -u 10 -r 2 -t 60s

# 运行登录流程测试
locust -f locustfile_login_flow.py --host=https://httpbin.org

# 运行高级特性测试（带标签过滤）
locust -f locustfile_advanced.py --host=https://httpbin.org --tags smoke
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

### 原生 Locust 脚本

**适用场景**：

- 开发人员或熟悉 Python 的测试人员
- 需要复杂逻辑的测试场景
- 需要使用 Locust 高级特性（事件钩子、响应验证等）

**基础示例**：

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    """模拟网站用户"""
    wait_time = between(1, 3)  # 任务间等待 1-3 秒
    host = "https://httpbin.org"
    
    @task(3)  # 权重 3
    def get_data(self):
        self.client.get("/get", name="GET /get")
    
    @task(1)  # 权重 1
    def post_data(self):
        self.client.post("/post", json={"user": "test"}, name="POST /post")
    
    def on_start(self):
        """用户启动时执行（如登录）"""
        self.client.post("/post", json={"action": "login"})
```

**响应验证示例**：

```python
@task
def validate_response(self):
    with self.client.get("/get", catch_response=True) as response:
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Got status {response.status_code}")
```

**顺序任务示例**：

```python
from locust import HttpUser, SequentialTaskSet, task

class LoginFlow(SequentialTaskSet):
    @task
    def login(self):
        self.client.post("/post", json={"action": "login"})
    
    @task
    def browse(self):
        self.client.get("/get")
    
    @task
    def logout(self):
        self.client.post("/post", json={"action": "logout"})
        self.interrupt()  # 结束任务集

class FlowUser(HttpUser):
    tasks = [LoginFlow]
    wait_time = between(1, 2)
```

## 关键字说明

基于 Locust 语法设计的关键字驱动系统，完整映射 Locust 核心特性。

### HTTP 请求

| 关键字   | 说明        | 参数                                    |
| -------- | ----------- | --------------------------------------- |
| `get`    | GET 请求    | url, name, params, headers, catch_response |
| `post`   | POST 请求   | url, name, json, data, headers, catch_response |
| `put`    | PUT 请求    | url, name, json, data, headers, catch_response |
| `delete` | DELETE 请求 | url, name, headers, catch_response      |
| `patch`  | PATCH 请求  | url, name, json, headers, catch_response |

**参数说明**：

- `url`: 请求路径（相对于 host）
- `name`: 请求名称（用于 Locust 报告分组）
- `params`: URL 参数
- `headers`: 请求头
- `json`: JSON 数据
- `data`: 表单数据
- `catch_response`: 启用响应验证模式（对应 Locust `catch_response=True`）

### 等待时间

| 关键字           | 说明                    | 参数              |
| ---------------- | ----------------------- | ----------------- |
| `wait`           | 等待时间（兼容 think_time）| seconds, min, max |
| `constant_pacing`| 固定节奏间隔            | seconds           |

**对应 Locust**：

```python
wait_time = between(min, max)  # 对应 wait: min/max
wait_time = constant(seconds)  # 对应 wait: seconds
```

### 响应验证 (catch_response 模式)

| 关键字              | 说明           | 参数                          |
| ------------------- | -------------- | ----------------------------- |
| `assert_status`     | 断言状态码     | expected, fail_on_error       |
| `assert_response_time` | 断言响应时间 | max_ms, fail_on_error         |
| `assert_contains`   | 断言包含文本   | text, fail_on_error           |
| `assert_json`       | 断言 JSON      | path, expected, operator, fail_on_error |
| `assert_header`     | 断言响应头     | name, expected, fail_on_error |
| `mark_success`      | 标记请求成功   | message                       |
| `mark_failure`      | 标记请求失败   | message                       |

**对应 Locust**：

```python
with self.client.get("/api", catch_response=True) as response:
    if response.status_code == 200:
        response.success()
    else:
        response.failure("Error message")
```

### 事务控制

| 关键字            | 说明       | 参数          |
| ----------------- | ---------- | ------------- |
| `transaction`     | 事务块     | name, steps   |
| `start_transaction` | 开始事务 | name          |
| `end_transaction` | 结束事务   | success       |

### 顺序任务集

| 关键字            | 说明                      | 参数               |
| ----------------- | ------------------------- | ------------------ |
| `sequential_tasks`| 顺序任务集                | name, steps, loop  |
| `interrupt`       | 中断任务集                | message            |

**对应 Locust**：

```python
class LoginFlow(SequentialTaskSet):
    @task
    def step1(self): ...
    @task
    def step2(self): ...
    @task
    def step3(self):
        self.interrupt()  # 结束任务集
```

### 数据操作

| 关键字          | 说明           | 参数                |
| --------------- | -------------- | ------------------- |
| `set_var`       | 设置变量       | name, value         |
| `extract_json`  | 提取 JSON      | path, var, index    |
| `extract_regex` | 正则提取       | pattern, var, group |
| `extract_header`| 提取响应头     | name, var           |

### 数据驱动

| 关键字        | 说明           | 参数                    |
| ------------- | -------------- | ----------------------- |
| `random_data` | 随机数据       | source, data, file, var |
| `cycle_data`  | 循环数据（轮询）| source, data, file, var |

**对应 Locust**：

```python
users = [{"username": "user1"}, {"username": "user2"}]
user = random.choice(users)  # 对应 random_data
```

### 条件与循环

| 关键字        | 说明       | 参数                    |
| ------------- | ---------- | ----------------------- |
| `if_condition`| 条件控制   | condition, then, else   |
| `loop`        | 循环执行   | count, steps, delay     |
| `foreach`     | 遍历执行   | items, var, steps       |

### 生命周期钩子

| 关键字      | 说明             | 参数   |
| ----------- | ---------------- | ------ |
| `on_start`  | 用户启动时执行   | steps  |
| `on_stop`   | 用户停止时执行   | steps  |

**对应 Locust**：

```python
class User(HttpUser):
    def on_start(self):
        # 登录等初始化操作
        pass
    
    def on_stop(self):
        # 清理操作
        pass
```

### 日志与调试

| 关键字          | 说明         | 参数           |
| --------------- | ------------ | -------------- |
| `log`           | 打印日志     | message, level |
| `print_response`| 打印响应     | format         |

## YAML 用例编写

### 示例用例文件

| 文件 | 说明 |
|------|------|
| `1_basic_api_test.yaml` | 基础 HTTP 请求、等待时间、响应验证 |
| `2_login_flow_test.yaml` | 事务控制、数据提取、生命周期钩子 |
| `3_data_driven_test.yaml` | 随机数据、循环数据、条件控制、循环 |
| `4_sequential_tasks_test.yaml` | 顺序任务集、事务块 |
| `5_response_validation_test.yaml` | catch_response 模式响应验证 |
| `6_extract_data_test.yaml` | JSONPath、正则、响应头提取 |

### 基础用例

```yaml
name: 基础性能测试
desc: 测试用户接口性能

steps:
  - 发送GET请求:
      关键字: get
      url: /api/users
      name: 获取用户列表
      headers:
        Authorization: "Bearer {{token}}"

  - 用户思考:
      关键字: wait
      min: 1
      max: 3

  - 验证状态码:
      关键字: assert_status
      expected: 200
```

### 响应验证用例 (catch_response 模式)

```yaml
name: 响应验证测试
desc: 对应 Locust catch_response=True 模式

steps:
  - 请求并验证:
      关键字: get
      url: /api/users
      name: 获取用户
      catch_response: true  # 启用响应验证模式

  - 验证状态码:
      关键字: assert_status
      expected: 200
      fail_on_error: true  # 失败时标记请求失败

  - 验证JSON:
      关键字: assert_json
      path: $.data[0].id
      expected: 1
      operator: eq
```

### 顺序任务用例

```yaml
name: 顺序任务测试
desc: 对应 Locust SequentialTaskSet

steps:
  - 购物流程:
      关键字: sequential_tasks
      name: 完整购物流程
      loop: 1
      steps:
        - 登录:
            关键字: post
            url: /login
            name: 1. 登录
            json:
              username: testuser
              password: password123

        - 浏览商品:
            关键字: get
            url: /products
            name: 2. 商品列表

        - 加入购物车:
            关键字: post
            url: /cart
            name: 3. 加入购物车
            json:
              product_id: 12345

        - 结算:
            关键字: post
            url: /checkout
            name: 4. 结算
```

### 数据驱动用例

```yaml
name: 数据驱动测试
desc: 随机数据和循环数据

steps:
  - 随机选择用户:
      关键字: random_data
      source: list
      data:
        - username: user1
          password: pass1
        - username: user2
          password: pass2
      var: current_user

  - 使用随机用户登录:
      关键字: post
      url: /login
      name: POST /login
      json: "{{current_user}}"

  - 循环请求:
      关键字: loop
      count: 3
      delay: 0.5
      steps:
        - 获取分页数据:
            关键字: get
            url: /list
            name: GET /list
            params:
              page: "{{_loop_index}}"
```

### 带生命周期钩子的用例

```yaml
name: 生命周期测试
desc: 对应 Locust on_start/on_stop

# 用户启动时执行 (登录)
on_start:
  - 初始化:
      关键字: post
      url: /login
      name: 登录
      json:
        username: "{{username}}"
        password: "{{password}}"

  - 提取Token:
      关键字: extract_json
      path: $.token
      var: auth_token

# 用户停止时执行 (登出)
on_stop:
  - 登出:
      关键字: post
      url: /logout
      name: 登出

steps:
  - 业务操作:
      关键字: get
      url: /api/data
      name: 获取数据
      headers:
        Authorization: "Bearer {{auth_token}}"
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

## 原生 Locust 脚本说明

### 示例文件

| 文件 | 说明 |
|------|------|
| `locustfile_basic.py` | 基础用法：HttpUser、@task、wait_time |
| `locustfile_login_flow.py` | 登录流程：SequentialTaskSet、用户权重 |
| `locustfile_advanced.py` | 高级特性：事件钩子、响应验证、标签过滤 |

### 运行命令

```bash
cd examples/example-locust-scripts

# Web UI 模式（浏览器访问 http://localhost:8089）
locust -f locustfile_basic.py

# 无界面模式
locust -f locustfile_basic.py --headless -u 100 -r 10 -t 5m --host=https://httpbin.org

# 指定用户类
locust -f locustfile_basic.py --class-picker

# 标签过滤
locust -f locustfile_advanced.py --tags smoke --exclude-tags slow

# 生成 HTML 报告
locust -f locustfile_basic.py --headless -u 10 -r 2 -t 60s --html=report.html
```

### Locust 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-f` | 指定 locustfile | `-f locustfile.py` |
| `--host` | 目标主机 | `--host=https://api.example.com` |
| `-u` | 并发用户数 | `-u 100` |
| `-r` | 每秒启动用户数 | `-r 10` |
| `-t` | 运行时长 | `-t 5m` 或 `-t 300s` |
| `--headless` | 无界面模式 | `--headless` |
| `--html` | 生成 HTML 报告 | `--html=report.html` |
| `--csv` | 生成 CSV 报告 | `--csv=results` |
| `--tags` | 只运行指定标签 | `--tags smoke,critical` |
| `--exclude-tags` | 排除指定标签 | `--exclude-tags slow` |

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
