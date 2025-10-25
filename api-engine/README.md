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
├── __init__.py                # 包初始化文件
├── README.md                  # 项目说明文档（本文件）
├── requirements.txt           # Python 依赖包配置
├── setup.py                   # 安装配置脚本
│
├── apirun/                    # 核心测试引擎代码
│   ├── __init__.py           # 包初始化文件
│   ├── cli.py                # 命令行入口（支持直接运行）
│   ├── pytest.ini            # Pytest 配置文件
│   │
│   ├── core/                 # 核心运行器模块
│   │   ├── __init__.py
│   │   ├── ApiTestRunner.py      # 测试执行器
│   │   ├── CasesPlugin.py        # Pytest 插件
│   │   ├── globalContext.py      # 全局上下文管理
│   │   ├── models.py             # 数据模型定义
│   │   ├── enums.py              # 枚举类型定义
│   │   └── exceptions.py         # 自定义异常类
│   │
│   ├── extend/               # 关键字扩展模块
│   │   ├── __init__.py
│   │   ├── keywords.py           # 关键字实现库
│   │   ├── keywords.yaml         # 关键字配置文件
│   │   ├── keywords_back.yaml    # 关键字备份配置
│   │   └── script/              # 脚本执行器
│   │       ├── __init__.py
│   │       └── run_script.py    # Python 脚本运行器
│   │
│   ├── parse/                # 用例解析器模块
│   │   ├── __init__.py
│   │   ├── CaseParser.py         # 解析器工厂/入口
│   │   ├── YamlCaseParser.py     # YAML 用例解析器
│   │   └── ExcelCaseParser.py    # Excel 用例解析器
│   │
│   └── utils/                # 工具类模块
│       ├── __init__.py
│       ├── VarRender.py          # 变量渲染工具
│       └── DynamicTitle.py       # 动态标题生成
│
├── examples/                 # 示例用例目录
│   ├── example-api-cases/        # YAML 格式用例示例
│   │   ├── context.yaml              # 全局配置（URL、数据库等）
│   │   ├── 1_login_success.yaml      # 登录成功用例
│   │   ├── 1_login_test_cases.yaml   # 登录测试用例集
│   │   ├── 2_database_keyword_call.yaml  # 数据库操作用例
│   │   ├── 2_interface_association.yaml  # 接口关联用例
│   │   ├── 3_json_login.yaml         # JSON 登录用例
│   │   ├── 4_upload_image_and_update_avatar.yaml  # 文件上传用例
│   │   ├── 5_download_image_comparison.yaml       # 文件下载用例
│   │   └── P1.png                    # 测试图片资源
│   │
│   └── example-pytest-scripts/   # Pytest 脚本示例
│       ├── conftest.py               # Pytest 配置和 Fixtures
│       ├── test_api_basic.py         # 基础 API 测试
│       ├── test_api_advanced.py      # 高级 API 测试
│       └── README.md                 # Pytest 示例说明
│
└── reports/                  # 测试报告目录（运行时自动生成）
    ├── allure-results/           # Allure 原始测试数据（JSON）
    ├── allure-report/            # Allure HTML 可视化报告
    └── logdata/                  # Pytest 测试日志
        └── log.log              # 测试执行日志文件
```

> **注意**:
>
> - `__pycache__/` 和 `.pytest_cache/` 等缓存目录已自动忽略
> - `reports/` 目录在首次运行测试后自动创建
> - 所有日志统一保存到 `reports/logdata/` 目录
> - 所有模块使用相对导入，`cli.py` 使用绝对导入以支持直接运行

## 导入策略说明

- **cli.py**: 作为命令行入口文件,使用**绝对导入**,支持直接运行 `python cli.py`
- **其他模块**: apirun 内部模块(core/extend/parse/utils)使用**相对导入**,提高模块独立性

## 快速开始

### 1. 安装依赖

```bash
cd api-engine
pip install -r requirements.txt
```

### 2. 运行示例用例

#### 方式一：运行 YAML 用例

**推荐方式 - 直接运行 cli.py**:

```bash
cd apirun
python cli.py --type=yaml --cases=../examples/example-api-cases
```

**模块方式运行**:

```bash
cd api-engine
python -m apirun.cli --type=yaml --cases=examples/example-api-cases
```

**使用 pytest 直接运行**:

```bash
cd apirun
pytest core/ApiTestRunner.py --type=yaml --cases=../examples/example-api-cases
```

#### 方式二：运行 Pytest 脚本

```bash
cd examples/example-pytest-scripts
pytest -v -s
```

### 3. 查看测试报告

测试执行完成后，报告会自动生成在 `reports/` 目录下：

```bash
# 报告已自动生成，直接打开查看
cd api-engine
allure open reports/allure-report

# 或手动生成报告
allure generate -c -o reports/allure-report reports/allure-results
```

**报告位置**：

- 测试结果数据：`api-engine/reports/allure-results/`
- HTML 报告：`api-engine/reports/allure-report/`

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

### 1. 为什么 cli.py 使用绝对导入,其他模块使用相对导入?

- **cli.py**: 作为入口文件,需要支持直接运行 `python cli.py`,因此使用绝对导入
- **其他模块**: 内部模块使用相对导入,提高模块独立性和可移植性
- **最佳实践**: 入口文件绝对导入,内部模块相对导入

### 2. 运行 cli.py 时报 ImportError 怎么办?

确保在正确的目录运行:

```bash
cd apirun
python cli.py --type=yaml --cases=../examples/example-api-cases
```

或使用模块方式:

```bash
cd api-engine
python -m apirun.cli --type=yaml --cases=examples/example-api-cases
```

### 3. 如何在 YAML 和 Pytest 之间选择？

- **YAML**：适合简单测试、数据驱动、非编程人员
- **Pytest**：适合复杂逻辑、需要编程灵活性、开发人员

### 4. Pytest 脚本可以使用 g_context 吗？

不建议。原生 Pytest 脚本应该使用 Python 原生方式管理变量，保持独立性。

### 5. 如何在 Pytest 中使用框架关键字？

通过 `api_keywords` fixture 注入：

```python
def test_example(api_keywords):
    api_keywords.send_request(...)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
