# Web Engine - Web 自动化测试引擎

基于 Selenium 的 Web 自动化测试引擎，采用关键字驱动和数据驱动的设计理念，参考 api-engine 的架构实现。

## 特性

- ✨ **关键字驱动**：丰富的 Selenium 关键字库，简化测试用例编写
- 🤖 **AI驱动操作**：基于Qwen-VL视觉模型，使用自然语言描述定位和操作元素（新功能）
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
├── __init__.py                # 包初始化文件
├── README.md                  # 项目说明文档（本文件）
├── requirements.txt           # Python 依赖包配置
├── setup.py                   # 安装配置脚本
│
├── webrun/                    # 核心测试引擎代码
│   ├── __init__.py           # 包初始化文件
│   ├── cli.py                # 命令行入口（支持直接运行）
│   ├── pytest.ini            # Pytest 配置文件
│   │
│   ├── core/                 # 核心运行器模块
│   │   ├── __init__.py
│   │   ├── WebTestRunner.py      # Web 测试执行器
│   │   ├── CasesPlugin.py        # Pytest 插件
│   │   ├── globalContext.py      # 全局上下文管理
│   │   ├── models.py             # 数据模型定义
│   │   ├── enums.py              # 枚举类型定义
│   │   └── exceptions.py         # 自定义异常类
│   │
│   ├── extend/               # 关键字扩展模块
│   │   ├── __init__.py
│   │   ├── keywords.py           # Selenium 关键字库
│   │   └── script/              # 脚本执行器
│   │       ├── __init__.py
│   │       └── run_script.py    # Python 脚本运行器
│   │
│   ├── parse/                # 用例解析器模块
│   │   ├── __init__.py
│   │   ├── CaseParser.py         # 解析器工厂/入口
│   │   └── YamlCaseParser.py     # YAML 用例解析器
│   │
│   └── utils/                # 工具类模块
│       ├── __init__.py
│       ├── DriverManager.py      # 浏览器驱动管理
│       ├── VarRender.py          # 变量渲染工具
│       └── DynamicTitle.py       # 动态标题生成
│
├── examples/                 # 示例用例目录
│   ├── example-web-cases/        # YAML 格式用例示例
│   │   ├── context.yaml              # 全局配置（URL等）
│   │   ├── 1_baidu_search_test.yaml      # 百度搜索测试
│   │   ├── 2_element_operations_test.yaml # 元素操作测试
│   │   ├── 3_ddt_search_test.yaml        # 数据驱动搜索测试
│   │   ├── 4_advanced_operations_test.yaml # 高级操作测试
│   │   └── 5_wait_and_assert_test.yaml   # 等待和断言测试
│   │
│   └── example-pytest-scripts/   # Pytest 脚本示例
│       ├── conftest.py               # Pytest 配置和 Fixtures
│       ├── test_web_basic.py         # 基础 Web 测试
│       ├── test_web_advanced.py      # 高级 Web 测试
│       └── README.md                 # Pytest 示例说明
│
└── reports/                  # 测试报告目录（运行时自动生成）
    ├── allure-results/           # Allure 原始测试数据（JSON）
    ├── allure-report/            # Allure HTML 可视化报告
    ├── screenshots/              # 测试截图（错误截图和主动截图）
    └── logdata/                  # Pytest 测试日志
        └── log.log              # 测试执行日志文件
```

> **注意**:
>
> - `__pycache__/` 和 `.pytest_cache/` 等缓存目录已自动忽略
> - `reports/` 目录在首次运行测试后自动创建
> - 所有截图统一保存到 `reports/screenshots/` 目录
> - 所有日志统一保存到 `reports/logdata/` 目录
> - 所有模块使用相对导入，`cli.py` 使用绝对导入以支持直接运行

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

#### 方式二：运行 Excel 用例

**模块方式运行**:

```bash
cd web-engine
python -m webrun.cli --type=excel --cases=examples/example-excel-cases --browser=chrome --headless=false
```

**说明**: Excel 用例格式详见 `examples/example-excel-cases/README.md`

#### 方式三：运行 Pytest 脚本

```bash
cd examples/example-pytest-scripts
pytest -v -s --browser=chrome --headless=false
```

### 3. 查看测试报告

测试执行完成后，报告会自动生成在 `reports/` 目录下：

```bash
# 报告已自动生成，直接打开查看
cd web-engine
allure open reports/allure-report

