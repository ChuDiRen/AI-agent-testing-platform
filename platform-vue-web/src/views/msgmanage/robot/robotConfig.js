import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "RobotConfig"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=robot-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=robot-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=robot-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=robot-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=robot-delete`)
}

// 扩展方法
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=robot-all`)
}

export function testConnection(data) {
    return axios.post(`/${module_name}/testConnection?_alias=robot-test`, data)
}

// 启用/禁用机器人
export function toggleEnabled(id, is_enabled) {
    return axios.put(`/${module_name}/toggleEnabled?id=${id}&is_enabled=${is_enabled}&_alias=robot-toggle`)
}
