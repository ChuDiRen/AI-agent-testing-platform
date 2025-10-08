/**
 * HTTP请求封装
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        // 从localStorage获取token
        const token = localStorage.getItem('token')
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

        // 如果是文件下载,直接返回
        if (response.config.responseType === 'blob') {
            return response
        }

        // 统一处理响应
        if (res.code !== undefined && res.code !== 200) {
            ElMessage.error(res.message || 'Error')

            // 401: Token过期或未登录
            if (res.code === 401) {
                // 跳转到登录页
                window.location.href = '/login'
            }

            return Promise.reject(new Error(res.message || 'Error'))
        }

        return res
    },
    (error: AxiosError) => {
        console.error('Response error:', error)

        if (error.response) {
            switch (error.response.status) {
                case 401:
                    ElMessage.error('未授权,请重新登录')
                    localStorage.removeItem('token')
                    window.location.href = '/login'
                    break
                case 403:
                    ElMessage.error('拒绝访问')
                    break
                case 404:
                    ElMessage.error('请求地址不存在')
                    break
                case 500:
                    ElMessage.error('服务器内部错误')
                    break
                default:
                    ElMessage.error(error.message || '请求失败')
            }
        } else if (error.request) {
            ElMessage.error('网络错误,请检查您的网络连接')
        } else {
            ElMessage.error(error.message || '请求失败')
        }

        return Promise.reject(error)
    }
)

// 封装请求方法
const request = {
    get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return service.get(url, config)
    },

    post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return service.post(url, data, config)
    },

    put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return service.put(url, data, config)
    },

    delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return service.delete(url, config)
    },

    patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return service.patch(url, data, config)
    }
}

export default request
export { service }

