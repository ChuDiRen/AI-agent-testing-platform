// AI模型管理API服务
import axios from "~/axios" // 统一使用~别名

// 模块名 - 和后台对应
const module_name = "AiModel"

// 标准 - 增删改查接口调用

/**
 * 分页查询
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=aimodel-page`, data)
}

/**
 * 根据ID查询
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=aimodel-detail`)
}

/**
 * 插入数据
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=aimodel-insert`, data)
}

/**
 * 更新数据
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=aimodel-update`, data)
}

/**
 * 删除数据
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=aimodel-delete`)
}

// 拓展其他方法

/**
 * 查询所有启用的模型
 */
export function queryEnabled() {
    return axios.get(`/${module_name}/queryEnabled?_alias=aimodel-enabled`)
}

/**
 * 切换模型启用/禁用状态
 */
export function toggleStatus(id) {
    return axios.post(`/${module_name}/toggleStatus?id=${id}&_alias=aimodel-toggle`)
}

/**
 * 测试模型连接
 */
export function testConnection(id) {
    return axios.post(`/${module_name}/testConnection?id=${id}&_alias=aimodel-test`)
}

// ==================== 模型同步相关接口 ====================

/**
 * 获取支持的提供商列表
 */
export function getSyncProviders() {
    return axios.get(`/${module_name}/sync/providers?_alias=modelsync-providers`)
}

/**
 * 同步单个提供商的模型
 * @param {Object} data - { provider: string, api_key?: string, update_existing?: boolean }
 */
export function syncProvider(data) {
    return axios.post(`/${module_name}/sync/provider?_alias=modelsync-provider`, data)
}

/**
 * 同步所有提供商的模型
 * @param {Object} data - { api_keys?: object, update_existing?: boolean }
 */
export function syncAllProviders(data = {}) {
    return axios.post(`/${module_name}/sync/all?_alias=modelsync-all`, data)
}

/**
 * 获取同步状态
 */
export function getSyncStatus() {
    return axios.get(`/${module_name}/sync/status?_alias=modelsync-status`)
}

