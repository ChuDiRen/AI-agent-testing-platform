// Copyright (c) 2025 左岚. All rights reserved.
//http.ts
import axios from 'axios'
import type { InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import notify from '@/utils/notify'
import { NProgressStart, NProgressDone } from '@/utils/nprogress'
import { BASE_URL } from './baseUrl'
import {
  getToken,
  getRefreshToken,
  setToken,
  setRefreshToken,
} from '@/utils/auth'
import { clearAllTokenData, isTokenValid, parseJWT } from '@/utils/tokenValidator' // 导入token验证器
import router from '@/router'
import { NETWORK_CONFIG, shouldRetry, getRetryDelay, getDedupeTTL } from '@/config/network'
import { handleApiError } from '@/utils/errorHandler'

// 后端API响应格式
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message: string
  error_code?: string
  timestamp: string
}

// 刷新token状态，避免并发风暴
let isRefreshing = false
let refreshPromise: Promise<any> | null = null
const requestQueue: Array<(token: string | null) => void> = []

function subscribeTokenRefresh(cb: (token: string | null) => void) {
  requestQueue.push(cb)
}

function onRefreshed(token: string | null) {
  requestQueue.forEach((cb) => cb(token))
  requestQueue.length = 0
}

// 创建axios实例
const http = axios.create({
  baseURL: BASE_URL,
  timeout: NETWORK_CONFIG.DEFAULT_TIMEOUT, // 使用配置中心的超时时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求去重/缓存容器
const inFlightMap = new Map<string, Promise<any>>()
const cacheMap = new Map<string, { expire: number; data: any }>()
function buildKey(method: string, url: string, payload?: any) {
  const d = payload ? (typeof payload === 'string' ? payload : JSON.stringify(payload)) : ''
  return `${method.toUpperCase()} ${url} | ${d}`
}

// 包装方法以支持请求去重与短缓存
function wrap<T>(
  method: 'get' | 'post' | 'put' | 'delete',
  url: string,
  payload?: any,
  config?: any,
): Promise<T> {
  const ttl = getDedupeTTL(url)
  const key = buildKey(method, url, method === 'get' ? config?.params : payload)
  const now = Date.now()
  if (ttl > 0) {
    const cached = cacheMap.get(key)
    if (cached && cached.expire > now) {
      return Promise.resolve(cached.data)
    }
    const inflight = inFlightMap.get(key)
    if (inflight) return inflight as any
  }
  const p = (http as any)[method](url, payload, config)
  if (ttl > 0) inFlightMap.set(key, p)
  return p
    .then((res: any) => {
      if (ttl > 0) {
        cacheMap.set(key, { expire: Date.now() + ttl, data: res })
        inFlightMap.delete(key)
      }
      return res
    })
    .catch((err: any) => {
      if (ttl > 0) inFlightMap.delete(key)
      throw err
    })
}

// 检查token是否即将过期（5分钟内）
function isTokenExpiringSoon(token: string, minutesThreshold: number = 5): boolean {
  try {
    const payload = parseJWT(token)
    if (!payload || !payload.exp) {
      return true // 无法解析或没有过期时间，视为即将过期
    }
    
    const currentTime = Math.floor(Date.now() / 1000)
    const timeLeft = payload.exp - currentTime
    const thresholdSeconds = minutesThreshold * 60
    
    return timeLeft <= thresholdSeconds
  } catch (error) {
    console.warn('Failed to check token expiration:', error)
    return true // 解析失败，视为即将过期
  }
}

// 预检查并刷新token的函数
async function preCheckAndRefreshToken(): Promise<string | null> {
  const token = getToken()
  if (!token) return null
  
  // 如果token无效，直接返回null
  if (!isTokenValid(token)) {
    console.warn('Invalid token detected in pre-check, clearing token data')
    clearAllTokenData()
    return null
  }
  
  // 如果token即将过期，尝试刷新
  if (isTokenExpiringSoon(token)) {
    console.log('Token expiring soon, attempting proactive refresh...')
    
    // 如果已经在刷新中，等待刷新完成
    if (isRefreshing && refreshPromise) {
      try {
        const newToken = await refreshPromise
        return newToken
      } catch (error) {
        console.warn('Failed to wait for ongoing refresh:', error)
        return null
      }
    }
    
    // 开始刷新流程
    isRefreshing = true
    const currentRefreshToken = getRefreshToken()
    
    if (!currentRefreshToken || !isTokenValid(currentRefreshToken)) {
      console.warn('No valid refresh token available for proactive refresh')
      clearAllTokenData()
      isRefreshing = false
      return null
    }
    
    refreshPromise = (async () => {
      try {
        // 直接调用刷新接口
        const res = await http.post('/users/refresh-token', {
          refresh_token: currentRefreshToken,
        })
        
        if ((res as any)?.success && (res as any)?.data?.access_token) {
          const newAccessToken = (res as any).data.access_token as string
          const newRefreshToken = (res as any).data.refresh_token as string | undefined
          
          // 验证新token的有效性
          if (!isTokenValid(newAccessToken)) {
            throw new Error('Received invalid access token from proactive refresh')
          }
          
          setToken(newAccessToken)
          if (newRefreshToken && isTokenValid(newRefreshToken)) {
            setRefreshToken(newRefreshToken)
          }
          
          console.log('Proactive token refresh successful')
          onRefreshed(newAccessToken)
          return newAccessToken
        }
        throw new Error('Proactive token refresh failed')
      } catch (e) {
        console.warn('Proactive token refresh failed:', e)
        // 不清理token数据，让401拦截器处理
        onRefreshed(null)
        throw e
      } finally {
        isRefreshing = false
        refreshPromise = null
      }
    })()
    
    try {
      const newToken = await refreshPromise
      return newToken
    } catch (error) {
      console.warn('Proactive refresh failed, will rely on 401 fallback:', error)
      return token // 返回原token，让请求继续，401拦截器会处理
    }
  }
  
  return token // token有效且未即将过期
}

// 请求拦截器
http.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // 开始进度条
    NProgressStart()

    // 跳过刷新token请求的预检查，避免循环
    if (config.url?.includes('/refresh-token')) {
      return config
    }

    // 预检查并刷新token
    const validToken = await preCheckAndRefreshToken()
    
    if (validToken) {
      config.headers.Authorization = `Bearer ${validToken}`
    } else {
      // 如果没有有效token且不是登录请求，重定向到登录页
      if (!config.url?.includes('/login')) {
        router.push('/login')
        return Promise.reject(new Error('No valid token available, redirecting to login'))
      }
    }

    return config
  },
  (error) => {
    NProgressDone()
    return Promise.reject(error)
  },
)

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse<any>) => {
    NProgressDone()

    // 如果是文件下载请求（blob类型），直接返回响应
    if (response.config.responseType === 'blob') {
      return response
    }

    const { data } = response

    // 适配新的返回格式 {code, msg, data}
    if (data.code !== undefined) {
      // 新格式：检查code是否为200
      if (data.code !== 200) {
        notify.error(data.msg || '操作失败')
        return Promise.reject(new Error(data.msg))
      }
      // 转换为前端期望的格式
      return {
        success: true,
        message: data.msg,
        data: data.data,
        total: data.total,
        page: data.page,
        page_size: data.page_size,
      } as any
    } else {
      // 兼容旧格式：检查success字段
      if (!data.success) {
        notify.error(data.message || '操作失败')
        return Promise.reject(new Error(data.message))
      }
      return data as any
    }
  },
  async (error) => {
    NProgressDone()

    // 命中请求级缓存的短路
    if (error?.__from_cache) {
      return Promise.resolve(error.__cache_data)
    }

    const { config, response } = error
    const { status } = response || {}

    // 使用统一错误处理器处理错误（但不显示消息，后面会处理）
    handleApiError(error, { 
      showMessage: false, 
      showModal: false, 
      autoRedirect: false 
    })

    // 处理网络超时和连接错误，自动重试
    const retryCount = (config as any).__retryCount || 0

    if (shouldRetry(error, retryCount)) {
      ;(config as any).__retryCount = retryCount + 1
      console.log(`请求重试第${retryCount + 1}次...`)

      // 延迟重试，避免频繁请求
      await new Promise((resolve) => setTimeout(resolve, getRetryDelay(retryCount)))

      return http(config)
    }

    // 401 处理：尝试无感刷新
    if (status === 401) {
      const originalRequest = config

      // 检查当前token是否有效，如果无效直接清理并跳转登录
      const currentToken = getToken()
      if (currentToken && !isTokenValid(currentToken)) {
        console.warn('401 error with invalid token, clearing all token data')
        clearAllTokenData()
        notify.error('登录已过期，请重新登录')
        router.push('/login')
        return Promise.reject(error)
      }

      // 如果已经在刷新中，挂起当前请求，等待刷新完成
      if (isRefreshing && refreshPromise) {
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((newToken) => {
            if (!newToken) {
              reject(error)
              return
            }
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            resolve(http(originalRequest))
          })
        })
      }

      // 否则发起刷新
      isRefreshing = true
      const currentRefreshToken = getRefreshToken()

      if (!currentRefreshToken || !isTokenValid(currentRefreshToken)) {
        console.warn('No valid refresh token available, clearing all token data')
        clearAllTokenData()
        notify.error('登录已过期，请重新登录')
        router.push('/login')
        isRefreshing = false
        refreshPromise = null
        return Promise.reject(error)
      }

      refreshPromise = (async () => {
        try {
          // 直接调用刷新接口
          const res = await http.post('/users/refresh-token', {
            refresh_token: currentRefreshToken,
          })
          if ((res as any)?.success && (res as any)?.data?.access_token) {
            const newAccessToken = (res as any).data.access_token as string
            const newRefreshToken = (res as any).data.refresh_token as string | undefined
            
            // 验证新token的有效性
            if (!isTokenValid(newAccessToken)) {
              throw new Error('Received invalid access token from refresh')
            }
            
            setToken(newAccessToken)
            if (newRefreshToken && isTokenValid(newRefreshToken)) {
              setRefreshToken(newRefreshToken)
            }
            onRefreshed(newAccessToken)
            return newAccessToken
          }
          throw new Error('刷新令牌失败')
        } catch (e) {
          // 刷新失败：清理并跳转登录
          console.warn('Token refresh failed, clearing all token data')
          clearAllTokenData()
          router.push('/login')
          onRefreshed(null)
          throw e
        } finally {
          isRefreshing = false
          refreshPromise = null
        }
      })()

      try {
        const token = await refreshPromise
        // 使用新的token重放原请求
        originalRequest.headers.Authorization = `Bearer ${token}`
        return http(originalRequest)
      } catch (e) {
        return Promise.reject(e)
      }
    }

    // 使用统一错误处理器显示错误消息和处理重定向
    handleApiError(error, { 
      showMessage: true, 
      showModal: false, 
      autoRedirect: true 
    })

    return Promise.reject(error)
  },
)

