import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "user"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=user-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=user-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=user-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=user-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=user-delete`)
}

// 为用户分配角色
export function assignRoles(data) {
    return axios.post(`/${module_name}/assignRoles?_alias=user-assign-roles`, data)
}

// 获取用户的角色
export function getUserRoles(userId) {
    return axios.get(`/${module_name}/roles/${userId}?_alias=user-roles`)
}

// 更新用户状态
export function updateStatus(data) {
    return axios.put(`/${module_name}/updateStatus?_alias=user-status`, data)
}