# Web Pytest 测试脚本示例（使用 Playwright）

本目录包含 Web UI 自动化测试的 Pytest 原生脚本示例，使用 [**Playwright**](https://github.com/microsoft/playwright) 框架，演示如何编写和组织 Web 测试用例。

## 🎭 为什么选择 Playwright？

- ✅ **自动管理浏览器**：无需手动下载驱动，首次运行自动安装
- ✅ **跨浏览器支持**：Chromium、Firefox、WebKit，一套代码多浏览器运行
- ✅ **自动等待机制**：智能等待元素可操作，减少 flaky 测试
- ✅ **更快的执行速度**：使用现代浏览器协议，性能更优
- ✅ **强大的调试工具**：Inspector、Trace Viewer、Codegen
- ✅ **网络控制**：可以拦截和修改网络请求
- ✅ **浏览器上下文**：快速隔离测试环境，无需重启浏览器

## 📁 文件结构

```
web-pytest-scripts/
├── conftest.py              # Pytest 配置和公共 Fixtures
├── test_web_basic.py        # 基础 Web 测试示例
├── test_web_advanced.py     # 高级 Web 测试示例
└── README.md               # 本文件
```

## 🎯 测试用例分类

### 1. **test_web_basic.py** - 基础测试

包含以下测试场景：

- **搜索功能测试**
  - ✅ 百度首页加载验证
  - ✅ 百度搜索功能测试
  - ✅ 多关键词搜索（参数化测试）

- **表单操作测试**
  - ✅ 输入框操作（输入、清空、追加）

- **元素定位测试**
  - ✅ 多种定位方式（ID、Name、CSS、XPath）

- **等待机制测试**
  - ✅ 显式等待元素可见
  - ✅ 显式等待元素可点击

- **页面导航测试**
  - ✅ 浏览器前进后退
  - ✅ 页面刷新

### 2. **test_web_advanced.py** - 高级测试

包含以下测试场景：

- **高级交互操作**
  - ✅ 键盘快捷键操作（Tab、Enter）
  - ✅ 组合键操作（Ctrl+A、Ctrl+C、Ctrl+V）

- **窗口和Frame操作**
  - ✅ 多窗口切换
  - ✅ 窗口大小和位置操作

- **JavaScript交互**
  - ✅ 执行JS获取页面信息
  - ✅ 使用JS操作元素
  - ✅ 页面滚动

- **截图操作**
  - ✅ 页面截图
  - ✅ 保存截图到文件

- **性能测试**
  - ✅ 页面加载时间测试
  - ✅ Navigation Timing API性能数据

- **数据驱动测试**
  - ✅ 使用外部数据进行搜索测试

## 📦 首次安装

### 1. 安装依赖

Playwright 已包含在 `requirements.txt` 中：

```bash
cd test-engine
pip install -r requirements.txt
```

### 2. 安装浏览器

**重要**：首次使用需要安装 Playwright 浏览器：

```bash
# 安装所有浏览器（Chromium、Firefox、WebKit）
playwright install

# 或只安装特定浏览器
playwright install chromium
playwright install firefox
playwright install webkit

# 如果遇到权限问题（Windows），以管理员权限运行
playwright install --with-deps  # 自动安装系统依赖
```

## 🚀 运行测试

### 运行全部测试

```bash
# 从 test-engine 根目录运行
# Chromium（默认，推荐）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chromium

# 或使用 chrome 别名
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome
```

### 指定浏览器运行

```bash
# 使用 Chromium（推荐，最稳定）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chromium

# 使用 Firefox
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=firefox

# 使用 WebKit（Safari 引擎）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=webkit
```

### 无头模式运行

```bash
# 使用无头模式（不显示浏览器窗口）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome --headless=true
```

### 运行指定测试文件

```bash
# 只运行基础测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py --browser=chrome

# 只运行高级测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_advanced.py --browser=chrome
```

### 运行指定测试类

```bash
# 运行百度搜索测试类
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py::TestBaiduSearch --browser=chrome
```

### 运行指定测试方法

```bash
# 运行百度首页测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py::TestBaiduSearch::test_baidu_homepage --browser=chrome
```

### 使用标记过滤

```bash
# 只运行冒烟测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome -m smoke

# 排除慢速测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome -m "not slow"
```

## 📚 Fixtures 说明

### 命令行参数 Fixtures

| Fixture | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `browser_type_name` | 浏览器类型 | chromium | chromium/firefox/webkit |
| `headless_mode` | 无头模式 | false | true/false |
| `base_url` | 测试基础URL | <https://www.baidu.com> | 任意URL |

### Playwright Fixtures

| Fixture | 说明 | 作用域 | 使用场景 |
|---------|------|--------|---------|
| `playwright_instance` | Playwright 实例 | session | 整个测试会话 |
| `browser` | 浏览器实例 | session | 所有测试共享浏览器 |
| `context` | 浏览器上下文 | function | 每个测试独立上下文 |
| `page` | 页面实例 | function | 每个测试独立页面 |
| `class_context` | 浏览器上下文 | class | 测试类共享上下文 |
| `class_page` | 页面实例 | class | 测试类共享页面 |

### 使用示例

```python
from playwright.sync_api import Page, expect

def test_example(page: Page):
    """使用 function 级别的 page"""
    page.goto("https://www.baidu.com")
    assert "百度" in page.title()

class TestExample:
    """使用 class 级别的 page"""
    
    def test_case1(self, class_page: Page):
        class_page.goto("https://www.baidu.com")
        expect(class_page.locator("#kw")).to_be_visible()
    
    def test_case2(self, class_page: Page):
        # 与 test_case1 共享同一个页面实例
        class_page.goto("https://www.example.com")
        # ...
```

## 🏷️ 测试标记说明

| 标记 | 说明 | 使用场景 |
|------|------|---------|
| `@pytest.mark.smoke` | 冒烟测试 | 核心功能快速验证 |
| `@pytest.mark.regression` | 回归测试 | 完整功能验证 |
| `@pytest.mark.slow` | 慢速测试 | 耗时较长的测试 |

## 📊 查看测试报告

### Allure 报告

测试执行后，Allure 报告会自动生成在 `test-engine/reports/allure-report/` 目录。

```bash
# 打开 Allure 报告
allure open test-engine/reports/allure-report
```

### 测试日志

测试日志保存在 `test-engine/reports/logdata/log.log`。

### 测试截图

- **自动截图**: 测试失败时自动截图，保存在 `test-engine/reports/screenshots/`
- **手动截图**: 在测试中调用截图功能，也保存在同一目录

## 🔧 元素定位方式

### Playwright 定位器（推荐使用）

Playwright 提供了多种强大且语义化的定位器：

| 定位方式 | 示例 | 说明 |
|---------|------|------|
| **CSS Selector** | `page.locator("#kw")` | 通过CSS选择器定位 |
| **文本内容** | `page.get_by_text("新闻")` | 通过可见文本定位（推荐） |
| **角色** | `page.get_by_role("button")` | 通过ARIA角色定位（推荐） |
| **标签** | `page.get_by_label("用户名")` | 通过label标签定位 |
| **占位符** | `page.get_by_placeholder("请输入")` | 通过placeholder定位 |
| **标题** | `page.get_by_title("提示")` | 通过title属性定位 |
| **测试ID** | `page.get_by_test_id("submit-btn")` | 通过data-testid定位 |
| **XPath** | `page.locator("xpath=//input")` | XPath表达式（不推荐） |

### 链式定位器

```python
# 在父元素中查找子元素
page.locator("form").locator("#kw")

# 过滤定位器
page.locator("button").filter(has_text="提交")

# 第 N 个元素
page.locator("button").nth(0)
```

### 推荐优先级

1. **get_by_role()** - 最符合用户体验，推荐优先使用
2. **get_by_text()** - 通过可见文本，语义清晰
3. **get_by_label()** - 适用于表单元素
4. **CSS Selector** - 灵活且性能好
5. **XPath** - 功能强大，但不推荐（可读性差）

## ✨ 最佳实践

### 1. Playwright 自动等待（无需手动等待）

```python
# ❌ 不推荐 - 手动等待
import time
page.goto(url)
time.sleep(5)  # 硬编码等待

# ✅ 推荐 - Playwright 自动等待元素可操作
from playwright.sync_api import Page, expect

page.goto(url)
# Playwright 自动等待元素可见且可操作
page.locator("#element_id").click()

# 或使用断言（自动重试直到满足条件）
expect(page.locator("#element_id")).to_be_visible()
```

### 2. 使用页面对象模式（POM）

```python
from playwright.sync_api import Page

class BasePage:
    """页面对象基类"""
    def __init__(self, page: Page):
        self.page = page
    
    def open(self, url: str):
        self.page.goto(url)

class SearchPage(BasePage):
    """搜索页面"""
    # 使用 Playwright 定位器
    SEARCH_BOX = "#kw"
    SEARCH_BUTTON = "#su"
    
    def search(self, keyword: str):
        self.page.locator(self.SEARCH_BOX).fill(keyword)
        self.page.locator(self.SEARCH_BUTTON).click()
```

### 3. 使用 expect 断言（自动重试）

```python
from playwright.sync_api import Page, expect

# ✅ Playwright 的 expect 会自动重试直到满足条件
expect(page.locator("#element_id")).to_be_visible(timeout=10000)
expect(page.locator("#element_id")).to_have_text("预期文本")
expect(page.locator("#element_id")).to_be_enabled()

# 异常处理（通常不需要，因为 expect 会自动失败）
try:
    expect(page.locator("#element_id")).to_be_visible(timeout=5000)
except Exception as e:
    pytest.fail(f"元素未出现: {e}")
```

### 4. 使用 Allure 注解增强报告

```python
import allure
from playwright.sync_api import Page

@allure.feature("功能模块")
@allure.story("用户故事")
class TestExample:
    
    @allure.title("测试用例标题")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_case(self, page: Page):
        with allure.step("步骤1: 打开页面"):
            page.goto("https://example.com")
            allure.attach(
                page.screenshot(),
                "页面截图",
                allure.attachment_type.PNG
            )
```

### 5. 失败时自动截图

`conftest.py` 中已配置失败时自动截图，无需手动添加。

## 🐛 调试技巧

### 1. 显示浏览器窗口

```bash
# 不使用无头模式，可以看到浏览器操作过程
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome --headless=false
```

### 2. 添加断点调试

```python
def test_example(driver):
    driver.get("https://www.baidu.com")
    
    # 添加断点
    import pdb; pdb.set_trace()
    # 或使用 Python 3.7+
    breakpoint()
    
    # 继续测试代码
```

### 3. 增加等待时间

```python
# 临时增加等待时间以观察页面状态
import time
driver.get(url)
time.sleep(5)  # 仅用于调试
```

### 4. 打印调试信息

```bash
# 显示 print 输出
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chrome -s
```

## 📝 编写新测试用例

### 1. 基本测试模板

```python
"""
测试模块描述
"""
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@allure.feature("功能模块")
class TestNewFeature:
    """测试类描述"""
    
    @allure.title("测试用例标题")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_case_name(self, driver: webdriver.Remote, base_url: str):
        """
        测试用例详细说明
        
        步骤：
        1. 步骤1
        2. 步骤2
        """
        with allure.step("步骤1: 打开页面"):
            driver.get(base_url)
        
        with allure.step("步骤2: 执行操作"):
            # 测试实现
            pass
```

### 2. 使用参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("value1", result1),
    ("value2", result2),
])
def test_with_params(driver, input, expected):
    # 测试实现
    pass
