// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试报告 API
 */
import { get, post, del, put } from './request'

export interface TestReport {
  id: number
  name: string
  description?: string
  report_type: string // execution | summary | detailed | custom
  status: string // generating | completed | failed | archived
  test_case_id?: number
  agent_id?: number
  created_by_id: number
  start_time?: string
  end_time?: string
  duration?: number
  total_cases: number
  passed_cases: number
  failed_cases: number
  skipped_cases: number
  blocked_cases: number
  executed_cases: number
  remaining_cases: number
  pass_rate: number
  execution_rate: number
  content?: any
  file_path?: string
  summary?: string
  issues?: any[]
  extra_data?: any
  created_at: string
  updated_at: string
}

export interface ReportListParams {
  page?: number
  page_size?: number
  keyword?: string
  report_type?: string
  status?: string
}

export interface ReportCreateData {
  name: string
  description?: string
  report_type?: string
  test_case_id?: number
  agent_id?: number
}

export interface ReportUpdateData {
  name?: string
  description?: string
  report_type?: string
  summary?: string
}

export interface ReportStatistics {
  total_reports: number
  generating_reports: number
  completed_reports: number
  failed_reports: number
  average_pass_rate: number
  total_test_cases: number
  passed_test_cases: number
  failed_test_cases: number
}

/**
 * 获取测试报告列表
 */
export function getReportList(params: ReportListParams = {}) {
  return get<{ code: number; data: { reports: TestReport[]; total: number; page: number; page_size: number } }>(
    '/test-reports',
    params
  )
}

/**
 * 获取测试报告详情
 */
export function getReportDetail(id: number) {
  return get<{ code: number; data: TestReport }>(`/test-reports/${id}`)
}

/**
 * 创建测试报告
 */
export function createReport(data: ReportCreateData) {
  return post<{ code: number; msg: string; data: TestReport }>('/test-reports', data)
}

/**
 * 更新测试报告
 */
export function updateReport(id: number, data: ReportUpdateData) {
  return put<{ code: number; msg: string; data: TestReport }>(`/test-reports/${id}`, data)
}

/**
 * 删除测试报告
 */
export function deleteReport(id: number) {
  return del<{ code: number; msg: string }>(`/test-reports/${id}`)
}

/**
 * 获取测试报告统计信息
 */
export function getReportStatistics() {
  return get<{ code: number; data: ReportStatistics }>('/test-reports/statistics')
}

