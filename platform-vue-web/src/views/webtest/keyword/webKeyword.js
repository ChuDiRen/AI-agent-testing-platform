import axios from '~/axios'

// 获取关键字列表
export function getKeywordList(params) {
  return axios.get('/api/web/keyword/list', { params })
}

// 获取关键字详情
export function getKeywordById(id) {
  return axios.get(`/api/web/keyword/${id}`)
}

// 保存关键字（新增/更新）
export function saveKeyword(data) {
  if (data.id) {
    return axios.put('/api/web/keyword/update', data)
  }
  return axios.post('/api/web/keyword/create', data)
}

// 删除关键字
export function deleteKeyword(id) {
  return axios.delete(`/api/web/keyword/${id}`)
}

// 批量删除关键字
export function batchDeleteKeyword(ids) {
  return axios.post('/api/web/keyword/batch-delete', { ids })
}

// 生成关键字文件
export function generateKeywordFile(data) {
  return axios.post('/api/web/keyword/generate-file', data)
}

// 导入关键字
export function importKeywords(formData) {
  return axios.post('/api/web/keyword/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 导出关键字
export function exportKeywords(ids) {
  return axios.post('/api/web/keyword/export', { ids })
}
