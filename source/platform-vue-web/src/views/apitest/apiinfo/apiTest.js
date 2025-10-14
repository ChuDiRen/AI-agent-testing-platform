import axios from '~/axios'

const module_name = "ApiTestHistory" // 模块名称

// 执行API测试
export function executeApiTest(data) {
    return axios.post(`/${module_name}/executeTest`, data)
}

// 查询测试历史（分页）
export function queryTestHistory(params) {
    return axios.post(`/${module_name}/queryByPage`, params)
}

// 查询测试历史（分页） - 别名
export function queryTestHistoryByPage(params) {
    return axios.post(`/${module_name}/queryByPage`, params)
}

// 根据ID查询测试历史
export function queryTestHistoryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 删除测试历史
export function deleteTestHistory(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}
