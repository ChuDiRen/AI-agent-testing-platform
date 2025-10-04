<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="ai-chat-container">
    <el-card class="chat-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 助手</span>
            <el-tag type="success" size="small" v-if="isOnline">在线</el-tag>
            <el-tag type="info" size="small" v-else>离线</el-tag>
          </div>
          <div class="header-actions">
            <el-dropdown @command="handleCommand">
              <el-button text>
                <el-icon><Setting /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="clear">清空对话</el-dropdown-item>
                  <el-dropdown-item command="export">导出对话</el-dropdown-item>
                  <el-dropdown-item command="settings">设置</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <div class="chat-content">
        <!-- 消息列表 -->
        <div class="message-list" ref="messageListRef">
          <el-empty v-if="messages.length === 0" description="开始与AI助手对话吧">
            <el-button type="primary" @click="showQuickStart">快速开始</el-button>
          </el-empty>

          <div v-for="(message, index) in messages" :key="index" class="message-item" :class="message.role">
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :src="userAvatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar v-else class="ai-avatar">
                <el-icon><Service /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-name">{{ message.role === 'user' ? '我' : 'AI 助手' }}</span>
                <span class="message-time">{{ message.timestamp }}</span>
              </div>
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div class="message-actions" v-if="message.role === 'assistant'">
                <el-button link size="small" @click="copyMessage(message.content)">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button link size="small" @click="regenerateMessage(index)">
                  <el-icon><RefreshRight /></el-icon>
                  重新生成
                </el-button>
              </div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="isLoading" class="message-item assistant">
            <div class="message-avatar">
              <el-avatar class="ai-avatar">
                <el-icon><Service /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="quick-actions" v-if="showQuickActions">
          <el-card shadow="never">
            <div class="quick-title">🚀 快速开始</div>
            <div class="quick-buttons">
              <el-button
                v-for="action in quickActions"
                :key="action.text"
                @click="sendQuickMessage(action.text)"
                class="quick-button"
              >
                <el-icon>
                  <component :is="action.icon" />
                </el-icon>
                {{ action.text }}
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息... (Ctrl+Enter 发送)"
            @keydown.ctrl.enter="handleSend"
            :disabled="isLoading"
          />
          <div class="input-actions">
            <div class="input-tools">
              <el-tooltip content="生成测试用例" placement="top">
                <el-button text @click="showTestCaseGenerator">
                  <el-icon><Document /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="错误分析" placement="top">
                <el-button text @click="showErrorAnalyzer">
                  <el-icon><Warning /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="测试建议" placement="top">
                <el-button text @click="showTestSuggestion">
                  <el-icon><Memo /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <el-button type="primary" @click="handleSend" :loading="isLoading" :disabled="!inputMessage.trim()">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 测试用例生成对话框 -->
    <el-dialog v-model="testCaseDialogVisible" title="智能生成测试用例" width="700px">
      <el-form :model="testCaseForm" label-width="100px">
        <el-form-item label="功能描述">
          <el-input
            v-model="testCaseForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述要测试的功能，例如：用户登录功能"
          />
        </el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="testCaseForm.type" placeholder="请选择测试类型">
            <el-option label="API 测试" value="api" />
            <el-option label="WEB 测试" value="web" />
            <el-option label="APP 测试" value="app" />
          </el-select>
        </el-form-item>
        <el-form-item label="覆盖度">
          <el-radio-group v-model="testCaseForm.coverage">
            <el-radio label="basic">基础用例</el-radio>
            <el-radio label="normal">常规用例</el-radio>
            <el-radio label="complete">完整用例</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testCaseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="generateTestCase" :loading="generating">生成用例</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  Setting,
  User,
  Service,
  CopyDocument,
  RefreshRight,
  Document,
  Warning,
  Memo,
  Promotion,
  MagicStick,
  List,
  DataAnalysis
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

const authStore = useAuthStore()
const userAvatar = computed(() => authStore.userInfo?.avatar || '')

const isOnline = ref(true)
const isLoading = ref(false)
const inputMessage = ref('')
const messages = ref<Message[]>([])
const messageListRef = ref<HTMLElement>()
const showQuickActions = ref(true)

// 快捷操作
const quickActions = [
  { text: '生成测试用例', icon: MagicStick },
  { text: '分析测试报告', icon: DataAnalysis },
  { text: '推荐测试策略', icon: List },
  { text: '优化测试流程', icon: Memo }
]

// 测试用例生成
const testCaseDialogVisible = ref(false)
const generating = ref(false)
const testCaseForm = ref({
  description: '',
  type: 'api',
  coverage: 'normal'
})

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage: Message = {
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date().toLocaleTimeString()
  }

  messages.value.push(userMessage)
  inputMessage.value = ''
  showQuickActions.value = false
  
  await scrollToBottom()

  // 模拟 AI 回复
  isLoading.value = true
  setTimeout(async () => {
    const aiMessage: Message = {
      role: 'assistant',
      content: generateAIResponse(userMessage.content),
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMessage)
    isLoading.value = false
    await scrollToBottom()
  }, 1500)
}

