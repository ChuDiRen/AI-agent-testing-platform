# Web Engine - Web 自动化测试引擎

基于 Selenium 的 Web 自动化测试引擎，采用关键字驱动和数据驱动的设计理念，参考 api-engine 的架构实现。

## 特性

- ✨ **关键字驱动**：丰富的 Selenium 关键字库，简化测试用例编写
- 📝 **YAML 格式**：使用 YAML 编写测试用例，清晰易读
- 🐍 **原生 Pytest**：支持使用 Python pytest 脚本编写测试
- 🔄 **数据驱动**：支持 DDT 数据驱动测试，一个用例多组数据
- 🌐 **多浏览器**：支持 Chrome、Firefox、Edge 浏览器
- 🎯 **智能等待**：支持隐式等待和显式等待策略
- 📊 **Allure 报告**：集成 Allure 测试报告，美观详细
- 🔧 **易扩展**：支持自定义关键字扩展
- 📸 **自动截图**：失败时自动截图，方便问题定位

## 目录结构

```
web-engine/
├── webrun/                 # 核心引擎代码
│   ├── core/              # 核心运行器 (使用相对导入)
│   │   ├── WebTestRunner.py    # 测试执行器
│   │   ├── globalContext.py    # 全局上下文
│   │   └── CasesPlugin.py      # pytest 插件
│   ├── extend/            # 关键字扩展 (使用相对导入)
│   │   ├── keywords.py         # 关键字库
│   │   └── script/            # 脚本执行器
│   ├── parse/             # 用例解析器 (使用相对导入)
│   │   ├── YamlCaseParser.py   # YAML 解析器
│   │   └── CaseParser.py       # 解析器入口
│   ├── utils/             # 工具类 (使用相对导入)
│   │   ├── DriverManager.py    # 浏览器驱动管理
│   │   ├── VarRender.py        # 变量渲染
│   │   └── DynamicTitle.py     # 动态标题
│   └── cli.py             # 命令行入口 (使用绝对导入,支持直接运行)
├── examples/              # 示例用例
│   ├── example-web-cases/     # YAML 用例
│   │   ├── context.yaml
│   │   ├── 1_baidu_search_test.yaml
│   │   ├── 2_element_operations_test.yaml
│   │   ├── 3_ddt_search_test.yaml
│   │   ├── 4_advanced_operations_test.yaml
│   │   └── 5_wait_and_assert_test.yaml
│   └── example-pytest-scripts/ # Pytest 脚本
│       ├── conftest.py
│       ├── test_web_basic.py
│       └── test_web_advanced.py
├── requirements.txt       # 依赖配置
├── setup.py              # 安装配置
└── README.md             # 项目文档
```

## 导入策略说明

- **cli.py**: 作为命令行入口文件,使用**绝对导入**,支持直接运行 `python cli.py`
- **其他模块**: webrun 内部模块(core/extend/parse/utils)使用**相对导入**,提高模块独立性

## 快速开始

### 1. 安装依赖

```bash
cd web-engine
pip install -r requirements.txt
```

或者安装整个包：

```bash
pip install -e .
```

### 2. 运行示例用例

#### 方式一：运行 YAML 用例

**推荐方式 - 直接运行 cli.py**:

```bash
cd webrun
python cli.py --type=yaml --cases=../examples/example-web-cases --browser=chrome --headless=false
```

**模块方式运行**:

```bash
cd web-engine
python -m webrun.cli --type=yaml --cases=examples/example-web-cases --browser=chrome --headless=false
```

**使用 pytest 直接运行**:

```bash
cd webrun
pytest core/WebTestRunner.py --type=yaml --cases=../examples/example-web-cases --browser=chrome --headless=false
```

#### 方式二：运行 Pytest 脚本

```bash
cd examples/example-pytest-scripts
pytest -v -s --browser=chrome --headless=false
```

### 3. 查看测试报告

```bash
# 生成 Allure 报告
allure generate -c -o allure-report

# 打开报告
allure open allure-report
```

## 关键字说明

### 浏览器操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `open_browser` | 打开浏览器 | 浏览器, 无头模式, 隐式等待, 窗口大小 |
| `close_browser` | 关闭浏览器 | - |
| `navigate_to` | 导航到URL | url |
| `refresh_page` | 刷新页面 | - |
| `back` | 后退 | - |
| `forward` | 前进 | - |

