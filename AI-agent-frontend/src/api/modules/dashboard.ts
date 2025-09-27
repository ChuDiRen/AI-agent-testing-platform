/**
 * 仪表板相关API接口
 */
import http from '@/api/http'
import type { ApiResponse } from '@/api/types'

/**
 * 仪表板统计数据接口
 */
export interface DashboardStats {
  user_count: number
  role_count: number
  menu_count: number
  department_count: number
  // AI代理相关统计 # 新增AI代理统计字段
  agent_count: number
  active_agent_count: number
  running_agent_count: number
  // 测试相关统计 # 新增测试统计字段
  test_case_count: number
  test_report_count: number
  // AI模型相关统计 # 新增AI模型统计字段
  ai_model_count: number
}

/**
 * 系统信息接口
 */
export interface SystemInfo {
  system_version: string
  server_info: string
  database_info: string
  last_login_time?: string
}

/**
 * 最近活动接口
 */
export interface RecentActivity {
  activity_type: string
  description: string
  user_name: string
  create_time: string
}

/**
 * 快捷操作接口
 */
export interface QuickAction {
  name: string
  icon: string
  path: string
  description: string
  permission?: string
}

/**
 * 仪表板概览接口
 */
export interface DashboardOverview {
  stats: DashboardStats
  system_info: SystemInfo
  recent_activities: RecentActivity[]
  quick_actions: QuickAction[] // 新增快捷操作
  agent_status_chart: { // 新增图表数据
    labels: string[]
    data: number[]
    colors: string[]
  }
}

/**
 * 仪表板API接口类
 */
export class DashboardApi {
  /**
   * 获取仪表板统计数据
   * @returns 统计数据
   */
  static async getStats(): Promise<ApiResponse<DashboardStats>> {
    return http.post<DashboardStats>('/dashboard/get-statistics-data', {})
  }

  /**
   * 获取系统信息
   * @returns 系统信息
   */
  static async getSystemInfo(): Promise<ApiResponse<SystemInfo>> {
    return http.post<SystemInfo>('/dashboard/get-system-info', {})
  }

  /**
   * 获取仪表板概览
   * @returns 概览数据
   */
  static async getOverview(): Promise<ApiResponse<DashboardOverview>> {
    return http.post<DashboardOverview>('/dashboard/get-overview-data', {})
  }
}

// 导出单个方法，保持兼容性
export const dashboardApi = {
  getStats: DashboardApi.getStats,
  getSystemInfo: DashboardApi.getSystemInfo,
  getOverview: DashboardApi.getOverview,
}