```

### 3. 使用测试数据

```python
@pytest.fixture
def test_data():
    """提供测试数据"""
    return {
        "username": "testuser",
        "password": "password123"
    }

def test_login(driver, test_data):
    # 使用 test_data
    pass
```

## 🔍 常见问题

### Q: 首次运行失败，提示浏览器未安装？

A: Playwright 需要首次安装浏览器。运行以下命令：

```bash
playwright install
# 或只安装需要的浏览器
playwright install chromium
```

### Q: 如何切换浏览器？

A: 使用 `--browser` 参数指定浏览器类型：

```bash
# Chromium（推荐）
python -m testrun.cli --engine-type=web --type=pytest --cases=... --browser=chromium

# Firefox
python -m testrun.cli --engine-type=web --type=pytest --cases=... --browser=firefox

# WebKit（Safari引擎）
python -m testrun.cli --engine-type=web --type=pytest --cases=... --browser=webkit
```

### Q: 无头模式下截图是否正常？

A: 是的，无头模式下截图功能正常，截图会保存在 `reports/screenshots/` 目录。

### Q: 如何处理动态加载的元素？

A: Playwright 自动等待元素可操作，无需手动等待：

```python
from playwright.sync_api import Page, expect

# Playwright 自动等待元素出现并可操作
page.locator("#dynamic_element").click()

