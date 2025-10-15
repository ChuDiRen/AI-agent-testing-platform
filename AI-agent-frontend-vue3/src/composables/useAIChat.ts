// Copyright (c) 2025 左岚. All rights reserved.
/**
 * AI聊天组合式函数 - 支持流式响应
 */
import { ref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chatAPI, chatStreamAPI, type ChatRequest, type ChatResponse } from '@/api/ai'

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  isStreaming?: boolean
}

export function useAIChat() {
  const messages: Ref<Message[]> = ref([])
  const isLoading = ref(false)
  const currentEventSource: Ref<EventSource | null> = ref(null)

  /**
   * 发送消息(流式)
   */
  const sendMessageStream = async (
    content: string,
    options: {
      sessionId?: number
      model?: string
      temperature?: number
      maxTokens?: number
    } = {}
  ): Promise<void> => {
    if (!content.trim()) return

    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(userMessage)

    // 创建AI消息占位符
    const aiMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true
    }
    messages.value.push(aiMessage)

    isLoading.value = true

    try {
      // 创建SSE连接
      const eventSource = chatStreamAPI({
        message: content,
        session_id: options.sessionId,
        model: options.model,
        temperature: options.temperature,
        max_tokens: options.maxTokens,
        stream: true
      })

      currentEventSource.value = eventSource

      // 监听消息事件
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.done) {
            // 流式传输完成
            aiMessage.isStreaming = false
            eventSource.close()
            currentEventSource.value = null
            isLoading.value = false
          } else if (data.content) {
            // 追加内容
            aiMessage.content += data.content
          } else if (data.error) {
            // 错误处理
            ElMessage.error(data.error)
            aiMessage.content = `错误: ${data.error}`
            aiMessage.isStreaming = false
            eventSource.close()
            currentEventSource.value = null
            isLoading.value = false
          }
        } catch (error) {
          console.error('解析SSE数据失败:', error)
        }
      }

      // 监听错误事件
      eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error)
        ElMessage.error('连接失败,请检查网络或稍后重试')
        aiMessage.content = '抱歉,连接出现问题,请重试'
        aiMessage.isStreaming = false
        eventSource.close()
        currentEventSource.value = null
        isLoading.value = false
      }

    } catch (error: any) {
      console.error('发送消息失败:', error)
      ElMessage.error(error.message || '发送失败')
      aiMessage.content = '抱歉,发送失败,请重试'
      aiMessage.isStreaming = false
      isLoading.value = false
    }
  }

  /**
   * 发送消息(非流式)
   */
  const sendMessage = async (
    content: string,
    options: {
      sessionId?: number
      model?: string
      temperature?: number
      maxTokens?: number
    } = {}
  ): Promise<void> => {
    if (!content.trim()) return

    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(userMessage)

    isLoading.value = true

    try {
      const response = await chatAPI({
        message: content,
        session_id: options.sessionId,
        model: options.model,
        temperature: options.temperature,
        max_tokens: options.maxTokens,
        stream: false
      })

      if (response.data) {
        const aiMessage: Message = {
          role: 'assistant',
          content: response.data.message.content,
          timestamp: new Date().toLocaleTimeString()
        }
        messages.value.push(aiMessage)
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
      ElMessage.error(error.message || '发送失败')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 停止流式传输
   */
  const stopStreaming = () => {
    if (currentEventSource.value) {
      currentEventSource.value.close()
      currentEventSource.value = null
      isLoading.value = false

      // 标记最后一条消息为非流式
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.isStreaming) {
        lastMessage.isStreaming = false
      }
    }
  }

  /**
   * 清空消息
   */
  const clearMessages = () => {
    messages.value = []
  }

  /**
   * 重新生成最后一条消息
   */
  const regenerateLastMessage = async (options: {
    sessionId?: number
    model?: string
    useStream?: boolean
  } = {}) => {
    // 找到最后一条用户消息
    const lastUserMessageIndex = messages.value.findLastIndex(m => m.role === 'user')
    if (lastUserMessageIndex === -1) return

    const lastUserMessage = messages.value[lastUserMessageIndex]

    // 删除该消息之后的所有消息
    messages.value = messages.value.slice(0, lastUserMessageIndex + 1)

    // 重新发送
    if (options.useStream !== false) {
      await sendMessageStream(lastUserMessage.content, options)
    } else {
      await sendMessage(lastUserMessage.content, options)
    }
  }

  return {
    messages,
    isLoading,
    sendMessage,
    sendMessageStream,
    stopStreaming,
    clearMessages,
    regenerateLastMessage
  }
}