### 元素操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `click_element` | 点击元素 | 定位方式, 元素, 等待时间 |
| `input_text` | 输入文本 | 定位方式, 元素, 文本, 清空, 等待时间 |
| `clear_text` | 清空文本 | 定位方式, 元素, 等待时间 |
| `get_text` | 获取文本 | 定位方式, 元素, 变量名, 等待时间 |
| `get_attribute` | 获取属性 | 定位方式, 元素, 属性名, 变量名, 等待时间 |
| `select_dropdown` | 下拉框选择 | 定位方式, 元素, 选择方式, 选项值, 等待时间 |

### 等待操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `wait_for_element` | 等待元素出现 | 定位方式, 元素, 超时时间 |
| `wait_for_element_visible` | 等待元素可见 | 定位方式, 元素, 超时时间 |
| `wait_for_element_clickable` | 等待元素可点击 | 定位方式, 元素, 超时时间 |
| `sleep` | 强制等待 | 时间 |

### 断言操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `assert_element_visible` | 断言元素可见 | 定位方式, 元素, 超时时间 |
| `assert_element_not_visible` | 断言元素不可见 | 定位方式, 元素, 超时时间 |
| `assert_text_equals` | 断言文本相等 | 定位方式, 元素, 期望文本, 等待时间 |
| `assert_text_contains` | 断言文本包含 | 定位方式, 元素, 期望文本, 等待时间 |
| `assert_title_equals` | 断言标题相等 | 期望标题 |
| `assert_title_contains` | 断言标题包含 | 期望文本 |

### 高级操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `switch_to_frame` | 切换到frame | 定位方式, 元素, 索引 |
| `switch_to_window` | 切换到窗口 | 索引, 句柄 |
| `execute_script` | 执行JavaScript | 脚本, 变量名 |
| `take_screenshot` | 截图 | 文件名 |
| `scroll_to_element` | 滚动到元素 | 定位方式, 元素, 等待时间 |
| `hover_element` | 鼠标悬停 | 定位方式, 元素, 等待时间 |
| `get_current_url` | 获取当前URL | 变量名 |

## 定位方式

支持以下 8 种定位方式：

- `id` - 通过 ID 定位
- `name` - 通过 name 属性定位
- `class` / `class_name` - 通过 class 名称定位
- `tag` / `tag_name` - 通过标签名定位
- `xpath` - 通过 XPath 定位
- `css` / `css_selector` - 通过 CSS 选择器定位
- `link` / `link_text` - 通过链接文本定位
- `partial_link` / `partial_link_text` - 通过部分链接文本定位

## 测试方式对比

### YAML 驱动测试

**适用场景**：
- 测试人员不熟悉编程
- 快速编写简单测试用例
- 数据驱动测试

### 原生 Pytest 测试

**适用场景**：
- 开发人员或熟悉 Python 的测试人员
- 需要复杂逻辑的测试场景
- 需要使用 pytest 高级特性

**示例**：

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

@pytest.mark.parametrize("keyword", ["Python", "Java", "Selenium"])
def test_search_ddt(web_keywords, driver, keyword):
    """数据驱动搜索测试"""
    web_keywords.navigate_to(url="https://www.baidu.com")
    web_keywords.input_text(定位方式="id", 元素="kw", 文本=keyword)
    web_keywords.click_element(定位方式="id", 元素="su")
```

## 原生 Pytest 支持

### 快速开始

```bash
cd examples/example-pytest-scripts
pytest -v -s --browser=chrome
```

### Fixtures 说明

#### driver

自动管理浏览器生命周期，测试结束自动关闭：

```python
def test_example(driver):
    driver.get("https://www.example.com")
    # 浏览器会自动关闭
```

#### web_keywords

提供 Web 关键字实例：

```python
def test_example(web_keywords, driver):
    web_keywords.navigate_to(url="https://www.example.com")
    web_keywords.click_element(定位方式="id", 元素="btn")
```

### 特性支持

- ✅ 参数化测试 (`@pytest.mark.parametrize`)
- ✅ Fixture 机制（自动管理浏览器）
- ✅ 测试类组织
- ✅ 测试标记 (`@pytest.mark.smoke`)
- ✅ Allure 报告集成
- ✅ 失败自动截图
- ✅ 所有 pytest 插件

### 运行选项

```bash
# 运行所有测试
pytest -v -s

# 指定浏览器
pytest -v -s --browser=chrome
pytest -v -s --browser=firefox
pytest -v -s --browser=edge

# 无头模式
pytest -v -s --headless=true

# 运行特定测试
pytest test_web_basic.py::test_baidu_search -v -s
pytest -k "test_search" -v -s

