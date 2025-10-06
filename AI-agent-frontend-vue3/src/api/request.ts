// Copyright (c) 2025 左岚. All rights reserved.
/**
 * Axios 请求封装 - 增强版
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

// API 基础URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 请求重试配置
const RETRY_CONFIG = {
  maxRetries: 3, // 最大重试次数
  retryDelay: 1000, // 重试延迟(ms)
  retryableStatuses: [408, 429, 500, 502, 503, 504] // 可重试的状态码
}

// Token 刷新状态
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

// 订阅 Token 刷新
function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb)
}

// 通知所有订阅者
function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求重试辅助函数
function shouldRetry(error: AxiosError): boolean {
  if (!error.config) return false
  
  const config: any = error.config
  const retryCount = config.__retryCount || 0
  
  // 已达到最大重试次数
  if (retryCount >= RETRY_CONFIG.maxRetries) return false
  
  // 检查状态码是否可重试
  const status = error.response?.status
  return status ? RETRY_CONFIG.retryableStatuses.includes(status) : false
}

function retryRequest(error: AxiosError): Promise<any> {
  const config: any = error.config
  config.__retryCount = (config.__retryCount || 0) + 1
  
  // 延迟重试
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log(`🔄 重试请求 (${config.__retryCount}/${RETRY_CONFIG.maxRetries}): ${config.url}`)
      resolve(service.request(config))
    }, RETRY_CONFIG.retryDelay * config.__retryCount)
  })
}

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')

    // 添加 token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 如果是 FormData，删除 Content-Type 让浏览器自动设置（包括 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
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

    // 检查是否需要重试
    if (shouldRetry(error)) {
      return retryRequest(error)
    }

    // 处理 HTTP 错误
    if (error.response) {
      const status = error.response.status
      const config = error.config

      switch (status) {
        case 401: {
          // Token过期，尝试刷新
          const refreshToken = localStorage.getItem('refreshToken')
          
          // 如果是刷新接口失败或没有 refresh_token
          if (!refreshToken || error.config?.url?.includes('/auth/refresh')) {
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.href = '/login'
            break
          }

          // 如果正在刷新 token，将请求加入队列
          if (isRefreshing) {
            return new Promise((resolve) => {
              subscribeTokenRefresh((token: string) => {
                if (config) {
                  config.headers!.Authorization = `Bearer ${token}`
                  resolve(service.request(config))
                }
              })
            })
          }

          isRefreshing = true

          try {
            // 动态导入避免循环依赖
            const { refreshToken: refreshTokenApi } = await import('./auth')
            const response = await refreshTokenApi(refreshToken)

            const newToken = response.data.access_token
            const newRefreshToken = response.data.refresh_token

            // 更新 token
            localStorage.setItem('token', newToken)
            localStorage.setItem('refreshToken', newRefreshToken)

            // 通知所有等待的请求
            onRefreshed(newToken)

            // 重试原请求
            if (config) {
              config.headers!.Authorization = `Bearer ${newToken}`
              return service.request(config)
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError)
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.href = '/login'
          } finally {
            isRefreshing = false
          }
          break
        }
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 429:
          ElMessage.warning('请求过于频繁，请稍后再试')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        case 502:
          ElMessage.error('网关错误')
          break
        case 503:
          ElMessage.error('服务暂时不可用')
          break
        case 504:
          ElMessage.error('网关超时')
          break
        default:
          ElMessage.error(error.message || '请求失败')
      }
    } else if (error.request) {
      // 网络错误
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请检查网络连接')
      } else if (error.code === 'ERR_NETWORK') {
        ElMessage.error('网络错误，请检查网络连接')
      } else {
        ElMessage.error('网络错误，请稍后重试')
      }
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

