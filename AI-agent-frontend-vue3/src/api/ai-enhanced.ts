// Copyright (c) 2025 左岚. All rights reserved.
/**
 * AI增强API - 支持流式响应和模型管理
 */
import request from './request'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  message: string
  session_id?: number
  model?: string
  stream?: boolean
  temperature?: number
  max_tokens?: number
}

export interface ChatResponse {
  session_id: number
  message: {
    message_id: number
    role: string
    content: string
    created_at: string
  }
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export interface AIModel {
  model_id: number
  name: string
  provider: string
  model_key: string
  api_base?: string
  max_tokens: number
  temperature: string
  is_enabled: boolean
  description?: string
  created_at: string
}

/**
 * 发送聊天消息(非流式)
 */
export function chatAPI(data: ChatRequest) {
  return request<ChatResponse>({
    url: '/ai/chat',
    method: 'post',
    data: { ...data, stream: false }
  })
}

/**
 * 发送聊天消息(流式) - 返回EventSource
 */
export function chatStreamAPI(data: ChatRequest): EventSource {
  const token = localStorage.getItem('token')
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  // 构建查询参数
  const params = new URLSearchParams({
    message: data.message,
    stream: 'true',
    ...(data.session_id && { session_id: data.session_id.toString() }),
    ...(data.model && { model: data.model }),
    ...(data.temperature && { temperature: data.temperature.toString() }),
    ...(data.max_tokens && { max_tokens: data.max_tokens.toString() })
  })
  
  // 创建EventSource连接
  const url = `${baseURL}/api/v1/ai/chat?${params.toString()}`
  const eventSource = new EventSource(url, {
    withCredentials: false
  })
  
  // 添加token到请求头(EventSource不支持自定义headers,需要后端支持token参数)
  return eventSource
}

/**
 * 获取可用AI模型列表
 */
export function getModelsAPI() {
  return request<AIModel[]>({
    url: '/ai/models',
    method: 'get'
  })
}

/**
 * 创建AI模型
 */
export function createModelAPI(data: Partial<AIModel>) {
  return request<AIModel>({
    url: '/ai/models',
    method: 'post',
    data
  })
}

/**
 * 更新AI模型
 */
export function updateModelAPI(modelId: number, data: Partial<AIModel>) {
  return request<AIModel>({
    url: `/ai/models/${modelId}`,
    method: 'put',
    data
  })
}

/**
 * 删除AI模型
 */
export function deleteModelAPI(modelId: number) {
  return request({
    url: `/ai/models/${modelId}`,
    method: 'delete'
  })
}

/**
 * 测试AI模型连接
 */
export function testModelConnectionAPI(modelId: number) {
  return request<{
    success: boolean
    message: string
    model?: string
    response_time?: number
  }>({
    url: `/ai/models/${modelId}/test`,
    method: 'post'
  })
}

/**
 * 获取会话列表
 */
export function getSessionsAPI() {
  return request({
    url: '/ai/sessions',
    method: 'get'
  })
}

/**
 * 创建会话
 */
export function createSessionAPI(data: { title: string; model?: string }) {
  return request({
    url: '/ai/sessions',
    method: 'post',
    data
  })
}

/**
 * 删除会话
 */
export function deleteSessionAPI(sessionId: number) {
  return request({
    url: `/ai/sessions/${sessionId}`,
    method: 'delete'
  })
}

