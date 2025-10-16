<template>
  <div class="ai-chat-interface">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <span class="app-name">🤖 AI测试助手</span>
      </div>
      <div class="toolbar-center">
        <el-select v-model="currentModel" placeholder="选择模型" size="small" style="width: 200px">
          <el-option v-for="model in enabledModels" :key="model.id" :label="model.model_name" :value="model.id" />
        </el-select>
        <el-tag type="success" size="small" style="margin-left: 10px">{{ currentTestType }}</el-tag>
      </div>
      <div class="toolbar-right">
        <el-button @click="showSettings" type="primary" size="small">新对话</el-button>
      </div>
    </div>

    <!-- 主体布局 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-button type="primary" style="width: 100%" @click="createNewConversation">
            <el-icon><Plus /></el-icon> 新对话
          </el-button>
        </div>
        <div class="conversation-list">
          <div v-for="conv in conversations" :key="conv.id" class="conversation-item" 
            :class="{ active: conv.id === currentConversationId }" @click="switchConversation(conv.id)">
            <span class="conv-title">{{ conv.session_title }}</span>
            <span class="conv-count">{{ conv.message_count }}</span>
          </div>
        </div>
      </div>

      <!-- 对话区域 -->
      <div class="chat-area">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">🚀</div>
            <h2>欢迎使用AI测试用例生成助手</h2>
            <p>请告诉我你的测试需求，我将为你生成专业的测试用例</p>
          </div>

          <div v-for="(message, idx) in messages" :key="idx" class="message" :class="message.role">
            <div class="message-bubble">
              <div class="message-text">{{ message.content }}</div>
              <div v-if="message.test_cases && message.test_cases.length > 0" class="test-cases-section">
                <div v-for="(tc, tcIdx) in message.test_cases" :key="tcIdx" class="test-case-card">
                  <div class="card-header">
                    <el-tag :type="getPriorityType(tc.priority)">{{ tc.priority }}</el-tag>
                    <span class="case-name">{{ tc.case_name }}</span>
                  </div>
                  <div class="card-body">
                    <div v-if="tc.precondition" class="case-section">
                      <strong>前置条件：</strong>{{ tc.precondition }}
                    </div>
                    <div v-if="tc.test_steps" class="case-section">
                      <strong>测试步骤：</strong>
                      <ol v-if="typeof tc.test_steps === 'string'" v-html="tc.test_steps"></ol>
                      <ol v-else>
                        <li v-for="(step, sIdx) in tc.test_steps" :key="sIdx">{{ step }}</li>
                      </ol>
                    </div>
                    <div v-if="tc.expected_result" class="case-section">
                      <strong>预期结果：</strong>{{ tc.expected_result }}
                    </div>
                  </div>
                  <div class="card-footer">
                    <el-button size="small" @click="saveTestCase(tc)">保存</el-button>
                  </div>
                </div>
              </div>
              <div v-if="message.isGenerating" class="generating">
                <el-icon class="rotating"><Loading /></el-icon> 生成中...
              </div>
              <span class="msg-time">{{ formatTime(message.create_time) }}</span>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-box">
            <el-input v-model="userInput" type="textarea" :rows="3" placeholder="输入你的测试需求..." 
              :disabled="isGenerating" @keydown.enter="handleEnter" />
            <el-button type="primary" :loading="isGenerating" @click="sendMessage" class="send-button">
              {{ isGenerating ? '生成中...' : '发送' }}
            </el-button>
          </div>
          <div class="input-hints">
            <el-select v-model="caseFormat" size="small" style="width: 100px">
              <el-option label="JSON" value="JSON" />
              <el-option label="YAML" value="YAML" />
            </el-select>
            <el-input-number v-model="caseCount" :min="1" :max="20" size="small" style="margin-left: 10px; width: 80px" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading } from '@element-plus/icons-vue'

// 状态管理
const currentConversationId = ref(null)
const conversations = ref([])
const messages = ref([])
const userInput = ref('')
const isGenerating = ref(false)
const currentModel = ref(null)
const currentTestType = ref('API')
const caseFormat = ref('JSON')
const caseCount = ref(10)
const messagesContainer = ref(null)
const enabledModels = ref([])

// 模拟数据
const initializeMockData = () => {
  enabledModels.value = [
    { id: 1, model_name: 'DeepSeek-Chat', provider: 'DeepSeek' },
    { id: 2, model_name: '通义千问', provider: '阿里云' }
  ]
  currentModel.value = 1
  
  conversations.value = [
    { id: 1, session_title: 'API登录测试', model_id: 1, message_count: 5, test_case_count: 3, status: 'active' }
  ]
  currentConversationId.value = 1
}

onMounted(() => {
  initializeMockData()
})

// 方法
const createNewConversation = async () => {
  const newId = Math.max(...conversations.value.map(c => c.id)) + 1
  const newConv = {
    id: newId,
    session_title: `新对话_${new Date().toLocaleTimeString()}`,
    model_id: currentModel.value,
    message_count: 0,
    test_case_count: 0,
    status: 'active'
  }
  conversations.value.unshift(newConv)
  switchConversation(newId)
  ElMessage.success('创建新对话成功')
}

const switchConversation = (convId) => {
  currentConversationId.value = convId
  messages.value = []
  scrollToBottom()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isGenerating.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value,
    create_time: new Date()
  })

  const messageContent = userInput.value
  userInput.value = ''
  isGenerating.value = true

  try {
    // 模拟生成AI回复
    await new Promise(resolve => setTimeout(resolve, 1000))

    const mockTestCases = [
      {
        case_name: '用户登录成功测试',
        priority: 'P0',
        precondition: '用户已注册',
        test_steps: ['输入正确用户名', '输入正确密码', '点击登录'],
        expected_result: '返回200，登录成功'
      }
    ]

    messages.value.push({
      role: 'assistant',
      content: `已为你生成${mockTestCases.length}个测试用例`,
      test_cases: mockTestCases,
      create_time: new Date(),
      isGenerating: false
    })

    ElMessage.success('生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    isGenerating.value = false
    scrollToBottom()
  }
}

const handleEnter = (e) => {
  if (e.shiftKey) return
  e.preventDefault()
  sendMessage()
}

const saveTestCase = (testCase) => {
  ElMessage.success('测试用例已保存')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleTimeString()
}

const getPriorityType = (priority) => {
  const typeMap = { 'P0': 'danger', 'P1': 'warning', 'P2': 'info', 'P3': 'success' }
  return typeMap[priority] || 'info'
}

const showSettings = () => {
  ElMessage.info('设置功能')
}
</script>

<style scoped>
.ai-chat-interface {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.top-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #ddd;
}

.app-name {
  font-size: 18px;
  font-weight: bold;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 10px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.conversation-item.active {
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.conv-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-count {
  color: #999;
  font-size: 12px;
  margin-left: 5px;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.user .message-bubble {
  background: #2196f3;
  color: white;
  max-width: 70%;
}

.message.assistant .message-bubble {
  background: #f0f0f0;
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-text {
  margin-bottom: 8px;
}

.test-cases-section {
  margin-top: 12px;
}

.test-case-card {
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.case-name {
  font-weight: bold;
}

.case-section {
  margin-bottom: 8px;
  font-size: 12px;
}

.card-footer {
  text-align: right;
  margin-top: 8px;
}

.msg-time {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #ddd;
  background: white;
}

.input-box {
  display: flex;
  gap: 10px;
}

.send-button {
  min-width: 80px;
}

.input-hints {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  align-items: center;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
