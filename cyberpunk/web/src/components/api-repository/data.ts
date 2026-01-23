import type { ApiService } from './types';

export const MOCK_API_DATA: ApiService[] = [
  {
    id: 'svc-auth',
    name: '认证服务',
    versions: [
      {
        id: 'v1-auth',
        version: 'v1.0.0',
        tags: [
          {
            id: 'tag-auth',
            name: '认证',
            endpoints: [
              {
                id: 'ep-1',
                method: 'POST',
                path: '/auth/login',
                summary: '用户登录',
                description: '验证用户身份并返回 JWT 令牌。',
                lastUpdated: '2024-03-10',
                requestBody: {
                  type: 'object',
                  properties: {
                    username: { type: 'string', description: '用户邮箱或用户名', example: 'neo@matrix.com' },
                    password: { type: 'string', description: '用户密码', example: 'password123' }
                  },
                  required: ['username', 'password']
                },
                responses: [
                  {
                    status: 200,
                    description: '登录成功',
                    schema: {
                      type: 'object',
                      properties: {
                        token: { type: 'string', description: 'JWT 访问令牌', example: 'eyJhbGciOiJIUz...' },
                        expiresIn: { type: 'integer', description: '令牌过期时间（秒）', example: 3600 }
                      }
                    }
                  },
                  {
                    status: 401,
                    description: '凭据无效',
                    schema: {
                      type: 'object',
                      properties: {
                        code: { type: 'string', example: 'AUTH_FAILED' },
                        message: { type: 'string', example: 'Invalid username or password' }
                      }
                    }
                  }
                ]
              },
              {
                id: 'ep-2',
                method: 'POST',
                path: '/auth/register',
                summary: '用户注册',
                lastUpdated: '2024-03-11',
                parameters: [
                  { name: 'X-Client-ID', in: 'header', required: true, type: 'string', description: '客户端应用 ID' }
                ],
                requestBody: {
                  type: 'object',
                  properties: {
                    email: { type: 'string', example: 'user@example.com' },
                    password: { type: 'string', example: 'securePass1!' },
                    name: { type: 'string', example: 'John Doe' }
                  },
                  required: ['email', 'password']
                },
                responses: [
                  { status: 201, description: '用户已创建' },
                  { status: 400, description: '验证错误' }
                ]
              },
              { id: 'ep-3', method: 'POST', path: '/auth/refresh', summary: '刷新令牌', lastUpdated: '2024-03-09' },
            ]
          },
          {
            id: 'tag-users',
            name: '用户',
            endpoints: [
              {
                id: 'ep-4',
                method: 'GET',
                path: '/users/me',
                summary: '获取当前用户',
                lastUpdated: '2024-03-12',
                parameters: [
                  { name: 'fields', in: 'query', required: false, type: 'string', description: '逗号分隔的返回字段' }
                ],
                responses: [
                  {
                    status: 200,
                    description: '用户资料',
                    schema: {
                      type: 'object',
                      properties: {
                        id: { type: 'string', example: 'usr_123' },
                        email: { type: 'string', example: 'neo@matrix.com' },
                        role: { type: 'string', example: 'admin' }
                      }
                    }
                  }
                ]
              },
              { id: 'ep-5', method: 'PATCH', path: '/users/me', summary: '更新资料', lastUpdated: '2024-03-12' },
            ]
          }
        ]
      },
      {
        id: 'v2-auth',
        version: 'v2.0.0 (Beta)',
        tags: [
          {
            id: 'tag-auth-v2',
            name: '认证',
            endpoints: [
              { id: 'ep-6', method: 'POST', path: '/v2/auth/login', summary: 'SSO 登录', lastUpdated: '2024-04-01' },
            ]
          }
        ]
      }
    ]
  },
  {
    id: 'svc-payment',
    name: '支付服务',
    versions: [
      {
        id: 'v1-pay',
        version: 'v1.0.0',
        tags: [
          {
            id: 'tag-invoices',
            name: '发票',
            endpoints: [
              {
                id: 'ep-7',
                method: 'GET',
                path: '/invoices',
                summary: '获取发票列表',
                lastUpdated: '2024-02-28',
                parameters: [
                  { name: 'page', in: 'query', required: false, type: 'integer', description: '页码' },
                  { name: 'limit', in: 'query', required: false, type: 'integer', description: '每页条数' }
                ],
                responses: [
                  { status: 200, description: '发票列表' }
                ]
              },
              { id: 'ep-8', method: 'POST', path: '/invoices', summary: '创建发票', lastUpdated: '2024-03-01' },
            ]
          }
        ]
      }
    ]
  }
];

