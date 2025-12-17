/**
 * 插件管理 API
 */
import axios from '~/axios'

// 分页查询插件
export function queryByPage(data) {
  return axios.post('/Plugin/queryByPage', data)
}

// 根据ID查询插件
export function queryById(id) {
  return axios.get('/Plugin/queryById', { params: { id } })
}

// 注册插件
export function registerPlugin(data) {
  return axios.post('/Plugin/register', data)
}

// 更新插件
export function updatePlugin(id, data) {
  return axios.put('/Plugin/update', data, { params: { id } })
}

// 注销插件
export function unregisterPlugin(id) {
  return axios.delete('/Plugin/unregister', { params: { id } })
}

// 启用/禁用插件
export function togglePlugin(id) {
  return axios.put('/Plugin/toggle', {}, { params: { id } })
}

// 健康检查
export function healthCheck(id) {
  return axios.post('/Plugin/healthCheck', {}, { params: { id } })
}

// 获取所有已启用的插件
export function listEnabledPlugins(pluginType) {
  return axios.get('/Plugin/list/enabled', { params: { plugin_type: pluginType } })
}

// 上传执行器（存入数据库，不用文件服务器）
export function uploadExecutor(formData) {
  return axios.post('/Plugin/uploadExecutor', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 安装执行器（异步启动）
export function installExecutor(id) {
  return axios.post('/Plugin/installExecutor', {}, { params: { id } })
}

// 查询安装进度
export function getInstallStatus(id) {
  return axios.get('/Plugin/installStatus', { params: { id } })
}

// 查询所有执行器插件
export function queryAllExecutors() {
  return axios.get('/Plugin/list/enabled', { params: { plugin_type: 'executor' } })
}

// 卸载执行器
export function uninstallExecutor(id, deleteFiles = true) {
  return axios.post('/Plugin/uninstallExecutor', {}, {
    params: { id, delete_files: deleteFiles }
  })
}
