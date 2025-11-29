import axios from "~/axios"

const module_name = "RobotConfig"

export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=feishu-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=feishu-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=feishu-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=feishu-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=feishu-delete`)
}

export function testConnection(id) {
    return axios.post(`/${module_name}/test?id=${id}&_alias=feishu-test`)
}
