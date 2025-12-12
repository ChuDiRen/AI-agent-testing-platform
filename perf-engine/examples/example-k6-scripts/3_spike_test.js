/**
 * 峰值测试
 * 测试系统应对突发流量的能力
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');

// 全局变量
const BASE_URL = 'https://httpbin.org';

// 测试配置
export const options = {
  // 峰值测试场景
  stages: [
    { duration: '10s', target: 5 },    // 正常负载
    { duration: '30s', target: 5 },    // 保持正常负载
    { duration: '5s', target: 50 },    // 突然增加到50用户 (峰值)
    { duration: '30s', target: 50 },   // 保持峰值
    { duration: '5s', target: 5 },     // 快速恢复正常
    { duration: '30s', target: 5 },    // 保持正常
    { duration: '10s', target: 0 },    // 结束
  ],
  // 性能阈值 - 峰值期间允许较宽松的阈值
  thresholds: {
    http_req_duration: ['p(95) < 5000'],  // 峰值期间允许较长响应时间
    http_req_failed: ['rate < 0.15'],      // 峰值期间允许较高错误率
  },
};

// 默认执行函数
export default function () {
  group('峰值测试接口', function () {
    const res = http.get(`${BASE_URL}/get?spike=true`, {
      headers: {
        'User-Agent': 'PerfEngine-Spike/1.0',
        'X-Test-Type': 'spike',
      },
    });

    const success = check(res, {
      'status is 200': (r) => r.status === 200,
    });

    errorRate.add(!success);
    requestDuration.add(res.timings.duration);
  });

  sleep(0.2);
}

// 测试开始时执行
export function setup() {
  console.log('⚡ 峰值测试开始');
  console.log('测试将模拟突发流量场景');
  return {};
}

// 测试结束时执行
export function teardown(data) {
  console.log('✅ 峰值测试结束');
}
