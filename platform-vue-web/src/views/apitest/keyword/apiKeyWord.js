import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiKeyWord"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=keyword-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=keyword-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=keyword-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=keyword-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=keyword-delete`)
}

// 拓展其他方法
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=keyword-all`)
}

//  扩展：生成关键字文件接口
export function keywordFile(data) {
    return axios.post(`/${module_name}/keywordFile?_alias=keyword-file`, data)
}