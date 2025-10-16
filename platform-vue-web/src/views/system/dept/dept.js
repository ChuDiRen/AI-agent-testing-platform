import axios from "~/axios"

const module_name = "dept" // 模块名

// 获取部门树
export function getDeptTree() {
    return axios.get(`/${module_name}/tree`)
}

// 根据ID查询部门
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 新增部门
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

// 更新部门
export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

// 删除部门
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

