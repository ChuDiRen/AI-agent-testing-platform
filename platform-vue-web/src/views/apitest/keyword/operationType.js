import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "OperationType"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=optype-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=optype-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=optype-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=optype-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=optype-delete`)
}

// 拓展其他方法
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=optype-all`)
}