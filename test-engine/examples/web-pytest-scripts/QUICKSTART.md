# Playwright Web 测试快速开始

## 🎭 关于 Playwright

Playwright 是 Microsoft 开发的现代化 Web 测试框架，相比 Selenium 具有以下优势：

- ✅ **无需手动管理驱动** - 自动下载和管理浏览器
- ✅ **自动等待机制** - 无需显式等待，减少 flaky 测试
- ✅ **跨浏览器支持** - Chromium、Firefox、WebKit 一套代码
- ✅ **更快的执行速度** - 使用现代浏览器协议
- ✅ **更好的调试工具** - Inspector、Trace Viewer

## 📦 快速安装（3步）

### 步骤 1: 安装依赖

```bash
cd test-engine
pip install -r requirements.txt
```

### 步骤 2: 安装浏览器（**重要！首次必须**）

```bash
playwright install chromium
```

### 步骤 3: 运行测试

```bash
# 运行示例测试（无头模式）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py::TestBaiduSearch::test_baidu_homepage --browser=chromium --headless=true

# 运行所有测试（有界面）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chromium --headless=false
```

## 🎯 支持的浏览器

```bash
# 安装单个浏览器
playwright install chromium   # ✅ 推荐
playwright install firefox
playwright install webkit      # Safari 引擎

# 或安装所有浏览器
playwright install
```

## 🚀 常用命令

```bash
# 运行基础测试（有界面，方便调试）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py --browser=chromium

# 运行高级测试（无头模式，适合 CI）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_advanced.py --browser=chromium --headless=true

# 只运行冒烟测试
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chromium -m smoke

# 使用 Firefox
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=firefox

# 使用 WebKit（Safari 引擎）
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=webkit
```

## 📊 查看报告

测试完成后，会自动生成 Allure 报告：

```bash
# 打开 Allure 报告
allure open reports/allure-report
```

截图保存在：`reports/screenshots/`  
日志保存在：`reports/logdata/log.log`

## 🔧 常见问题

### Q: 提示 "Executable doesn't exist"？

A: 需要先安装浏览器：

```bash
playwright install chromium
```

### Q: 安装失败，提示网络错误？

A: Playwright 从 npmmirror 下载浏览器，如果网络问题，可以：

1. 检查网络连接
2. 使用代理
3. 手动下载并指定浏览器路径

### Q: 如何在 CI/CD 中使用？

A: 使用无头模式并在 CI 脚本中先安装浏览器：

```yaml
# GitHub Actions 示例
- name: Install Playwright browsers
  run: playwright install chromium

- name: Run tests
  run: python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts --browser=chromium --headless=true
```

## 💡 从 Selenium 迁移

如果你之前使用 Selenium，以下是主要区别：

| Selenium | Playwright |
|----------|-----------|
| `driver.find_element(By.ID, "kw")` | `page.locator("#kw")` |
| `element.click()` | `page.locator("#kw").click()` |
| `element.send_keys("text")` | `page.locator("#kw").fill("text")` |
| `WebDriverWait(driver, 10)` | ✅ 自动等待，无需手动 |
| `driver.get(url)` | `page.goto(url)` |
| `driver.title` | `page.title()` |
| `driver.get_screenshot_as_png()` | `page.screenshot()` |

## 📚 更多资源

- [完整文档](README.md) - 详细使用指南
- [Playwright 官方文档](https://playwright.dev/python/)
- [Playwright GitHub](https://github.com/microsoft/playwright)
- [示例代码](test_web_basic.py) - 基础测试示例
- [高级示例](test_web_advanced.py) - 高级特性演示

## 🎉 开始测试

现在你已经准备好了！运行你的第一个 Playwright 测试：

```bash
python -m testrun.cli --engine-type=web --type=pytest --cases=examples/web-pytest-scripts/test_web_basic.py::TestBaiduSearch::test_baidu_homepage --browser=chromium
```

祝测试顺利！🚀