// 生成 AI 回复（模拟）
const generateAIResponse = (userInput: string): string => {
  const input = userInput.toLowerCase()
  
  if (input.includes('测试用例') || input.includes('用例')) {
    return `我可以帮你生成测试用例！请告诉我：
    
1. 需要测试的功能是什么？
2. 测试类型是 API、WEB 还是 APP？
3. 需要覆盖哪些场景？

你也可以点击下方的"生成测试用例"按钮，通过表单来创建。

**示例：**
- 功能描述：用户登录
- 测试类型：WEB
- 场景：正常登录、密码错误、账号不存在等`
  }
  
  if (input.includes('错误') || input.includes('失败') || input.includes('bug')) {
    return `我可以帮你分析测试错误！请提供以下信息：

1. **错误信息**：具体的错误提示是什么？
2. **复现步骤**：如何触发这个错误？
3. **环境信息**：测试环境、浏览器版本等

**常见错误分析：**
- ❌ **断言失败**：预期结果与实际结果不符
- ❌ **超时错误**：请求响应时间过长
- ❌ **元素未找到**：页面元素定位失败
- ❌ **网络错误**：接口调用失败

请提供更多详细信息，我会帮你深入分析。`
  }
  
  if (input.includes('优化') || input.includes('建议')) {
    return `关于测试优化，我有以下建议：

**🎯 测试策略优化：**
1. **优先级排序**：先执行核心功能和高风险用例
2. **并行执行**：使用多线程提高执行效率
3. **分层测试**：单元测试 → 集成测试 → 端到端测试

**⚡ 性能优化：**
1. 使用数据驱动测试，减少重复代码
2. 合理设置等待时间和超时时间
3. 复用测试数据和测试环境

**📊 报告优化：**
1. 添加截图和日志，便于问题排查
2. 生成详细的测试报告
3. 集成到 CI/CD 流程

你想深入了解哪个方面呢？`
  }
  
  if (input.includes('报告') || input.includes('分析')) {
    return `我可以帮你分析测试报告！

**📊 报告关键指标：**
- **通过率**：通过用例数 / 总用例数
- **执行率**：已执行用例数 / 总用例数
- **缺陷密度**：发现的bug数量
- **执行时间**：总执行耗时

**🔍 分析维度：**
1. **趋势分析**：对比历史数据，查看质量趋势
2. **覆盖率分析**：代码覆盖率、功能覆盖率
3. **失败原因分析**：统计常见失败原因

请上传你的测试报告，或告诉我具体的数据，我来帮你分析。`
  }
  
  return `收到你的消息："${userInput}"

我是 AI 测试助手，我可以帮你：

🎯 **智能生成测试用例**
📊 **分析测试报告**
🔍 **定位和分析错误**
💡 **提供测试建议**
⚡ **优化测试流程**

请告诉我你需要什么帮助！`
}

// 快速发送消息
const sendQuickMessage = (text: string) => {
  inputMessage.value = text
  handleSend()
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 格式化消息
const formatMessage = (content: string): string => {
  // 转换 Markdown 样式的文本
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

// 复制消息
const copyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
  ElMessage.success('已复制到剪贴板')
}

// 重新生成消息
const regenerateMessage = (index: number) => {
  if (index > 0) {
    const previousUserMessage = messages.value[index - 1]
    messages.value.splice(index, 1)
    inputMessage.value = previousUserMessage.content
    handleSend()
  }
}

// 处理命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'clear':
      try {
        await ElMessageBox.confirm('确定要清空所有对话记录吗？', '清空确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        messages.value = []
        showQuickActions.value = true
        ElMessage.success('已清空对话')
      } catch {
        // 用户取消
      }
      break
    case 'export':
      exportChat()
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
  }
}

// 导出对话
const exportChat = () => {
  const content = messages.value.map(msg => 
    `[${msg.timestamp}] ${msg.role === 'user' ? '我' : 'AI助手'}: ${msg.content}`
  ).join('\n\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AI对话记录_${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('对话记录已导出')
}

// 显示快速开始
const showQuickStart = () => {
  showQuickActions.value = true
}

// 显示测试用例生成器
const showTestCaseGenerator = () => {
  testCaseDialogVisible.value = true
}

// 显示错误分析器
const showErrorAnalyzer = () => {
  inputMessage.value = '我遇到了一个测试错误，请帮我分析：'
  nextTick(() => {
    const textarea = document.querySelector('.input-area textarea') as HTMLTextAreaElement
    textarea?.focus()
  })
}

// 显示测试建议
const showTestSuggestion = () => {
  inputMessage.value = '请给我一些测试优化建议'
  handleSend()
}

// 生成测试用例
const generateTestCase = async () => {
  if (!testCaseForm.value.description.trim()) {
    ElMessage.warning('请输入功能描述')
    return
  }
  
  generating.value = true
  
  setTimeout(() => {
    const message = `请帮我生成 ${testCaseForm.value.type.toUpperCase()} 测试用例：

**功能描述：** ${testCaseForm.value.description}
**测试类型：** ${testCaseForm.value.type.toUpperCase()}
**覆盖度：** ${testCaseForm.value.coverage === 'basic' ? '基础' : testCaseForm.value.coverage === 'normal' ? '常规' : '完整'}

请生成详细的测试用例，包括：
1. 用例标题
2. 前置条件
3. 测试步骤
4. 预期结果
5. 优先级`
    
    inputMessage.value = message
    handleSend()
    
    testCaseDialogVisible.value = false
    generating.value = false
    testCaseForm.value = { description: '', type: 'api', coverage: 'normal' }
  }, 500)
}
</script>

<style scoped>
.ai-chat-container {
  padding: 20px;
  height: calc(100vh - 40px);
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  background-color: #f5f7fa;
  line-height: 1.6;
  word-break: break-word;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', monospace;
}

.message-actions {
  display: flex;
  gap: 10px;
}

.loading-dots {
  display: flex;
  gap: 6px;
  padding: 16px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

.quick-actions {
  padding: 0 20px 20px;
}

.quick-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
}

.quick-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.quick-button {
  justify-content: flex-start;
}

.input-area {
  border-top: 1px solid #ebeef5;
  padding: 20px;
  background-color: #fafafa;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.input-tools {
  display: flex;
  gap: 5px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}
</style>

