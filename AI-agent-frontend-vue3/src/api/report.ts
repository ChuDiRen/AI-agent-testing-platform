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
  return get<{ success: boolean; data: { items: TestReport[]; total: number; page: number; page_size: number } }>(
    '/api/v1/reports',
    params
  )
}

/**
 * 获取测试报告详情
 */
export function getReportDetail(id: number) {
  return get<{ success: boolean; data: TestReport }>(`/api/v1/reports/${id}`)
}

/**
 * 创建测试报告
 */
export function createReport(data: ReportCreateData) {
  return post<{ success: boolean; message: string; data: TestReport }>('/api/v1/reports', data)
}

/**
 * 更新测试报告
 */
export function updateReport(id: number, data: ReportUpdateData) {
  return put<{ success: boolean; message: string; data: TestReport }>(`/api/v1/reports/${id}`, data)
}

/**
 * 删除测试报告
 */
export function deleteReport(id: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/reports/${id}`)
}

/**
 * 获取测试报告统计信息
 */
export function getReportStatistics() {
  return get<{ success: boolean; data: ReportStatistics }>('/api/v1/reports/statistics')
}

/**
 * 生成测试报告
 */
export function generateReport(data: { name: string; description?: string; report_type?: string; testcase_ids: number[]; environment?: string }) {
  return post<{ success: boolean; message: string; data: TestReport }>('/api/v1/reports/generate', data)
}

/**
 * 导出测试报告（直接下载文件）
 */
export function exportReportFile(reportId: number, format: 'pdf' | 'excel') {
  // 使用window.open直接触发下载
  const token = localStorage.getItem('access_token')
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const url = `${baseURL}/api/v1/reports/${reportId}/export/${format}`

  // 创建隐藏的a标签触发下载
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `test_report_${reportId}.${format === 'pdf' ? 'pdf' : 'xlsx'}`)

  // 添加token到请求头（通过iframe方式）
  // 由于下载链接需要认证，使用fetch+blob方式
  return fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('导出失败')
      }
      return response.blob()
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob)
      link.href = url
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      return { success: true, message: '导出成功' }
    })
    .catch(error => {
      throw error
    })
}

