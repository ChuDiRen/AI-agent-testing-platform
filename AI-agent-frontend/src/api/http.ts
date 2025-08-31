// Copyright (c) 2025 左岚. All rights reserved.
//http.ts
import axios from 'axios'
import type { InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { NProgressStart, NProgressDone } from '@/utils/nprogress'
import { BASE_URL } from './baseUrl'
import { getToken, removeToken } from '@/utils/auth'
import router from '@/router'
import { NETWORK_CONFIG, shouldRetry, getRetryDelay } from '@/config/network'

// 后端API响应格式
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message: string
  error_code?: string
  timestamp: string
}

// 创建axios实例
const http = axios.create({
  baseURL: BASE_URL || 'http://localhost:8000/api/v1',
  timeout: NETWORK_CONFIG.DEFAULT_TIMEOUT, // 使用配置中心的超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 开始进度条
    NProgressStart()
    
    // 添加认证token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    NProgressDone()
    return Promise.reject(error)
  }
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
        ElMessage.error(data.msg || '操作失败')
        return Promise.reject(new Error(data.msg))
      }
      // 转换为前端期望的格式
      return {
        success: true,
        message: data.msg,
        data: data.data,
        total: data.total,
        page: data.page,
        page_size: data.page_size
      } as any
    } else {
      // 兼容旧格式：检查success字段
      if (!data.success) {
        ElMessage.error(data.message || '操作失败')
        return Promise.reject(new Error(data.message))
      }
      return data as any
    }
  },
  async (error) => {
    NProgressDone()

    const { config, response, code } = error
    const { status, data } = response || {}

    // 处理网络超时和连接错误，自动重试
    const retryCount = config.__retryCount || 0

    if (shouldRetry(error, retryCount)) {
      config.__retryCount = retryCount + 1
      console.log(`请求重试第${retryCount + 1}次...`)

      // 延迟重试，避免频繁请求
      await new Promise(resolve => setTimeout(resolve, getRetryDelay(retryCount)))

      return http(config)
    } else if (code === 'ECONNABORTED' || code === 'NETWORK_ERROR' || !response) {
      ElMessage.error('网络连接超时，请检查网络或稍后重试')
    }

    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      removeToken()
      router.push('/login')
    } else if (status === 403) {
      ElMessage.error('权限不足')
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else if (!response) {
      ElMessage.error('网络连接失败，请检查网络连接')
    } else {
      ElMessage.error(data?.message || '请求失败')
    }

    return Promise.reject(error)
  }
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
    return http.get(url, { params }) as unknown as Promise<ApiResponse<T>>
  },

  post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return http.post(url, data) as unknown as Promise<ApiResponse<T>>
  },

  put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return http.put(url, data) as unknown as Promise<ApiResponse<T>>
  },

  delete<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return http.delete(url, { params }) as unknown as Promise<ApiResponse<T>>
  },

  upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return http.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }) as unknown as Promise<ApiResponse<T>>
  },

  async download(url: string, params?: any, filename?: string): Promise<void> {
    try {
      const response = await http.get(url, {
        params,
        responseType: 'blob',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
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
      ElMessage.error('文件下载失败')
      throw error
    }
  }
}

export default httpMethods
export type { ApiResponse }
