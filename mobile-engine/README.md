# mobile-engine

基于 Appium 的移动端自动化测试引擎（Android + iOS），用例模型与 `web-engine` 完全对齐。

## 特性

- ✅ **关键字驱动**：70+ 内置关键字，覆盖移动端全部操作场景
- ✅ **数据驱动**：支持 YAML/Excel 用例格式，支持 DDT 数据驱动测试
- ✅ **原生 Pytest**：支持使用 Python pytest 脚本编写测试
- ✅ **变量渲染**：Jinja2 模板引擎，支持 `{{variable}}` 语法
- ✅ **生命周期**：context.yaml 全局上下文 + 用例级 context 覆盖 + pre_script/post_script
- ✅ **Allure 报告**：自动生成 complete.html 单文件报告
- ✅ **失败截图**：关键字执行失败时自动截图并附加到报告
- ✅ **双平台支持**：Android (uiautomator2) + iOS (xcuitest)

## 安装

```bash
cd mobile-engine
pip install -e .
```

## 前置条件

1. 安装并启动 Appium Server（默认连接 `http://127.0.0.1:4723`）
2. Android：安装 Android SDK，配置 ANDROID_HOME
3. iOS：安装 Xcode，配置 WebDriverAgent

## 运行方式

### YAML 用例

#### Android（apk 路径）

```bash
mobilerun --type=yaml --cases=./examples/example-mobile-cases --platform=android --app=E:\\path\\to\\app.apk --udid=emulator-5554
```

#### iOS（bundleId）

```bash
mobilerun --type=yaml --cases=./examples/example-mobile-cases --platform=ios --bundleId=com.example.app --udid=00008110-...
```

### Excel 用例

```bash
mobilerun --type=excel --cases=./examples/example-excel-cases --platform=android --udid=emulator-5554
```

### 完整参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--type` | 用例格式 (yaml/excel) | yaml |
| `--cases` | 用例目录 | ../examples |
| `--platform` | 平台 (android/ios) | android |
| `--server` | Appium Server 地址 | http://127.0.0.1:4723 |
| `--deviceName` | 设备名称 | - |
| `--udid` | 设备 UDID | - |
| `--app` | APK/IPA 路径 | - |
| `--bundleId` | iOS Bundle ID | - |
| `--noReset` | 不重置 App | true |
| `--keyDir` | 扩展关键字目录 | - |

## 用例格式

### YAML 用例示例

```yaml
desc: 登录测试
featureName: 用户认证
storyName: 登录功能
rank: critical
context:
  username: "testuser"
  password: "123456"
steps:
  - 启动应用:
      关键字: open_app

  - 输入用户名:
      关键字: input_text
      locator_type: accessibility_id
      element: username_input
      text: "{{username}}"

  - 输入密码:
      关键字: input_text
      locator_type: accessibility_id
      element: password_input
      text: "{{password}}"

  - 点击登录:
      关键字: tap_element
      locator_type: accessibility_id
      element: login_button

  - 断言登录成功:
      关键字: assert_element_visible
      locator_type: accessibility_id
      element: welcome_text

  - 关闭应用:
      关键字: close_app
```

### 数据驱动测试

```yaml
desc: 搜索测试
ddts:
  - desc: 搜索苹果
    keyword: "苹果"
  - desc: 搜索香蕉
    keyword: "香蕉"
steps:
  - 搜索:
      关键字: input_text
      locator_type: id
      element: search_input
      text: "{{keyword}}"
```

## 元素定位方式

| locator_type | 说明 | 示例 |
|--------------|------|------|
| `id` / `resource_id` | Android resource-id | `com.example:id/button` |
| `accessibility_id` / `aid` | 无障碍 ID | `login_button` |
| `xpath` | XPath 表达式 | `//android.widget.Button[@text='登录']` |
| `class` / `class_name` | 类名 | `android.widget.Button` |
| `android_uiautomator` | UiAutomator 表达式 | `new UiSelector().text("登录")` |
| `ios_predicate` | iOS Predicate | `name == 'login'` |
| `ios_class_chain` | iOS Class Chain | `**/XCUIElementTypeButton[`name == 'login'`]` |
| `name` | name 属性 | `login` |

## 关键字列表

### App 启动与关闭

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `open_app` | 启动 App | platform, server, deviceName, udid, app, bundleId, noReset, automationName, newCommandTimeout |
| `close_app` | 关闭 App | - |

### 元素操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `tap_element` | 点击元素 | locator_type, element, wait_time |
| `input_text` | 输入文本 | locator_type, element, text, clear, wait_time |
| `clear_text` | 清空文本 | locator_type, element, wait_time |
| `get_text` | 获取文本 | locator_type, element, variable_name, wait_time |
| `get_attribute` | 获取属性 | locator_type, element, attribute_name, variable_name, wait_time |
| `long_press` | 长按元素 | locator_type, element, duration, wait_time |
| `double_tap` | 双击元素 | locator_type, element, wait_time |
| `scroll_to_element` | 滚动到元素 | locator_type, element, max_swipes, direction |
| `drag_and_drop` | 拖拽元素 | source_locator_type, source_element, target_locator_type, target_element |
| `tap_coordinates` | 坐标点击 | x, y |
| `swipe_coordinates` | 坐标滑动 | start_x, start_y, end_x, end_y, duration |
| `pinch` | 捏合缩放 | locator_type, element, percent, steps |
| `zoom` | 放大 | locator_type, element, percent, steps |

