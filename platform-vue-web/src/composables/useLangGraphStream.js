import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createLangGraphClient, streamMessages, getThreadState } from '@/api/langgraph'

/**
 * LangGraph 流式通信 Composable
 */
export function useLangGraphStream(threadId) {
    const client = ref(null)
    const messages = ref([])
    const isSending = ref(false)
    const isThinking = ref(false)
    const currentStreamingMessage = ref(null)
    const toolCalls = ref([])
    const interrupt = ref(null)

    // 初始化客户端
    const initClient = () => {
        try {
            client.value = createLangGraphClient()
            return true
        } catch (error) {
            console.error('Failed to initialize LangGraph client:', error)
            ElMessage.error('初始化 LangGraph 客户端失败')
            return false
        }
    }

    // 添加消息到列表
    const addMessage = (role, content, metadata = {}) => {
        const message = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            role,
            content,
            timestamp: new Date().toISOString(),
            streaming: false,
            ...metadata
        }
        messages.value.push(message)
        return message
    }

    // 发送消息
    const sendMessage = async (content, currentThreadId) => {
        if (!client.value && !initClient()) {
            return
        }

        if (!content || !content.trim()) {
            ElMessage.warning('请输入消息内容')
            return
        }

        if (!currentThreadId) {
            ElMessage.error('请先创建或选择对话')
            return
        }

        // 添加用户消息
        addMessage('human', content)

        // 创建 AI 消息占位符
        const aiMessage = addMessage('ai', '', { streaming: true })
        currentStreamingMessage.value = aiMessage

        isSending.value = true
        isThinking.value = true

        try {
            const userMessage = {
                role: 'human',
                content
            }

            let accumulatedContent = ''

            await streamMessages(
                client.value,
                currentThreadId,
                userMessage,
                // onChunk - 处理消息流
                (chunk) => {
                    if (chunk && chunk.length > 0) {
                        const latestMessage = chunk[chunk.length - 1]
                        if (latestMessage && latestMessage.content) {
                            accumulatedContent = latestMessage.content
                            aiMessage.content = accumulatedContent
                        }
                    }
                },
                // onEvent - 处理事件流
                (event) => {
                    // 处理工具调用
                    if (event.event === 'on_chat_model_stream') {
                        isThinking.value = false
                    }

                    // 处理工具调用事件
                    if (event.data?.tool_calls) {
                        toolCalls.value = event.data.tool_calls
                    }

                    // 处理中断
                    if (event.event === 'interrupt') {
                        interrupt.value = event.data
                    }
                }
            )

            // 流式完成
            aiMessage.streaming = false
            isThinking.value = false
            currentStreamingMessage.value = null
        } catch (error) {
            console.error('Send message error:', error)
            ElMessage.error('发送消息失败: ' + (error.message || '未知错误'))

            // 移除失败的消息
            const index = messages.value.findIndex(m => m.id === aiMessage.id)
            if (index > -1) {
                messages.value.splice(index, 1)
            }
        } finally {
            isSending.value = false
        }
    }

    // 停止生成
    const stopGeneration = () => {
        // TODO: 实现停止生成逻辑
        isSending.value = false
        isThinking.value = false

        if (currentStreamingMessage.value) {
            currentStreamingMessage.value.streaming = false
            currentStreamingMessage.value = null
        }
    }

    // 清空消息
    const clearMessages = () => {
        messages.value = []
        toolCalls.value = []
        interrupt.value = null
    }

    // 加载线程历史消息
    const loadThreadHistory = async (currentThreadId) => {
        if (!client.value && !initClient()) {
            return
        }

        if (!currentThreadId) {
            return
        }

        try {
            const state = await getThreadState(client.value, currentThreadId)

            if (state && state.values && state.values.messages) {
                messages.value = state.values.messages.map((msg, index) => ({
                    id: msg.id || `msg_${index}`,
                    role: msg.type === 'human' ? 'human' : 'ai',
                    content: msg.content,
                    timestamp: msg.timestamp || new Date().toISOString(),
                    streaming: false,
                    toolCalls: msg.tool_calls || null
                }))
            }
        } catch (error) {
            console.error('Load thread history error:', error)
            // 不显示错误提示，因为可能是新线程
        }
    }

    // 计算属性
    const hasMessages = computed(() => messages.value.length > 0)
    const lastMessage = computed(() => messages.value[messages.value.length - 1])

    return {
        // 状态
        messages,
        isSending,
        isThinking,
        toolCalls,
        interrupt,
        currentStreamingMessage,
        hasMessages,
        lastMessage,

        // 方法
        initClient,
        sendMessage,
        stopGeneration,
        clearMessages,
        loadThreadHistory,
        addMessage
    }
}

