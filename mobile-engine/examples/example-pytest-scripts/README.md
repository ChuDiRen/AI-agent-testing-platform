# Mobile Engine Pytest 脚本示例

本目录包含使用原生 pytest 编写移动端测试的示例。

## 文件说明

| 文件 | 说明 |
|------|------|
| `conftest.py` | Pytest 配置和 Fixtures |
| `test_mobile_basic.py` | 基础移动端测试示例 |
| `test_mobile_advanced.py` | 高级测试示例（参数化、测试类等） |

## 快速开始

### 1. 启动 Appium 服务器

```bash
appium
```

### 2. 连接设备

确保 Android 设备已连接并启用 USB 调试，或 iOS 设备已配置好。

### 3. 运行测试

```bash
cd mobile-engine/examples/example-pytest-scripts

# 运行所有测试
pytest -v -s

# 指定平台
pytest -v -s --platform=android

# 指定设备和应用
pytest -v -s --platform=android --device-name="emulator-5554" --app-package="com.android.settings" --app-activity=".Settings"

# 运行冒烟测试
pytest -v -s -m smoke

# 运行特定测试
pytest test_mobile_basic.py::test_open_app -v -s
```

## Fixtures 说明

### driver

自动管理 Appium driver 生命周期：

```python
def test_example(driver):
    # driver 已自动创建
    driver.find_element(...)
    # 测试结束后自动关闭
```

### mobile_keywords

提供 Mobile 关键字实例（依赖 driver）：

```python
def test_example(mobile_keywords, driver):
    mobile_keywords.click_element(定位方式="id", 元素="button")
```

### mobile_keywords_no_driver

提供 Mobile 关键字实例（不自动创建 driver）：

```python
def test_example(mobile_keywords_no_driver):
    mobile_keywords_no_driver.open_app(platform="android", ...)
    # 手动管理 driver
    mobile_keywords_no_driver.close_app()
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--platform` | 移动平台 (android/ios) | android |
| `--appium-server` | Appium 服务器地址 | http://127.0.0.1:4723 |
| `--device-name` | 设备名称 | None |
| `--app-package` | Android 应用包名 | None |
| `--app-activity` | Android 入口 Activity | None |

## 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.smoke` | 冒烟测试 |
| `@pytest.mark.regression` | 回归测试 |
| `@pytest.mark.mobile` | 移动端测试 |
| `@pytest.mark.android` | Android 测试 |
| `@pytest.mark.ios` | iOS 测试 |

## 与 YAML 用例对比

| 特性 | YAML 用例 | Pytest 脚本 |
|------|-----------|-------------|
| 编写难度 | 简单 | 需要 Python 基础 |
| 灵活性 | 一般 | 高 |
| 参数化 | DDT 支持 | 原生支持 |
| 复杂逻辑 | 有限 | 完全支持 |
| 调试 | 困难 | 方便 |
| IDE 支持 | 一般 | 完整 |
