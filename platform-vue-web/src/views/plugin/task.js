/**
 * 任务执行 API
 */
import axios from '~/axios'

// 执行测试任务
export function executeTest(data) {
    return axios.post('/Task/execute', data)
}

// 查询任务状态
export function getTaskStatus(data) {
    return axios.post('/Task/status', data)
}

// 获取测试报告
export function getTestReport(data) {
    return axios.post('/Task/report', data)
}

// 取消任务
export function cancelTask(data) {
    return axios.post('/Task/cancel', data)
}

// 获取可用执行器列表
export function listExecutors() {
    return axios.get('/Task/executors')
}
