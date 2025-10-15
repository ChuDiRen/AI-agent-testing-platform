// Copyright (c) 2025 左岚. All rights reserved.
/**
 * AI助手 API - 统一模块
 * 支持流式和非流式响应、会话管理、模型管理、测试用例生成
 */
import request from './request'

// ==================== 类型定义 ====================

export interface ChatMessage {
  message_id?: number
  session_id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens?: number
  model?: string
  created_at?: string
}

export interface ChatSession {
  session_id: number
  user_id: number
  title: string
  model: string
  system_prompt?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[]
  context?: any
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
  message: ChatMessage
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

export interface TestCaseGenerateRequest {
  requirement: string
  test_type: string
  module?: string
  count: number
}

// ==================== 非流式AI接口 ====================

/**
 * AI聊天（非流式）
 */
export function chatAPI(data: ChatRequest) {
  return request<ChatResponse>({
    url: '/api/v1/ai/chat',
    method: 'post',
    data: { ...data, stream: false }
  })
}

/**
 * AI聊天（兼容旧接口）
 * @deprecated 请使用 chatAPI
 */
export function chat(data: ChatRequest) {
  return chatAPI(data)
}

// ==================== 流式AI接口 ====================

/**
 * AI聊天（流式）- 返回EventSource
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

  return eventSource
}

// ==================== 会话管理 ====================

/**
 * 创建聊天会话
 */
export function createChatSession(data: { title?: string; model?: string; system_prompt?: string }) {
  return request<ChatSession>({
    url: '/api/v1/ai/sessions',
    method: 'post',
    data
  })
}

/**
 * 获取用户的所有会话
 */
export function getChatSessions() {
  return request<ChatSession[]>({
    url: '/api/v1/ai/sessions',
    method: 'get'
  })
}

/**
 * 获取会话详情
 */
export function getChatSessionDetail(sessionId: number) {
  return request<ChatSessionDetail>({
    url: `/api/v1/ai/sessions/${sessionId}`,
    method: 'get'
  })
}

/**
 * 更新会话
 */
export function updateChatSession(sessionId: number, data: { title?: string; model?: string; is_active?: boolean }) {
  return request<ChatSession>({
    url: `/api/v1/ai/sessions/${sessionId}`,
    method: 'put',
    data
  })
}

/**
 * 删除会话
 */
export function deleteChatSession(sessionId: number) {
  return request({
    url: `/api/v1/ai/sessions/${sessionId}`,
    method: 'delete'
  })
}

/**
 * 获取会话列表（兼容旧接口）
 * @deprecated 请使用 getChatSessions
 */
export function getSessionsAPI() {
  return getChatSessions()
}

/**
 * 创建会话（兼容旧接口）
 * @deprecated 请使用 createChatSession
 */
export function createSessionAPI(data: { title: string; model?: string }) {
  return createChatSession(data)
}

/**
 * 删除会话（兼容旧接口）
 * @deprecated 请使用 deleteChatSession
 */
export function deleteSessionAPI(sessionId: number) {
  return deleteChatSession(sessionId)
}

// ==================== 模型管理 ====================

/**
 * 获取可用AI模型列表
 */
export function getAIModels() {
  return request<AIModel[]>({
    url: '/api/v1/ai/models',
    method: 'get'
  })
}

/**
 * 获取可用AI模型列表（兼容旧接口）
 * @deprecated 请使用 getAIModels
 */
export function getModelsAPI() {
  return getAIModels()
}

/**
 * 创建AI模型
 */
export function createModelAPI(data: Partial<AIModel>) {
  return request<AIModel>({
    url: '/api/v1/ai/models',
    method: 'post',
    data
  })
}

/**
 * 更新AI模型
 */
export function updateModelAPI(modelId: number, data: Partial<AIModel>) {
  return request<AIModel>({
    url: `/api/v1/ai/models/${modelId}`,
    method: 'put',
    data
  })
}

/**
 * 删除AI模型
 */
export function deleteModelAPI(modelId: number) {
  return request({
    url: `/api/v1/ai/models/${modelId}`,
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
    url: `/api/v1/ai/models/${modelId}/test`,
    method: 'post'
  })
}

// ==================== 测试用例生成 ====================

/**
 * AI生成测试用例
 */
export function generateTestCases(data: TestCaseGenerateRequest) {
  return request<{
    testcases: any[]
    total: number
  }>({
    url: '/api/v1/ai/generate-testcases',
    method: 'post',
    data
  })
}

/**
 * AI生成测试用例（兼容旧接口）
 * @deprecated 请使用 generateTestCases
 */
export function generateTestCasesAPI(data: TestCaseGenerateRequest) {
  return generateTestCases(data)
}

/**
 * 批量保存AI生成的测试用例
 */
export function saveGeneratedTestCasesAPI(testcases: any[]) {
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

// ==================== 健康检查 ====================

/**
 * AI服务健康检查
 */
export function aiHealthCheck() {
  return request<{ status: string; service: string; version: string }>({
    url: '/api/v1/ai/health',
    method: 'get'
  })
}

