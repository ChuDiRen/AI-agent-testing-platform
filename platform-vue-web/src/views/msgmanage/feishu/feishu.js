import axios from "~/axios"

const module_name = "RobotConfig"

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

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

export function testConnection(id) {
    return axios.post(`/${module_name}/test?id=${id}`)
}
