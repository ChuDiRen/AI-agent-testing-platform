# Test Engine - 统一自动化测试引擎

统一的自动化测试引擎，支持 **API 测试**、**Web UI 测试**、**移动端测试** 和 **性能测试**，采用关键字驱动和数据驱动的设计理念。

## ✨ 特性

### 核心特性

- 🔄 **统一入口**：一个命令支持 API、Web、移动端和性能四种测试类型
- ✨ **关键字驱动**：丰富的测试关键字库，简化用例编写
- 📝 **YAML 格式**：使用 YAML 编写测试用例，清晰易读
- 🐍 **原生 Pytest**：支持使用 Python pytest 脚本编写测试
- 🔄 **数据驱动**：支持 DDT 数据驱动测试
- 📊 **Allure 报告**：集成 Allure 测试报告
- 🔧 **易扩展**：支持自定义关键字扩展

### API 测试特性

- 📡 **纯异步架构** - 基于 httpx 异步库,真正的异步执行
- ⚡ **连接池复用** - 智能连接池管理,性能提升 3-5 倍
- 🔄 **HTTP/2 支持** - 现代化协议支持
- 🔧 **灵活配置** - 支持连接池、超时、重试等参数配置
- 🗄️ **数据库操作** - 支持数据库查询和断言
- 🔗 **接口关联** - 支持接口间数据传递
- 📤 **文件上传下载** - 支持文件上传和下载功能

### Web 测试特性

- 🌐 基于 Playwright - 现代化 Web 自动化测试框架
- 🎯 多浏览器支持（Chromium、Firefox、WebKit）
- ⚡ 内置自动等待 - 无需显式等待
- 🎭 现代化定位方式（role、text、label、placeholder 等）
- 📸 失败自动截图 + 完整页面截图
- 🖱️ 丰富的元素操作（点击、输入、悬停、拖拽等）
- 🔍 强大的断言功能（expect API）
- 📊 内置追踪功能（trace viewer）
- 🚀 更快的执行速度和更好的稳定性

### 移动端测试特性

- 📱 基于 Appium - 支持 Android 和 iOS 双平台
- 🎯 多种定位方式（id、accessibility_id、xpath、uiautomator、ios_predicate 等）
- 📸 失败自动截图 + 页面源码附加
- 👆 丰富的手势操作（点击、长按、滑动、捏合、拖拽等）
- 📊 70+ 内置关键字，覆盖移动端全部操作场景
- 🔄 App 生命周期管理（安装、卸载、启动、终止等）
- 📋 剪贴板、通知栏、Context 切换等高级功能

### 性能测试特性

- ⚡ 基于 Locust - 高性能分布式负载测试框架
- 📈 实时监控 - Web UI 实时查看测试指标
- 🔄 关键字驱动 - 使用 YAML 编写性能测试用例
- 🐍 **Pytest 支持** - 使用 Python pytest 脚本编写性能测试（新增）
- 📊 丰富指标 - RPS、响应时间、失败率等
- 🎯 灵活配置 - 并发用户数、生成速率、运行时长
- 📝 HTML 报告 - 自动生成详细的测试报告
- 🔗 接口关联 - 支持接口间数据传递
- 🧩 可扩展 - 支持自定义 Locust 脚本

## 📁 目录结构

```
test-engine/
├── testrun/                # 统一入口模块
│   ├── __init__.py
│   └── cli.py             # 统一命令行入口
├── testengine_api/        # API测试引擎
│   ├── core/              # 核心运行器
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   ├── utils/             # 工具类
│   └── pytest.ini         # Pytest 配置文件
├── testengine_web/        # Web测试引擎
│   ├── core/              # 核心运行器
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   ├── utils/             # 工具类
│   └── pytest.ini         # Pytest 配置文件
├── testengine_mobile/     # 移动端测试引擎
│   ├── core/              # 核心运行器
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   ├── utils/             # 工具类
│   └── pytest.ini         # Pytest 配置文件
├── testengine_perf/       # 性能测试引擎
│   ├── core/              # 核心运行器 (Locust)
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   ├── utils/             # 工具类
│   └── pytest.ini         # Pytest 配置文件
├── examples/              # 示例用例
│   ├── api-cases/         # API测试示例
│   ├── web-cases/         # Web测试示例
│   ├── mobile-cases_yaml/ # 移动端测试示例
│   ├── perf-cases_yaml/   # 性能测试示例（YAML）
│   └── perf-cases_pytest/ # 性能测试示例（Pytest）
├── reports/               # 测试报告目录（运行时自动生成）
│   ├── allure-results/    # Allure 原始测试数据（JSON）
│   ├── allure-report/     # Allure HTML 可视化报告
│   ├── screenshots/       # Web 测试截图（仅 Web 测试）
│   └── logdata/           # Pytest 测试日志
│       └── log.log       # 测试执行日志文件
├── requirements.txt       # 依赖配置
├── setup.py              # 安装配置
└── README.md             # 项目文档
```

