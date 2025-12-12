/**
 * 基础负载测试
 * 测试 API 在正常负载下的性能表现
 */
import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend } from "k6/metrics";

// 自定义指标
const errorRate = new Rate("errors");
const requestDuration = new Trend("request_duration");

// 全局变量
const BASE_URL = "https://httpbin.org";
const username = "testuser";
const password = "test123456";

// 测试配置
export const options = {
  // 阶段式负载
  stages: [
    { duration: "10s", target: 5 }, // 10秒内逐步增加到5个用户
    { duration: "30s", target: 5 }, // 保持5个用户30秒
    { duration: "10s", target: 0 }, // 10秒内逐步减少到0
  ],
  // 性能阈值
  thresholds: {
    http_req_duration: ["p(95) < 1000", "p(99) < 2000"], // 响应时间阈值
    http_req_failed: ["rate < 0.05"], // 错误率小于5%
    errors: ["rate < 0.05"], // 自定义错误率
  },
};

// 默认执行函数
export default function () {
  // GET 请求测试
  group("GET 请求测试", function () {
    const res = http.get(`${BASE_URL}/get`, {
      headers: {
        "User-Agent": "PerfEngine/1.0",
      },
    });

    check(res, {
      "status is 200": (r) => r.status === 200,
      "response time < 500ms": (r) => r.timings.duration < 500,
    });

    errorRate.add(res.status !== 200);
    requestDuration.add(res.timings.duration);
  });

  sleep(1);

  // POST 请求测试
  group("POST 请求测试", function () {
    const payload = JSON.stringify({
      username: username,
      password: password,
    });

    const res = http.post(`${BASE_URL}/post`, payload, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    check(res, {
      "status is 200": (r) => r.status === 200,
      "response contains username": (r) => r.body.includes(username),
    });

    errorRate.add(res.status !== 200);
    requestDuration.add(res.timings.duration);
  });

  sleep(1);
}