# 或手动生成报告
allure generate -c -o reports/allure-report reports/allure-results
```

**报告位置**：

- 测试结果数据：`web-engine/reports/allure-results/`
- HTML 报告：`web-engine/reports/allure-report/`

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

### AI 驱动操作 🤖 NEW

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `ai_operation` | AI通用操作 | 操作描述 |
| `ai_click` | AI点击元素 | 元素描述 |
| `ai_input` | AI输入文本 | 元素描述, 文本 |
| `ai_extract_text` | AI提取文本 | 文本描述, 变量名 |
| `ai_scroll` | AI滚动到元素 | 元素描述 |
| `ai_hover` | AI鼠标悬停 | 元素描述 |
| `ai_drag` | AI拖拽元素 | 源元素描述, 目标元素描述 |
| `ai_assert_visible` | AI断言可见 | 元素描述 |

**AI操作特点**：

- ✅ 使用自然语言描述元素，无需编写XPath或CSS选择器
- ✅ 基于Qwen-VL视觉模型，智能识别页面元素
- ✅ 适用于元素定位困难或动态变化的场景
- ⚠️ 需要配置阿里云百炼API Key
- 📖 详细文档请参考：[AI_OPERATIONS_README.md](AI_OPERATIONS_README.md)

**快速示例**：

```yaml
- AI点击登录按钮:
    关键字: ai_click
    元素描述: 蓝色的登录按钮

- AI输入用户名:
    关键字: ai_input
    元素描述: 用户名输入框
    文本: admin
```

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

## Excel 用例编写指南

### Excel 用例格式

Web Engine 支持使用 Excel 文件编写测试用例，适合非技术人员编写和维护测试用例。

### Excel 文件结构

#### 1. context.xlsx - 全局配置文件（可选）

**表格格式**:

| 类型 | 变量描述 | 变量值 |
|------|---------|--------|
| 变量 | BASE_URL | <https://www.baidu.com> |
| 变量 | TEST_USERNAME | testuser |
| 变量 | TEST_PASSWORD | test123456 |

#### 2. 测试用例文件

**文件命名**: `数字_用例名称.xlsx` (例如: `1_百度搜索测试.xlsx`)

**表格格式**:

| 编号 | 测试用例标题 | 用例等级 | 步骤描述 | 关键字 | 参数_1 | 参数_2 | 参数_3 | 参数_4 |
|-----|-------------|---------|---------|--------|--------|--------|--------|--------|
| 1 | 百度搜索测试 | P0 | 打开浏览器 | open_browser | chrome | false | 10 | maximize |
| 2 |  |  | 导航到百度 | navigate_to | <https://www.baidu.com> |  |  |  |
| 3 |  |  | 等待搜索框 | wait_for_element_visible | id | kw | 15 |  |
| 4 |  |  | 输入关键词 | input_text | id | kw | Selenium | true |
| 5 |  |  | 点击搜索 | click_element | id | su |  |  |
| 6 |  |  | 等待结果 | wait_for_element_visible | id | content_left | 15 |  |
| 7 |  |  | 断言包含 | assert_text_contains | id | content_left | Selenium |  |
| 8 |  |  | 截图 | take_screenshot | search_result |  |  |  |
| 9 |  |  | 关闭浏览器 | close_browser |  |  |  |  |

### Excel 用例说明

1. **文件命名**: 必须以数字开头，格式为 `数字_名称.xlsx`
2. **用例标题**: 每个测试用例的第一行必须填写标题
3. **步骤描述**: 清晰描述每个步骤的目的
4. **关键字**: 必须是 `keywords.yaml` 中定义的关键字
5. **参数列**: 从 `参数_1` 开始，根据关键字需要添加足够的参数列
6. **数据类型**:
   - 字符串: 直接填写
   - 数字: 直接填写数字
   - 布尔值: `true` 或 `false`
   - 列表: `['item1', 'item2']`
   - 字典: `{'key': 'value'}`

### 运行 Excel 用例

```bash
cd web-engine
python -m webrun.cli --type=excel --cases=examples/example-excel-cases
```

### Excel 用例优势

- ✅ **易于编写**: 使用 Excel 编写，无需编程基础
- ✅ **易于维护**: 表格格式直观，易于修改
- ✅ **团队协作**: 测试人员和业务人员都能参与编写
- ✅ **版本管理**: Excel 文件可以纳入版本控制
- ✅ **数据驱动**: 通过复制行可以快速创建数据驱动测试

### 详细示例

完整的 Excel 用例示例和说明，请参考:

- `examples/example-excel-cases/README.md` - Excel 用例详细文档
- `webrun/extend/keywords.yaml` - 所有可用关键字及参数说明

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

所有截图统一保存在 `reports/screenshots/` 目录，同时会自动附加到 Allure 报告中。

### 9. Pytest 测试失败时会自动截图吗？

是的，driver fixture 会在测试失败时自动截图并附加到 Allure 报告。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：[GitHub](https://github.com/yourusername/web-engine)
- 问题反馈：[Issues](https://github.com/yourusername/web-engine/issues)
