import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "ApiTest"

// ==================== 测试执行相关接口 ====================

/**
 * 执行API测试
 * @param {Object} params - 测试参数
 * @param {Number} params.api_info_id - 接口信息ID
 * @param {String} params.test_name - 测试名称（可选）
 * @param {Object} params.context_vars - 上下文变量（可选）
 * @param {Array} params.pre_script - 前置脚本列表（可选）
 * @param {Array} params.post_script - 后置脚本列表（可选）
 * @param {Array} params.variable_extracts - 变量提取配置列表（可选）
 * @param {Array} params.assertions - 断言配置列表（可选）
 * @returns {Promise}
 */
export function executeTest(params) {
    return axios.post(`/${module_name}/execute?_alias=test-execute`, params)
}

/**
 * 查询测试状态
 * @param {Number} testId - 测试ID
 * @returns {Promise}
 */
export function getTestStatus(testId) {
    return axios.get(`/${module_name}/status?_alias=test-status`, {
        params: { test_id: testId }
    })
}

/**
 * 轮询查询测试状态
 * @param {Number} testId - 测试ID
 * @param {Object} options - 配置选项
 * @param {Number} options.interval - 轮询间隔（毫秒），默认2000
 * @param {Number} options.maxAttempts - 最大尝试次数，默认30
 * @param {Function} options.onProgress - 进度回调
 * @param {Function} options.onComplete - 完成回调
 * @param {Function} options.onError - 错误回调
 * @returns {Promise}
 */
export function pollTestStatus(testId, options = {}) {
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
                const error = new Error('测试执行超时')
                if (onError) onError(error)
                reject(error)
                return
            }

            try {
                const result = await getTestStatus(testId)

                if (result.code === 200 && result.data) {
                    const status = result.data.status

                    // 进度回调
                    if (onProgress) {
                        onProgress({
                            status,
                            attempts,
                            maxAttempts,
                            progress: Math.min((attempts / maxAttempts) * 100, 99)
                        })
                    }

                    // 检查状态
                    if (status === 'success' || status === 'failed') {
                        // 测试完成
                        if (onComplete) onComplete(result.data)
                        resolve(result.data)
                    } else if (status === 'running') {
                        // 继续轮询
                        setTimeout(poll, interval)
                    } else {
                        // 未知状态
                        const error = new Error(`未知的测试状态: ${status}`)
                        if (onError) onError(error)
                        reject(error)
                    }
                } else {
                    // API返回错误
                    const error = new Error(result.msg || '查询测试状态失败')
                    if (onError) onError(error)
                    reject(error)
                }
            } catch (error) {
                // 网络错误，继续重试
                console.warn(`查询测试状态失败（尝试 ${attempts}/${maxAttempts}）:`, error)
                setTimeout(poll, interval)
            }
        }

        // 开始轮询
        poll()
    })
}

/**
 * 批量执行测试
 * @param {Array} apiInfoList - 接口信息列表
 * @param {Object} options - 配置选项
 * @param {Number} options.concurrent - 并发数，默认1
 * @param {Function} options.onProgress - 进度回调
 * @param {Function} options.onComplete - 完成回调
 * @returns {Promise}
 */
export async function executeBatchTests(apiInfoList, options = {}) {
    const {
        concurrent = 1,       // 并发数
        onProgress = null,    // 进度回调
        onComplete = null     // 完成回调
    } = options

    const results = []
    let completed = 0

    // 执行单个测试
    const executeOne = async (apiInfo) => {
        try {
            const result = await executeTest({
                api_info_id: apiInfo.id,
                test_name: `${apiInfo.api_name}_批量测试`
            })

            if (result.code === 200 && result.data) {
                const testId = result.data.test_id
                const testResult = await pollTestStatus(testId)

                completed++
                if (onProgress) {
                    onProgress({
                        completed,
                        total: apiInfoList.length,
                        progress: (completed / apiInfoList.length) * 100
                    })
                }

                return {
                    apiInfo,
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
                    total: apiInfoList.length,
                    progress: (completed / apiInfoList.length) * 100
                })
            }

            return {
                apiInfo,
                success: false,
                error: error.message
            }
        }
    }

    // 控制并发执行
    for (let i = 0; i < apiInfoList.length; i += concurrent) {
        const batch = apiInfoList.slice(i, i + concurrent)
        const batchResults = await Promise.all(batch.map(executeOne))
        results.push(...batchResults)
    }

    if (onComplete) onComplete(results)
    return results
}

/**
 * 获取测试报告URL
 * @param {Number} testId - 测试ID
 * @returns {String}
 */
export function getReportUrl(testId) {
    return `/api/reports/allure/${testId}/index.html`
}

/**
 * 检查api-engine是否可用
 * @returns {Promise<Boolean>}
 */
export async function checkEngineAvailable() {
    try {
        const response = await axios.get('/ApiTest/engine/health?_alias=engine-health')
        return response.code === 200
    } catch {
        return false
    }
}
