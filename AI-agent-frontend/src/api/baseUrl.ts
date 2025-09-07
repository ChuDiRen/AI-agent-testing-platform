// Copyright (c) 2025 左岚. All rights reserved.
// baseUrl.ts
const baseUrl: any = {
  development: 'http://localhost:8000/api/v1', // 直接指向后端服务
  production: 'https://your-production-api.com/api/v1',
}

// 获取当前环境
const currentEnv = import.meta.env.MODE || 'development'

export const BASE_URL = baseUrl[currentEnv] || baseUrl.development;
