import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "RobotConfig"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=dingtalk-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=dingtalk-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=dingtalk-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=dingtalk-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=dingtalk-delete`)
}

// 拓展其他方法 - 测试机器人连接
export function testConnection(id) {
    return axios.post(`/${module_name}/test?id=${id}&_alias=dingtalk-test`)
}
