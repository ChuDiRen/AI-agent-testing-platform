# API Engine AI 功能指南

基于 LLM 的智能 API 测试功能，支持自然语言描述进行 API 测试。

## 功能特点

- 🤖 **AI 生成请求** - 根据自然语言描述自动生成 API 请求参数
- ✅ **AI 智能断言** - 用自然语言描述期望结果，AI 自动验证
- 📊 **AI 数据提取** - 从响应中智能提取需要的数据
- 📝 **AI 生成测试用例** - 根据 API 文档自动生成测试用例
- 🔍 **AI 响应分析** - 分析 API 响应，提供测试建议

## 快速开始

### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 硅基流动 (推荐国内用户)
SILICONFLOW_API_KEY=your_api_key_here

# 或者使用 DeepSeek
DEEPSEEK_API_KEY=your_api_key_here

# 或者使用 OpenAI
OPENAI_API_KEY=your_api_key_here
```

### 2. YAML 用例示例

```yaml
desc: AI API 测试示例

steps:
  # 配置 AI 助手
  - 配置AI:
      关键字: ai_configure
      llm_provider: siliconflow
      llm_model: deepseek-ai/DeepSeek-V3

  # AI 生成并发送请求
  - AI发送请求:
      关键字: ai_send_request
      task: "获取所有用户列表"
      base_url: "https://jsonplaceholder.typicode.com"

  # AI 智能断言
  - AI断言响应:
      关键字: ai_assert_response
      assertion: "状态码应该是 200，响应应该是一个数组"

  # AI 提取数据
  - AI提取数据:
      关键字: ai_extract_data
      extraction: "提取第一个用户的邮箱地址"
      variable_name: first_user_email
```

## AI 关键字详解

### ai_configure - 配置 AI 助手

```yaml
- 配置AI:
    关键字: ai_configure
    llm_provider: siliconflow # openai/deepseek/siliconflow
    llm_model: deepseek-ai/DeepSeek-V3 # 可选，使用默认模型
    api_key: xxx # 可选，从环境变量读取
    timeout: 30 # 超时时间（秒）
```

### ai_generate_request - AI 生成请求参数

```yaml
- AI生成请求:
    关键字: ai_generate_request
    task: "创建一个用户，用户名 test_user，邮箱 test@example.com"
    base_url: "https://api.example.com"
    api_doc: "POST /users - 创建用户" # 可选
    variable_name: request_params # 保存到的变量名
```

### ai_send_request - AI 发送请求

```yaml
- AI发送请求:
    关键字: ai_send_request
    task: "获取用户 ID 为 1 的详细信息"
    base_url: "https://jsonplaceholder.typicode.com"
    headers: # 可选，额外的请求头
      Authorization: Bearer xxx
```

### ai_assert_response - AI 智能断言

```yaml
- AI断言:
    关键字: ai_assert_response
    assertion: "状态码应该是 200，响应中应该包含 id 字段"
```

**断言示例：**

- `"状态码应该是 200"`
- `"响应中应该包含 user_id 字段"`
- `"返回的用户列表应该不为空"`
- `"name 字段的值应该是 'test_user'"`
- `"响应时间应该小于 2 秒"`

### ai_extract_data - AI 数据提取

```yaml
- AI提取:
    关键字: ai_extract_data
    extraction: "提取 token 字段的值"
    variable_name: auth_token
```

**提取示例：**

- `"提取第一个用户的 ID"`
- `"提取所有用户的邮箱地址"`
- `"提取响应中的 access_token"`
- `"提取错误信息"`

### ai_generate_test_cases - AI 生成测试用例

```yaml
- AI生成测试用例:
    关键字: ai_generate_test_cases
    api_doc: |
      POST /users - 创建用户
      参数:
        - name: 用户名（必填，2-50字符）
        - email: 邮箱（必填，有效邮箱格式）
        - age: 年龄（可选，0-150）
    test_scenarios: "正常创建、缺少必填参数、参数格式错误、边界值测试"
    variable_name: generated_cases
```

### ai_analyze_response - AI 响应分析

```yaml
- AI分析响应:
    关键字: ai_analyze_response
    focus: "数据完整性" # 可选：性能、安全、数据完整性
