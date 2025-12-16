import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiCollectionInfo"

// ==================== 标准 CRUD 接口 ====================

/**
 * 分页查询测试计划
 */
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=collection-page`, data)
}

/**
 * 根据ID查询测试计划（含关联用例）
 */
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=collection-detail`)
}

/**
 * 新增测试计划
 */
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=collection-insert`, data)
}

/**
 * 更新测试计划
 */
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=collection-update`, data)
}

/**
 * 删除测试计划
 */
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=collection-delete`)
}

// ==================== 扩展接口 - 用例关联 ====================

/**
 * 添加用例到计划
 */
export function addCase(data) {
    return axios.post(`/${module_name}/addCase?_alias=collection-add-case`, data)
}

/**
 * 批量添加用例到计划
 */
export function batchAddCases(data) {
    return axios.post(`/${module_name}/batchAddCases?_alias=collection-batch-add`, data)
}

/**
 * 从计划中移除用例
 */
export function removeCase(planCaseId) {
    return axios.delete(`/${module_name}/removeCase?plan_case_id=${planCaseId}&_alias=collection-remove`)
}

/**
 * 更新用例的数据驱动数据
 */
export function updateDdtData(data) {
    return axios.post(`/${module_name}/updateDdtData?_alias=collection-ddt`, data)
}

/**
 * 获取用例数据驱动模板
 */
export function getDdtTemplate(caseInfoId) {
    return axios.get(`/ApiCollectionDetail/getDdtTemplate?case_info_id=${caseInfoId}&_alias=ddt-template`)
}

// ==================== 扩展接口 - 测试执行 ====================

/**
 * 执行测试计划（调用统一的 executeCase 接口，传入 plan_id）
 */
export function executePlan(data) {
    return axios.post(`/ApiInfoCase/executeCase?_alias=collection-execute`, data)
}

/**
 * 根据测试计划ID查询历史记录
 */
export function queryHistoryByPlanId(planId) {
    return axios.get(`/ApiHistory/queryByPlanId?plan_id=${planId}&_alias=test-by-plan`)
}

/**
 * 根据执行UUID查询历史记录
 */
export function queryHistoryByUuid(executionUuid) {
    return axios.get(`/ApiHistory/queryByExecutionUuid?execution_uuid=${executionUuid}&_alias=test-by-uuid`)
}

/**
 * 复制测试计划
 */
export function copyPlan(id) {
    return axios.post(`/${module_name}/copy?id=${id}&_alias=collection-copy`)
}

/**
 * 获取Jenkins配置信息
 */
export function getJenkinsConfig(id) {
    return axios.get(`/${module_name}/getJenkinsConfig?id=${id}&_alias=collection-jenkins`)
}

// ==================== 扩展接口 - 机器人通知 ====================

/**
 * 获取测试计划关联的机器人
 */
export function getPlanRobots(planId) {
    return axios.get(`/${module_name}/getRobots?plan_id=${planId}&_alias=plan-robots`)
}

/**
 * 为测试计划添加机器人通知
 */
export function addPlanRobot(data) {
    return axios.post(`/${module_name}/addRobot?_alias=plan-add-robot`, data)
}

/**
 * 更新测试计划机器人配置
 */
export function updatePlanRobot(data) {
    return axios.put(`/${module_name}/updateRobot?_alias=plan-update-robot`, data)
}

/**
 * 移除测试计划机器人关联
 */
export function removePlanRobot(id) {
    return axios.delete(`/${module_name}/removeRobot?id=${id}&_alias=plan-remove-robot`)
}

