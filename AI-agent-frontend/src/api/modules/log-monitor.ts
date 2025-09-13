// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 日志监控API接口
 */

import { http } from '@/utils/http'
import type { ApiResponse } from '@/types/api'

// 实时统计数据类型
export interface RealTimeStats {
  time_range: {
    start_time: string
    end_time: string
    minutes: number
  }
  system_logs: {
    total_count: number
    level_stats: Record<string, number>
    top_modules: Array<{ module: string; count: number }>
  }
  audit_logs: {
    total_count: number
    success_count: number
    failed_count: number
    success_rate: number
    top_operations: Array<{ operation: string; count: number }>
  }
  error_rate: {
    system_error_rate: number
    audit_error_rate: number
    total_errors: number
  }
  active_users: {
    active_users_count: number
    top_users: Array<{ username: string; operations: number }>
  }
  timestamp: string
}

// 告警数据类型
export interface LogAlert {
  type: string
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  message: string
  details?: any
  time_range?: string
  count?: number
  ip_address?: string
  username?: string
}

// 趋势数据类型
export interface LogTrends {
  time_range: {
    start_time: string
    end_time: string
    days: number
  }
  daily_system_logs: Array<{
    date: string
    total: number
    debug?: number
    info?: number
    warning?: number
    error?: number
    critical?: number
  }>
  daily_audit_logs: Array<{
    date: string
    total: number
    success: number
    failed: number
    success_rate: number
  }>
  error_trends: Array<{
    date: string
    error_count: number
  }>
}

/**
 * 日志监控API类
 */
export class LogMonitorApi {
  /**
   * 获取实时日志统计
   * @param minutes 统计时间范围（分钟）
   * @returns 实时统计数据
   */
  static async getRealTimeStats(minutes: number = 5): Promise<ApiResponse<RealTimeStats>> {
    return http.post<RealTimeStats>('/logs/get-real-time-stats', { minutes })
  }

  /**
   * 获取日志告警
   * @param hours 检查时间范围（小时）
   * @returns 告警列表
   */
  static async getAlerts(hours: number = 1): Promise<ApiResponse<LogAlert[]>> {
    return http.post<LogAlert[]>('/logs/get-alerts', { hours })
  }

  /**
   * 获取日志趋势
   * @param days 分析天数
   * @returns 趋势分析数据
   */
  static async getLogTrends(days: number = 7): Promise<ApiResponse<LogTrends>> {
    return http.post<LogTrends>('/logs/get-log-trends', { days })
  }
}

// 导出单个方法，保持兼容性
export const logMonitorApi = {
  getRealTimeStats: LogMonitorApi.getRealTimeStats,
  getAlerts: LogMonitorApi.getAlerts,
  getLogTrends: LogMonitorApi.getLogTrends,
}

// 告警级别颜色映射
export const ALERT_LEVEL_COLORS = {
  LOW: '#52c41a',      // 绿色
  MEDIUM: '#faad14',   // 橙色
  HIGH: '#ff4d4f',     // 红色
  CRITICAL: '#722ed1'  // 紫色
}

// 告警级别标签映射
export const ALERT_LEVEL_LABELS = {
  LOW: '低',
  MEDIUM: '中',
  HIGH: '高',
  CRITICAL: '严重'
}

// 日志级别颜色映射
export const LOG_LEVEL_COLORS = {
  DEBUG: '#d9d9d9',    // 灰色
  INFO: '#1890ff',     // 蓝色
  WARNING: '#faad14',  // 橙色
  ERROR: '#ff4d4f',    // 红色
  CRITICAL: '#722ed1'  // 紫色
}

export default LogMonitorApi
