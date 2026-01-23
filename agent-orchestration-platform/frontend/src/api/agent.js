import axios from './index'

/**
 * 获取代理列表
 */
export function getAgents(params = {}) {
  return axios.get('/v1/Agent/', { params })
}

/**
 * 获取单个代理
 */
export function getAgent(agentId) {
  return axios.get(`/v1/Agent/${agentId}`)
}

/**
 * 创建代理
 */
export function createAgent(data) {
  return axios.post('/v1/Agent/', data)
}

/**
 * 更新代理
 */
export function updateAgent(agentId, data) {
  return axios.put(`/v1/Agent/${agentId}`, data)
}

/**
 * 删除代理
 */
export function deleteAgent(agentId) {
  return axios.delete(`/v1/Agent/${agentId}`)
}

/**
 * 测试代理
 */
export function testAgent(agentId, message) {
  return axios.post(`/v1/Agent/${agentId}/test`, { message })
}