# 或使用 expect 断言（自动重试）
expect(page.locator("#dynamic_element")).to_be_visible()
```

### Q: 如何处理弹窗（Alert/Dialog）？

A: 使用 Playwright 的对话框处理：

```python
# 监听对话框并自动处理
page.on("dialog", lambda dialog: dialog.accept())

# 或手动处理
dialog = page.wait_for_event("dialog")
dialog.accept()  # 或 dialog.dismiss()
```

### Q: 如何上传文件？

A: 使用 Playwright 的文件上传方法：

```python
# 方法 1: 直接设置文件
page.locator("input[type='file']").set_input_files("/path/to/file.txt")

# 方法 2: 多文件上传
page.locator("input[type='file']").set_input_files([
    "/path/to/file1.txt",
    "/path/to/file2.txt"
])
```

### Q: 如何切换到 iframe？

A: Playwright 自动处理 iframe，无需手动切换：

```python
# ✅ Playwright 自动穿透 iframe
page.frame_locator("iframe#myframe").locator("#element").click()

# 或获取 frame 对象
frame = page.frame("frame_name")
frame.locator("#element").click()
```

## 📖 参考资料

- [Playwright 官方文档](https://playwright.dev/python/)
- [Playwright GitHub](https://github.com/microsoft/playwright)
- [Playwright Python API](https://playwright.dev/python/docs/api/class-playwright)
- [Pytest 官方文档](https://docs.pytest.org/)
- [Allure Pytest 集成](https://docs.qameta.io/allure/#_pytest)

## 💡 提示

1. **首次安装浏览器**: 运行 `playwright install` 安装浏览器，只需一次
2. **自动等待机制**: Playwright 自动等待元素可操作，无需手动等待
3. **失败自动截图**: `conftest.py` 已配置失败时自动截图到报告
4. **使用 expect 断言**: 自动重试，减少 flaky 测试
5. **页面对象模式**: 对于复杂项目，建议使用 POM 提高代码可维护性
6. **Allure 报告**: 充分使用 `@allure.step` 和 `allure.attach` 增强报告
7. **参数化测试**: 使用 `@pytest.mark.parametrize` 减少重复代码
8. **测试独立性**: 每个测试应该独立运行，不依赖其他测试的执行结果
9. **浏览器上下文**: 使用 `context` 创建隔离的测试环境，比重启浏览器快 10 倍

## 🌟 进阶主题

### 数据驱动测试

从外部文件（JSON/YAML/Excel）加载测试数据：

```python
import json

@pytest.fixture
def test_data():
    with open("test_data.json") as f:
        return json.load(f)

@pytest.mark.parametrize("case", test_data())
def test_with_external_data(driver, case):
    # 使用外部数据
    pass
```

### 并行执行

使用 `pytest-xdist` 插件实现并行执行：

```bash
pip install pytest-xdist
python -m testrun.cli ... -n 4  # 使用4个进程
```

### 失败重试

使用 `pytest-rerunfailures` 插件：

```bash
pip install pytest-rerunfailures
python -m testrun.cli ... --reruns 3  # 失败重试3次
```
