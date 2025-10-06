// Copyright (c) 2025 左岚. All rights reserved.
import request from './request'

export interface TestData {
    id?: number
    name: string
    data_type: 'json' | 'csv' | 'text' | 'sql'
    description?: string
    content: string
    created_at?: string
    updated_at?: string
}

export interface TestDataListParams {
    keyword?: string
    data_type?: string
    page?: number
    page_size?: number
}

/**
 * 获取测试数据列表
 */
export const getTestDataListAPI = (params: TestDataListParams) => {
    return request({
        url: '/api/v1/test-data',
        method: 'get',
        params
    })
}

/**
 * 获取测试数据详情
 */
export const getTestDataDetailAPI = (id: number) => {
    return request({
        url: `/api/v1/test-data/${id}`,
        method: 'get'
    })
}

/**
 * 创建测试数据
 */
export const createTestDataAPI = (data: TestData) => {
    return request({
        url: '/api/v1/test-data',
        method: 'post',
        data
    })
}

/**
 * 更新测试数据
 */
export const updateTestDataAPI = (id: number, data: Partial<TestData>) => {
    return request({
        url: `/api/v1/test-data/${id}`,
        method: 'put',
        data
    })
}

/**
 * 删除测试数据
 */
export const deleteTestDataAPI = (id: number) => {
    return request({
        url: `/api/v1/test-data/${id}`,
        method: 'delete'
    })
}

