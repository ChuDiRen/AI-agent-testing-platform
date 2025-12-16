import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiDbBase"

// 标准 - 增删改查接口调用

export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=dbbase-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=dbbase-detail`)
}


export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=dbbase-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=dbbase-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=dbbase-delete`)
}

// 拓展其他方法
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=dbbase-all`)
}

// 测试连接
export function testConnection(data) {
    return axios.post(`/${module_name}/testConnection?_alias=dbbase-test`, data)
}

// 启用/禁用配置
export function toggleEnabled(id, is_enabled) {
    return axios.put(`/${module_name}/toggleEnabled?id=${id}&is_enabled=${is_enabled}&_alias=dbbase-toggle`)
}

// 根据项目ID查询数据库配置
export function queryByProject(project_id) {
    return axios.get(`/${module_name}/queryByProject?project_id=${project_id}&_alias=dbbase-project`)
}