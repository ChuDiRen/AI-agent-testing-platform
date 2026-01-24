import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiCollectionInfo"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/api/v1/${module_name}/queryByPage`, data)
}

export function queryById(id) {
    return axios.get(`/api/v1/${module_name}/queryById?id=${id}`)
}

export function insertData(data) {
    return axios.post(`/api/v1/${module_name}/insert`, data)
}

export function updateData(data) {
    return axios.put(`/api/v1/${module_name}/update`, data)
}

export function deleteData(id){
    return axios.delete(`/api/v1/${module_name}/delete?id=${id}`)
}

// 拓展其他方法
export function excuteTest(data){
    return axios.post(`/api/v1/${module_name}/excuteTest`, data)
}

// 复制测试集合
export function copyCollectionData(data){
    return axios.post(`/api/v1/${module_name}/copyData`, data)
}
