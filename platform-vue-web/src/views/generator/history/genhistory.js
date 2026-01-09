import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "Generator"

// 获取生成历史
export function queryByPage(data) {
    return axios.get(`/${module_name}/history?_alias=genhistory-page`, { params: data })
}

// 根据ID查询生成历史
export function queryById(id) {
    return axios.get(`/${module_name}/history?id=${id}&_alias=genhistory-detail`)
}

// 删除生成历史
export function deleteData(id) {
    return axios.delete(`/${module_name}/history?id=${id}&_alias=genhistory-delete`)
}
