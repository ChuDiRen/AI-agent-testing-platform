import axios from '~/axios'

// ==================== 执行队列 ====================

// 获取队列列表
export function getQueueList(params) {
  return axios.get('/api/queue/list', { params })
}

// 取消排队任务
export function cancelQueueTask(taskId) {
  return axios.post(`/api/queue/cancel/${taskId}`)
}

// 清空队列
export function clearQueue() {
  return axios.post('/api/queue/clear')
}

// 移动任务位置
export function moveQueueTask(taskId, direction) {
  return axios.post(`/api/queue/move/${taskId}`, { direction })
}

// 停止正在执行的任务
export function stopRunningTask(taskId) {
  return axios.post(`/api/queue/stop/${taskId}`)
}

// 获取队列统计
export function getQueueStats() {
  return axios.get('/api/queue/stats')
}
