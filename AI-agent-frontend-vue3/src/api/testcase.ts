// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试用例 API
 */
import { get, post, put, del } from './request'

export interface TestCase {
  testcase_id: number
  name: string
  test_type: string  // API/WEB/APP
  module?: string
  description?: string
  preconditions?: string
  test_steps?: string
  expected_result?: string
  priority: string  // P0/P1/P2/P3
  status: string  // draft/active/deprecated
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
  environment?: string
  config?: Record<string, any>
}

export interface TestCaseStatistics {
  total: number
  by_status: Record<string, number>
  by_priority: Record<string, number>
}

/**
 * 获取测试用例列表
 */
export function getTestCaseList(params: {
  page?: number
  page_size?: number
  test_type?: string
  keyword?: string
  status?: string
  priority?: string
}) {
  return get<{
    success: boolean
    data: {
      items: TestCase[]
      total: number
      page: number
      page_size: number
      pages: number
    }
  }>('/api/v1/testcases/', { params })
}

/**
 * 获取测试用例详情
 */
export function getTestCase(id: number) {
  return get<{ success: boolean; data: TestCase }>(`/api/v1/testcases/${id}`)
}

/**
 * 创建测试用例
 */
export function createTestCase(data: TestCaseCreate) {
  return post<{ success: boolean; message: string; data: TestCase }>('/api/v1/testcases/', data)
}

/**
 * 更新测试用例
 */
export function updateTestCase(id: number, data: TestCaseUpdate) {
  return put<{ success: boolean; message: string; data: TestCase }>(`/api/v1/testcases/${id}`, data)
}

/**
 * 删除测试用例
 */
export function deleteTestCase(id: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/testcases/${id}`)
}

/**
 * 执行测试用例
 */
export function executeTestCase(id: number, data: TestCaseExecute) {
  return post<{ success: boolean; message: string; data: any }>(`/api/v1/testcases/${id}/execute`, data)
}

/**
 * 获取统计信息
 */
export function getTestCaseStatistics(test_type?: string) {
  return get<{ success: boolean; data: TestCaseStatistics }>('/api/v1/testcases/statistics', {
    params: { test_type }
  })
}