### 滑动与导航

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `swipe` | 滑动 | direction (up/down/left/right), percent, duration |
| `back` | 返回 | - |

### 等待操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `wait_for_element` | 等待元素出现 | locator_type, element, timeout |
| `wait_for_element_visible` | 等待元素可见 | locator_type, element, timeout |
| `wait_for_element_gone` | 等待元素消失 | locator_type, element, timeout |
| `wait_for_element_clickable` | 等待元素可点击 | locator_type, element, timeout |
| `sleep` | 强制等待 | time |

### 断言操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `assert_element_visible` | 断言元素可见 | locator_type, element, timeout |
| `assert_element_not_visible` | 断言元素不可见 | locator_type, element, timeout |
| `assert_text_equals` | 断言文本相等 | locator_type, element, expected_text, wait_time |
| `assert_text_contains` | 断言文本包含 | locator_type, element, expected_text, wait_time |
| `assert_element_exists` | 断言元素存在 | locator_type, element, timeout |
| `assert_element_not_exists` | 断言元素不存在 | locator_type, element, timeout |
| `assert_element_enabled` | 断言元素启用 | locator_type, element, timeout |
| `assert_element_selected` | 断言元素选中 | locator_type, element, timeout |
| `assert_variable_equals` | 断言变量相等 | variable_name, expected_value |

### 截图与页面源码

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `take_screenshot` | 截图 | filename |
| `take_full_screenshot` | 全屏截图 | filename |
| `get_page_source` | 获取页面源码 | variable_name, save_to_file |

### 设备操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `press_home` | 按 Home 键 | - |
| `lock_device` | 锁屏 | duration |
| `unlock_device` | 解锁 | - |
| `shake_device` | 摇一摇 | - |
| `rotate_screen` | 旋转屏幕 | orientation (PORTRAIT/LANDSCAPE) |
| `get_orientation` | 获取屏幕方向 | variable_name |
| `hide_keyboard` | 隐藏键盘 | - |
| `is_keyboard_shown` | 检查键盘状态 | variable_name |
| `press_keycode` | 按键码 (Android) | keycode, metastate |
| `long_press_keycode` | 长按键码 (Android) | keycode, metastate |

### App 操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `start_activity` | 启动 Activity (Android) | app_package, app_activity |
| `get_current_activity` | 获取当前 Activity | variable_name |
| `get_current_package` | 获取当前 Package | variable_name |
| `background_app` | 后台运行 | duration |
| `reset_app` | 重置 App | - |
| `install_app` | 安装 App | app_path |
| `remove_app` | 卸载 App | app_id |
| `is_app_installed` | 检查是否安装 | app_id, variable_name |
| `terminate_app` | 终止 App | app_id |
| `activate_app` | 激活 App | app_id |
| `query_app_state` | 获取 App 状态 | app_id, variable_name |

### Context 切换

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `get_contexts` | 获取所有 Context | variable_name |
| `switch_context` | 切换 Context | context_name |
| `get_current_context` | 获取当前 Context | variable_name |

### 通知与剪贴板

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `open_notifications` | 打开通知栏 (Android) | - |
| `get_clipboard` | 获取剪贴板 | variable_name |
| `set_clipboard` | 设置剪贴板 | content |

### 文件操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `push_file` | 推送文件到设备 | remote_path, local_path |
| `pull_file` | 从设备拉取文件 | remote_path, local_path |

### 变量操作

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `set_variable` | 设置变量 | variable_name, value |
| `get_variable` | 获取变量 | variable_name |

### Python 脚本执行

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `run_script` | 执行 Python 脚本文件 | script_path, function_name, variable_name |
| `run_code` | 执行 Python 代码片段 | code, variable_name |

**run_script 示例**：

```yaml
- 执行自定义脚本:
    关键字: run_script
    script_path: scripts/my_script.py
    function_name: process_data
    variable_name: result
```

**run_code 示例**：

```yaml
- 执行Python代码:
    关键字: run_code
    code: |
      import random
      __result__ = random.randint(1, 100)
    variable_name: random_number
```

## 目录结构

