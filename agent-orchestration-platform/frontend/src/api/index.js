import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 authStore 获取 token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const { code, msg, data, total } = response.data
    if (code === 200) {
      return response.data // 返回完整的响应，包含 total
    } else {
      ElMessage.error(msg || '请求失败')
      return Promise.reject(new Error(msg))
    }
  },
  (error) => {
    console.error('Response error:', error)
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// 认证 API
export const login = (data) => {
  return service.post('/v1/Auth/login', data)
}

export const register = (data) => {
  return service.post('/v1/Auth/register', data)
}

export const logout = () => {
  return service.post('/v1/Auth/logout')
}

export const refreshToken = () => {
  return service.post('/v1/Auth/refresh')
}

export const getUserInfo = () => {
  return service.get('/v1/Auth/me')
}

// 成本配额 API
export const getCostQuotas = (params = {}) => {
  return service.get('/v1/Billing/quotas', { params })
}

export const createCostQuota = (data) => {
  return service.post('/v1/Billing/quotas', data)
}

export const updateCostQuota = (id, data) => {
  return service.put(`/v1/Billing/quotas/${id}`, data)
}

export const deleteCostQuota = (id) => {
  return service.delete(`/v1/Billing/quotas/${id}`)
}

// 仪表板 API
export const getBillingDashboard = () => {
  return service.get('/v1/Billing/dashboard')
}

export const getInvoices = (params = {}) => {
  return service.get('/v1/Billing/invoices', { params })
}

export const getUsageAlerts = (params = {}) => {
  return service.get('/v1/Billing/alerts', { params })
}

export default service
