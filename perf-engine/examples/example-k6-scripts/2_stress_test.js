/**
 * 压力测试
 * 测试系统在高负载下的极限性能
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');
const requestCount = new Counter('request_count');

// 全局变量
const BASE_URL = 'https://httpbin.org';

// 测试配置
export const options = {
  // 阶段式增加负载
  stages: [
    { duration: '30s', target: 20 },   // 30秒内增加到20个用户
    { duration: '1m', target: 20 },    // 保持20个用户1分钟
    { duration: '30s', target: 50 },   // 继续增加到50个用户
    { duration: '1m', target: 50 },    // 保持50个用户1分钟
    { duration: '30s', target: 0 },    // 逐步减少
  ],
  // 性能阈值 - 高负载下允许更宽松的阈值
  thresholds: {
    http_req_duration: ['p(95) < 3000'],  // 高负载下允许更长响应时间
    http_req_failed: ['rate < 0.10'],      // 允许10%错误率
    errors: ['rate < 0.10'],
  },
};

// 默认执行函数
export default function () {
  group('压力测试接口', function () {
    // 使用 delay 接口模拟慢响应
    const res = http.get(`${BASE_URL}/delay/1`, {
      headers: {
        'User-Agent': 'PerfEngine-Stress/1.0',
      },
      timeout: '10s',
    });

    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 3000ms': (r) => r.timings.duration < 3000,
    });

    errorRate.add(!success);
    requestDuration.add(res.timings.duration);
    requestCount.add(1);
  });

  sleep(0.5);
}

// 测试开始时执行
export function setup() {
  console.log('🚀 压力测试开始');
  console.log(`目标 URL: ${BASE_URL}`);
  return { startTime: new Date().toISOString() };
}

// 测试结束时执行
export function teardown(data) {
  console.log('✅ 压力测试结束');
  console.log(`开始时间: ${data.startTime}`);
  console.log(`结束时间: ${new Date().toISOString()}`);
}
