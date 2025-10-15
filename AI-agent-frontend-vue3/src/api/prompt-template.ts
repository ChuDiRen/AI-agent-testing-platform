// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 提示词模板管理 API
 */
import request from './request'

// ==================== 类型定义 ====================

export interface PromptTemplate {
    template_id: number
    name: string
    template_type: string
    test_type?: string
    content: string
    variables?: string
    description?: string
    is_default: boolean
    is_active: boolean
    created_by?: number
    create_time: string
    modify_time?: string
}

export interface PromptTemplateCreate {
    name: string
    template_type?: string
    test_type?: string
    content: string
    variables?: string
    description?: string
    is_active?: boolean
}

export interface PromptTemplateUpdate {
    name?: string
    template_type?: string
    test_type?: string
    content?: string
    variables?: string
    description?: string
    is_active?: boolean
}

// ==================== API 接口 ====================

/**
 * 创建提示词模板
 */
export function createPromptTemplateAPI(data: PromptTemplateCreate) {
    return request<PromptTemplate>({
        url: '/api/v1/prompt-templates',
        method: 'post',
        data
    })
}

/**
 * 获取提示词模板列表
 */
export function getPromptTemplatesAPI(params?: {
    template_type?: string
    test_type?: string
    is_active?: boolean
}) {
    return request<PromptTemplate[]>({
        url: '/api/v1/prompt-templates',
        method: 'get',
        params
    })
}

/**
 * 获取默认提示词模板
 */
export function getDefaultPromptTemplateAPI(params?: {
    template_type?: string
    test_type?: string
}) {
    return request<PromptTemplate>({
        url: '/api/v1/prompt-templates/default',
        method: 'get',
        params
    })
}

/**
 * 获取提示词模板详情
 */
export function getPromptTemplateAPI(templateId: number) {
    return request<PromptTemplate>({
        url: `/api/v1/prompt-templates/${templateId}`,
        method: 'get'
    })
}

/**
 * 更新提示词模板
 */
export function updatePromptTemplateAPI(templateId: number, data: PromptTemplateUpdate) {
    return request<PromptTemplate>({
        url: `/api/v1/prompt-templates/${templateId}`,
        method: 'put',
        data
    })
}

/**
 * 删除提示词模板
 */
export function deletePromptTemplateAPI(templateId: number) {
    return request({
        url: `/api/v1/prompt-templates/${templateId}`,
        method: 'delete'
    })
}

/**
 * 设置为默认模板
 */
export function setDefaultPromptTemplateAPI(templateId: number) {
    return request<PromptTemplate>({
        url: `/api/v1/prompt-templates/${templateId}/set-default`,
        method: 'post'
    })
}

