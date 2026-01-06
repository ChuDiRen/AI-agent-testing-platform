import axios from '~/axios'

// 获取元素列表
export function getElementList(params) {
  return axios.get('/api/web/element/list', { params })
}

// 获取元素详情
export function getElementById(id) {
  return axios.get(`/api/web/element/${id}`)
}

// 保存元素（新增/更新）
export function saveElement(data) {
  if (data.id) {
    return axios.put('/api/web/element/update', data)
  }
  return axios.post('/api/web/element/create', data)
}

// 删除元素
export function deleteElement(id) {
  return axios.delete(`/api/web/element/${id}`)
}

// 批量删除元素
export function batchDeleteElement(ids) {
  return axios.post('/api/web/element/batch-delete', { ids })
}

// 导入元素
export function importElements(formData) {
  return axios.post('/api/web/element/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 导出元素
export function exportElements(ids) {
  return axios.post('/api/web/element/export', { ids })
}

// 按模块获取元素
export function getElementsByModule(module) {
  return axios.get('/api/web/element/by-module', { params: { module } })
}
