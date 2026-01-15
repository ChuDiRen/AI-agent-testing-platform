import axios from "~/axios"

const module_name = "departments" // 模块名

// 获取部门树
export function getDeptTree() {
    return axios.get(`/${module_name}/tree?_alias=dept-tree`)
}

// 根据ID查询部门
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=dept-detail`)
}

// 新增部门
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=dept-insert`, data)
}

// 更新部门
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=dept-update`, data)
}

// 删除部门
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=dept-delete`)
}

