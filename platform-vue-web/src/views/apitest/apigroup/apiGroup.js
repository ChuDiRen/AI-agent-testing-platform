import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiGroup"

// 标准 - 增删改查接口调用

/**
 * 分页查询分组
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

/**
 * 根据ID查询分组
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

/**
 * 新增分组
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

/**
 * 更新分组
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

/**
 * 删除分组
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 拓展其他方法

/**
 * 获取项目下的分组树
 */
export function getGroupTree(projectId) {
    return axios.get(`/${module_name}/tree?project_id=${projectId}`)
}

/**
 * 根据项目获取所有分组（平铺）
 */
export function getByProject(projectId) {
    return axios.get(`/${module_name}/getByProject?project_id=${projectId}`)
}
