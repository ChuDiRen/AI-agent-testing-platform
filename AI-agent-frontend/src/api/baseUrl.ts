// baseUrl.ts
const baseUrl: any = {
  development: 'http://localhost:8080/api',
  production: 'https://your-production-api.com/api',
}

export const BASE_URL = baseUrl[import.meta.env.VITE_ENV];
