import axios from '~/axios'

// ==================== 全局变量 ====================

// 获取全局变量列表
export function getGlobalVariableList(params) {
  return axios.get('/api/resource/variable/list', { params })
}

// 保存全局变量
export function saveGlobalVariable(data) {
  return axios.post('/api/resource/variable/save', data)
}

// 删除全局变量
export function deleteGlobalVariable(id) {
  return axios.delete(`/api/resource/variable/${id}`)
}

// ==================== 测试数据 ====================

// 获取测试数据列表
export function getTestDataList(params) {
  return axios.get('/api/resource/testdata/list', { params })
}

// 上传测试数据
export function uploadTestData(formData) {
  return axios.post('/api/resource/testdata/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 下载测试数据
export function downloadTestData(id) {
  return axios.get(`/api/resource/testdata/download/${id}`, {
    responseType: 'blob'
  })
}

// 预览测试数据
export function getTestDataPreview(id) {
  return axios.get(`/api/resource/testdata/preview/${id}`)
}

// 保存测试数据
export function saveTestData(data) {
  if (data.id) {
    return axios.put('/api/resource/testdata/update', data)
  }
  return axios.post('/api/resource/testdata/create', data)
}

// 删除测试数据
export function deleteTestData(id) {
  return axios.delete(`/api/resource/testdata/${id}`)
}

// 批量删除测试数据
export function batchDeleteTestData(ids) {
  return axios.post('/api/resource/testdata/batch-delete', { ids })
}

// ==================== 脚本库 ====================

// 获取脚本列表
export function getScriptList(params) {
  return axios.get('/api/resource/script/list', { params })
}

// 获取脚本详情
export function getScriptById(id) {
  return axios.get(`/api/resource/script/${id}`)
}

// 保存脚本
export function saveScript(data) {
  if (data.id) {
    return axios.put('/api/resource/script/update', data)
  }
  return axios.post('/api/resource/script/create', data)
}

// 删除脚本
export function deleteScript(id) {
  return axios.delete(`/api/resource/script/${id}`)
}

// 批量删除脚本
export function batchDeleteScript(ids) {
  return axios.post('/api/resource/script/batch-delete', { ids })
}

// 执行脚本
export function runScript(id, params) {
  return axios.post(`/api/resource/script/execute/${id}`, params)
}

// 执行脚本 (别名)
export function executeScript(id, params) {
  return axios.post(`/api/resource/script/execute/${id}`, params)
}

// ==================== 全局变量 (新) ====================

// 获取变量列表
export function getVariableList(params) {
  return axios.get('/api/resource/variable/list', { params })
}

// 保存变量
export function saveVariables(data) {
  return axios.post('/api/resource/variable/save', data)
}

// ==================== 文件管理 ====================

// 获取文件列表
export function getFileList(params) {
  return axios.get('/api/resource/file/list', { params })
}

// 上传文件
export function uploadFile(formData) {
  return axios.post('/api/resource/file/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 下载文件
export function downloadFile(id) {
  return axios.get(`/api/resource/file/download/${id}`, {
    responseType: 'blob'
  })
}

// 删除文件
export function deleteFile(id) {
  return axios.delete(`/api/resource/file/${id}`)
}

// 批量删除文件
export function batchDeleteFile(ids) {
  return axios.post('/api/resource/file/batch-delete', { ids })
}

// 创建文件夹
export function createFolder(data) {
  return axios.post('/api/resource/file/folder/create', data)
}
