# mobile-engine

基于 Appium 的移动端自动化测试引擎（Android + iOS），用例模型与 `web-engine` 完全对齐。

## 特性

- ✅ **关键字驱动**：70+ 内置关键字，覆盖移动端全部操作场景
- ✅ **数据驱动**：支持 YAML/Excel 用例格式，支持 DDT 数据驱动测试
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

### Android（apk 路径）

```bash
mobilerun --type=yaml --cases=./examples --platform=android --app=E:\\path\\to\\app.apk --udid=emulator-5554
```

### iOS（bundleId）

```bash
mobilerun --type=yaml --cases=./examples --platform=ios --bundleId=com.example.app --udid=00008110-...
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

## 目录结构

```
mobile-engine/
├── plugin.yaml          # 插件配置
├── setup.py             # 安装配置
├── requirements.txt     # 依赖
├── README.md            # 文档
├── examples/            # 示例用例
│   ├── context.yaml     # 全局配置
│   ├── 1_android_smoke.yaml
│   ├── 2_ios_smoke.yaml
│   ├── 3_login_flow.yaml
│   └── ...
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

## Mobile-Use AI 关键字

基于 [mobile-use](https://github.com/minitap-ai/mobile-use) 的 AI 驱动移动端自动化，支持自然语言控制。

### 安装 mobile-use

```bash
pip install mobile-use
# 或从源码安装
git clone https://github.com/minitap-ai/mobile-use.git
cd mobile-use && pip install -e .
```

### 配置 LLM

设置环境变量：
```bash
export OPENAI_API_KEY=your_api_key
# 或使用其他 LLM
export DEEPSEEK_API_KEY=your_api_key
export SILICONFLOW_API_KEY=your_api_key
```

### AI 关键字列表

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `mu_configure` | 配置 Mobile-Use | llm_provider, llm_model, api_key, timeout, max_steps |
| `mu_init_agent` | 初始化 AI Agent | platform, device_id, llm_provider, llm_model |
| `mu_close_agent` | 关闭 AI Agent | - |
| `mu_run_task` | 执行 AI 任务 | goal, output_description, max_steps, variable_name |
| `mu_analyze_screen` | 分析屏幕 | prompt, variable_name |
| `mu_tap` | AI 点击 | element_desc |
| `mu_input` | AI 输入 | element_desc, text, clear_first |
| `mu_swipe` | AI 滑动 | direction, element_desc |
| `mu_back` | AI 返回 | - |
| `mu_home` | AI 回主屏幕 | - |
| `mu_open_app` | AI 打开应用 | app_name |
| `mu_close_app` | AI 关闭应用 | app_name |
| `mu_extract_data` | AI 数据抓取 | data_desc, output_format, variable_name |
| `mu_get_text` | AI 获取文本 | element_desc, variable_name |
| `mu_assert_visible` | AI 断言可见 | element_desc |
| `mu_assert_text_contains` | AI 断言文本 | expected_text, element_desc |
| `mu_login` | AI 智能登录 | username, password, app_name |
| `mu_search` | AI 智能搜索 | keyword, app_name |
| `mu_send_message` | AI 发送消息 | recipient, message, app_name |
| `mu_screenshot` | AI 截图 | filename, description |
| `mu_wait` | AI 等待条件 | condition, timeout |

### AI 用例示例

```yaml
desc: AI 自动化测试
steps:
  - 配置 AI:
      关键字: mu_configure
      llm_provider: "openai"
      llm_model: "gpt-4o"

  - 启动应用:
      关键字: open_app

  - AI 执行任务:
      关键字: mu_run_task
      goal: "打开设置，查看电池电量"
      variable_name: battery_info

  - AI 数据抓取:
      关键字: mu_extract_data
      data_desc: "获取前3个联系人的姓名和电话"
      output_format: "JSON 数组"
      variable_name: contacts

  - AI 断言:
      关键字: mu_assert_visible
      element_desc: "设置页面"

  - 关闭应用:
      关键字: close_app
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
| AI 关键字 | browser-use | mobile-use |
