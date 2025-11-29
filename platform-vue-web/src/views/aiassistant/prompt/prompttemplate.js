// 提示词模板管理API服务
import axios from "~/axios" // 统一使用~别名

// 模块名 - 和后台对应
const module_name = "PromptTemplate"

// 标准 - 增删改查接口调用

/**
 * 分页查询
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=prompt-page`, data)
}

/**
 * 根据ID查询
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=prompt-detail`)
}

/**
 * 插入数据
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=prompt-insert`, data)
}

/**
 * 更新数据
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=prompt-update`, data)
}

/**
 * 删除数据
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=prompt-delete`)
}

// 拓展其他方法

/**
 * 切换模板激活/停用状态
 */
export function toggleActive(id) {
    return axios.post(`/${module_name}/toggleActive?id=${id}&_alias=prompt-toggle`)
}

/**
 * 按测试类型查询模板
 */
export function queryByTestType(testType) {
    return axios.get(`/${module_name}/queryByTestType?test_type=${testType}&_alias=prompt-by-type`)
}

