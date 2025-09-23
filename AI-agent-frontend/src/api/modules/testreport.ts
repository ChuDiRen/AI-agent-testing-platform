// 测试报告相关API
import { http } from '@/api/http'
import type { ApiResponse } from '@/api/types'

// 测试报告信息接口
export interface TestReportInfo {
  id: number
  title: string
  description?: string
  test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit' | 'regression' | 'load' | 'stress'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timeout'
  priority: 'low' | 'medium' | 'high' | 'critical'
  
  // 执行信息
  start_time: string
  end_time?: string
  execution_time?: number // 执行时长（秒）
  
  // 统计信息
  total_cases: number
  passed_cases: number
  failed_cases: number
  skipped_cases: number
  success_rate: number
  
  // 关联信息
  test_case_ids: number[]
  agent_id?: number
  agent_name?: string
  created_by_id: number
  creator_name?: string
  
  // 配置信息
  config?: {
    timeout?: number
    retry_count?: number
    parallel_execution?: boolean
    environment?: string
    browser?: string
    [key: string]: any
  }
  
  // 结果信息
  summary?: {
    overview: string
    key_findings: string[]
    recommendations: string[]
    risk_level: 'low' | 'medium' | 'high' | 'critical'
  }
  
  // 附件信息
  attachments?: Array<{
    name: string
    url: string
    type: 'screenshot' | 'video' | 'log' | 'report' | 'other'
    size: number
  }>
  
  created_at: string
  updated_at: string
}

// 测试报告详细结果接口
export interface TestReportDetail extends TestReportInfo {
  test_results: TestCaseResult[]
  performance_metrics?: PerformanceMetrics
  error_logs?: ErrorLog[]
  coverage_info?: CoverageInfo
}

// 测试用例结果接口
export interface TestCaseResult {
  id: number
  test_case_id: number
  test_case_name: string
  status: 'passed' | 'failed' | 'skipped' | 'error'
  start_time: string
  end_time?: string
  execution_time: number
  error_message?: string
  stack_trace?: string
  screenshots?: string[]
  logs?: string[]
  metrics?: {
    response_time?: number
    memory_usage?: number
    cpu_usage?: number
    [key: string]: any
  }
  steps?: Array<{
    step_number: number
    description: string
    status: 'passed' | 'failed' | 'skipped'
    screenshot?: string
    error_message?: string
  }>
}

// 性能指标接口
export interface PerformanceMetrics {
  response_times: {
    min: number
    max: number
    avg: number
    p95: number
    p99: number
  }
  throughput: {
    requests_per_second: number
    transactions_per_second: number
  }
  resource_usage: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    network_usage: number
  }
  error_rates: {
    http_4xx: number
    http_5xx: number
    timeout: number
    connection_error: number
  }
}

// 错误日志接口
export interface ErrorLog {
  id: number
  timestamp: string
  level: 'error' | 'warning' | 'info' | 'debug'
  message: string
  source: string
  stack_trace?: string
  context?: Record<string, any>
}

// 代码覆盖率信息接口
export interface CoverageInfo {
  overall_coverage: number
  line_coverage: number
  branch_coverage: number
  function_coverage: number
  file_coverage: Array<{
    file_path: string
    coverage_percentage: number
    covered_lines: number
    total_lines: number
  }>
}

// 测试报告统计接口
export interface TestReportStatistics {
  total_reports: number
  completed_reports: number
  running_reports: number
  failed_reports: number
  overall_success_rate: number
  avg_execution_time: number
  total_test_cases: number
  recent_trends: Array<{
    date: string
    reports_count: number
    success_rate: number
    avg_execution_time: number
  }>
  type_distribution: Array<{
    test_type: string
    count: number
    success_rate: number
  }>
}

// 搜索参数接口
export interface TestReportSearchParams {
  page?: number
  page_size?: number
  keyword?: string
  test_type?: string
  status?: string
  priority?: string
  agent_id?: number
  created_by_id?: number
  start_date?: string
  end_date?: string
  order_by?: string
  order_desc?: boolean
}

