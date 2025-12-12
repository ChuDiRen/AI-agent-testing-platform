/**
 * API 工作流测试
 * 模拟真实用户操作流程：登录 -> 获取数据 -> 提交数据
 */
import http from 'k6/http';
import { check, sleep, group, fail } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// 自定义指标
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const getDuration = new Trend('get_duration');
const postDuration = new Trend('post_duration');

// 全局变量
const BASE_URL = 'https://httpbin.org';

// 测试数据 - 模拟多用户
const users = new SharedArray('users', function () {
  return [
    { username: 'user1', password: 'pass1' },
    { username: 'user2', password: 'pass2' },
    { username: 'user3', password: 'pass3' },
    { username: 'user4', password: 'pass4' },
    { username: 'user5', password: 'pass5' },
  ];
});

// 测试配置
export const options = {
  scenarios: {
    // 场景1: 正常用户流程
    normal_flow: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '20s', target: 5 },
        { duration: '1m', target: 5 },
        { duration: '20s', target: 0 },
      ],
      gracefulRampDown: '10s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95) < 2000'],
    http_req_failed: ['rate < 0.05'],
    login_duration: ['p(95) < 1000'],
    get_duration: ['p(95) < 1500'],
    post_duration: ['p(95) < 1500'],
  },
};

// 默认执行函数
export default function () {
  // 随机选择一个用户
  const user = users[Math.floor(Math.random() * users.length)];

  // 步骤1: 登录
  let token = '';
  group('1. 用户登录', function () {
    const loginPayload = JSON.stringify({
      username: user.username,
      password: user.password,
    });

    const loginRes = http.post(`${BASE_URL}/post`, loginPayload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'login' },
    });

    const loginSuccess = check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'login response has data': (r) => r.json().data !== undefined,
    });

    if (!loginSuccess) {
      errorRate.add(1);
      fail('登录失败');
    }

    loginDuration.add(loginRes.timings.duration);
    
    // 模拟获取 token
    token = 'mock_token_' + Date.now();
  });

  sleep(1);

  // 步骤2: 获取用户数据
  group('2. 获取用户数据', function () {
    const getRes = http.get(`${BASE_URL}/get?user=${user.username}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      tags: { name: 'get_user_data' },
    });

    const getSuccess = check(getRes, {
      'get status is 200': (r) => r.status === 200,
    });

    errorRate.add(!getSuccess);
    getDuration.add(getRes.timings.duration);
  });

  sleep(1);

  // 步骤3: 提交数据
  group('3. 提交数据', function () {
    const submitPayload = JSON.stringify({
      action: 'update_profile',
      user: user.username,
      timestamp: Date.now(),
    });

    const postRes = http.post(`${BASE_URL}/post`, submitPayload, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      tags: { name: 'submit_data' },
    });

    const postSuccess = check(postRes, {
      'post status is 200': (r) => r.status === 200,
    });

    errorRate.add(!postSuccess);
    postDuration.add(postRes.timings.duration);
  });

  sleep(2);
}

// 测试开始时执行
export function setup() {
  console.log('🔄 API 工作流测试开始');
  console.log(`测试用户数: ${users.length}`);
  
  // 验证目标服务是否可用
  const healthCheck = http.get(`${BASE_URL}/get`);
  if (healthCheck.status !== 200) {
    fail('目标服务不可用');
  }
  
  return { startTime: Date.now() };
}

// 测试结束时执行
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log('✅ API 工作流测试结束');
  console.log(`总运行时间: ${duration.toFixed(2)} 秒`);
}
