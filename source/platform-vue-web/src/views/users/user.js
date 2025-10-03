import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "user"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

export function deleteData(id){
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 拓展其他方法