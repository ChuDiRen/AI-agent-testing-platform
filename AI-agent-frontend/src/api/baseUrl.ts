// baseUrl.ts
const baseUrl: any = {
  development: 'http://localhost:8000/api/v1',
  production: 'https://your-production-api.com/api/v1',
}

export const BASE_URL = baseUrl[import.meta.env.VITE_ENV] || baseUrl.development;
