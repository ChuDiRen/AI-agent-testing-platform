import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebExecution"

// ==================== Web测试执行相关接口 ====================

/**
 * 执行Web测试
 * @param {Object} params - 测试参数
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.execution_name - 执行名称
 * @param {String} params.execution_type - 执行类型：single/batch/schedule
 * @param {Array} params.case_ids - 要执行的用例ID列表
 * @param {String} params.browser_type - 浏览器类型：chrome/firefox/safari/edge
 * @param {String} params.environment - 执行环境：dev/test/prod
 * @param {Number} params.parallel_count - 并发数，默认1
 * @param {Number} params.retry_count - 重试次数，默认0
 * @param {Number} params.timeout - 超时时间（分钟），默认30
 * @param {Boolean} params.generate_report - 是否生成报告，默认true
 * @param {Boolean} params.take_screenshot - 是否截图，默认true
 * @returns {Promise}
 */
export function executeWebTest(params) {
    return axios.post(`/${module_name}/run?_alias=web-execute`, params)
}

/**
 * 停止Web测试执行
 * @param {String} executionId - 执行ID
 * @param {Boolean} forceStop - 是否强制停止，默认false
 * @returns {Promise}
 */
export function stopWebTest(executionId, forceStop = false) {
    return axios.post(`/${module_name}/stop?_alias=web-stop`, {
        execution_id: executionId,
        force_stop: forceStop
    })
}

/**
 * 查询Web测试执行状态
 * @param {String} executionId - 执行ID
 * @returns {Promise}
 */
export function getExecutionStatus(executionId) {
    return axios.get(`/${module_name}/status/${executionId}?_alias=web-status`)
}

/**
 * 轮询查询Web测试执行状态
 * @param {String} executionId - 执行ID
 * @param {Object} options - 配置选项
 * @param {Number} options.interval - 轮询间隔（毫秒），默认2000
 * @param {Number} options.maxAttempts - 最大尝试次数，默认30
 * @param {Function} options.onProgress - 进度回调
 * @param {Function} options.onComplete - 完成回调
 * @param {Function} options.onError - 错误回调
 * @returns {Promise}
 */
export function pollExecutionStatus(executionId, options = {}) {
    const {
        interval = 2000,      // 轮询间隔（毫秒）
        maxAttempts = 30,     // 最大尝试次数
        onProgress = null,    // 进度回调
        onComplete = null,    // 完成回调
        onError = null        // 错误回调
    } = options

    return new Promise((resolve, reject) => {
        let attempts = 0

        const poll = async () => {
            attempts++

            // 检查是否超过最大尝试次数
            if (attempts > maxAttempts) {
                const error = new Error('Web测试执行超时')
                if (onError) onError(error)
                reject(error)
                return
            }

            try {
                const result = await getExecutionStatus(executionId)

                if (result.code === 200 && result.data) {
                    const status = result.data.status
                    const progress = result.data.progress || 0

                    // 进度回调
                    if (onProgress) {
                        onProgress({
                            status,
                            progress,
                            attempts,
                            maxAttempts,
                            total_cases: result.data.total_cases || 0,
                            passed_cases: result.data.passed_cases || 0,
                            failed_cases: result.data.failed_cases || 0,
                            current_case: result.data.current_case
                        })
                    }

                    // 检查状态
                    if (status === 'completed' || status === 'failed' || status === 'stopped') {
                        // 测试完成
                        if (onComplete) onComplete(result.data)
                        resolve(result.data)
                    } else if (status === 'running' || status === 'pending') {
                        // 继续轮询
                        setTimeout(poll, interval)
                    } else {
                        // 未知状态
                        const error = new Error(`未知的执行状态: ${status}`)
                        if (onError) onError(error)
                        reject(error)
                    }
                } else {
                    // API返回错误
                    const error = new Error(result.msg || '查询执行状态失败')
                    if (onError) onError(error)
                    reject(error)
                }
            } catch (error) {
                // 网络错误，继续重试
                console.warn(`查询执行状态失败（尝试 ${attempts}/${maxAttempts}）:`, error)
                setTimeout(poll, interval)
            }
        }

        // 开始轮询
        poll()
    })
}