> **注意**:
>
> - `__pycache__/` 和 `.pytest_cache/` 等缓存目录已自动忽略
> - `reports/` 目录在首次运行测试后自动创建
> - 所有日志统一保存到 `reports/logdata/` 目录
> - Web 测试的所有截图统一保存到 `reports/screenshots/` 目录

## 🚀 快速开始

### 1. 安装依赖

```bash
cd test-engine
pip install -r requirements.txt
```

**注意**: API 测试引擎已从 `requests` 迁移到 `httpx` 异步库,享受更高性能和 HTTP/2 支持。

或者安装整个包：

```bash
pip install -e .
```

### 2. 运行测试

#### 方式一：通过命令行指定引擎类型

```bash
# API 测试
python -m testrun.cli --engine-type=api --type=yaml --cases=examples/api-cases

# Web 测试（有头模式）
python -m testrun.cli --engine-type=web --type=yaml --cases=examples/web-cases --browser=chromium --headless=false

# Web 测试（无头模式 - 适用于 CI/CD）
python -m testrun.cli --engine-type=web --type=yaml --cases=examples/web-cases --browser=chromium --headless=true

# 移动端测试（需要先启动 Appium Server）
python -m testrun.cli --engine-type=mobile --type=yaml --cases=examples/mobile-cases_yaml --platform=android --app=/path/to/app.apk

# 安装后可直接使用 testrun 命令
testrun --engine-type=api --type=yaml --cases=examples/api-cases
testrun --engine-type=web --type=yaml --cases=examples/web-cases --browser=chromium --headless=true
testrun --engine-type=mobile --type=yaml --cases=examples/mobile-cases_yaml --platform=android

# 性能测试（YAML 格式）
python -m testrun.cli --engine-type=perf --type=yaml --cases=examples/perf-cases_yaml --host=https://api.example.com --users=100 --run_time=60s

# 性能测试（Pytest 格式 - 新增）
python -m testrun.cli --engine-type=perf --type=pytest --cases=examples/perf-cases_pytest

# 安装后可直接使用 testrun 命令
testrun --engine-type=perf --type=yaml --cases=examples/perf-cases_yaml --host=https://api.example.com --users=50 --spawn_rate=5
testrun --engine-type=perf --type=pytest --cases=examples/perf-cases_pytest
```

#### 方式二：通过配置文件指定

在用例目录的 `context.yaml` 中配置 `ENGINE_TYPE`:

```yaml
# context.yaml
ENGINE_TYPE: api  # 或 web 或 mobile 或 perf
```

然后运行：

```bash
# 自动从 context.yaml 读取 ENGINE_TYPE
python -m testrun.cli --type=yaml --cases=examples/api-cases

# 或使用 testrun 命令
testrun --type=yaml --cases=examples/api-cases
```

### 3. 查看测试报告

测试执行完成后，报告会自动生成到 `reports/` 目录：

```bash
# 打开 Allure 报告（测试执行后自动生成）
allure open reports/allure-report

# 查看测试日志
cat reports/logdata/log.log

# 查看 Web 测试截图（仅 Web 测试）
ls reports/screenshots/
```

**报告文件说明**:

- `reports/allure-report/` - HTML 可视化报告，可在浏览器中查看
- `reports/allure-results/` - Allure 原始数据（JSON 格式）
- `reports/logdata/log.log` - 测试执行日志
- `reports/screenshots/` - Web 测试截图（仅 Web 测试）

## 📖 使用指南

### 指定测试引擎类型

Test Engine 支持两种方式指定测试类型，**命令行参数优先级更高**：

#### 1. 命令行参数（优先级高）

```bash
testrun --engine-type=api ...   # API 测试
testrun --engine-type=web ...   # Web 测试
```

#### 2. 配置文件

