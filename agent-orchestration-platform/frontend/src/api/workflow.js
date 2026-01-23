import axios from './index'

/**
 * 获取工作流列表
 */
export function getWorkflows(params = {}) {
  return axios.get('/v1/Workflow/', { params })
}

/**
 * 获取单个工作流
 */
export function getWorkflow(workflowId) {
  return axios.get(`/v1/Workflow/${workflowId}`)
}

/**
 * 创建工作流
 */
export function createWorkflow(data) {
  return axios.post('/v1/Workflow/', data)
}

/**
 * 更新工作流
 */
export function updateWorkflow(workflowId, data) {
  return axios.put(`/v1/Workflow/${workflowId}`, data)
}

/**
 * 删除工作流
 */
export function deleteWorkflow(workflowId) {
  return axios.delete(`/v1/Workflow/${workflowId}`)
}

/**
 * 发布工作流
 */
export function publishWorkflow(workflowId) {
  return axios.post(`/v1/Workflow/${workflowId}/publish`)
}

/**
 * 执行工作流
 */
export function executeWorkflow(workflowId, params = {}) {
  return axios.post(`/v1/Workflow/${workflowId}/execute`, params)
}
