/**
 * 请求历史 API
 */
import axios from '~/axios'

const module_name = "ApiRequestHistory"

// 分页查询
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

// 根据ID查询
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 查询最近请求
export function queryRecent(projectId, limit = 10) {
    return axios.get(`/${module_name}/queryRecent?project_id=${projectId}&limit=${limit}`)
}

// 查询收藏的请求
export function queryFavorites(projectId) {
    return axios.get(`/${module_name}/queryFavorites?project_id=${projectId}`)
}

// 新增历史记录
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

// 删除
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 批量删除
export function batchDelete(ids) {
    return axios.post(`/${module_name}/batchDelete`, { ids })
}

// 切换收藏
export function toggleFavorite(id) {
    return axios.put(`/${module_name}/toggleFavorite?id=${id}`)
}

// 清空历史
export function clearHistory(data) {
    return axios.post(`/${module_name}/clear`, data)
}

// 统计
export function getStatistics(projectId, days = 7) {
    return axios.get(`/${module_name}/statistics?project_id=${projectId}&days=${days}`)
}
