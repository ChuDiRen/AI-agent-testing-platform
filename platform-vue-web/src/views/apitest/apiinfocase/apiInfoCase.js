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

/**
 * 获取用例使用的引擎列表
 */
export function getCaseEngines(caseId) {
    return axios.get(`/${module_name}/getCaseEngines?case_id=${caseId}&_alias=case-engines`)
}

// ==================== 执行相关接口 ====================

/**
 * 执行单个用例（后端统一处理 YAML 构建）
 * executor_code 可为空，后端会自动检测
 */
export function executeCase(data) {
    return axios.post(`/${module_name}/executeCase?_alias=case-execute`, data)
}

/**
 * 查询执行状态
 */
export function getExecutionStatus(testId) {
    return axios.get(`/${module_name}/executionStatus?test_id=${testId}&_alias=case-status`)
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

/**
 * 按执行引擎分组查询所有关键字
 */
export function queryKeywordsGroupedByEngine() {
    return axios.get(`/ApiKeyWord/queryGroupedByEngine?_alias=keyword-grouped`)
}

/**
 * 从XMind文件导入测试用例
 */
export function importXMind(formData) {
    return axios.post(`/${module_name}/importXMind?_alias=case-import-xmind`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

