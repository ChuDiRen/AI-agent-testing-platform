import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiProject"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=project-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=project-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=project-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=project-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=project-delete`)
}

// 批量删除项目
export function batchDeleteData(ids) {
    return axios.delete(`/${module_name}/batchDelete?_alias=project-batch-delete`, { data: { ids } })
}

// 拓展其他方法
export function queryAllProject() {
    return axios.get(`/${module_name}/queryAll?_alias=project-all`)
}

// 别名导出，用于其他组件
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=project-all`)
}