<script setup>
import { h, onMounted, ref, nextTick, computed } from 'vue'
import {
  NButton,
  NInput,
  NCard,
  NSpace,
  NAvatar,
  NSpin,
  NEmpty,
  NSelect,
  NTag,
  NPopover,
  NScrollbar,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import { formatDate, renderIcon } from '@/utils'
import { useUserStore } from '@/store'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: 'AI对话' })

const userStore = useUserStore()
const loading = ref(false)
const sending = ref(false)
const messageInput = ref('')
const messages = ref([])
const chatSessions = ref([])
const currentSessionId = ref(null)
const scrollbarRef = ref(null)

// AI代理选项
const agentOptions = ref([])
const selectedAgentId = ref(null)

// 当前会话
const currentSession = computed(() => {
  return chatSessions.value.find(s => s.id === currentSessionId.value)
})

// 加载聊天会话列表
async function loadChatSessions() {
  try {
    const response = await api.getChatSessionList({ page: 1, page_size: 50 })
    if (response.data?.items) {
      chatSessions.value = response.data.items
      // 默认选择第一个会话
      if (chatSessions.value.length > 0 && !currentSessionId.value) {
        currentSessionId.value = chatSessions.value[0].id
        await loadMessages(currentSessionId.value)
      }
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

// 加载AI代理选项
async function loadAgents() {
  try {
    const response = await api.getAgentList({ 
      page: 1, 
      page_size: 100, 
      status: 'active',
      type: 'chat' 
    })
    if (response.data?.items) {
      agentOptions.value = response.data.items.map(agent => ({
        label: agent.name,
        value: agent.id,
      }))
      // 默认选择第一个代理
      if (agentOptions.value.length > 0 && !selectedAgentId.value) {
        selectedAgentId.value = agentOptions.value[0].value
      }
    }
  } catch (error) {
    console.error('加载AI代理失败:', error)
  }
}

// 加载消息历史
async function loadMessages(sessionId) {
  try {
    loading.value = true
    const response = await api.getChatMessages(sessionId, { page: 1, page_size: 100 })
    if (response.data?.items) {
      messages.value = response.data.items.sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
      )
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载消息失败:', error)
    $message.error('加载消息失败')
  } finally {
    loading.value = false
  }
}

// 创建新会话
async function handleNewSession() {
  if (!selectedAgentId.value) {
    $message.warning('请先选择AI代理')
    return
  }

  try {
    const response = await api.createChatSession({
      agent_id: selectedAgentId.value,
      title: `会话 ${new Date().toLocaleString()}`,
    })
    if (response.data) {
      chatSessions.value.unshift(response.data)
      currentSessionId.value = response.data.id
      messages.value = []
      $message.success('新会话创建成功')
    }
  } catch (error) {
    console.error('创建会话失败:', error)
    $message.error('创建会话失败')
  }
}

// 切换会话
async function handleSwitchSession(sessionId) {
  currentSessionId.value = sessionId
  await loadMessages(sessionId)
}

// 发送消息
async function handleSendMessage() {
  if (!messageInput.value.trim()) {
    return
  }

  if (!currentSessionId.value) {
    await handleNewSession()
    if (!currentSessionId.value) return
  }

  const userMessage = {
    id: Date.now(),
    session_id: currentSessionId.value,
    role: 'user',
    content: messageInput.value,
    created_at: new Date().toISOString(),
  }

  messages.value.push(userMessage)
  const messageContent = messageInput.value
  messageInput.value = ''

  await nextTick()
  scrollToBottom()

  try {
    sending.value = true
    const response = await api.sendChatMessage(currentSessionId.value, {
      content: messageContent,
      agent_id: selectedAgentId.value,
    })

    if (response.data) {
      const assistantMessage = {
        id: response.data.id || Date.now() + 1,
        session_id: currentSessionId.value,
        role: 'assistant',
        content: response.data.content,
        created_at: response.data.created_at || new Date().toISOString(),
      }
      messages.value.push(assistantMessage)
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    $message.error('发送消息失败')
    // 移除用户消息
    messages.value = messages.value.filter(m => m.id !== userMessage.id)
  } finally {
    sending.value = false
  }
}

// 删除会话
async function handleDeleteSession(sessionId) {
  try {
    await api.deleteChatSession(sessionId)
    chatSessions.value = chatSessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      messages.value = []
      if (chatSessions.value.length > 0) {
        await handleSwitchSession(chatSessions.value[0].id)
      }
    }
    $message.success('会话删除成功')
  } catch (error) {
    console.error('删除会话失败:', error)
    $message.error('删除会话失败')
  }
}

// 滚动到底部
function scrollToBottom() {
  if (scrollbarRef.value) {
    scrollbarRef.value.scrollTo({ top: scrollbarRef.value.scrollHeight, behavior: 'smooth' })
  }
}

// 处理Enter键发送
function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSendMessage()
  }
}

onMounted(() => {
  loadAgents()
  loadChatSessions()
})
</script>

<template>
  <CommonPage show-footer title="AI对话" class="chat-page">
    <div class="chat-container">
      <!-- 左侧会话列表 -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <NButton type="primary" block @click="handleNewSession">
            <template #icon>
              <TheIcon icon="mdi:plus" :size="18" />
            </template>
            新建对话
          </NButton>
        </div>

        <div class="sidebar-content">
          <NScrollbar style="max-height: calc(100vh - 200px)">
            <div
              v-for="session in chatSessions"
              :key="session.id"
              class="session-item"
              :class="{ active: session.id === currentSessionId }"
              @click="handleSwitchSession(session.id)"
            >
              <div class="session-info">
                <div class="session-title">{{ session.title || '未命名会话' }}</div>
                <div class="session-time">{{ formatDate(session.updated_at || session.created_at) }}</div>
              </div>
              <NButton
                text
                type="error"
                size="small"
                @click.stop="handleDeleteSession(session.id)"
              >
                <TheIcon icon="mdi:delete" :size="16" />
              </NButton>
            </div>
          </NScrollbar>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <div class="chat-header">
          <NSpace align="center">
            <span class="text-lg font-bold">{{ currentSession?.title || 'AI对话' }}</span>
            <NSelect
              v-model:value="selectedAgentId"
              :options="agentOptions"
              placeholder="选择AI代理"
              style="width: 200px"
              size="small"
            />
          </NSpace>
        </div>

        <div class="chat-messages">
          <NSpin :show="loading">
            <NScrollbar ref="scrollbarRef" style="height: calc(100vh - 320px)">
              <div v-if="messages.length === 0" class="empty-state">
                <NEmpty description="暂无消息，开始对话吧！" />
              </div>
              <div v-else class="messages-list">
                <div
                  v-for="message in messages"
                  :key="message.id"
                  class="message-item"
                  :class="message.role"
                >
                  <NAvatar
                    :size="36"
                    round
                    :src="message.role === 'user' ? userStore.avatar : undefined"
                  >
                    <TheIcon
                      v-if="message.role === 'assistant'"
                      icon="mdi:robot"
                      :size="24"
                    />
                  </NAvatar>
                  <div class="message-content">
                    <div class="message-header">
                      <span class="message-role">
                        {{ message.role === 'user' ? userStore.name || '用户' : 'AI助手' }}
                      </span>
                      <span class="message-time">{{ formatDate(message.created_at) }}</span>
                    </div>
                    <div class="message-text">{{ message.content }}</div>
                  </div>
                </div>
              </div>
            </NScrollbar>
          </NSpin>
        </div>

        <div class="chat-input">
          <NInput
            v-model:value="messageInput"
            type="textarea"
            placeholder="输入消息... (Shift + Enter 换行, Enter 发送)"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :disabled="sending"
            @keydown="handleKeyDown"
          />
          <div class="input-actions">
            <NButton
              type="primary"
              :loading="sending"
              :disabled="!messageInput.trim() || sending"
              @click="handleSendMessage"
            >
              <template #icon>
                <TheIcon icon="mdi:send" :size="18" />
              </template>
              发送
            </NButton>
          </div>
        </div>
      </div>
    </div>
  </CommonPage>
</template>

<style scoped>
.chat-page {
  height: 100vh;
  overflow: hidden;
}

.chat-container {
  display: flex;
  height: calc(100vh - 120px);
  gap: 16px;
}

.chat-sidebar {
  width: 280px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  margin-bottom: 16px;
}

.sidebar-content {
  flex: 1;
  overflow: hidden;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.session-item:hover {
  background: #f5f5f5;
}

.session-item.active {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.session-title {
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 12px;
  color: #999;
}

.chat-main {
  flex: 1;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chat-messages {
  flex: 1;
  overflow: hidden;
  padding: 16px 20px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.message-role {
  font-weight: 500;
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f5f5f5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-item.user .message-text {
  background: #1890ff;
  color: white;
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>

