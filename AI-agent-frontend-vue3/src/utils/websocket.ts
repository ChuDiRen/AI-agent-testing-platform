// Copyright (c) 2025 左岚. All rights reserved.
/**
 * WebSocket 服务封装
 * 支持自动重连、心跳检测、消息队列
 */

export interface WebSocketMessage {
  type: string
  data: any
  timestamp?: number
}

export interface WebSocketConfig {
  url: string
  heartbeatInterval?: number
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

type MessageHandler = (message: WebSocketMessage) => void
type EventHandler = () => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private config: Required<WebSocketConfig>
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map()
  private eventHandlers: Map<string, Set<EventHandler>> = new Map()
  private reconnectAttempts = 0
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private isManualClose = false

  constructor(config: WebSocketConfig) {
    this.config = {
      url: config.url,
      heartbeatInterval: config.heartbeatInterval || 30000, // 30秒
      reconnectInterval: config.reconnectInterval || 5000, // 5秒
      maxReconnectAttempts: config.maxReconnectAttempts || 10
    }
  }

  /**
   * 连接 WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 如果已经连接，先关闭
        if (this.ws) {
          this.ws.close()
        }

        this.isManualClose = false
        this.ws = new WebSocket(this.config.url)

        this.ws.onopen = () => {
          console.log('[WebSocket] 连接成功')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          this.triggerEvent('open')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('[WebSocket] 消息解析失败:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] 连接错误:', error)
          this.triggerEvent('error')
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('[WebSocket] 连接关闭')
          this.stopHeartbeat()
          this.triggerEvent('close')

          if (!this.isManualClose) {
            this.reconnect()
          }
        }
      } catch (error) {
        console.error('[WebSocket] 连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.isManualClose = true
    this.stopHeartbeat()
    this.stopReconnect()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 发送消息
   */
  send(type: string, data: any): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] 连接未就绪，无法发送消息')
      return false
    }

    try {
      const message: WebSocketMessage = {
        type,
        data,
        timestamp: Date.now()
      }
      this.ws.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('[WebSocket] 发送消息失败:', error)
      return false
    }
  }

  /**
   * 订阅消息类型
   */
  on(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    this.messageHandlers.get(type)!.add(handler)
  }

  /**
   * 取消订阅
   */
  off(type: string, handler?: MessageHandler): void {
    if (!handler) {
      this.messageHandlers.delete(type)
    } else {
      this.messageHandlers.get(type)?.delete(handler)
    }
  }

  /**
   * 监听事件（open, close, error）
   */
  addEventListener(event: string, handler: EventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  /**
   * 移除事件监听
   */
  removeEventListener(event: string, handler?: EventHandler): void {
    if (!handler) {
      this.eventHandlers.delete(event)
    } else {
      this.eventHandlers.get(event)?.delete(handler)
    }
  }

  /**
   * 获取连接状态
   */
  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  /**
   * 是否已连接
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    console.log('[WebSocket] 收到消息:', message)

    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('[WebSocket] 消息处理失败:', error)
        }
      })
    }

    // 处理特殊消息类型
    if (message.type === 'pong') {
      // 心跳响应
      console.log('[WebSocket] 心跳正常')
    }
  }

  /**
   * 触发事件
   */
  private triggerEvent(event: string): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler()
        } catch (error) {
          console.error('[WebSocket] 事件处理失败:', error)
        }
      })
    }
  }

  /**
   * 开始心跳检测
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatTimer = window.setInterval(() => {
      if (this.isConnected) {
        this.send('ping', {})
      }
    }, this.config.heartbeatInterval)
  }

  /**
   * 停止心跳检测
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 重新连接
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('[WebSocket] 达到最大重连次数，停止重连')
      return
    }

    this.reconnectAttempts++
    console.log(`[WebSocket] 尝试重连... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`)

    this.reconnectTimer = window.setTimeout(() => {
      this.connect().catch(() => {
        // 重连失败会自动触发下一次重连
      })
    }, this.config.reconnectInterval)
  }

  /**
   * 停止重连
   */
  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.reconnectAttempts = 0
  }
}

// 创建全局 WebSocket 实例
let wsInstance: WebSocketService | null = null

/**
 * 获取 WebSocket 实例
 */
export function getWebSocketInstance(url?: string): WebSocketService {
  if (!wsInstance && url) {
    // 根据环境自动配置 WebSocket URL
    const wsUrl = url || (
      import.meta.env.VITE_WS_URL || 
      `ws://${window.location.hostname}:${import.meta.env.VITE_API_PORT || 8000}/ws`
    )
    
    wsInstance = new WebSocketService({ url: wsUrl })
  }
  
  if (!wsInstance) {
    throw new Error('WebSocket 实例未初始化，请提供 URL')
  }
  
  return wsInstance
}

/**
 * 初始化 WebSocket 连接
 */
export async function initWebSocket(url?: string): Promise<WebSocketService> {
  const ws = getWebSocketInstance(url)
  
  if (!ws.isConnected) {
    await ws.connect()
  }
  
  return ws
}

/**
 * 销毁 WebSocket 连接
 */
export function destroyWebSocket(): void {
  if (wsInstance) {
    wsInstance.disconnect()
    wsInstance = null
  }
}

