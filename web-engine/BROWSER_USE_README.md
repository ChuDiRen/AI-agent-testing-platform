# Browser-Use AI 自动化集成指南

基于 [browser-use](https://github.com/browser-use/browser-use) 库的智能浏览器自动化功能，使用 LLM 驱动的方式执行复杂的 Web 自动化任务。

## 特性

- 🤖 **LLM 驱动**：使用自然语言描述任务，AI 自动规划并执行
- 🌐 **多模型支持**：支持 OpenAI、DeepSeek、Qwen、Claude 等多种 LLM
- 🔧 **无缝集成**：与现有 web-engine 框架完美兼容
- 📝 **YAML 用例**：可在 YAML 测试用例中直接使用
- 🎯 **智能操作**：自动处理复杂的多步骤任务

## 核心特点

| 特性           | 说明                                           |
| -------------- | ---------------------------------------------- |
| **底层技术**   | Playwright + LLM                               |
| **定位方式**   | DOM 分析 + 智能识别                            |
| **任务复杂度** | 支持多步骤复杂任务                             |
| **模型选择**   | 多种 LLM 可选 (OpenAI, DeepSeek, Qwen, Claude) |
| **适用场景**   | 复杂业务流程自动化                             |

## 快速开始

### 1. 安装依赖

```bash
cd web-engine
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 选择一个 LLM 提供商配置

# 硅基流动 SiliconFlow (推荐国内用户)
SILICONFLOW_API_KEY=your-siliconflow-key

# DeepSeek (推荐，性价比高)
DEEPSEEK_API_KEY=your-deepseek-key

# OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o

# 阿里云通义千问
DASHSCOPE_API_KEY=your-dashscope-key

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-key
```

### 3. 运行示例

```bash
cd webrun
python cli.py --type=yaml --cases=../examples/example-web-cases/7_browser_use_test.yaml
```

## 关键字说明

### 配置与浏览器管理

| 关键字             | 说明             | 主要参数                        |
| ------------------ | ---------------- | ------------------------------- |
| `bu_configure`     | 配置 Browser-Use | llm_provider, headless, timeout |
| `bu_open_browser`  | 启动 AI 浏览器   | headless, llm_provider          |
| `bu_close_browser` | 关闭浏览器       | -                               |

### 核心 AI 任务

| 关键字            | 说明             | 主要参数                 |
| ----------------- | ---------------- | ------------------------ |
| `bu_run_task`     | 执行复杂 AI 任务 | task (自然语言描述)      |
| `bu_navigate`     | AI 导航到 URL    | url                      |
| `bu_click`        | AI 点击元素      | element_desc             |
| `bu_input`        | AI 输入文本      | element_desc, text       |
| `bu_extract_text` | AI 提取文本      | text_desc, variable_name |
| `bu_scroll`       | AI 滚动页面      | direction, element_desc  |
| `bu_hover`        | AI 鼠标悬停      | element_desc             |
| `bu_drag`         | AI 拖拽操作      | source_desc, target_desc |
| `bu_select`       | AI 选择下拉框    | element_desc, option     |

### 断言关键字

| 关键字                    | 说明          | 主要参数                    |
| ------------------------- | ------------- | --------------------------- |
| `bu_assert_visible`       | 断言元素可见  | element_desc                |
| `bu_assert_text_contains` | 断言文本包含  | element_desc, expected_text |
| `bu_assert_url_contains`  | 断言 URL 包含 | expected_url                |

### 高级功能

| 关键字            | 说明         | 主要参数           |
| ----------------- | ------------ | ------------------ |
| `bu_fill_form`    | 智能填写表单 | form_data (字典)   |
| `bu_login`        | 智能登录     | username, password |
| `bu_search`       | 智能搜索     | keyword            |
| `bu_screenshot`   | AI 截图      | filename           |
| `bu_wait`         | 等待条件满足 | condition          |
| `bu_switch_tab`   | 切换标签页   | tab_desc, index    |
| `bu_handle_alert` | 处理弹窗     | action             |

## YAML 用例示例

### 基础示例

```yaml
desc: Browser-Use 基础测试

steps:
  - 配置AI引擎:
      关键字: bu_configure
      llm_provider: deepseek
      headless: false

  - 启动浏览器:
      关键字: bu_open_browser

  - 执行搜索任务:
      关键字: bu_run_task
      task: "打开百度，搜索 Python，点击第一个结果"

  - 关闭浏览器:
      关键字: bu_close_browser
```

### 登录示例

```yaml
desc: Browser-Use 登录测试

steps:
  - 配置并启动:
      关键字: bu_open_browser
      llm_provider: openai

  - 导航到登录页:
      关键字: bu_navigate
      url: https://example.com/login

  - 智能登录:
      关键字: bu_login
      username: admin
      password: 123456

  - 断言登录成功:
      关键字: bu_assert_visible
      element_desc: 欢迎信息或用户头像

  - 关闭浏览器:
      关键字: bu_close_browser
```

### 表单填写示例

```yaml
desc: Browser-Use 表单填写测试

steps:
  - 启动浏览器:
      关键字: bu_open_browser
      llm_provider: deepseek

  - 导航到表单页:
      关键字: bu_navigate
      url: https://example.com/form

  - 智能填写表单:
      关键字: bu_fill_form
      form_data:
        姓名: 张三
        邮箱: zhangsan@example.com
        电话: 13800138000
        地址: 北京市朝阳区

  - 提交表单:
      关键字: bu_click
      element_desc: 提交按钮

  - 关闭浏览器:
      关键字: bu_close_browser
```

## Python 代码使用

```python
from webrun.extend.browser_use_keywords import BrowserUseKeywords

# 创建实例
bu = BrowserUseKeywords()

# 配置
bu.bu_configure(llm_provider="deepseek", headless=False)

# 启动浏览器
bu.bu_open_browser()

# 执行任务
bu.bu_run_task(task="打开百度，搜索 AI 测试，截图保存结果")

# 关闭浏览器
bu.bu_close_browser()
```

## LLM 提供商配置

### DeepSeek (推荐)

性价比最高，中文理解能力强：

```yaml
- 配置AI引擎:
    关键字: bu_configure
    llm_provider: deepseek
```

环境变量：`DEEPSEEK_API_KEY`

### 硅基流动 SiliconFlow (推荐国内用户)

国内访问稳定，支持多种开源模型：

```yaml
- 配置AI引擎:
    关键字: bu_configure
    llm_provider: siliconflow
    llm_model: deepseek-ai/DeepSeek-V3
```

环境变量：`SILICONFLOW_API_KEY`

**支持的模型**：

- `deepseek-ai/DeepSeek-V3` (默认，推荐)
- `deepseek-ai/DeepSeek-R1`
- `Qwen/Qwen2.5-72B-Instruct`
- `Pro/Qwen/Qwen2.5-Coder-32B-Instruct`
- 更多模型请参考 [硅基流动官网](https://siliconflow.cn)

### OpenAI

最强大的通用能力：

```yaml
- 配置AI引擎:
    关键字: bu_configure
    llm_provider: openai
    llm_model: gpt-4o
```

环境变量：`OPENAI_API_KEY`

### 通义千问 (Qwen)

阿里云服务，国内访问稳定：

```yaml
- 配置AI引擎:
    关键字: bu_configure
    llm_provider: qwen
    llm_model: qwen-max
```

环境变量：`DASHSCOPE_API_KEY`

### Claude

Anthropic 的模型，推理能力强：

```yaml
- 配置AI引擎:
    关键字: bu_configure
    llm_provider: anthropic
    llm_model: claude-3-5-sonnet-20241022
```

环境变量：`ANTHROPIC_API_KEY`

## 最佳实践

### 1. 任务描述要清晰

```yaml
# ✅ 好的描述
task: "在搜索框中输入 'Python 教程'，然后点击蓝色的搜索按钮"

# ❌ 模糊的描述
task: "搜索一下"
```

### 2. 合理设置 max_steps

```yaml
# 简单任务
bu_run_task:
  task: "点击登录按钮"
  max_steps: 10

# 复杂任务
bu_run_task:
  task: "填写完整的注册表单并提交"
  max_steps: 50
```

### 3. 结合传统关键字使用

Browser-Use 关键字可以与原有 Playwright 关键字混合使用：

```yaml
steps:
  # 使用传统方式打开浏览器
  - 打开浏览器:
      关键字: open_browser
      browser: chrome

  # 使用 Browser-Use 执行复杂任务
  - AI执行任务:
      关键字: bu_run_task
      task: "完成复杂的表单填写流程"

  # 使用传统方式断言
  - 断言结果:
      关键字: assert_text_contains
      locator_type: xpath
      element: //div[@class='result']
      expected_text: 成功
```

## 常见问题

### 1. 如何选择 LLM 提供商？

- **国内用户**：推荐 **硅基流动 SiliconFlow**，访问稳定，支持多种开源模型
- **追求效果**：推荐 OpenAI GPT-4o 或 Claude
- **预算有限**：推荐 DeepSeek 或硅基流动，性价比最高

### 2. 任务执行失败怎么办？

1. 检查任务描述是否清晰
2. 增加 `max_steps` 参数
3. 查看截图和日志定位问题
4. 尝试拆分为多个简单任务

### 3. Browser-Use 与 Playwright 关键字如何配合？

`bu_*` 关键字基于 Playwright + LLM，适合复杂的多步骤任务。可以与传统 Playwright 关键字混合使用，根据场景选择最合适的方式。

## 更新日志

### v1.0.0 (2024-12)

- 初始版本
- 集成 browser-use 库
- 支持多种 LLM 提供商
- 提供完整的关键字库