/**
 * 批量执行Web测试
 * @param {Array} caseList - 用例列表
 * @param {Object} options - 配置选项
 * @param {Number} options.concurrent - 并发数，默认1
 * @param {Function} options.onProgress - 进度回调
 * @param {Function} options.onComplete - 完成回调
 * @returns {Promise}
 */
export async function executeBatchWebTests(caseList, options = {}) {
    const {
        concurrent = 1,       // 并发数
        onProgress = null,    // 进度回调
        onComplete = null     // 完成回调
    } = options

    const results = []
    let completed = 0

    // 执行单个测试
    const executeOne = async (caseInfo) => {
        try {
            const result = await executeWebTest({
                project_id: caseInfo.project_id,
                execution_name: `${caseInfo.name}_批量测试`,
                execution_type: 'batch',
                case_ids: [caseInfo.id],
                browser_type: 'chrome',
                environment: 'test'
            })

            if (result.code === 200 && result.data) {
                const executionId = result.data.execution_id
                const testResult = await pollExecutionStatus(executionId, {
                    onProgress: (progress) => {
                        // 子进度回调
                    }
                })

                completed++
                if (onProgress) {
                    onProgress({
                        completed,
                        total: caseList.length,
                        progress: (completed / caseList.length) * 100
                    })
                }

                return {
                    caseInfo,
                    success: true,
                    result: testResult
                }
            } else {
                throw new Error(result.msg || '执行失败')
            }
        } catch (error) {
            completed++
            if (onProgress) {
                onProgress({
                    completed,
                    total: caseList.length,
                    progress: (completed / caseList.length) * 100
                })
            }

            return {
                caseInfo,
                success: false,
                error: error.message
            }
        }
    }

    // 控制并发执行
    for (let i = 0; i < caseList.length; i += concurrent) {
        const batch = caseList.slice(i, i + concurrent)
        const batchResults = await Promise.all(batch.map(executeOne))
        results.push(...batchResults)
    }

    if (onComplete) onComplete(results)
    return results
}

// ==================== 项目和用例相关接口 ====================

/**
 * 获取Web项目列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getWebProjects() {
    return axios.get('/WebProject/queryAll?_alias=web-projects')
}

/**
 * 获取项目下的用例列表
 * @param {Number} projectId - 项目ID
 * @param {Object} options - 查询选项
 * @param {Number} options.pageSize - 每页数量，默认1000
 * @returns {Promise}
 */
export function getWebCasesByProject(projectId, options = {}) {
    const { pageSize = 1000 } = options
    return axios.post('/WebCase/queryByPage?_alias=web-cases', {
        project_id: projectId,
        pageSize: pageSize
    })
}

// ==================== 历史和报告相关接口 ====================

/**
 * 获取Web测试执行历史
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getExecutionHistory(params) {
    return axios.post('/WebHistory/queryByPage?_alias=web-history', params)
}

/**
 * 获取Web测试执行详情
 * @param {String} id - 执行ID
 * @returns {Promise}
 */
export function getExecutionDetail(id) {
    return axios.get('/WebHistory/queryById?_alias=web-detail', { params: { id } })
}

/**
 * 获取Web测试报告链接
 * @param {String} executionId - 执行ID
 * @returns {Promise}
 */
export function getReportUrl(executionId) {
    return axios.get(`/WebReport/allure/${executionId}?_alias=web-report`)
}

/**
 * 获取Web测试执行统计
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getExecutionStats(params) {
    return axios.get('/WebHistory/getStatistics?_alias=web-stats', { params })
}

/**
 * 检查Web测试引擎是否可用
 * @returns {Promise<Boolean>}
 */
export async function checkWebEngineAvailable() {
    try {
        const response = await axios.get('/WebExecution/engine/health?_alias=web-engine-health')
        return response.code === 200
    } catch {
        return false
    }
}
