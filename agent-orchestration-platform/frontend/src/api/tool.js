import axios from './index'

/**
 * 获取工具列表
 */
export function getTools(params = {}) {
  return axios.get('/v1/Tool/', { params })
}

/**
 * 获取单个工具
 */
export function getTool(toolId) {
  return axios.get(`/v1/Tool/${toolId}`)
}

/**
 * 创建工具
 */
export function createTool(data) {
  return axios.post('/v1/Tool/', data)
}

/**
 * 更新工具
 */
export function updateTool(toolId, data) {
  return axios.put(`/v1/Tool/${toolId}`, data)
}

/**
 * 删除工具
 */
export function deleteTool(toolId) {
  return axios.delete(`/v1/Tool/${toolId}`)
}

/**
 * 测试工具
 */
export function testTool(toolId, params = {}) {
  return axios.post(`/v1/Tool/${toolId}/test`, params)
}
