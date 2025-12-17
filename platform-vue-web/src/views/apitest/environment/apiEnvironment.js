/**
 * 环境管理 API
 */
import axios from '~/axios'

const module_name = "ApiEnvironment"

// 分页查询
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

// 根据ID查询
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 查询项目下所有环境
export function queryByProject(projectId) {
    return axios.get(`/${module_name}/queryByProject?project_id=${projectId}`)
}

// 获取默认环境
export function getDefaultEnv(projectId) {
    return axios.get(`/${module_name}/getDefaultEnv?project_id=${projectId}`)
}

// 新增
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

// 更新
export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

// 删除
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 设置默认环境
export function setDefault(id) {
    return axios.put(`/${module_name}/setDefault?id=${id}`)
}

// 切换启用状态
export function toggleEnabled(id) {
    return axios.put(`/${module_name}/toggleEnabled?id=${id}`)
}

// 复制环境
export function copyEnv(data) {
    return axios.post(`/${module_name}/copy`, data)
}

// 初始化默认环境
export function initDefaultEnvs(projectId) {
    return axios.post(`/${module_name}/initDefaultEnvs?project_id=${projectId}`)
}
