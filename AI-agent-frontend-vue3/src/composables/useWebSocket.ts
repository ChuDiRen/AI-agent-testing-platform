// Copyright (c) 2025 左岚. All rights reserved.
/**
 * WebSocket Composable
 * 在 Vue 组件中使用 WebSocket
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { getWebSocketInstance, type WebSocketMessage } from '@/utils/websocket'
import { ElNotification } from 'element-plus'

export interface NotificationMessage {
  title: string
  message: string
  type: 'success' | 'warning' | 'info' | 'error'
  duration?: number
}

export function useWebSocket() {
  const isConnected = ref(false)
  const ws = getWebSocketInstance()

  // 连接 WebSocket
  const connect = async () => {
    try {
      await ws.connect()
      isConnected.value = true
      console.log('[useWebSocket] 连接成功')
    } catch (error) {
      console.error('[useWebSocket] 连接失败:', error)
      isConnected.value = false
    }
  }

  // 断开连接
  const disconnect = () => {
    ws.disconnect()
    isConnected.value = false
  }

  // 发送消息
  const send = (type: string, data: any) => {
    return ws.send(type, data)
  }

  // 订阅消息
  const subscribe = (type: string, handler: (message: WebSocketMessage) => void) => {
    ws.on(type, handler)
  }

  // 取消订阅
  const unsubscribe = (type: string, handler?: (message: WebSocketMessage) => void) => {
    ws.off(type, handler)
  }

  return {
    isConnected,
    connect,
    disconnect,
    send,
    subscribe,
    unsubscribe
  }
}

/**
 * 消息通知 Hook
 * 自动处理系统通知消息
 */
export function useNotification() {
  const { subscribe, unsubscribe } = useWebSocket()

  // 处理系统通知
  const handleNotification = (message: WebSocketMessage) => {
    const data: NotificationMessage = message.data
    
    ElNotification({
      title: data.title,
      message: data.message,
      type: data.type,
      duration: data.duration || 4500,
      position: 'top-right'
    })
  }

  // 处理测试通知
  const handleTestNotification = (message: WebSocketMessage) => {
    const { title, status, progress } = message.data
    
    let type: 'success' | 'warning' | 'info' | 'error' = 'info'
    if (status === 'completed') type = 'success'
    if (status === 'failed') type = 'error'
    if (status === 'running') type = 'info'
    
    ElNotification({
      title: title || '测试执行通知',
      message: `测试进度: ${progress}%`,
      type,
      duration: 4500,
      position: 'top-right'
    })
  }

  onMounted(() => {
    // 订阅通知消息
    subscribe('notification', handleNotification)
    subscribe('test_progress', handleTestNotification)
  })

  onUnmounted(() => {
    // 取消订阅
    unsubscribe('notification', handleNotification)
    unsubscribe('test_progress', handleTestNotification)
  })

  return {
    // 可以在这里添加更多通知相关的方法
  }
}

