<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>智能问答</h2>
      <div class="header-actions">
        <el-button type="info" plain :icon="Refresh" circle @click="refreshHistory" :loading="refreshing" />
        <el-button type="warning" plain :icon="Delete" @click="clearHistory" :loading="clearing" />
        <el-dropdown @command="handleCommand">
          <el-button type="primary" plain :icon="Setting">
            设置
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="new-chat">新建对话</el-dropdown-item>
              <el-dropdown-item command="export">导出对话</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="messages" ref="messagesRef">
      <div v-if="!chatStore.hasMessages" class="empty-state">
        <el-empty description="开始您的第一次对话吧">
          <template #image>
            <el-icon size="80" color="#409eff"><ChatDotRound /></el-icon>
          </template>
        </el-empty>
      </div>
      
      <ChatMessage
        v-for="message in chatStore.messages"
        :key="message.id"
        :message="message"
        @feedback="handleFeedback"
      />
      
      <div v-if="chatStore.isLoading" class="typing-indicator">
        <div class="message assistant">
          <div class="avatar">
            <el-avatar :icon="Avatar" />
          </div>
          <div class="content">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <div class="input-container">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="3"
          :maxlength="2000"
          show-word-limit
          placeholder="请输入您的问题... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="sendMessage"
          @keydown.meta.enter="sendMessage"
          :disabled="chatStore.isLoading"
        />
        
        <div class="input-actions">
          <el-button
            type="primary"
            @click="sendMessage"
            :disabled="!userInput.trim() || chatStore.isLoading"
            :loading="chatStore.isLoading"
          >
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
      
      <div class="quick-actions">
        <el-text size="small" type="info">
          提示：您可以询问关于文档内容、技术问题、流程说明等
        </el-text>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete, Setting, ChatDotRound, Avatar } from '@element-plus/icons-vue'
import { useChatStore } from '../store/chat'
import { useAuthStore } from '../store/auth'
import ChatMessage from '../components/ChatMessage.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()

const messagesRef = ref(null)
const userInput = ref('')
const refreshing = ref(false)
const clearing = ref(false)

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || chatStore.isLoading) return

  userInput.value = ''
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })

  try {
    await chatStore.sendMessage(message)
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    ElMessage.error('发送消息失败，请稍后重试')
  }
}

const scrollToBottom = () => {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const refreshHistory = async () => {
  refreshing.value = true
  try {
    if (chatStore.conversationId) {
      await chatStore.loadChatHistory(chatStore.conversationId)
      ElMessage.success('历史记录刷新成功')
    } else {
      ElMessage.info('当前没有会话历史')
    }
  } catch (error) {
    ElMessage.error('刷新历史记录失败')
  } finally {
    refreshing.value = false
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前对话历史吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    clearing.value = true
    
    if (chatStore.conversationId) {
      await chatStore.clearHistory(chatStore.conversationId)
    } else {
      chatStore.clearMessages()
    }
    
    ElMessage.success('对话历史已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空历史记录失败')
    }
  } finally {
    clearing.value = false
  }
}

const handleCommand = async (command) => {
  switch (command) {
    case 'new-chat':
      chatStore.createNewConversation()
      ElMessage.success('新对话已创建')
      break
    case 'export':
      await exportChatHistory()
      break
  }
}

const exportChatHistory = async () => {
  if (!chatStore.hasMessages) {
    ElMessage.info('没有可导出的对话内容')
    return
  }

  try {
    const content = chatStore.messages.map(msg => {
      const time = new Date(msg.timestamp).toLocaleString('zh-CN')
      const role = msg.role === 'user' ? '用户' : '助手'
      return `[${time}] ${role}:\n${msg.content}\n`
    }).join('\n---\n\n')

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-history-${new Date().toISOString().slice(0, 10)}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success('对话历史导出成功')
  } catch (error) {
    ElMessage.error('导出对话历史失败')
  }
}

const handleFeedback = async ({ messageId, feedback }) => {
  try {
    // 这里可以调用反馈API
    chatStore.updateMessageFeedback(messageId, feedback)
    
    const feedbackText = feedback === 'like' ? '有帮助' : '没帮助'
    ElMessage.success(`感谢您的反馈：${feedbackText}`)
  } catch (error) {
    ElMessage.error('提交反馈失败')
  }
}

onMounted(() => {
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.typing-indicator {
  margin-bottom: 20px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.input-area {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 20px;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-container .el-textarea {
  flex: 1;
}

.input-actions {
  flex-shrink: 0;
}

.quick-actions {
  margin-top: 8px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .messages {
    padding: 16px;
  }
  
  .input-area {
    padding: 16px;
  }
  
  .input-container {
    flex-direction: column;
    gap: 8px;
  }
  
  .input-actions {
    width: 100%;
  }
  
  .input-actions .el-button {
    width: 100%;
  }
}
</style>
