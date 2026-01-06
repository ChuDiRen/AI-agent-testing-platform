import axios from '~/axios'

// ==================== 定时任务 ====================

// 获取定时任务列表
export function getScheduleList(params) {
  return axios.get('/api/schedule/list', { params })
}

// 获取定时任务详情
export function getScheduleById(id) {
  return axios.get(`/api/schedule/${id}`)
}

// 保存定时任务
export function saveSchedule(data) {
  if (data.id) {
    return axios.put('/api/schedule/update', data)
  }
  return axios.post('/api/schedule/create', data)
}

// 删除定时任务
export function deleteSchedule(id) {
  return axios.delete(`/api/schedule/${id}`)
}

// 切换定时任务状态
export function toggleScheduleStatus(id, status) {
  return axios.post(`/api/schedule/${id}/status`, { status })
}

// 立即执行定时任务
export function runScheduleNow(id) {
  return axios.post(`/api/schedule/${id}/run`)
}

// 获取定时任务执行日志
export function getScheduleLog(id, params) {
  return axios.get(`/api/schedule/${id}/log`, { params })
}
