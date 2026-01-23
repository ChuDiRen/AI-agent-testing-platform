import axios from './index'

/**
 * 获取执行列表
 */
export function getExecutions(params = {}) {
  return axios.get('/v1/Execution/', { params })
}

/**
 * 获取单个执行
 */
export function getExecution(executionId) {
  return axios.get(`/v1/Execution/${executionId}`)
}

/**
 * 创建执行
 */
export function createExecution(data) {
  return axios.post('/v1/Execution/', data)
}

/**
 * 更新执行
 */
export function updateExecution(executionId, data) {
  return axios.put(`/v1/Execution/${executionId}`, data)
}

/**
 * 取消执行
 */
export function cancelExecution(executionId) {
  return axios.post(`/v1/Execution/${executionId}/cancel`)
}
