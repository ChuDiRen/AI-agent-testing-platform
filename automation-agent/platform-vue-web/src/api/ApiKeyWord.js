import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiKeyWord"

export function queryByPage(data) {
    return axios.post(`/api/v1/${module_name}/queryByPage`, data)
}

export function queryById(id) {
    return axios.get(`/api/v1/${module_name}/queryById?id=${id}`)
}

export function insertData(data) {
    console.log(data)
    return axios.post(`/api/v1/${module_name}/insert`, data)
}

export function updateData(data) {
    return axios.put(`/api/v1/${module_name}/update`, data)
}

export function deleteData(id){
    return axios.delete(`/api/v1/${module_name}/delete?id=${id}`)
}

// 拓展其他方法
export function queryAll(){
    return axios.get(`/api/v1/${module_name}/queryAll`)
}

//  扩展：生成关键字文件接口
export function keywordFile(data) {
    return axios.post(`/api/v1/${module_name}/keywordFile`, data)
}

//  扩展：查询关键字级联数据的接口
export function queryAllKeyWordList() {
    return axios.get(`/api/v1/${module_name}/queryAllKeyWordList`)
}
