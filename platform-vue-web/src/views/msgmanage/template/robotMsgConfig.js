import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "RobotMsgConfig"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=msgconfig-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=msgconfig-detail`)
}

export function queryByRobotId(robot_id) {
    return axios.get(`/${module_name}/queryByRobotId?robot_id=${robot_id}&_alias=msgconfig-by-robot`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=msgconfig-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=msgconfig-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=msgconfig-delete`)
}

// 扩展方法
export function sendMessage(data) {
    return axios.post(`/${module_name}/send?_alias=msgconfig-send`, data)
}

export function sendToRabbitMQ(data) {
    return axios.post(`/${module_name}/sendToRabbitMQ?_alias=msgconfig-mq`, data)
}