```

## LLM 提供商配置

### 硅基流动 (SiliconFlow) - 推荐国内用户

```yaml
- 配置AI:
    关键字: ai_configure
    llm_provider: siliconflow
    llm_model: deepseek-ai/DeepSeek-V3
```

环境变量：`SILICONFLOW_API_KEY`

**支持的模型：**

- `deepseek-ai/DeepSeek-V3` (推荐)
- `Qwen/Qwen2.5-72B-Instruct`
- `THUDM/glm-4-9b-chat`

### DeepSeek

```yaml
- 配置AI:
    关键字: ai_configure
    llm_provider: deepseek
    llm_model: deepseek-chat
```

环境变量：`DEEPSEEK_API_KEY`

### OpenAI

```yaml
- 配置AI:
    关键字: ai_configure
    llm_provider: openai
    llm_model: gpt-4o
```

环境变量：`OPENAI_API_KEY`

## 完整示例

### 示例 1：用户 CRUD 测试

```yaml
desc: 用户 CRUD AI 测试

context:
  base_url: https://jsonplaceholder.typicode.com

steps:
  - 配置AI:
      关键字: ai_configure
      llm_provider: siliconflow

  - 获取用户列表:
      关键字: ai_send_request
      task: "获取所有用户"
      base_url: ${{base_url}}

  - 验证列表:
      关键字: ai_assert_response
      assertion: "状态码 200，返回数组且不为空"

  - 获取单个用户:
      关键字: ai_send_request
      task: "获取 ID 为 1 的用户详情"
      base_url: ${{base_url}}

  - 验证用户:
      关键字: ai_assert_response
      assertion: "响应包含 id、name、email 字段"

  - 提取邮箱:
      关键字: ai_extract_data
      extraction: "提取用户邮箱"
      variable_name: user_email
```

### 示例 2：登录流程测试

```yaml
desc: 登录流程 AI 测试

steps:
  - 配置AI:
      关键字: ai_configure
      llm_provider: siliconflow

  - 登录请求:
      关键字: ai_send_request
      task: "使用用户名 admin 密码 123456 登录"
      base_url: "https://api.example.com"
      api_doc: "POST /auth/login - 用户登录，参数 username, password"

  - 验证登录:
      关键字: ai_assert_response
      assertion: "登录成功，返回 token"

  - 提取Token:
      关键字: ai_extract_data
      extraction: "提取 access_token 或 token 字段"
      variable_name: auth_token

  - 分析响应:
      关键字: ai_analyze_response
      focus: "安全性"
```

## 与传统关键字混合使用

AI 关键字可以与传统关键字混合使用：

```yaml
steps:
  # 传统方式发送请求
  - 发送请求:
      关键字: send_request
      method: GET
      url: https://api.example.com/users

  # 使用 AI 断言
  - AI验证:
      关键字: ai_assert_response
      assertion: "返回用户列表，每个用户都有 id 和 name"

  # 使用 AI 提取
  - AI提取:
      关键字: ai_extract_data
      extraction: "提取第一个用户的 ID"
      variable_name: user_id

  # 传统方式使用提取的数据
  - 获取用户详情:
      关键字: send_request
      method: GET
      url: https://api.example.com/users/${{user_id}}
```

## 常见问题

### 1. 如何选择 LLM 提供商？

- **国内用户**：推荐 **硅基流动 SiliconFlow**，访问稳定，价格实惠
- **追求效果**：推荐 OpenAI GPT-4o
- **预算有限**：推荐 DeepSeek，性价比最高

### 2. AI 断言失败怎么办？

1. 检查断言描述是否清晰明确
2. 查看响应内容是否符合预期
3. 尝试更具体的断言描述

### 3. 如何提高 AI 准确性？

1. 提供清晰的任务描述
2. 如果有 API 文档，通过 `api_doc` 参数提供
3. 使用更强大的模型（如 GPT-4o）

## 更新日志

### v1.0.0 (2024-12)

- 初始版本
- 支持 AI 生成请求、断言、提取数据
- 支持多种 LLM 提供商
- 与传统关键字无缝集成
