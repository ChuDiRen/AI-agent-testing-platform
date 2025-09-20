/**
 * 日志管理相关API接口
 */
import http from '@/api/http'
import type { ApiResponse } from '@/api/types'

/**
 * 日志级别枚举
 */
export const LogLevel = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
} as const

export type LogLevel = (typeof LogLevel)[keyof typeof LogLevel]

/**
 * 日志查询参数接口
 */
export interface LogQueryParams {
  level?: LogLevel
  start_time?: string
  end_time?: string
  keyword?: string
  module?: string
  user?: string
  page?: number
  size?: number
}

/**
 * 日志信息接口
 */
export interface LogInfo {
  id: number
  timestamp: string
  level: LogLevel
  module: string
  message: string
  user?: string
  ip_address?: string
  user_agent?: string
  details?: string
}

/**
 * 日志列表响应接口
 */
export interface LogListResponse {
  items: LogInfo[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * 日志统计接口
 */
export interface LogStats {
  total_count: number
  debug_count: number
  info_count: number
  warning_count: number
  error_count: number
  critical_count: number
  today_count: number
}

/**
 * 日志API接口类
 */
export class LogsApi {
  /**
   * 获取日志列表
   * @param params 查询参数
   * @returns 日志列表
   */
  static async getLogs(params?: LogQueryParams): Promise<ApiResponse<LogListResponse>> {
    // 使用POST请求，参数通过请求体传递
    const requestBody = {
      page: params?.page || 1,
      size: params?.size || 20,
      level: params?.level,
      start_time: params?.start_time,
      end_time: params?.end_time,
      keyword: params?.keyword,
      module: params?.module,
      user: params?.user,
    }

    return http.post<LogListResponse>('/logs/get-log-list', requestBody)
  }

  /**
   * 获取日志详情
   * @param id 日志ID
   * @returns 日志详情
   */
  static async getLogDetail(id: number): Promise<ApiResponse<LogInfo>> {
    return http.post<LogInfo>('/logs/get-log-info', { log_id: id })
  }

  /**
   * 获取日志统计
   * @returns 日志统计信息
   */
  static async getLogStats(): Promise<ApiResponse<LogStats>> {
    return http.post<LogStats>('/logs/get-log-statistics', {})
  }

  /**
   * 清空日志
   * @param beforeDate 清空指定日期之前的日志
   * @returns 清空结果
   */
  static async clearLogs(beforeDate?: string): Promise<ApiResponse<{ deleted_count: number }>> {
    const requestBody = beforeDate ? { before_date: beforeDate } : {}
    return http.post<{ deleted_count: number }>('/logs/clear-logs', requestBody)
  }
}

// 导出单个方法，保持兼容性
export const logsApi = {
  getLogs: LogsApi.getLogs,
  getLogDetail: LogsApi.getLogDetail,
  getLogStats: LogsApi.getLogStats,
  clearLogs: LogsApi.clearLogs,
}
