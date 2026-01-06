import axios from '~/axios'

// 获取用例列表
export function getWebCaseList(params) {
  return axios.get('/api/web/case/list', { params })
}

// 获取用例目录树
export function getWebCaseTree(projectId) {
  return axios.get('/api/web/case/tree', { params: { project_id: projectId } })
}

// 获取用例详情
export function getWebCaseById(id) {
  return axios.get(`/api/web/case/${id}`)
}

// 保存用例（新增/更新）
export function saveWebCase(data) {
  if (data.id) {
    return axios.put('/api/web/case/update', data)
  }
  return axios.post('/api/web/case/create', data)
}

// 删除用例
export function deleteWebCase(id) {
  return axios.delete(`/api/web/case/${id}`)
}

// 批量删除用例
export function batchDeleteWebCase(ids) {
  return axios.post('/api/web/case/batch-delete', { ids })
}

// 导入 XMind 用例
export function importXMindCase(formData) {
  return axios.post('/api/web/case/import-xmind', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 添加用例到测试计划
export function addCasesToPlan(data) {
  return axios.post('/api/web/case/add-to-plan', data)
}

// 创建目录
export function createFolder(data) {
  return axios.post('/api/web/case/folder/create', data)
}

// 删除目录
export function deleteFolder(id) {
  return axios.delete(`/api/web/case/folder/${id}`)
}

// 复制用例
export function copyCase(id) {
  return axios.post(`/api/web/case/copy/${id}`)
}
