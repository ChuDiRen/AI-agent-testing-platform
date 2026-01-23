import { defineStore } from 'pinia'
import { askQuestion, getChatHistory, clearChatHistory } from '../api/chat'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    conversationId: null,
    isLoading: false,
    conversations: [], // 会话列表
    currentConversation: null
  }),

  getters: {
    lastMessage: (state) => state.messages[state.messages.length - 1],
    messageCount: (state) => state.messages.length,
    hasMessages: (state) => state.messages.length > 0
  },

  actions: {
    addMessage(message) {
      this.messages.push({
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString(),
        ...message
      })
    },

    addUserMessage(content) {
      this.addMessage({
        role: 'user',
        content
      })
    },

    addAssistantMessage(content, citations = null) {
      this.addMessage({
        role: 'assistant',
        content,
        citations
      })
    },

    setConversationId(id) {
      this.conversationId = id
    },

    clearMessages() {
      this.messages = []
    },

    setLoading(loading) {
      this.isLoading = loading
    },

    async sendMessage(content) {
      if (!content.trim()) return

      this.addUserMessage(content)
      this.setLoading(true)

      try {
        const response = await askQuestion({
          message: content,
          conversation_id: this.conversationId
        })

        if (response.code === 0) {
          const { answer, citations, session_id } = response.data
          
          // 设置会话ID
          if (session_id && !this.conversationId) {
            this.setConversationId(session_id)
          }

          // 添加助手回复
          this.addAssistantMessage(answer, citations)
          
          return {
            success: true,
            data: response.data
          }
        } else {
          throw new Error(response.message || '发送消息失败')
        }
      } catch (error) {
        console.error('发送消息失败:', error)
        
        // 添加错误消息
        this.addAssistantMessage('抱歉，发送消息时出现错误，请稍后重试。')
        
        return {
          success: false,
          error: error.message
        }
      } finally {
        this.setLoading(false)
      }
    },

    async loadChatHistory(conversationId) {
      if (!conversationId) return

      try {
        const response = await getChatHistory(conversationId)
        
        if (response.success) {
          this.messages = response.data.messages || []
          this.setConversationId(conversationId)
        }
      } catch (error) {
        console.error('加载聊天历史失败:', error)
      }
    },

    async clearHistory(conversationId) {
      try {
        const response = await clearChatHistory(conversationId)
        
        if (response.success) {
          this.clearMessages()
        }
        
        return response
      } catch (error) {
        console.error('清除聊天历史失败:', error)
        return {
          success: false,
          error: error.message
        }
      }
    },

    updateMessageFeedback(messageId, feedback) {
      const message = this.messages.find(msg => msg.id === messageId)
      if (message) {
        message.feedback = feedback
      }
    },

    // 创建新会话
    createNewConversation() {
      this.clearMessages()
      this.setConversationId(null)
      this.currentConversation = null
    },

    // 设置当前会话
    setCurrentConversation(conversation) {
      this.currentConversation = conversation
      this.setConversationId(conversation.id)
      this.loadChatHistory(conversation.id)
    }
  }
})
