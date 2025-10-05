// Copyright (c) 2025 左岚. All rights reserved.
/**
 * Axios 请求封装
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

// API 基础URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')

    // 添加 token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 如果返回的状态码为 200，说明接口请求成功
    if (response.status === 200) {
      return res
    }

    // 其他情况视为错误
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || 'Error'))
  },
  async (error: AxiosError) => {
    console.error('Response error:', error)

    // 处理 HTTP 错误
    if (error.response) {
      const status = error.response.status

      switch (status) {
        case 401: {
          // Token过期，尝试刷新
          const refreshToken = localStorage.getItem('refreshToken')
          if (!refreshToken || error.config?.url?.includes('/auth/refresh')) {
            // 无refresh_token或刷新接口本身失败，直接跳转登录
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.href = '/login'
            break
          }

          try {
            // 动态导入避免循环依赖
            const { refreshToken: refreshTokenApi } = await import('./auth')
            const response = await refreshTokenApi(refreshToken)

            // 更新token和refresh_token
            localStorage.setItem('token', response.data.access_token)
            localStorage.setItem('refreshToken', response.data.refresh_token)

            // 重试原请求
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${response.data.access_token}`
              return service.request(error.config)
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError)
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.href = '/login'
          }
          break
        }
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// 通用请求方法
export function request<T = any>(config: AxiosRequestConfig): Promise<T> {
  return service.request<any, T>(config)
}

// GET 请求
export function get<T = any>(url: string, params?: any): Promise<T> {
  return request<T>({
    url,
    method: 'GET',
    params
  })
}

// POST 请求
export function post<T = any>(url: string, data?: any): Promise<T> {
  return request<T>({
    url,
    method: 'POST',
    data
  })
}

// PUT 请求
export function put<T = any>(url: string, data?: any): Promise<T> {
  return request<T>({
    url,
    method: 'PUT',
    data
  })
}

// DELETE 请求
export function del<T = any>(url: string, params?: any): Promise<T> {
  return request<T>({
    url,
    method: 'DELETE',
    params
  })
}

export default service

