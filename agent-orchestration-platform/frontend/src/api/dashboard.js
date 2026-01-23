import axios from './index'

/**
 * 获取工作台统计数据
 */
export function getDashboardStats() {
  return axios.get('/v1/Dashboard/stats')
}

/**
 * 获取最近活动
 */
export function getRecentActivities(params = {}) {
  return axios.get('/v1/Dashboard/activities', { params })
}
