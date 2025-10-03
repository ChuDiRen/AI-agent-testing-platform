// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 仪表板相关 API
 */
import { get } from './request'

export interface DashboardStats {
  totalCases: number
  webCases: number
  apiCases: number
  appCases: number
}

export interface TrendData {
  timeline: string[]
  web: number[]
  api: number[]
  app: number[]
}

/**
 * 获取仪表板统计数据
 */
export function getDashboardStats() {
  return get<{ code: number; data: DashboardStats }>('/api/v1/dashboard/stats')
}

/**
 * 获取趋势图表数据
 */
export function getTrendData() {
  return get<{ code: number; data: TrendData }>('/api/v1/dashboard/trend')
}

/**
 * 获取最近活动
 */
export function getRecentActivities() {
  return get<any>('/api/v1/dashboard/activities')
}

