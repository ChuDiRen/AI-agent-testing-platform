import axios from '~/axios'

// 执行 Web 测试
export function executeWebTest(data) {
  return axios.post('/api/web/execution/run', data)
}

// 停止执行
export function stopWebTest(executionId) {
  return axios.post('/api/web/execution/stop', { execution_id: executionId })
}

// 获取执行状态
export function getExecutionStatus(executionId) {
  return axios.get(`/api/web/execution/status/${executionId}`)
}

// 获取项目列表
export function getWebProjects() {
  return axios.get('/api/web/project/list')
}

// 获取项目下的用例列表
export function getWebCasesByProject(projectId) {
  return axios.get('/api/web/case/list', { params: { project_id: projectId, pageSize: 1000 } })
}

// 获取执行历史
export function getExecutionHistory(params) {
  return axios.get('/api/web/execution/history', { params })
}

// 获取执行详情
export function getExecutionDetail(id) {
  return axios.get(`/api/web/execution/detail/${id}`)
}

// 获取报告链接
export function getReportUrl(executionId) {
  return axios.get(`/api/web/execution/report/${executionId}`)
}
