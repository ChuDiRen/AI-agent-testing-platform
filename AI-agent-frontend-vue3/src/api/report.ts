// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试报告管理 API
 */
import request from './request'

// ==================== 类型定义 ====================

export interface TestReport {
    report_id: number
    name: string
    description?: string
    report_type: string
    test_case_id?: number
    agent_id?: number
    status: string
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
    file_path?: string
    summary?: string
    created_at: string
    updated_at?: string
}

export interface TestReportDetail extends TestReport {
    executions?: TestExecution[]
    summary?: ReportSummary
}

export interface TestExecution {
    execution_id: number
    report_id: number
    testcase_id: number
    environment?: string
    executor?: string
    status: string
    start_time?: string
    end_time?: string
    duration?: number
    actual_result?: string
    error_message?: string
    created_at: string
    updated_at?: string
}

export interface ReportSummary {
    total_cases: number
    passed: number
    failed: number
    skipped: number
    error: number
    pass_rate: number
    total_duration: number
}

export interface TestReportCreate {
    name: string
    description?: string
    report_type?: string
    test_case_id?: number
    agent_id?: number
}

export interface TestReportUpdate {
    name?: string
    description?: string
    report_type?: string
    status?: string
    summary?: string
    content?: Record<string, any>
    issues?: any[]
}

export interface ReportGenerateRequest {
    name: string
    description?: string
    report_type: string
    testcase_ids: number[]
    environment?: string
    config?: Record<string, any>
}

export interface TestReportStatistics {
    total_reports: number
    generating_reports: number
    completed_reports: number
    failed_reports: number
    average_pass_rate: number
    total_test_cases: number
    passed_test_cases: number
    failed_test_cases: number
}

export interface PaginatedReports {
    items: TestReport[]
    total: number
    page: number
    page_size: number
    total_pages: number
}

// ==================== API 接口 ====================

/**
 * 创建测试报告
 */
export function createReportAPI(data: TestReportCreate) {
    return request<TestReport>({
        url: '/api/v1/reports',
        method: 'post',
        data
    })
}

/**
 * 获取测试报告列表（分页）
 */
export function getReportsAPI(params?: {
    page?: number
    page_size?: number
    keyword?: string
    report_type?: string
    status?: string
}) {
    return request<PaginatedReports>({
        url: '/api/v1/reports',
        method: 'get',
        params
    })
}

/**
 * 获取测试报告详情
 */
export function getReportAPI(reportId: number) {
    return request<TestReportDetail>({
        url: `/api/v1/reports/${reportId}`,
        method: 'get'
    })
}

/**
 * 更新测试报告
 */
export function updateReportAPI(reportId: number, data: TestReportUpdate) {
    return request<TestReport>({
        url: `/api/v1/reports/${reportId}`,
        method: 'put',
        data
    })
}

/**
 * 删除测试报告
 */
export function deleteReportAPI(reportId: number) {
    return request({
        url: `/api/v1/reports/${reportId}`,
        method: 'delete'
    })
}

/**
 * 生成测试报告
 */
export function generateReportAPI(data: ReportGenerateRequest) {
    return request<TestReport>({
        url: '/api/v1/reports/generate',
        method: 'post',
        data
    })
}

/**
 * 获取报告的执行记录
 */
export function getReportExecutionsAPI(reportId: number) {
    return request<TestExecution[]>({
        url: `/api/v1/reports/${reportId}/executions`,
        method: 'get'
    })
}

/**
 * 导出测试报告 (PDF/Excel)
 */
export function exportReportAPI(reportId: number, format: 'pdf' | 'excel') {
    return request({
        url: `/api/v1/reports/${reportId}/export/${format}`,
        method: 'get',
        responseType: 'blob'
    })
}

/**
 * 获取测试报告统计信息
 */
export function getReportStatisticsAPI(reportType?: string) {
    return request<TestReportStatistics>({
        url: '/api/v1/reports/statistics',
        method: 'get',
        params: reportType ? { report_type: reportType } : undefined
    })
}

/**
 * 下载报告文件
 */
export function downloadReportFile(reportId: number, format: 'pdf' | 'excel', filename?: string) {
    return exportReportAPI(reportId, format).then((blob) => {
        const url = window.URL.createObjectURL(blob as Blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename || `test_report_${reportId}.${format === 'pdf' ? 'pdf' : 'xlsx'}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    })
}

