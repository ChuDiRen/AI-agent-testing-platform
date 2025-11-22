/**
 * WebSocket Composable
 * 用于测试执行实时进度推送
 */
import { ref, onUnmounted } from 'vue'

export function useWebSocket(executionId) {
    const ws = ref(null)
    const isConnected = ref(false)
    const messages = ref([])
    const error = ref(null)
    const reconnectAttempts = ref(0)
    const maxReconnectAttempts = 5
    const reconnectDelay = 3000 // 3秒

    // WebSocket URL
    const getWebSocketUrl = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.hostname
        const port = import.meta.env.VITE_WS_PORT || '8000'
        return `${protocol}//${host}:${port}/ws/test-execution/${executionId}`
    }

    // 连接WebSocket
    const connect = () => {
        try {
            const url = getWebSocketUrl()
            console.log(`[WebSocket] 正在连接: ${url}`)

            ws.value = new WebSocket(url)

            // 连接成功
            ws.value.onopen = () => {
                console.log('[WebSocket] 连接成功')
                isConnected.value = true
                error.value = null
                reconnectAttempts.value = 0

                // 发送心跳
                startHeartbeat()
            }

            // 接收消息
            ws.value.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    console.log('[WebSocket] 收到消息:', data)
                    messages.value.push({
                        ...data,
                        timestamp: new Date().toISOString()
                    })
                } catch (e) {
                    // 如果不是JSON，直接添加文本消息
                    messages.value.push({
                        type: 'text',
                        content: event.data,
                        timestamp: new Date().toISOString()
                    })
                }
            }

            // 连接关闭
            ws.value.onclose = (event) => {
                console.log('[WebSocket] 连接关闭:', event.code, event.reason)
                isConnected.value = false
                stopHeartbeat()

                // 非正常关闭，尝试重连
                if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts) {
                    reconnectAttempts.value++
                    console.log(`[WebSocket] 尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})`)
                    setTimeout(() => {
                        connect()
                    }, reconnectDelay)
                }
            }

            // 连接错误
            ws.value.onerror = (event) => {
                console.error('[WebSocket] 连接错误:', event)
                error.value = '连接失败，请检查网络或服务器状态'
                isConnected.value = false
            }
        } catch (e) {
            console.error('[WebSocket] 创建连接失败:', e)
            error.value = e.message
        }
    }

    // 断开连接
    const disconnect = () => {
        if (ws.value) {
            console.log('[WebSocket] 主动断开连接')
            stopHeartbeat()
            ws.value.close(1000, 'Client disconnect')
            ws.value = null
            isConnected.value = false
        }
    }

    // 发送消息
    const send = (message) => {
        if (ws.value && isConnected.value) {
            const data = typeof message === 'string' ? message : JSON.stringify(message)
            ws.value.send(data)
            console.log('[WebSocket] 发送消息:', data)
        } else {
            console.warn('[WebSocket] 未连接，无法发送消息')
        }
    }

    // 心跳机制
    let heartbeatTimer = null
    const startHeartbeat = () => {
        heartbeatTimer = setInterval(() => {
            if (isConnected.value) {
                send('ping')
            }
        }, 30000) // 每30秒发送一次心跳
    }

    const stopHeartbeat = () => {
        if (heartbeatTimer) {
            clearInterval(heartbeatTimer)
            heartbeatTimer = null
        }
    }

    // 清空消息
    const clearMessages = () => {
        messages.value = []
    }

    // 获取最新消息
    const getLatestMessage = () => {
        return messages.value.length > 0 ? messages.value[messages.value.length - 1] : null
    }

    // 根据类型过滤消息
    const getMessagesByType = (type) => {
        return messages.value.filter(msg => msg.type === type)
    }

    // 组件卸载时自动断开
    onUnmounted(() => {
        disconnect()
    })

    return {
        // 状态
        isConnected,
        messages,
        error,
        reconnectAttempts,

        // 方法
        connect,
        disconnect,
        send,
        clearMessages,
        getLatestMessage,
        getMessagesByType
    }
}
