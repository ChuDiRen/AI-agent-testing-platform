//http.ts
import axios, { InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { NProgressStart, NProgressDone } from '@/utils/nprogress'
import { BASE_URL } from './baseUrl'
import { getToken, removeToken } from '@/utils/auth'
import router from '@/router'

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
  timeout: 10000,
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
  (response: AxiosResponse<ApiResponse>) => {
    NProgressDone()
    
    const { data } = response
    
    // 检查业务状态码
    if (!data.success) {
      ElMessage.error(data.message || '操作失败')
      return Promise.reject(new Error(data.message))
    }
    
    return data
  },
  (error) => {
    NProgressDone()
    
    const { status, data } = error.response || {}
    
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      removeToken()
      router.push('/login')
    } else if (status === 403) {
      ElMessage.error('权限不足')
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
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
  download(url: string, filename?: string): void
}

// 扩展axios实例方法
const httpMethods: HttpMethods = {
  get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return http.get(url, { params })
  },

  post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return http.post(url, data)
  },

  put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return http.put(url, data)
  },

  delete<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return http.delete(url, { params })
  },

  upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return http.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  download(url: string, filename?: string): void {
    const link = document.createElement('a')
    link.href = url
    if (filename) {
      link.download = filename
    }
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

export default httpMethods
export type { ApiResponse }