在用例目录的 `context.yaml` 中添加：

```yaml
ENGINE_TYPE: api  # 或 web
```

### API 测试示例

#### YAML 用例格式

```yaml
desc: 登录接口测试
steps:
  - 发送登录请求:
      关键字: send_request
      method: POST
      url: "{{URL}}/api/login"
      json:
        username: admin
        password: admin123
  
  - 提取token:
      关键字: ex_jsonData
      EXVALUE: "$.data.token"
      VARNAME: "token"
  
  - 断言状态码:
      关键字: assert_text_comparators
      VALUE: "{{response.status_code}}"
      OP_STR: "=="
      EXPECTED: 200
```

#### 常用关键字

| 关键字 | 说明 | 主要参数 |
|--------|------|---------|
| `send_request` | 发送 HTTP 请求 | method, url, params, headers, data, json |
| `ex_jsonData` | 提取 JSON 数据 | EXVALUE, VARNAME |
| `ex_mysqlData` | 提取数据库数据 | 数据库, SQL, 引用变量 |
| `assert_text_comparators` | 文本比较断言 | VALUE, OP_STR, EXPECTED |

#### Excel 用例格式 📊

Excel 用例格式适合非编程人员使用，通过 Excel 表格的方式编写测试用例。

**Excel 文件结构**：

一个完整的 Excel 测试用例文件包含 3 个 sheets：

1. **context** - 存储配置信息
2. **关键字说明** - 关键字参数说明（参考用）
3. **测试用例** - 具体的测试用例

**context sheet 示例**：

| 类型 | 变量描述 | 变量值 |
|------|----------|--------|
| 变量 | URL | http://example.com/ |
| 变量 | username | admin |
| 变量 | password | 123456 |
| 数据库 | my_mysql | {"host": "localhost", "port": 3306, "user": "root", "password": "123456", "db": "testdb"} |

**测试用例 sheet 示例**：

| 编号 | 测试用例标题 | 一级模块 | 二级模块 | 步骤 | 步骤描述 | 关键字 | 参数_1 | 参数_2 | 参数_3 | 参数_4 |
|------|-------------|----------|----------|------|----------|--------|--------|--------|--------|--------|
| 1 | 登录接口测试 | 用户模块 | 登录模块 | 1 | 发送登录请求 | request_post_form_urlencoded | {{URL}}/api/login | | | {"username": "{{username}}", "password": "{{password}}"} |
| | | | | 2 | 提取token | ex_jsonData | $..token | | token | |
| | | | | 3 | 断言状态码 | assert_text_comparators | {{response.status_code}} | 200 | == | |

**运行 Excel 用例**：

```bash
# API 测试
python -m testrun.cli --engine-type=api --type=excel --cases=examples/api-cases_execl

# Web 测试
python -m testrun.cli --engine-type=web --type=excel --cases=examples/web-cases_execl
```

**Excel 用例特点**：
- ✅ 无需编程基础，易于上手
- ✅ 适合团队协作，非技术人员也能编写
- ✅ 支持变量替换（使用 `{{变量名}}` 语法）
- ✅ 支持数据库配置
- ✅ 可直接在 Excel 中查看和修改用例
- ✅ 支持多个测试用例在同一个 Excel 文件中

### Web 测试示例

#### YAML 用例格式

```yaml
desc: 百度搜索测试
steps:
  - 打开浏览器:
      关键字: open_browser
      浏览器: chrome
      无头模式: false
  
  - 导航到百度:
      关键字: navigate_to
      url: https://www.baidu.com
  
  - 输入搜索词:
      关键字: input_text
      定位方式: id
      元素: kw
      文本: Selenium
  
  - 点击搜索:
      关键字: click_element
      定位方式: id
      元素: su
  
  - 关闭浏览器:
      关键字: close_browser
```

#### 常用关键字

| 关键字 | 说明 | 主要参数 |
|--------|------|---------|
| `open_browser` | 打开浏览器 | 浏览器, 无头模式, 隐式等待 |
| `navigate_to` | 导航到URL | url |
| `click_element` | 点击元素 | 定位方式, 元素 |
| `input_text` | 输入文本 | 定位方式, 元素, 文本 |
| `assert_element_visible` | 断言元素可见 | 定位方式, 元素 |

### 数据驱动测试

