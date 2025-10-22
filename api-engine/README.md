# API Engine - API 自动化测试引擎

基于 requests 的 API 自动化测试引擎，采用关键字驱动和数据驱动的设计理念。

## 特性

- ✨ **关键字驱动**：丰富的 API 关键字库，简化测试用例编写
- 📝 **YAML 格式**：使用 YAML 编写测试用例，清晰易读
- 🐍 **原生 Pytest**：支持使用 Python pytest 脚本编写测试
- 🔄 **数据驱动**：支持 DDT 数据驱动测试，一个用例多组数据
- 📊 **Allure 报告**：集成 Allure 测试报告，美观详细
- 🔧 **易扩展**：支持自定义关键字扩展
- 🗄️ **数据库支持**：支持 MySQL 数据库操作

## 目录结构

```
api-engine/
├── apirun/                 # 核心引擎代码
│   ├── core/              # 核心运行器
│   │   ├── ApiTestRunner.py    # 测试执行器
│   │   ├── globalContext.py    # 全局上下文
│   │   └── CasesPlugin.py      # pytest 插件
│   ├── extend/            # 关键字扩展
│   │   ├── keywords.py         # 关键字库
│   │   └── script/            # 脚本执行器
│   ├── parse/             # 用例解析器
│   │   ├── YamlCaseParser.py   # YAML 解析器
│   │   └── CaseParser.py       # 解析器入口
│   └── utils/             # 工具类
│       ├── VarRender.py        # 变量渲染
│       └── DynamicTitle.py     # 动态标题
├── examples/              # 示例用例
│   ├── example-api-cases/     # YAML 用例
│   └── example-pytest-scripts/ # Pytest 脚本
├── requirements.txt       # 依赖配置
└── setup.py              # 安装配置
```

## 快速开始

### 1. 安装依赖

```bash
cd api-engine
pip install -r requirements.txt
```

### 2. 运行示例用例

#### 方式一：运行 YAML 用例

```bash
cd apirun
python cli.py --type=yaml --cases=../examples/example-api-cases
```

#### 方式二：运行 Pytest 脚本

```bash
cd api-engine/examples/example-pytest-scripts
pytest -v -s
```

### 3. 查看测试报告

```bash
# 生成 Allure 报告
allure generate -c -o allure-report

# 打开报告
allure open allure-report
```

## 测试方式对比

### YAML 驱动测试

**适用场景**：
- 测试人员不熟悉编程
- 快速编写简单测试用例
- 数据驱动测试

**示例**：

```yaml
desc: 登录测试用例
steps:
  - 发送请求:
      关键字: send_request
      method: POST
      url: "{{URL}}/api/login"
      data:
        username: admin
        password: admin123
```

### 原生 Pytest 测试

**适用场景**：
- 开发人员或熟悉 Python 的测试人员
- 需要复杂逻辑的测试场景
- 需要使用 pytest 高级特性

**示例**：

```python
import pytest
import allure

def test_login_api(api_keywords):
    """测试登录接口"""
    with allure.step("发送登录请求"):
        api_keywords.send_request(
            关键字="send_request",
            method="POST",
            url="http://example.com/api/login",
            data={"username": "admin", "password": "123456"}
        )

@pytest.mark.parametrize("username,password", [
    ("user1", "pass1"),
    ("user2", "pass2"),
])
def test_login_ddt(api_keywords, username, password):
    """数据驱动登录测试"""
    api_keywords.send_request(
        关键字="send_request",
        method="POST",
        url="http://example.com/api/login",
        data={"username": username, "password": password}
    )
```

## 原生 Pytest 支持

### 快速开始

```bash
cd api-engine/examples/example-pytest-scripts
pytest -v -s
```

### Fixtures 说明

#### api_keywords

提供 API 关键字实例，自动初始化：

```python
def test_example(api_keywords):
    api_keywords.send_request(
        method="GET",
        url="http://example.com/api/users"
    )
```

### 特性支持

- ✅ 参数化测试 (`@pytest.mark.parametrize`)
- ✅ Fixture 机制
- ✅ 测试类组织
- ✅ 测试标记 (`@pytest.mark.smoke`)
- ✅ Allure 报告集成
- ✅ 所有 pytest 插件

### 运行选项

```bash
# 运行所有测试
pytest -v -s

# 运行特定测试
pytest test_api_basic.py::test_login_api -v -s
pytest -k "test_login" -v -s

# 运行标记的测试
pytest -m smoke -v -s

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 关键字说明

### HTTP 请求

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `send_request` | 发送 HTTP 请求 | method, url, params, headers, data, json, files |
| `send_request_and_download` | 发送请求并下载文件 | 同上 |

### 数据提取

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `ex_jsonData` | 提取 JSON 数据 | EXVALUE, INDEX, VARNAME |
| `ex_reData` | 提取正则数据 | EXVALUE, INDEX, VARNAME |
| `ex_mysqlData` | 提取数据库数据 | 数据库, SQL, 引用变量 |

### 断言

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `assert_text_comparators` | 文本比较断言 | VALUE, OP_STR, EXPECTED, MESSAGE |
| `assert_files_by_md5_comparators` | 文件 MD5 比较 | value, expected |

## YAML 用例编写

### 基础用例

```yaml
desc: API 基础测试
steps:
  - 发送GET请求:
      关键字: send_request
      method: GET
      url: "{{URL}}/api/users"
      headers:
        Authorization: "Bearer {{token}}"
  
  - 提取数据:
      关键字: ex_jsonData
      EXVALUE: "$.data.user_id"
      VARNAME: "user_id"
  
  - 断言状态码:
      关键字: assert_text_comparators
      VALUE: 200
      OP_STR: "=="
      EXPECTED: 200
```

### 数据驱动用例

```yaml
desc: 登录测试
steps:
  - 发送登录请求:
      关键字: send_request
      method: POST
      url: "{{URL}}/api/login"
      data:
        username: "{{username}}"
        password: "{{password}}"

ddts:
  - desc: "正确的用户名和密码"
    username: "admin"
    password: "123456"
  
  - desc: "错误的密码"
    username: "admin"
    password: "wrong"
```

## 配置文件

`context.yaml` 示例：

```yaml
URL: http://example.com
_database:
  mysql001:
    host: localhost
    port: 3306
    user: root
    password: password
    db: test_db
```

## 命令行参数

- `--type`: 用例类型（yaml/pytest）
- `--cases`: 用例目录路径
- `--keyDir`: 自定义关键字目录

## 自定义关键字

```python
class MyKeyword:
    def my_custom_keyword(self, **kwargs):
        # 实现自定义逻辑
        pass
```

## 常见问题

### 1. 如何在 YAML 和 Pytest 之间选择？

- **YAML**：适合简单测试、数据驱动、非编程人员
- **Pytest**：适合复杂逻辑、需要编程灵活性、开发人员

### 2. Pytest 脚本可以使用 g_context 吗？

不建议。原生 Pytest 脚本应该使用 Python 原生方式管理变量，保持独立性。

### 3. 如何在 Pytest 中使用框架关键字？

通过 `api_keywords` fixture 注入：

```python
def test_example(api_keywords):
    api_keywords.send_request(...)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

