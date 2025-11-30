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
 * 生成用例YAML文件
 */
export function generateYaml(data) {
    return axios.post(`/${module_name}/generateYaml?_alias=case-yaml`, data)
}

/**
 * 执行用例（异步提交）
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

/**
 * 执行用例并轮询结果
 * @param {Object} data - 执行参数
 * @param {Object} options - 轮询选项
 * @param {Function} options.onProgress - 进度回调 (status, data)
 * @param {number} options.interval - 轮询间隔(ms)，默认2000
 * @param {number} options.timeout - 超时时间(ms)，默认120000
 * @returns {Promise} - 最终执行结果
 */
export async function executeCaseWithPolling(data, options = {}) {
    const { onProgress, interval = 2000, timeout = 120000 } = options

    // 1. 提交执行请求
    const submitRes = await executeCase(data)
    if (submitRes.code !== 200 || !submitRes.data?.test_id) {
        throw new Error(submitRes.msg || '提交执行失败')
    }

    const testId = submitRes.data.test_id
    onProgress?.('running', { test_id: testId, message: '测试已提交，正在执行...' })

    // 2. 轮询状态
    const startTime = Date.now()
    return new Promise((resolve, reject) => {
        const poll = async () => {
            try {
                // 超时检查
                if (Date.now() - startTime > timeout) {
                    reject(new Error('执行超时'))
                    return
                }

                const statusRes = await getExecutionStatus(testId)
                if (statusRes.code !== 200) {
                    reject(new Error(statusRes.msg || '查询状态失败'))
                    return
                }

                const { data: statusData, finished } = statusRes.data
                onProgress?.(statusData.status, statusData)

                if (finished) {
                    // 执行完成
                    resolve(statusData)
                } else {
                    // 继续轮询
                    setTimeout(poll, interval)
                }
            } catch (error) {
                reject(error)
            }
        }

        // 延迟一点再开始轮询，给后台一点启动时间
        setTimeout(poll, 500)
    })
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

