# k6 原生脚本示例

本目录包含原生 k6 JavaScript 性能测试脚本示例。

## 脚本列表

| 脚本                | 说明           | 用途                 |
| ------------------- | -------------- | -------------------- |
| `1_basic_load.js`   | 基础负载测试   | 测试正常负载下的性能 |
| `2_stress_test.js`  | 压力测试       | 测试系统极限性能     |
| `3_spike_test.js`   | 峰值测试       | 测试突发流量处理能力 |
| `4_soak_test.js`    | 浸泡测试       | 测试长时间运行稳定性 |
| `5_api_workflow.js` | API 工作流测试 | 模拟真实用户操作流程 |

## 运行方式

### 安装 k6

**Windows:**

```bash
choco install k6
# 或
winget install k6
```

**macOS:**

```bash
brew install k6
```

**Linux:**

```bash
sudo apt-get install k6
```

### 运行单个脚本

```bash
# 基础负载测试
k6 run 1_basic_load.js

# 压力测试
k6 run 2_stress_test.js

# 峰值测试
k6 run 3_spike_test.js

# 浸泡测试
k6 run 4_soak_test.js

# API 工作流测试
k6 run 5_api_workflow.js
```

### 输出报告

```bash
# 输出 JSON 报告
k6 run --out json=result.json 1_basic_load.js

# 输出到 InfluxDB (需要配置)
k6 run --out influxdb=http://localhost:8086/k6 1_basic_load.js

# 输出到 Prometheus (需要配置)
k6 run --out experimental-prometheus-rw 1_basic_load.js
```

### 自定义参数

```bash
# 覆盖虚拟用户数
k6 run --vus 20 1_basic_load.js

# 覆盖测试时长
k6 run --duration 2m 1_basic_load.js

# 覆盖迭代次数
k6 run --iterations 100 1_basic_load.js
```

## 测试类型说明

### 1. 基础负载测试 (Load Test)

- **目的**: 验证系统在预期负载下的性能
- **特点**: 逐步增加用户，保持稳定负载，然后逐步减少
- **指标**: 响应时间、吞吐量、错误率

### 2. 压力测试 (Stress Test)

- **目的**: 找出系统的性能极限
- **特点**: 持续增加负载直到系统出现问题
- **指标**: 最大吞吐量、崩溃点、恢复时间

### 3. 峰值测试 (Spike Test)

- **目的**: 验证系统处理突发流量的能力
- **特点**: 突然大幅增加负载，然后快速恢复
- **指标**: 响应时间变化、错误率、恢复速度

### 4. 浸泡测试 (Soak Test)

- **目的**: 检测长时间运行下的问题（内存泄漏等）
- **特点**: 固定负载长时间运行
- **指标**: 性能退化、资源使用趋势

### 5. API 工作流测试

- **目的**: 模拟真实用户操作流程
- **特点**: 多步骤、有状态、数据驱动
- **指标**: 各步骤响应时间、整体流程成功率

## 性能指标说明

| 指标                       | 说明                |
| -------------------------- | ------------------- |
| `http_reqs`                | 总请求数            |
| `http_req_duration`        | 请求响应时间        |
| `http_req_failed`          | 失败请求率          |
| `http_req_waiting`         | 等待响应时间 (TTFB) |
| `http_req_connecting`      | TCP 连接时间        |
| `http_req_tls_handshaking` | TLS 握手时间        |
| `vus`                      | 当前虚拟用户数      |
| `iterations`               | 完成的迭代次数      |

## 阈值配置示例

```javascript
export const options = {
  thresholds: {
    // 95% 的请求响应时间小于 500ms
    http_req_duration: ["p(95) < 500"],

    // 99% 的请求响应时间小于 1000ms
    http_req_duration: ["p(99) < 1000"],

    // 平均响应时间小于 200ms
    http_req_duration: ["avg < 200"],

    // 最大响应时间小于 2000ms
    http_req_duration: ["max < 2000"],

    // 错误率小于 1%
    http_req_failed: ["rate < 0.01"],
  },
};
```
