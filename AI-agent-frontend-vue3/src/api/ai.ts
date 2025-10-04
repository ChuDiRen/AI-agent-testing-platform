// Copyright (c) 2025 左岚. All rights reserved.
/**
 * AI助手 API
 */
import { get, post, put, del } from './request'

export interface ChatMessage {
  message_id: number
  session_id: number
  role: string // user/assistant/system
  content: string
  tokens?: number
  model?: string
  created_at: string
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

/**
 * AI聊天
 */
export function chat(data: ChatRequest) {
  return post<{ success: boolean; data: ChatResponse }>('/api/v1/ai/chat', data)
}

/**
 * 创建聊天会话
 */
export function createChatSession(data: { title?: string; model?: string; system_prompt?: string }) {
  return post<{ success: boolean; message: string; data: ChatSession }>('/api/v1/ai/sessions', data)
}

/**
 * 获取用户的所有会话
 */
export function getChatSessions() {
  return get<{ success: boolean; data: ChatSession[] }>('/api/v1/ai/sessions')
}

/**
 * 获取会话详情
 */
export function getChatSessionDetail(sessionId: number) {
  return get<{ success: boolean; data: ChatSessionDetail }>(`/api/v1/ai/sessions/${sessionId}`)
}

/**
 * 更新会话
 */
export function updateChatSession(sessionId: number, data: { title?: string; model?: string; is_active?: boolean }) {
  return put<{ success: boolean; message: string; data: ChatSession }>(`/api/v1/ai/sessions/${sessionId}`, data)
}

/**
 * 删除会话
 */
export function deleteChatSession(sessionId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/ai/sessions/${sessionId}`)
}

/**
 * AI生成测试用例
 */
export function generateTestCases(data: TestCaseGenerateRequest) {
  return post<{ success: boolean; message: string; data: { testcases: any[]; total: number } }>('/api/v1/ai/generate-testcases', data)
}

/**
 * 获取可用的AI模型列表
 */
export function getAIModels() {
  return get<{ success: boolean; data: AIModel[] }>('/api/v1/ai/models')
}

/**
 * AI服务健康检查
 */
export function aiHealthCheck() {
  return get<{ success: boolean; data: { status: string; service: string; version: string } }>('/api/v1/ai/health')
}

