// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试用例相关 API
 */
import { get, post, put, del } from './request'

export interface TestCase {
  id: number
  name: string
  description: string
  type: 'web' | 'api' | 'app'
  status: 'draft' | 'active' | 'archived'
  priority: 'low' | 'medium' | 'high'
  steps: any[]
  expected_result: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface TestCaseListParams {
  page?: number
  page_size?: number
  name?: string
  type?: string
  status?: string
}

export interface TestCaseListResponse {
  code: number
  data: {
    items: TestCase[]
    total: number
  }
}

/**
 * 获取测试用例列表
 */
export function getTestCaseList(params: TestCaseListParams) {
  return get<TestCaseListResponse>('/api/v1/testcase/list', params)
}

/**
 * 获取测试用例详情
 */
export function getTestCase(id: number) {
  return get<{ code: number; data: TestCase }>(`/api/v1/testcase/${id}`)
}

/**
 * 创建测试用例
 */
export function createTestCase(data: Partial<TestCase>) {
  return post<any>('/api/v1/testcase/create', data)
}

/**
 * 更新测试用例
 */
export function updateTestCase(id: number, data: Partial<TestCase>) {
  return put<any>(`/api/v1/testcase/${id}`, data)
}

/**
 * 删除测试用例
 */
export function deleteTestCase(id: number) {
  return del<any>(`/api/v1/testcase/${id}`)
}

/**
 * 执行测试用例
 */
export function executeTestCase(id: number) {
  return post<any>(`/api/v1/testcase/${id}/execute`)
}

