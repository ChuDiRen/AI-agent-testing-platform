/**
 * Mock服务 API
 */
import axios from '~/axios'

const module_name = "ApiMock"

// 分页查询
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

// 根据ID查询
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 查询接口的Mock规则
export function queryByApi(apiId) {
    return axios.get(`/${module_name}/queryByApi?api_id=${apiId}`)
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

// 切换启用状态
export function toggleEnabled(id) {
    return axios.put(`/${module_name}/toggleEnabled?id=${id}`)
}

// 从接口生成Mock
export function generateFromApi(data) {
    return axios.post(`/${module_name}/generateFromApi`, data)
}

// 查询Mock日志
export function queryLogs(data) {
    return axios.post(`/${module_name}/queryLogs`, data)
}

// 清空Mock日志
export function clearLogs(projectId, days = 7) {
    return axios.delete(`/${module_name}/clearLogs?project_id=${projectId}&days=${days}`)
}

// 获取Mock URL
export function getMockUrl(id) {
    return axios.get(`/${module_name}/getMockUrl?id=${id}`)
}
