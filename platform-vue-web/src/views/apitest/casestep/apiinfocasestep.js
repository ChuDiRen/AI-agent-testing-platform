import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiInfoCaseStep"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=step-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=step-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=step-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=step-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=step-delete`)
}

// 拓展其他方法 - 更新步骤顺序
export function updateOrder(data) {
    return axios.put(`/${module_name}/updateOrder?_alias=step-order`, data)
}
