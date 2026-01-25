import axios from "@/axios"

// 模块名 - 和后台对应
const module_name = "Settings"

// 查询系统设置
export function querySettings() {
    return axios.get(`/api/v1/${module_name}/query`)
}

// 更新系统设置
export function updateSettings(data) {
    return axios.put(`/api/v1/${module_name}/update`, data)
}