```yaml
desc: 数据驱动登录测试
steps:
  - 发送登录请求:
      关键字: send_request
      method: POST
      url: "{{URL}}/api/login"
      data:
        username: "{{username}}"
        password: "{{password}}"

ddts:
  - desc: "正确的用户名和密码"
    username: "admin"
    password: "123456"
  
  - desc: "错误的密码"
    username: "admin"
    password: "wrong"
```

### 原生 Pytest 支持

#### API 测试

```python
import pytest
import allure

def test_login_api(api_keywords):
    """测试登录接口"""
    with allure.step("发送登录请求"):
        api_keywords.send_request(
            关键字="send_request",
            method="POST",
            url="http://example.com/api/login",
            data={"username": "admin", "password": "123456"}
        )

@pytest.mark.parametrize("username,password", [
    ("user1", "pass1"),
    ("user2", "pass2"),
])
def test_login_ddt(api_keywords, username, password):
    """数据驱动登录测试"""
    api_keywords.send_request(
        关键字="send_request",
        method="POST",
        url="http://example.com/api/login",
        data={"username": username, "password": password}
    )
```

#### Web 测试

```python
import pytest
import allure

def test_baidu_search(web_keywords, driver):
    """测试百度搜索"""
    with allure.step("打开百度"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("输入搜索词"):
        web_keywords.input_text(定位方式="id", 元素="kw", 文本="Selenium")
    
    with allure.step("点击搜索"):
        web_keywords.click_element(定位方式="id", 元素="su")
```

## ⚙️ 配置说明

### context.yaml 配置示例

#### API 测试配置

```yaml
# 引擎类型
ENGINE_TYPE: api

# 基础配置
URL: http://example.com

# 数据库配置
_database:
  mysql001:
    host: localhost
    port: 3306
    user: root
    password: password
    db: test_db

# 测试数据
USERNAME: admin
PASSWORD: admin123
```

#### Web 测试配置

```yaml
# 引擎类型
ENGINE_TYPE: web

# 基础配置
BASE_URL: https://www.example.com

# 浏览器配置
BROWSER: chrome
HEADLESS: false
IMPLICIT_WAIT: 10
WINDOW_SIZE: maximize

# 测试数据
TEST_USERNAME: testuser
TEST_PASSWORD: testpass123
```

## 📋 命令行参数

### 通用参数

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `--engine-type` | 测试引擎类型 (api/web) | 是* | `--engine-type=api` |
| `--type` | 用例类型 (yaml/excel/pytest) | 否 | `--type=yaml` |
| `--cases` | 用例目录路径 | 是 | `--cases=examples/api-cases` |
| `--keyDir` | 自定义关键字目录 | 否 | `--keyDir=./custom_keywords` |

*注：如果在 context.yaml 中配置了 ENGINE_TYPE，则不是必填

**用例类型说明**：
- `yaml` - YAML 格式用例（默认）
- `excel` - Excel 格式用例
- `pytest` - 原生 Pytest 脚本

### API 测试专用参数

无特殊参数

### Web 测试专用参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--browser` | 浏览器类型 (chromium/firefox/webkit) | chrome | `--browser=chromium` |
| `--headless` | 无头模式 (true/false) | false | `--headless=true` |

**参数优先级**: 命令行参数 > context.yaml 配置文件 > 默认值

**说明**:

- 命令行参数会覆盖 `context.yaml` 中的 `BROWSER` 和 `HEADLESS` 配置
- 适用于 CI/CD 环境动态切换浏览器模式，无需修改配置文件

## 🔧 自定义关键字

创建自定义关键字类：

```python
# my_keywords.py
class MyKeyword:
    def my_custom_keyword(self, **kwargs):
        """自定义关键字实现"""
        param1 = kwargs.get('参数1')
        param2 = kwargs.get('参数2')
        # 实现你的逻辑
        print(f"执行自定义关键字: {param1}, {param2}")
```

在 YAML 用例中使用：

```yaml
steps:
  - 执行自定义操作:
      关键字: my_custom_keyword
      参数1: value1
      参数2: value2
```

## 🎯 最佳实践

### 1. 选择合适的测试方式

- **YAML 用例**：适合简单测试场景、数据驱动、非编程人员
- **Pytest 脚本**：适合复杂逻辑、需要编程灵活性、开发人员

### 2. 合理使用变量

- 全局变量在 `context.yaml` 中定义
- 用例级变量在 YAML 的 `context` 字段中定义
- 支持 `{{变量名}}` 语法进行变量替换