// HTTP请求方法类型
interface HttpMethods {
  get<T = any>(url: string, params?: any): Promise<ApiResponse<T>>
  post<T = any>(url: string, data?: any): Promise<ApiResponse<T>>
  put<T = any>(url: string, data?: any): Promise<ApiResponse<T>>
  delete<T = any>(url: string, params?: any): Promise<ApiResponse<T>>
  upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>>
  download(url: string, params?: any, filename?: string): Promise<void>
}

// 扩展axios实例方法
const httpMethods: HttpMethods = {
  get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return wrap<ApiResponse<T>>('get', url, undefined, { params })
  },

  post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return wrap<ApiResponse<T>>('post', url, data)
  },

  put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return wrap<ApiResponse<T>>('put', url, data)
  },

  delete<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return wrap<ApiResponse<T>>('delete', url, undefined, { params })
  },

  upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return http.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }) as unknown as Promise<ApiResponse<T>>
  },

  async download(url: string, params?: any, filename?: string): Promise<void> {
    try {
      const response = await http.get(url, {
        params,
        responseType: 'blob',
        headers: {
          Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      })

      // 创建blob URL
      const blob = new Blob([response.data])
      const blobUrl = window.URL.createObjectURL(blob)

      // 从响应头获取文件名
      const contentDisposition = response.headers['content-disposition']
      let downloadFilename = filename
      if (contentDisposition) {
        // 优先处理 UTF-8 编码的文件名
        const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/)
        if (utf8Match) {
          try {
            downloadFilename = decodeURIComponent(utf8Match[1])
          } catch (e) {
            console.warn('Failed to decode UTF-8 filename:', e)
          }
        }

        // 如果没有UTF-8文件名或解码失败，尝试普通文件名
        if (!utf8Match || downloadFilename === filename) {
          const filenameMatch = contentDisposition.match(/filename=([^;]+)/)
          if (filenameMatch) {
            downloadFilename = filenameMatch[1].replace(/['"]/g, '').trim()
          }
        }
      }

      // 创建下载链接
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = downloadFilename || 'download.xlsx'
      document.body.appendChild(link)
      link.click()

      // 清理
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (error) {
      console.error('Download failed:', error)
      notify.error('文件下载失败')
      throw error
    }
  },
}

export default httpMethods
export { httpMethods as http }
export type { ApiResponse }
