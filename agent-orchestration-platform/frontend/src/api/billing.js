import axios from './index'

/**
 * 获取使用量统计
 */
export function getUsageStats(params = {}) {
  return axios.get('/v1/Billing/usage', { params })
}

/**
 * 获取按代理分组的成本统计
 */
export function getAgentBreakdown(params = {}) {
  return axios.get('/v1/Billing/agent-breakdown', { params })
}

/**
 * 获取使用警报列表
 */
export function getUsageAlerts(params = {}) {
  return axios.get('/v1/Billing/alerts', { params })
}

/**
 * 关闭警报
 */
export function dismissAlert(alertId) {
  return axios.delete(`/v1/Billing/alerts/${alertId}`)
}

/**
 * 获取配额列表
 */
export function getCostQuotas(params = {}) {
  return axios.get('/v1/Billing/quotas', { params })
}

/**
 * 创建配额
 */
export function createCostQuota(data) {
  return axios.post('/v1/Billing/quotas', data)
}

/**
 * 更新配额
 */
export function updateCostQuota(quotaId, data) {
  return axios.put(`/v1/Billing/quotas/${quotaId}`, data)
}