### 3. 数据驱动测试

对于相同步骤、不同数据的场景，使用 `ddts` 字段实现数据驱动。

### 4. 接口关联

API 测试中使用 `ex_jsonData` 提取响应数据，保存到变量中供后续步骤使用。

### 5. 元素定位

Web 测试推荐使用稳定的定位方式：

1. ID（最稳定）
2. CSS Selector
3. XPath（最灵活但维护成本高）

## 🆚 API vs Web 对比

| 特性 | API 测试 | Web 测试 |
|------|---------|----------|
| 测试类型 | 接口测试 | UI 测试 |
| 核心库 | requests | selenium |
| 速度 | 快 | 较慢 |
| 稳定性 | 高 | 中等 |
| 维护成本 | 低 | 中等 |
| 适用场景 | 后端接口、数据验证 | 前端交互、UI验证 |

## ❓ 常见问题

### 1. 如何指定测试引擎类型？

有两种方式，命令行参数优先级更高：

- 命令行：`--engine-type=api` 或 `--engine-type=web`
- 配置文件：在 `context.yaml` 中添加 `ENGINE_TYPE: api` 或 `ENGINE_TYPE: web`

### 2. 命令行参数 --headless=true 不生效怎么办？

**已修复**！现在命令行参数会正确覆盖 `context.yaml` 中的配置。

**参数优先级**: 命令行参数 > context.yaml > 默认值

```bash
# 命令行参数会覆盖配置文件中的 HEADLESS: false
testrun --engine-type=web --cases=examples/web-cases --headless=true
```

### 3. 可以在一次运行中同时执行 API 和 Web 测试吗？

不可以。每次运行只能选择一种引擎类型。如需同时执行，请分别运行两次。

### 3. 原有的 api-engine 和 web-engine 还能用吗？

可以。Test Engine 是整合版本，原有的独立引擎依然可以正常使用。

### 4. 如何迁移现有用例？

只需在 `context.yaml` 中添加 `ENGINE_TYPE` 配置即可，其他无需修改。

### 5. 浏览器驱动如何管理？

Web 引擎使用 `webdriver-manager` 自动管理驱动，无需手动下载。

## 📝 更新日志

### v2.0.0 (2025-10-24) - 异步架构重构

- 🚀 **全面异步重构** - API 测试引擎改为纯异步架构
- ⚡ **连接池优化** - 重新设计 httpx 连接池管理,真正复用连接
- 🔧 **配置化管理** - 新增 `httpx_config.yaml` 支持连接池参数配置
- 📝 **日志优化** - 移除冗余日志和 emoji,保留关键错误日志
- 🔐 **线程安全** - 添加线程锁保护,确保多线程环境下的安全性
- 📊 **性能提升** - 异步执行测试,性能提升 3-5 倍
- 🧪 **pytest-asyncio** - 集成 pytest-asyncio,支持异步测试用例

### v1.0.0 (2025-10-22)

- ✨ 首次发布
- 🔄 整合 API Engine 和 Web Engine
- 📝 统一命令行入口
- 📖 完整的文档和示例

## 🔧 连接池配置

API 测试引擎支持通过 `testengine_api/utils/httpx_config.yaml` 配置连接池参数：

```yaml
# 连接池配置
pool:
  max_connections: 100              # 最大连接数
  max_keepalive_connections: 20     # keep-alive 连接数
  keepalive_expiry: 30.0            # keep-alive 过期时间(秒)

# 超时配置
timeout:
  connect: 10.0   # 连接超时(秒)
  read: 30.0      # 读取超时(秒)
  write: 10.0     # 写入超时(秒)
  pool: 10.0      # 连接池超时(秒)

# 重试配置
retry:
  max_retries: 3  # 最大重试次数

# 其他配置
other:
  follow_redirects: true  # 是否跟随重定向
  verify: true            # SSL 验证
  http2: false            # HTTP/2 支持
```

**配置说明：**

- `max_connections`: 控制最大并发连接数,根据目标服务器性能调整
- `max_keepalive_connections`: 保持活跃的连接数,提高复用率
- `keepalive_expiry`: 连接保持时间,过期后自动关闭
- `max_retries`: 请求失败时的重试次数,提高稳定性

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 项目地址：[GitHub](https://github.com/yourusername/test-engine)
- 问题反馈：[Issues](https://github.com/yourusername/test-engine/issues)
