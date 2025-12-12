# Perf Engine - 性能测试引擎

基于 k6 的性能测试引擎，采用关键字驱动和数据驱动的设计理念，支持 YAML 格式编写性能测试用例。

## 特性

- ✨ **关键字驱动**：通过 YAML 配置性能测试场景，无需编写 JavaScript
- 📝 **YAML 格式**：使用 YAML 编写测试用例，清晰易读
- 🚀 **k6 引擎**：底层使用 Grafana k6，高性能负载测试
- 📊 **多种报告**：支持 JSON、HTML、InfluxDB 等多种输出格式
- 🔧 **易扩展**：支持自定义场景和阈值配置
- 🔄 **数据驱动**：支持参数化测试数据

## 目录结构

```
perf-engine/
├── README.md                  # 项目说明文档
├── requirements.txt           # Python 依赖包配置
├── setup.py                   # 安装配置脚本
│
├── perfrun/                   # 核心测试引擎代码
│   ├── __init__.py
│   ├── cli.py                 # 命令行入口
│   │
│   ├── core/                  # 核心运行器模块
│   │   ├── __init__.py
│   │   ├── runner.py          # k6 测试执行器
│   │   ├── generator.py       # k6 脚本生成器
│   │   └── reporter.py        # 报告生成器
│   │
│   ├── parse/                 # 用例解析器模块
│   │   ├── __init__.py
│   │   └── yaml_parser.py     # YAML 用例解析器
│   │
│   └── utils/                 # 工具类模块
│       ├── __init__.py
│       └── k6_installer.py    # k6 安装检测工具
│
├── examples/                  # 示例用例目录
│   └── example-perf-cases/
│       ├── context.yaml       # 全局配置
│       ├── 1_basic_load.yaml  # 基础负载测试
│       ├── 2_stress_test.yaml # 压力测试
│       └── 3_spike_test.yaml  # 峰值测试
│
├── scripts/                   # 生成的 k6 脚本目录
│
└── reports/                   # 测试报告目录
```

## 前置要求

- **Python 3.7+**
- **k6 已安装并配置到系统 PATH**
  - 确保在命令行中可以直接运行 `k6 version`
  - k6 应该通过系统包管理器安装（如 winget、brew、apt 等）

## 快速开始

### 1. 安装依赖

```bash
cd perf-engine
pip install -r requirements.txt
```

### 2. 运行示例用例

```bash
cd perfrun
python cli.py --cases=../examples/example-perf-cases
```

### 3. 查看测试报告

测试执行完成后，报告会自动生成在 `reports/` 目录下。

## YAML 用例编写

### 基础负载测试

```yaml
name: 基础负载测试
description: 测试 API 在正常负载下的性能表现

# 测试配置
config:
  # 虚拟用户配置
  stages:
    - duration: 30s
      target: 10 # 30秒内逐步增加到10个用户
    - duration: 1m
      target: 10 # 保持10个用户1分钟
    - duration: 30s
      target: 0 # 30秒内逐步减少到0

  # 性能阈值
  thresholds:
    http_req_duration:
      - p(95) < 500 # 95%的请求响应时间小于500ms
      - p(99) < 1000 # 99%的请求响应时间小于1000ms
    http_req_failed:
      - rate < 0.01 # 错误率小于1%

# 测试场景
scenarios:
  - name: 登录接口
    method: POST
    url: "{{BASE_URL}}/api/login"
    headers:
      Content-Type: application/json
    body:
      username: "{{username}}"
      password: "{{password}}"
    checks:
      - status == 200
      - body.contains("token")

  - name: 获取用户列表
    method: GET
    url: "{{BASE_URL}}/api/users"
    headers:
      Authorization: "Bearer {{token}}"
    checks:
      - status == 200
```

### 压力测试

```yaml
name: 压力测试
description: 测试系统在高负载下的极限性能

config:
  stages:
    - duration: 2m
      target: 100 # 2分钟内增加到100个用户
    - duration: 5m
      target: 100 # 保持100个用户5分钟
    - duration: 2m
      target: 200 # 继续增加到200个用户
    - duration: 5m
      target: 200 # 保持200个用户5分钟
    - duration: 2m
      target: 0 # 逐步减少

  thresholds:
    http_req_duration:
      - p(95) < 2000
    http_req_failed:
      - rate < 0.05 # 允许5%错误率
```

### 峰值测试

```yaml
name: 峰值测试
description: 测试系统应对突发流量的能力

config:
  stages:
    - duration: 10s
      target: 10 # 正常负载
    - duration: 1m
      target: 10
    - duration: 10s
      target: 100 # 突然增加到100用户
    - duration: 3m
      target: 100 # 保持峰值
    - duration: 10s
      target: 10 # 恢复正常
    - duration: 1m
      target: 10
    - duration: 10s
      target: 0
```

## 关键字说明

### 测试配置 (config)

| 配置项       | 说明           | 示例                                 |
| ------------ | -------------- | ------------------------------------ |
| `stages`     | 负载阶段配置   | `[{duration: 30s, target: 10}]`      |
| `thresholds` | 性能阈值       | `{http_req_duration: [p(95) < 500]}` |
| `iterations` | 固定迭代次数   | `100`                                |
| `vus`        | 固定虚拟用户数 | `10`                                 |
| `duration`   | 固定测试时长   | `5m`                                 |

### 场景配置 (scenarios)

| 配置项    | 说明      | 示例                               |
| --------- | --------- | ---------------------------------- |
| `name`    | 场景名称  | `登录接口`                         |
| `method`  | HTTP 方法 | `GET`, `POST`, `PUT`, `DELETE`     |
| `url`     | 请求地址  | `{{BASE_URL}}/api/login`           |
| `headers` | 请求头    | `{Content-Type: application/json}` |
| `body`    | 请求体    | `{username: admin}`                |
| `params`  | URL 参数  | `{page: 1, size: 10}`              |
| `checks`  | 响应检查  | `[status == 200]`                  |
| `sleep`   | 请求间隔  | `1s`                               |

## 命令行参数

```bash
python cli.py [OPTIONS]

Options:
  --cases PATH      用例目录路径
  --output PATH     报告输出目录 (默认: ../reports)
  --format FORMAT   报告格式: json, html, influxdb (默认: json)
  --k6-path PATH    k6 可执行文件路径 (默认: 自动检测)
  --dry-run         仅生成脚本，不执行测试
  --verbose         显示详细日志
```

## 报告输出

支持多种报告格式：

- **JSON**: 详细的测试数据，适合程序处理
- **HTML**: 可视化报告，适合人工查看
- **InfluxDB**: 时序数据，适合 Grafana 可视化

## License

MIT License
