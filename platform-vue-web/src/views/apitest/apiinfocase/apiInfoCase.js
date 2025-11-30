import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiInfoCase"

// ==================== 标准 CRUD 接口 ====================

/**
 * 分页查询用例
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=case-page`, data)
}

/**
 * 根据ID查询用例（含步骤）
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=case-detail`)
}

/**
 * 新增用例
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=case-insert`, data)
}

/**
 * 更新用例
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=case-update`, data)
}

/**
 * 删除用例
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=case-delete`)
}

// ==================== 扩展接口 ====================

/**
 * 获取用例的所有步骤
 */
export function getSteps(caseId) {
    return axios.get(`/${module_name}/getSteps?case_id=${caseId}&_alias=case-steps`)
}

// ==================== 关键字相关接口 ====================

/**
 * 根据操作类型ID查询关键字列表
 */
export function queryKeywordsByType(operationTypeId) {
    return axios.get(`/ApiKeyWord/queryByOperationType?operation_type_id=${operationTypeId}&_alias=keyword-by-type`)
}

/**
 * 获取关键字的字段描述
 */
export function getKeywordFields(keywordId) {
    return axios.get(`/ApiKeyWord/getKeywordFields?keyword_id=${keywordId}&_alias=keyword-fields`)
}

