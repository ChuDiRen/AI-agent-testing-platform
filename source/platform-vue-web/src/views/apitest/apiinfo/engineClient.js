/**
 * api-engine执行客户端封装
 */

import axios from 'axios'

const API_TEST_BASE_URL = '/api/ApiTest'

/**
 * 执行API测试
 * @param {Object} params - 测试参数
 * @returns {Promise}
 */
export const executeTest = async (params) => {
    try {
        const response = await axios.post(`${API_TEST_BASE_URL}/execute`, params)
        return response.data
    } catch (error) {
        console.error('执行测试失败:', error)
        throw error
    }
}

/**
 * 查询测试状态
 * @param {Number} testId - 测试ID
 * @returns {Promise}
 */
export const getTestStatus = async (testId) => {
    try {
        const response = await axios.get(`${API_TEST_BASE_URL}/status`, {
            params: { test_id: testId }
        })
        return response.data
    } catch (error) {
        console.error('查询测试状态失败:', error)
        throw error
    }
}

/**
 * 轮询查询测试状态
 * @param {Number} testId - 测试ID
 * @param {Object} options - 配置选项
 * @returns {Promise}
 */
export const pollTestStatus = (testId, options = {}) => {
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
 * @returns {Promise}
 */
export const executeBatchTests = async (apiInfoList, options = {}) => {
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
 * 取消测试执行（如果支持）
 * @param {Number} testId - 测试ID
 * @returns {Promise}
 */
export const cancelTest = async (testId) => {
    // TODO: 后端需要实现取消测试的接口
    console.warn('取消测试功能尚未实现')
    return Promise.reject(new Error('功能未实现'))
}

/**
 * 获取测试报告URL
 * @param {Number} testId - 测试ID
 * @returns {String}
 */
export const getReportUrl = (testId) => {
    return `/api/reports/allure/${testId}/index.html`
}

/**
 * 检查api-engine是否可用
 * @returns {Promise<Boolean>}
 */
export const checkEngineAvailable = async () => {
    try {
        const response = await axios.get('/api/engine/health')
        return response.data.code === 200
    } catch {
        return false
    }
}