# 运行标记的测试
pytest -m smoke -v -s

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## YAML 用例编写示例

### 基础用例

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
  
  - 输入搜索关键词:
      关键字: input_text
      定位方式: id
      元素: kw
      文本: Selenium
  
  - 点击搜索:
      关键字: click_element
      定位方式: id
      元素: su
  
  - 断言搜索结果:
      关键字: assert_text_contains
      定位方式: id
      元素: content_left
      期望文本: Selenium
  
  - 关闭浏览器:
      关键字: close_browser
```

### 数据驱动用例

```yaml
desc: 数据驱动搜索测试
steps:
  - 打开浏览器:
      关键字: open_browser
      浏览器: chrome
  
  - 搜索:
      关键字: input_text
      定位方式: id
      元素: kw
      文本: "{{keyword}}"
  
  - 关闭浏览器:
      关键字: close_browser

ddts:
  - desc: 搜索Python
    keyword: Python
  
  - desc: 搜索Java
    keyword: Java
```

### 变量使用

```yaml
desc: 变量使用示例
context:
  BASE_URL: https://www.example.com
  USERNAME: admin
  PASSWORD: admin123

steps:
  - 打开浏览器:
      关键字: open_browser
  
  - 导航:
      关键字: navigate_to
      url: "{{BASE_URL}}/login"
  
  - 输入用户名:
      关键字: input_text
      定位方式: id
      元素: username
      文本: "{{USERNAME}}"
```

## 配置文件

`context.yaml` 示例：

```yaml
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

# 超时配置
DEFAULT_TIMEOUT: 10
```

## 命令行参数

- `--type`: 用例类型，默认 yaml
- `--cases`: 用例目录路径
- `--browser`: 浏览器类型 (chrome/firefox/edge)
- `--headless`: 无头模式 (true/false)
- `--keyDir`: 自定义关键字目录

## 自定义关键字

在指定的关键字目录创建 Python 文件，实现自定义关键字：

```python
class MyCustomKeyword:
    def my_custom_keyword(self, **kwargs):
        # 实现你的关键字逻辑
        pass
```

## 与 api-engine 的对比

| 特性 | api-engine | web-engine |
|------|-----------|-----------|
| 测试类型 | API 接口测试 | Web UI 测试 |
| 核心库 | requests | selenium |
| 关键字 | HTTP 请求、JSON 提取 | 元素操作、断言 |
| 驱动管理 | - | webdriver-manager |
| 截图功能 | ❌ | ✅ |
| 等待策略 | - | 隐式/显式等待 |

## 常见问题

### 1. 为什么 cli.py 使用绝对导入,其他模块使用相对导入?

- **cli.py**: 作为入口文件,需要支持直接运行 `python cli.py`,因此使用绝对导入
- **其他模块**: 内部模块使用相对导入,提高模块独立性和可移植性
- **最佳实践**: 入口文件绝对导入,内部模块相对导入

### 2. 如何在 YAML 和 Pytest 之间选择？

- **YAML**：适合简单测试、数据驱动、非编程人员
- **Pytest**：适合复杂逻辑、需要编程灵活性、开发人员

### 3. 运行 cli.py 时报 ImportError 怎么办?

确保在正确的目录运行:
```bash
cd webrun
python cli.py --type=yaml --cases=../examples/example-web-cases
```

或使用模块方式:
```bash
cd web-engine
python -m webrun.cli --type=yaml --cases=examples/example-web-cases
```

### 4. Pytest 脚本可以使用 g_context 吗？

不建议。原生 Pytest 脚本应该使用 Python 原生方式管理变量，保持独立性。

### 5. 如何在 Pytest 中使用框架关键字？

通过 `web_keywords` 和 `driver` fixtures 注入：

```python
def test_example(web_keywords, driver):
    web_keywords.navigate_to(url="https://example.com")
```

### 6. 浏览器驱动下载慢？

使用国内镜像或手动下载驱动放到系统 PATH。

### 7. 元素定位不到？

- 检查定位方式和元素标识是否正确
- 增加等待时间
- 使用浏览器开发者工具验证定位器

### 8. 截图保存在哪里？

截图默认保存在 `screenshots/` 目录，同时会附加到 Allure 报告中。

### 9. Pytest 测试失败时会自动截图吗？

是的，driver fixture 会在测试失败时自动截图并附加到 Allure 报告。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：[GitHub](https://github.com/yourusername/web-engine)
- 问题反馈：[Issues](https://github.com/yourusername/web-engine/issues)