// 搜索结果接口
export interface TestReportSearchResult {
  test_reports: TestReportInfo[]
  total: number
  page: number
  page_size: number
}

// 创建报告请求接口
export interface TestReportCreateRequest {
  title: string
  description?: string
  test_type: string
  priority?: string
  test_case_ids: number[]
  agent_id?: number
  config?: Record<string, any>
  schedule?: {
    run_immediately?: boolean
    scheduled_time?: string
    recurring?: {
      enabled: boolean
      frequency: 'daily' | 'weekly' | 'monthly'
      interval: number
    }
  }
}

// 更新报告请求接口
export interface TestReportUpdateRequest {
  title?: string
  description?: string
  test_type?: string
  priority?: string
  status?: string
  config?: Record<string, any>
}

// 批量操作请求接口
export interface TestReportBatchRequest {
  report_ids: number[]
  operation: 'delete' | 'cancel' | 'rerun' | 'export'
  params?: Record<string, any>
}

// 导出选项接口
export interface ExportOptions {
  format: 'pdf' | 'html' | 'excel' | 'json'
  include_screenshots?: boolean
  include_logs?: boolean
  include_metrics?: boolean
  template?: string
  language?: string
}

export const testReportApi = {
  /**
   * 获取测试报告统计信息
   */
  getStatistics(): Promise<ApiResponse<TestReportStatistics>> {
    return http.get('/test-reports/statistics')
  },

  /**
   * 获取测试报告列表
   */
  getTestReportList(params?: TestReportSearchParams): Promise<ApiResponse<TestReportSearchResult>> {
    return http.get('/test-reports', { params })
  },

  /**
   * 搜索测试报告
   */
  searchTestReports(params: TestReportSearchParams): Promise<ApiResponse<TestReportSearchResult>> {
    return http.get('/test-reports/search', { params })
  },

  /**
   * 获取测试报告详情
   */
  getTestReportDetail(reportId: number): Promise<ApiResponse<TestReportDetail>> {
    return http.get(`/test-reports/${reportId}`)
  },

  /**
   * 创建测试报告
   */
  createTestReport(data: TestReportCreateRequest): Promise<ApiResponse<TestReportInfo>> {
    return http.post('/test-reports', data)
  },

  /**
   * 生成测试报告（快速创建并执行）
   */
  generateReport(data: TestReportCreateRequest): Promise<ApiResponse<TestReportInfo>> {
    return http.post('/test-reports/generate', data)
  },

  /**
   * 更新测试报告
   */
  updateTestReport(reportId: number, data: TestReportUpdateRequest): Promise<ApiResponse<TestReportInfo>> {
    return http.put(`/test-reports/${reportId}`, data)
  },

  /**
   * 删除测试报告
   */
  deleteTestReport(reportId: number): Promise<ApiResponse<void>> {
    return http.delete(`/test-reports/${reportId}`)
  },

  /**
   * 执行测试报告
   */
  executeReport(reportId: number, config?: Record<string, any>): Promise<ApiResponse<{ execution_id: string }>> {
    return http.post(`/test-reports/${reportId}/execute`, config || {})
  },

  /**
   * 停止测试报告执行
   */
  stopExecution(reportId: number): Promise<ApiResponse<void>> {
    return http.post(`/test-reports/${reportId}/stop`)
  },

  /**
   * 重新运行测试报告
   */
  rerunReport(reportId: number, config?: Record<string, any>): Promise<ApiResponse<{ execution_id: string }>> {
    return http.post(`/test-reports/${reportId}/rerun`, config || {})
  },

  /**
   * 获取报告执行状态
   */
  getExecutionStatus(reportId: number): Promise<ApiResponse<{
    status: string
    progress: number
    current_case: string
    elapsed_time: number
    estimated_remaining_time: number
  }>> {
    return http.get(`/test-reports/${reportId}/status`)
  },

  /**
   * 导出测试报告
   */
  exportReport(reportId: number, options: ExportOptions): Promise<Blob> {
    return http.post(`/test-reports/${reportId}/export`, options, {
      responseType: 'blob'
    })
  },

  /**
   * 批量导出测试报告
   */
  batchExportReports(reportIds: number[], options: ExportOptions): Promise<Blob> {
    return http.post('/test-reports/batch-export', {
      report_ids: reportIds,
      ...options
    }, {
      responseType: 'blob'
    })
  },

  /**
   * 批量操作测试报告
   */
  batchOperation(data: TestReportBatchRequest): Promise<ApiResponse<{
    success_count: number
    failed_count: number
    failed_reports?: Array<{ id: number; title: string; error: string }>
  }>> {
    return http.post('/test-reports/batch-operation', data)
  },

  /**
   * 获取报告模板列表
   */
  getTemplates(): Promise<ApiResponse<Array<{
    id: string
    name: string
    description: string
    format: string
    preview_url?: string
  }>>> {
    return http.get('/test-reports/templates')
  },

  /**
   * 获取测试用例结果详情
   */
  getTestCaseResult(reportId: number, resultId: number): Promise<ApiResponse<TestCaseResult>> {
    return http.get(`/test-reports/${reportId}/results/${resultId}`)
  },

  /**
   * 获取报告的错误日志
   */
  getReportLogs(reportId: number, params?: {
    level?: string
    page?: number
    page_size?: number
  }): Promise<ApiResponse<{ logs: ErrorLog[]; total: number }>> {
    return http.get(`/test-reports/${reportId}/logs`, { params })
  },

  /**
   * 获取报告的性能指标
   */
  getReportMetrics(reportId: number): Promise<ApiResponse<PerformanceMetrics>> {
    return http.get(`/test-reports/${reportId}/metrics`)
  },

  /**
   * 获取报告的覆盖率信息
   */
  getReportCoverage(reportId: number): Promise<ApiResponse<CoverageInfo>> {
    return http.get(`/test-reports/${reportId}/coverage`)
  },

  /**
   * 获取报告趋势数据
   */
  getReportTrends(params?: {
    days?: number
    test_type?: string
      agent_id?: number
  }): Promise<ApiResponse<{
    trends: Array<{
          date: string
          total_reports: number
          success_rate: number
          avg_execution_time: number
          total_cases: number
        }>
        summary: {
          total_reports: number
          avg_success_rate: number
      avg_execution_time: number
      trend_direction: 'up' | 'down' | 'stable'
    }
  }>> {
    return http.get('/test-reports/trends', { params })
  },

  /**
   * 比较测试报告
   */
  compareReports(reportIds: number[]): Promise<ApiResponse<{
    comparison: {
      reports: TestReportInfo[]
      metrics_comparison: {
        success_rates: number[]
        execution_times: number[]
        case_counts: number[]
      }
      differences: Array<{
        metric: string
        values: any[]
        trend: 'improved' | 'degraded' | 'stable'
      }>
    }
  }>> {
    return http.post('/test-reports/compare', { report_ids: reportIds })
  },

  /**
   * 获取报告附件
   */
  getReportAttachments(reportId: number): Promise<ApiResponse<Array<{
    id: number
    name: string
    type: string
    size: number
    url: string
    created_at: string
  }>>> {
    return http.get(`/test-reports/${reportId}/attachments`)
  },

  /**
   * 上传报告附件
   */
  uploadAttachment(reportId: number, file: File, type?: string): Promise<ApiResponse<{
    id: number
    name: string
    url: string
  }>> {
    const formData = new FormData()
    formData.append('file', file)
    if (type) {
      formData.append('type', type)
    }
    
    return http.post(`/test-reports/${reportId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 删除报告附件
   */
  deleteAttachment(reportId: number, attachmentId: number): Promise<ApiResponse<void>> {
    return http.delete(`/test-reports/${reportId}/attachments/${attachmentId}`)
  }
}

// 测试报告工具类
export const testReportUtils = {
  /**
   * 格式化报告状态
   */
  formatStatus(status: string): { text: string; type: string; color: string } {
    const statusMap = {
      pending: { text: '待执行', type: 'info', color: '#909399' },
      running: { text: '执行中', type: 'warning', color: '#e6a23c' },
      completed: { text: '已完成', type: 'success', color: '#67c23a' },
      failed: { text: '执行失败', type: 'danger', color: '#f56c6c' },
      cancelled: { text: '已取消', type: 'info', color: '#909399' },
      timeout: { text: '超时', type: 'danger', color: '#f56c6c' }
    }
    return statusMap[status as keyof typeof statusMap] || statusMap.pending
  },

  /**
   * 格式化测试类型
   */
  formatTestType(type: string): { text: string; icon: string; color: string } {
    const typeMap = {
      functional: { text: '功能测试', icon: '🔧', color: '#409eff' },
      performance: { text: '性能测试', icon: '⚡', color: '#e6a23c' },
      security: { text: '安全测试', icon: '🔒', color: '#f56c6c' },
      integration: { text: '集成测试', icon: '🔗', color: '#67c23a' },
      unit: { text: '单元测试', icon: '📦', color: '#909399' },
      regression: { text: '回归测试', icon: '🔄', color: '#9c27b0' },
      load: { text: '负载测试', icon: '📊', color: '#ff9800' },
      stress: { text: '压力测试', icon: '💥', color: '#f44336' }
    }
    return typeMap[type as keyof typeof typeMap] || typeMap.functional
  },

  /**
   * 格式化优先级
   */
  formatPriority(priority: string): { text: string; type: string; color: string } {
    const priorityMap = {
      low: { text: '低', type: 'info', color: '#909399' },
      medium: { text: '中', type: 'warning', color: '#e6a23c' },
      high: { text: '高', type: 'primary', color: '#409eff' },
      critical: { text: '紧急', type: 'danger', color: '#f56c6c' }
    }
    return priorityMap[priority as keyof typeof priorityMap] || priorityMap.medium
  },

  /**
   * 计算成功率
   */
  calculateSuccessRate(passed: number, total: number): number {
    if (total === 0) return 0
    return Math.round((passed / total) * 100)
  },

  /**
   * 格式化执行时间
   */
  formatDuration(seconds: number): string {
    if (seconds < 60) {
      return `${seconds}秒`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}分${remainingSeconds}秒`
    } else {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}小时${minutes}分钟`
    }
  },

  /**
   * 获取风险等级颜色
   */
  getRiskLevelColor(level: string): string {
    const colorMap = {
      low: '#67c23a',
      medium: '#e6a23c',
      high: '#f56c6c',
      critical: '#ff4d4f'
    }
    return colorMap[level as keyof typeof colorMap] || colorMap.medium
  },

  /**
   * 生成报告摘要
   */
  generateSummary(report: TestReportInfo): string {
    const { total_cases, passed_cases, failed_cases, success_rate, test_type } = report
    const typeText = this.formatTestType(test_type).text
    
    return `${typeText}共执行${total_cases}个用例，通过${passed_cases}个，失败${failed_cases}个，成功率${success_rate}%。`
  },

  /**
   * 导出文件名生成
   */
  generateExportFileName(report: TestReportInfo, format: string): string {
    const date = new Date().toISOString().split('T')[0]
    const safeName = report.title.replace(/[^\w\u4e00-\u9fa5]/g, '_')
    return `${safeName}_${date}.${format}`
  },

  /**
   * 解析测试结果趋势
   */
  analyzeTrend(data: number[]): 'up' | 'down' | 'stable' {
    if (data.length < 2) return 'stable'
    
    const first = data[0]
    const last = data[data.length - 1]
    const diff = last - first
    const threshold = Math.abs(first) * 0.05 // 5% threshold
    
    if (Math.abs(diff) <= threshold) return 'stable'
    return diff > 0 ? 'up' : 'down'
  },

  /**
   * 格式化文件大小
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }
}

export default testReportApi