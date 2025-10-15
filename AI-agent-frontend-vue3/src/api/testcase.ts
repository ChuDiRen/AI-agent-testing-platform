// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试用例管理 API
 */
import request from './request'

// ==================== 类型定义 ====================

export interface TestCase {
    testcase_id: number
    name: string
    test_type: string
    module?: string
    description?: string
    preconditions?: string
    test_steps?: string
    expected_result?: string
    priority: string
    status: string
    tags?: string
    created_by: number
    create_time: string
    modify_time?: string
}

export interface TestCaseCreate {
    name: string
    test_type: string
    module?: string
    description?: string
    preconditions?: string
    test_steps?: string
    expected_result?: string
    priority?: string
    status?: string
    tags?: string
}

export interface TestCaseUpdate {
    name?: string
    test_type?: string
    module?: string
    description?: string
    preconditions?: string
    test_steps?: string
    expected_result?: string
    priority?: string
    status?: string
    tags?: string
}

export interface TestCaseExecute {
    config?: Record<string, any>
}

export interface TestCaseExecutionResult {
    testcase_id: number
    testcase_name: string
    status: 'passed' | 'failed' | 'error'
    duration: number
    error_message?: string
    actual_result?: any
    expected_result?: any
}

export interface BatchExecutionResult {
    total: number
    passed: number
    failed: number
    error: number
    total_duration: number
    results: TestCaseExecutionResult[]
}

export interface TestCaseStatistics {
    total: number
    by_type?: Record<string, number>
    by_status?: Record<string, number>
    by_priority?: Record<string, number>
}

export interface PaginatedTestCases {
    items: TestCase[]
    total: number
    page: number
    page_size: number
    total_pages: number
}

// ==================== API 接口 ====================

/**
 * 创建测试用例
 */
export function createTestCaseAPI(data: TestCaseCreate) {
    return request<TestCase>({
        url: '/api/v1/testcases',
        method: 'post',
        data
    })
}

/**
 * 获取测试用例列表（分页）
 */
export function getTestCasesAPI(params?: {
    page?: number
    page_size?: number
    test_type?: string
    keyword?: string
    status?: string
    priority?: string
}) {
    return request<PaginatedTestCases>({
        url: '/api/v1/testcases',
        method: 'get',
        params
    })
}

/**
 * 获取测试用例详情
 */
export function getTestCaseAPI(testcaseId: number) {
    return request<TestCase>({
        url: `/api/v1/testcases/${testcaseId}`,
        method: 'get'
    })
}

/**
 * 更新测试用例
 */
export function updateTestCaseAPI(testcaseId: number, data: TestCaseUpdate) {
    return request<TestCase>({
        url: `/api/v1/testcases/${testcaseId}`,
        method: 'put',
        data
    })
}

/**
 * 删除测试用例
 */
export function deleteTestCaseAPI(testcaseId: number) {
    return request({
        url: `/api/v1/testcases/${testcaseId}`,
        method: 'delete'
    })
}

/**
 * 执行测试用例
 */
export function executeTestCaseAPI(testcaseId: number, data?: TestCaseExecute) {
    return request<TestCaseExecutionResult>({
        url: `/api/v1/testcases/${testcaseId}/execute`,
        method: 'post',
        data: data || {}
    })
}

/**
 * 批量执行测试用例
 */
export function batchExecuteTestCasesAPI(testcaseIds: number[], config?: Record<string, any>) {
    return request<BatchExecutionResult>({
        url: '/api/v1/testcases/batch-execute',
        method: 'post',
        data: {
            testcase_ids: testcaseIds,
            config: config || {}
        }
    })
}

/**
 * 获取测试用例统计信息
 */
export function getTestCaseStatisticsAPI(testType?: string) {
    return request<TestCaseStatistics>({
        url: '/api/v1/testcases/statistics',
        method: 'get',
        params: testType ? { test_type: testType } : undefined
    })
}

/**
 * 导出测试用例（CSV/JSON）
 */
export function exportTestCasesAPI(format: 'csv' | 'json', filters?: {
    test_type?: string
    status?: string
    priority?: string
}) {
    return request({
        url: '/api/v1/testcases/export',
        method: 'get',
        params: { format, ...filters },
        responseType: 'blob'
    })
}

// ==================== AI生成测试用例相关 ====================

export interface AIGenerateRequest {
    requirement: string
    test_type: string
    module?: string
    count?: number
    model_key?: string
    template_id?: number
    use_custom_prompt?: boolean
    custom_prompt?: string
}

export interface AIGenerateResponse {
    testcases: any[]
    total: number
}

/**
 * AI生成测试用例（文本输入）
 */
export function generateTestCasesWithTextAPI(data: AIGenerateRequest) {
    return request<AIGenerateResponse>({
        url: '/api/v1/ai/generate-testcases',
        method: 'post',
        data
    })
}

/**
 * AI生成测试用例（文件上传）
 */
export function generateTestCasesWithFileAPI(file: File, params: {
    test_type?: string
    module?: string
    count?: number
    model_key?: string
    template_id?: number
}) {
    const formData = new FormData()
    formData.append('file', file)
    if (params.test_type) formData.append('test_type', params.test_type)
    if (params.module) formData.append('module', params.module)
    if (params.count) formData.append('count', params.count.toString())
    if (params.model_key) formData.append('model_key', params.model_key)
    if (params.template_id) formData.append('template_id', params.template_id.toString())

    return request<AIGenerateResponse>({
        url: '/api/v1/ai/generate-testcases/upload',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 批量保存AI生成的测试用例
 */
export function batchSaveTestCasesAPI(testcases: any[]) {
    return request<{
        saved_count: number
        failed_count: number
        saved_ids: number[]
        errors: any[]
    }>({
        url: '/api/v1/ai/testcases/batch-save',
        method: 'post',
        data: testcases
    })
}

/**
 * 获取可用的AI模型列表
 */
export function getAIModelsAPI() {
    return request<any[]>({
        url: '/api/v1/ai/models',
        method: 'get'
    })
}

