// AI模型管理API服务
import axios from "~/axios" // 统一使用~别名

// 模块名 - 和后台对应
const module_name = "AiModel"

// 标准 - 增删改查接口调用

/**
 * 分页查询
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

/**
 * 根据ID查询
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

/**
 * 插入数据
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

/**
 * 更新数据
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

/**
 * 删除数据
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 拓展其他方法

/**
 * 查询所有启用的模型
 */
export function queryEnabled() {
    return axios.get(`/${module_name}/queryEnabled`)
}

/**
 * 切换模型启用/禁用状态
 */
export function toggleStatus(id) {
    return axios.post(`/${module_name}/toggleStatus?id=${id}`)
}

/**
 * 测试模型连接
 */
export function testConnection(id) {
    return axios.post(`/${module_name}/testConnection?id=${id}`)
}

