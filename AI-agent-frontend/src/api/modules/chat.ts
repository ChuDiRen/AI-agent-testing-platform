// AI聊天管理API
import { http } from '@/api/http'

// 聊天消息接口
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

// 聊天请求接口
export interface ChatRequest {
  large_model_id: number
  messages: ChatMessage[]
  temperature?: number
  max_tokens?: number
  stream?: boolean
  session_id?: string
}

// 聊天响应接口
export interface ChatResponse {
  content: string
  tokens_used: number
  cost: number
  response_time: number
  metadata: Record<string, any>
}

// 聊天会话接口
export interface ChatSession {
  session_id: string
  title: string
  large_model_id: number
  system_prompt?: string
  created_at: string
  updated_at: string
  message_count: number
  last_message?: {
    content: string
    role: string
    created_at: string
  }
}

// 创建会话请求
export interface CreateSessionRequest {
  title?: string
  large_model_id: number
  system_prompt?: string
}

// 更新会话请求
export interface UpdateSessionRequest {
  title?: string
  system_prompt?: string
}

// 会话消息
export interface SessionMessage {
  id: number
  role: string
  content: string
  metadata?: Record<string, any>
  created_at: string
}

export const chatApi = {
  /**
   * 创建聊天会话
   */
  createSession(data: CreateSessionRequest) {
    return http.post<{ success: boolean; message: string; data: ChatSession }>(
      '/chat/sessions',
      data,
    )
  },

  /**
   * 获取用户聊天会话列表
   */
  getSessions(page: number = 1, pageSize: number = 20) {
    return http.get<{
      success: boolean
      message: string
      data: {
        sessions: ChatSession[]
        total: number
        page: number
        page_size: number
        total_pages: number
      }
    }>('/chat/sessions', { params: { page, page_size: pageSize } })
  },

  /**
   * 获取聊天会话详情
   */
  getSession(sessionId: string) {
    return http.get<{ success: boolean; message: string; data: ChatSession }>(
      `/chat/sessions/${sessionId}`,
    )
  },

  /**
   * 更新聊天会话
   */
  updateSession(sessionId: string, data: UpdateSessionRequest) {
    return http.put<{ success: boolean; message: string; data: ChatSession }>(
      `/chat/sessions/${sessionId}`,
      data,
    )
  },

  /**
   * 删除聊天会话
   */
  deleteSession(sessionId: string) {
    return http.delete<{ success: boolean; message: string }>(`/chat/sessions/${sessionId}`)
  },

  /**
   * 发送聊天消息
   */
  sendMessage(data: ChatRequest) {
    return http.post<{ success: boolean; message: string; data: ChatResponse }>('/chat', data)
  },

  /**
   * 发送流式聊天消息
   */
  sendStreamMessage(data: ChatRequest) {
    return fetch(`${http.defaults.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      body: JSON.stringify({ ...data, stream: true }),
    })
  },

  /**
   * 获取会话消息历史
   */
  getSessionMessages(sessionId: string, page: number = 1, pageSize: number = 50) {
    return http.get<{
      success: boolean
      message: string
      data: {
        messages: SessionMessage[]
        total: number
        page: number
        page_size: number
        total_pages: number
      }
    }>(`/chat/sessions/${sessionId}/messages`, {
      params: { page, page_size: pageSize },
    })
  },

  /**
   * 清空会话消息
   */
  clearSessionMessages(sessionId: string) {
    return http.delete<{ success: boolean; message: string }>(
      `/chat/sessions/${sessionId}/messages`,
    )
  },

  /**
   * 获取可用的AI模型列表
   */
  getAvailableModels() {
    return http.get<{
      success: boolean
      message: string
      data: {
        models: Array<{
          id: number
          name: string
          display_name: string
          provider: string
          model_type: string
          status: string
          max_tokens: number
          temperature: number
        }>
      }
    }>('/model-configs')
  },

  /**
   * 测试模型连接
   */
  testModel(modelId: number, testPrompt?: string) {
    return http.post<{
      success: boolean
      message: string
      data: {
        test_id: string
        model_id: number
        test_prompt: string
        response_text?: string
        tokens_used: number
        response_time: number
        cost: number
        success: boolean
        error_message?: string
        tested_at: string
      }
    }>(`/model-configs/${modelId}/test`, {
      test_prompt: testPrompt || 'Hello, please respond with "Test successful"',
      test_config: {},
    })
  },
}

// 聊天工具函数
export const chatUtils = {
  /**
   * 格式化消息时间
   */
  formatMessageTime(timeStr: string): string {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  },

  /**
   * 格式化消息内容（简单的markdown渲染）
   */
  formatMessageContent(content: string): string {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/\n/g, '<br>')
  },

  /**
   * 复制文本到剪贴板
   */
  async copyToClipboard(text: string): Promise<boolean> {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch (error) {
      console.error('Failed to copy text:', error)
      return false
    }
  },

  /**
   * 计算消息token数量（估算）
   */
  estimateTokens(text: string): number {
    // 简单估算：中文字符按2个token计算，英文单词按1个token计算
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length
    const englishWords = (text.match(/[a-zA-Z]+/g) || []).length
    const otherChars = text.length - chineseChars - englishWords

    return chineseChars * 2 + englishWords + Math.ceil(otherChars / 4)
  },

  /**
   * 生成会话标题
   */
  generateSessionTitle(firstMessage: string): string {
    const maxLength = 20
    const cleaned = firstMessage.replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s]/g, '').trim()

    if (cleaned.length <= maxLength) {
      return cleaned || '新对话'
    }

    return cleaned.substring(0, maxLength) + '...'
  },

  /**
   * 验证消息内容
   */
  validateMessage(content: string): { valid: boolean; error?: string } {
    if (!content || !content.trim()) {
      return { valid: false, error: '消息内容不能为空' }
    }

    if (content.length > 10000) {
      return { valid: false, error: '消息内容过长，请控制在10000字符以内' }
    }

    return { valid: true }
  },

  /**
   * 处理流式响应
   */
  async handleStreamResponse(
    response: Response,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: string) => void,
  ) {
    if (!response.body) {
      onError('响应体为空')
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          onComplete()
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)

            if (data === '[DONE]') {
              onComplete()
              return
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.type === 'chunk' && parsed.content) {
                onChunk(parsed.content)
              } else if (parsed.type === 'error') {
                onError(parsed.error || '未知错误')
                return
              }
            } catch (e) {
              // 忽略解析错误，可能是不完整的数据
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : '流式响应处理失败')
    } finally {
      reader.releaseLock()
    }
  },
}