```
mobile-engine/
├── plugin.yaml          # 插件配置
├── setup.py             # 安装配置
├── requirements.txt     # 依赖
├── README.md            # 文档
├── examples/            # 示例用例
│   ├── example-mobile-cases/    # YAML 格式用例示例
│   │   ├── context.yaml             # 全局配置
│   │   ├── 1_android_smoke.yaml     # Android 冒烟测试
│   │   ├── 2_ios_smoke.yaml         # iOS 冒烟测试
│   │   ├── 3_login_flow.yaml        # 登录流程测试
│   │   ├── 4_element_operations.yaml # 元素操作测试
│   │   ├── 5_swipe_scroll.yaml      # 滑动滚动测试
│   │   ├── 6_device_operations.yaml # 设备操作测试
│   │   ├── 7_app_management.yaml    # App 管理测试
│   │   ├── 8_data_driven.yaml       # 数据驱动测试
│   │   ├── 9_assertions.yaml        # 断言测试
│   │   └── 10_clipboard_notifications.yaml # 剪贴板通知测试
│   │
│   ├── example-excel-cases/     # Excel 格式用例示例
│   │   ├── context.xlsx             # 全局配置
│   │   ├── 1_android_basic.xlsx     # Android 基础测试
│   │   ├── 2_element_operations.xlsx # 元素操作测试
│   │   ├── 3_swipe_operations.xlsx  # 滑动操作测试
│   │   └── 4_assertions.xlsx        # 断言测试
│   │
│   └── example-pytest-scripts/  # Pytest 脚本示例
│       ├── conftest.py          # Pytest 配置和 Fixtures
│       ├── test_mobile_basic.py # 基础移动端测试
│       └── test_mobile_advanced.py # 高级测试示例
├── mobilerun/           # 核心代码
│   ├── cli.py           # 命令行入口
│   ├── core/            # 核心模块
│   │   ├── CasesPlugin.py
│   │   ├── MobileTestRunner.py
│   │   ├── globalContext.py
│   │   └── exceptions.py
│   ├── extend/          # 扩展模块
│   │   ├── keywords.py  # 关键字实现
│   │   ├── keywords.yaml
│   │   └── script/
│   ├── parse/           # 用例解析
│   │   ├── CaseParser.py
│   │   ├── YamlCaseParser.py
│   │   └── ExcelCaseParser.py
│   └── utils/           # 工具类
│       ├── AppiumManager.py
│       ├── VarRender.py
│       └── DynamicTitle.py
└── reports/             # 测试报告
    ├── complete.html
    └── screenshots/
```

## 扩展关键字

在 `--keyDir` 指定的目录下创建 Python 文件，类名与文件名相同，即可扩展自定义关键字：

```python
# my_keywords.py
class my_keywords:
    def my_custom_action(self, **kwargs):
        # 自定义逻辑
        pass
```

## 原生 Pytest 支持

### 快速开始

```bash
cd mobile-engine/examples/example-pytest-scripts
pytest -v -s --platform=android --device-name="emulator-5554"
```

### Fixtures 说明

#### driver

自动管理 Appium driver 生命周期：

```python
def test_example(driver):
    # driver 已自动创建
    driver.find_element(...)
    # 测试结束后自动关闭
```

#### mobile_keywords

提供 Mobile 关键字实例（依赖 driver）：

```python
def test_example(mobile_keywords, driver):
    mobile_keywords.click_element(定位方式="id", 元素="button")
```

#### mobile_keywords_no_driver

提供 Mobile 关键字实例（不自动创建 driver）：

```python
def test_example(mobile_keywords_no_driver):
    mobile_keywords_no_driver.open_app(platform="android", ...)
    mobile_keywords_no_driver.close_app()
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--platform` | 移动平台 (android/ios) | android |
| `--appium-server` | Appium 服务器地址 | http://127.0.0.1:4723 |
| `--device-name` | 设备名称 | None |
| `--app-package` | Android 应用包名 | None |
| `--app-activity` | Android 入口 Activity | None |

### Pytest 示例

```python
import pytest
import allure

@allure.feature("登录功能")
def test_login(mobile_keywords_no_driver):
    """测试登录流程"""
    with allure.step("启动应用"):
        mobile_keywords_no_driver.open_app(
            platform="android",
            app_package="com.example.app",
            app_activity=".MainActivity"
        )
    
    with allure.step("输入用户名"):
        mobile_keywords_no_driver.input_text(
            定位方式="id",
            元素="username",
            文本="testuser"
        )
    
    with allure.step("关闭应用"):
        mobile_keywords_no_driver.close_app()

@pytest.mark.parametrize("keyword", ["苹果", "香蕉", "橙子"])
def test_search(mobile_keywords, driver, keyword):
    """参数化搜索测试"""
    mobile_keywords.input_text(定位方式="id", 元素="search", 文本=keyword)
    mobile_keywords.click_element(定位方式="id", 元素="search_btn")
```

### 运行选项

```bash
# 运行所有测试
pytest -v -s

# 运行冒烟测试
pytest -v -s -m smoke

# 运行 Android 测试
pytest -v -s -m android

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 与 web-engine 的对比

| 特性 | web-engine | mobile-engine |
|------|------------|---------------|
| 驱动 | Playwright | Appium |
| 平台 | Web 浏览器 | Android / iOS |
| 用例格式 | YAML / Excel | YAML / Excel |
| 变量渲染 | Jinja2 | Jinja2 |
| 报告 | Allure | Allure |
| 基础关键字 | 50+ | 70+ |
| 脚本支持 | run_script / run_code | run_script / run_code |
