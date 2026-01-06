import axios from '~/axios'

// ==================== 测试计划 ====================

// 获取测试计划列表
export function getPlanList(params) {
  return axios.get('/api/testplan/list', { params })
}

// 获取测试计划详情
export function getPlanById(id) {
  return axios.get(`/api/testplan/${id}`)
}

// 保存测试计划
export function savePlan(data) {
  if (data.id) {
    return axios.put('/api/testplan/update', data)
  }
  return axios.post('/api/testplan/create', data)
}

// 删除测试计划
export function deletePlan(id) {
  return axios.delete(`/api/testplan/${id}`)
}

// 批量删除测试计划
export function batchDeletePlan(ids) {
  return axios.post('/api/testplan/batch-delete', { ids })
}

// 复制测试计划
export function copyPlan(id) {
  return axios.post(`/api/testplan/copy/${id}`)
}

// 执行测试计划
export function executePlan(data) {
  return axios.post('/api/testplan/execute', data)
}

// 获取测试计划关联的用例
export function getPlanCases(planId) {
  return axios.get(`/api/testplan/${planId}/cases`)
}

// 添加用例到测试计划
export function addCaseToPlan(planId, caseIds) {
  return axios.post(`/api/testplan/${planId}/cases`, { case_ids: caseIds })
}

// 从测试计划移除用例
export function removeCaseFromPlan(planId, caseId) {
  return axios.delete(`/api/testplan/${planId}/cases/${caseId}`)
}

// 获取测试计划执行历史
export function getPlanHistory(planId) {
  return axios.get(`/api/testplan/${planId}/history`)
}
