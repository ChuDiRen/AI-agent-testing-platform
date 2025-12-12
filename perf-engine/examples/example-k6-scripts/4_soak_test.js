/**
 * 浸泡测试 (耐久测试)
 * 测试系统在长时间运行下的稳定性
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');
const totalRequests = new Counter('total_requests');

// 全局变量
const BASE_URL = 'https://httpbin.org';

// 测试配置
export const options = {
  // 固定负载，长时间运行
  vus: 10,
  duration: '5m',  // 运行5分钟 (实际生产可设置更长时间，如 1h, 4h, 24h)
  
  // 性能阈值 - 长时间运行要求更严格
  thresholds: {
    http_req_duration: ['p(95) < 1500', 'p(99) < 3000'],
    http_req_failed: ['rate < 0.01'],  // 长时间运行要求更低的错误率
    errors: ['rate < 0.01'],
  },
};

// 默认执行函数
export default function () {
  group('耐久测试接口', function () {
    const res = http.get(`${BASE_URL}/get`, {
      headers: {
        'User-Agent': 'PerfEngine-Soak/1.0',
        'X-Test-Type': 'soak',
      },
    });

    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 1500ms': (r) => r.timings.duration < 1500,
    });

    errorRate.add(!success);
    requestDuration.add(res.timings.duration);
    totalRequests.add(1);
  });

  sleep(2);
}

// 测试开始时执行
export function setup() {
  console.log('🔄 浸泡测试开始');
  console.log('测试将持续运行以检测内存泄漏和性能退化');
  return { startTime: Date.now() };
}

// 测试结束时执行
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log('✅ 浸泡测试结束');
  console.log(`总运行时间: ${duration.toFixed(2)} 秒`);
}
