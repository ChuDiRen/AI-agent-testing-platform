import type { ApiService } from './types';

export const MOCK_API_DATA: ApiService[] = [
  {
    id: 'svc-auth',
    name: 'Auth Service',
    versions: [
      {
        id: 'v1-auth',
        version: 'v1.0.0',
        tags: [
          {
            id: 'tag-auth',
            name: 'Authentication',
            endpoints: [
              { 
                id: 'ep-1', 
                method: 'POST', 
                path: '/auth/login', 
                summary: 'User Login', 
                description: 'Authenticates a user and returns a JWT token.',
                lastUpdated: '2024-03-10',
                requestBody: {
                  type: 'object',
                  properties: {
                    username: { type: 'string', description: 'User email or username', example: 'neo@matrix.com' },
                    password: { type: 'string', description: 'User password', example: 'password123' }
                  },
                  required: ['username', 'password']
                },
                responses: [
                  {
                    status: 200,
                    description: 'Login successful',
                    schema: {
                      type: 'object',
                      properties: {
                        token: { type: 'string', description: 'JWT Access Token', example: 'eyJhbGciOiJIUz...' },
                        expiresIn: { type: 'integer', description: 'Token expiration in seconds', example: 3600 }
                      }
                    }
                  },
                  {
                    status: 401,
                    description: 'Invalid credentials',
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
                summary: 'User Registration', 
                lastUpdated: '2024-03-11',
                parameters: [
                  { name: 'X-Client-ID', in: 'header', required: true, type: 'string', description: 'Client application ID' }
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
                  { status: 201, description: 'User created' },
                  { status: 400, description: 'Validation error' }
                ]
              },
              { id: 'ep-3', method: 'POST', path: '/auth/refresh', summary: 'Refresh Token', lastUpdated: '2024-03-09' },
            ]
          },
          {
            id: 'tag-users',
            name: 'Users',
            endpoints: [
              { 
                id: 'ep-4', 
                method: 'GET', 
                path: '/users/me', 
                summary: 'Get Current User', 
                lastUpdated: '2024-03-12',
                parameters: [
                  { name: 'fields', in: 'query', required: false, type: 'string', description: 'Comma-separated fields to return' }
                ],
                responses: [
                  {
                    status: 200,
                    description: 'User profile',
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
              { id: 'ep-5', method: 'PATCH', path: '/users/me', summary: 'Update Profile', lastUpdated: '2024-03-12' },
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
            name: 'Authentication',
            endpoints: [
              { id: 'ep-6', method: 'POST', path: '/v2/auth/login', summary: 'SSO Login', lastUpdated: '2024-04-01' },
            ]
          }
        ]
      }
    ]
  },
  {
    id: 'svc-payment',
    name: 'Payment Service',
    versions: [
      {
        id: 'v1-pay',
        version: 'v1.0.0',
        tags: [
          {
            id: 'tag-invoices',
            name: 'Invoices',
            endpoints: [
              { 
                id: 'ep-7', 
                method: 'GET', 
                path: '/invoices', 
                summary: 'List Invoices', 
                lastUpdated: '2024-02-28',
                parameters: [
                  { name: 'page', in: 'query', required: false, type: 'integer', description: 'Page number' },
                  { name: 'limit', in: 'query', required: false, type: 'integer', description: 'Items per page' }
                ],
                responses: [
                  { status: 200, description: 'List of invoices' }
                ]
              },
              { id: 'ep-8', method: 'POST', path: '/invoices', summary: 'Create Invoice', lastUpdated: '2024-03-01' },
            ]
          }
        ]
      }
    ]
  }
];
