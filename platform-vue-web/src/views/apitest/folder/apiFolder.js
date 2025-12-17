/**
 * 接口目录 API
 */
import axios from '~/axios'

const module_name = "ApiFolder"

// 查询目录树
export function queryTree(data) {
    return axios.post(`/${module_name}/queryTree`, data)
}

// 查询目录列表
export function queryList(projectId, parentId = null) {
    let url = `/${module_name}/queryList?project_id=${projectId}`
    if (parentId !== null) {
        url += `&parent_id=${parentId}`
    }
    return axios.get(url)
}

// 根据ID查询
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 新增目录
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

// 更新目录
export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

// 删除目录
export function deleteData(id, moveToParent = true) {
    return axios.delete(`/${module_name}/delete?id=${id}&move_to_parent=${moveToParent}`)
}

// 移动目录
export function moveFolder(data) {
    return axios.put(`/${module_name}/move`, data)
}

// 移动接口到目录
export function moveApis(data) {
    return axios.post(`/${module_name}/moveApis`, data)
}

// 批量排序
export function batchSort(data) {
    return axios.post(`/${module_name}/batchSort`, data)
}

// 获取目录路径
export function getPath(id) {
    return axios.get(`/${module_name}/getPath?id=${id}`)
}
