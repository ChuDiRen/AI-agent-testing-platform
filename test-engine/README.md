# Test Engine - 统一自动化测试引擎

统一的自动化测试引擎，支持 **API 测试** 和 **Web UI 测试**，采用关键字驱动和数据驱动的设计理念。

## ✨ 特性

### 核心特性
- 🔄 **统一入口**：一个命令支持 API 和 Web 两种测试类型
- ✨ **关键字驱动**：丰富的测试关键字库，简化用例编写
- 📝 **YAML 格式**：使用 YAML 编写测试用例，清晰易读
- 🐍 **原生 Pytest**：支持使用 Python pytest 脚本编写测试
- 🔄 **数据驱动**：支持 DDT 数据驱动测试
- 📊 **Allure 报告**：集成 Allure 测试报告
- 🔧 **易扩展**：支持自定义关键字扩展

### API 测试特性
- 📡 基于 requests 库
- 🗄️ 支持数据库操作
- 🔗 支持接口关联
- 📤 支持文件上传下载

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

## 📁 目录结构

```
test-engine/
├── testrun/                # 统一入口模块
│   ├── __init__.py
│   └── cli.py             # 统一命令行入口
├── apirun/                # API测试引擎
│   ├── core/              # 核心运行器
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   └── utils/             # 工具类
├── webrun/                # Web测试引擎
│   ├── core/              # 核心运行器
│   ├── extend/            # 关键字扩展
│   ├── parse/             # 用例解析器
│   └── utils/             # 工具类
├── examples/              # 示例用例
│   ├── api-cases/         # API测试示例
│   └── web-cases/         # Web测试示例
├── requirements.txt       # 依赖配置
├── setup.py              # 安装配置
└── README.md             # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd test-engine
pip install -r requirements.txt
```

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

# 安装后可直接使用 testrun 命令
testrun --engine-type=api --type=yaml --cases=examples/api-cases
testrun --engine-type=web --type=yaml --cases=examples/web-cases --browser=chromium --headless=true
```

#### 方式二：通过配置文件指定

在用例目录的 `context.yaml` 中配置 `ENGINE_TYPE`:

```yaml
# context.yaml
ENGINE_TYPE: api  # 或 web
```

然后运行：

```bash
# 自动从 context.yaml 读取 ENGINE_TYPE
python -m testrun.cli --type=yaml --cases=examples/api-cases

# 或使用 testrun 命令
testrun --type=yaml --cases=examples/api-cases
```

### 3. 查看测试报告

```bash
# 生成 Allure 报告
allure generate -c -o allure-report

# 打开报告
allure open allure-report
```

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
| `--type` | 用例类型 (yaml/pytest) | 否 | `--type=yaml` |
| `--cases` | 用例目录路径 | 是 | `--cases=examples/api-cases` |
| `--keyDir` | 自定义关键字目录 | 否 | `--keyDir=./custom_keywords` |

*注：如果在 context.yaml 中配置了 ENGINE_TYPE，则不是必填

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

### v1.0.0 (2025-10-22)

- ✨ 首次发布
- 🔄 整合 API Engine 和 Web Engine
- 📝 统一命令行入口
- 📖 完整的文档和示例

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 项目地址：[GitHub](https://github.com/yourusername/test-engine)
- 问题反馈：[Issues](https://github.com/yourusername/test-engine/issues)

