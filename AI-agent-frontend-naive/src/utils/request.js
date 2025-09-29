import axios from 'axios'
import { getToken, removeToken, toLogin } from '@/utils'

// 创建axios实例
export const request = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api',
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加token
    const token = getToken()
    if (token && !config.noNeedToken) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response
    
    // 如果是文件下载
    if (response.config.responseType === 'blob') {
      return response
    }
    
    // 统一处理响应
    if (data.code === 200) {
      return data
    } else if (data.code === 401) {
      // token过期或无效
      window.$message?.error('登录已过期，请重新登录')
      removeToken()
      toLogin()
      return Promise.reject(new Error('登录已过期'))
    } else {
      // 其他错误
      const message = data.msg || '请求失败'
      window.$message?.error(message)
      return Promise.reject(new Error(message))
    }
  },
  (error) => {
    console.error('响应错误:', error)
    
    let message = '网络错误'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data.msg || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          removeToken()
          toLogin()
          break
        case 403:
          message = '没有权限访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.msg || `请求失败 (${status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时'
    }
    
    window.$message?.error(message)
    return Promise.reject(error)
  }
)
