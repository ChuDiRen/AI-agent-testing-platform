---
name: webapp-testing
description: 使用 Playwright 与本地 Web 应用交互与测试的工具包。支持验证前端功能、调试 UI 行为、捕获浏览器截图以及查看浏览器日志。
---

# Web 应用测试

要测试本地 Web 应用，请编写原生的 Python Playwright 脚本。

**可用辅助脚本**：
- `scripts/with_server.py` - 管理服务器生命周期（支持多个服务器）

**务必先使用 `--help` 运行脚本** 以查看用法。在你先尝试直接运行脚本并确认必须定制之前，不要阅读源码。这些脚本可能非常庞大，会污染你的上下文窗口。它们的设计目的是作为黑盒脚本被直接调用，而不是被纳入你的上下文窗口。

## 决策树：选择你的方法

```
用户任务 → 是静态 HTML 吗？
    ├─ 是 → 直接读取 HTML 文件以识别选择器
    │         ├─ 成功 → 使用这些选择器编写 Playwright 脚本
    │         └─ 失败/不完整 → 按动态应用处理（见下）
    │
    └─ 否（动态 Web 应用） → 服务器是否已在运行？
        ├─ 否 → 运行：python scripts/with_server.py --help
        │        然后使用该助手 + 编写精简的 Playwright 脚本
        │
        └─ 是 → 先侦察，后操作：
            1. 导航并等待 networkidle
            2. 截图或检查 DOM
            3. 从渲染状态中识别选择器
            4. 使用发现的选择器执行操作
```

## 示例：使用 with_server.py

要启动服务器，先运行 `--help`，然后使用该助手：

**单个服务器：**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**多个服务器（例如后端 + 前端）：**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

编写自动化脚本时，只包含 Playwright 逻辑（服务器由助手自动管理）：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # 始终以无头模式启动 chromium
    page = browser.new_page()
    page.goto('http://localhost:5173') # 服务器已运行且就绪
    page.wait_for_load_state('networkidle') # 关键：等待 JS 执行
    # ... 你的自动化逻辑
    browser.close()
```

## “先侦察，后操作”模式

1. **检查渲染后的 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. 根据检查结果**识别选择器**

3. 使用发现的选择器**执行操作**

## 常见陷阱

❌ 在动态应用中，等待 `networkidle` 之前不要检查 DOM
✅ 在检查之前请等待 `page.wait_for_load_state('networkidle')`

## 最佳实践

- **将捆绑脚本作为黑盒使用** - 处理任务时，考虑 `scripts/` 中是否已有脚本可用。这些脚本可以可靠地处理常见且复杂的工作流，同时不污染你的上下文窗口。使用 `--help` 查看用法，然后直接调用。
- 对同步脚本使用 `sync_playwright()`
- 完成后务必关闭浏览器
- 使用描述性选择器：`text=`、`role=`、CSS 选择器或 ID
- 添加适当的等待：`page.wait_for_selector()` 或 `page.wait_for_timeout()`

## 参考文件

- **examples/** - 展示常见模式的示例：
  - `element_discovery.py` - 发现页面上的按钮、链接和输入框
  - `static_html_automation.py` - 使用 file:// URL 操作本地 HTML
  - `console_logging.py` - 在自动化过程中捕获控制台日志