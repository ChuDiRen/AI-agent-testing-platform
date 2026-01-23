import { createPinia } from 'pinia'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/api'

export const useExecutionStore = defineStore('execution', () => {
  const currentExecution = ref(null)
  const executionLogs = ref([])
  const wsConnected = ref(false)
  let websocket = null

  // WebSocket 连接
  function connectWebSocket(executionId) {
    const wsUrl = `ws://localhost:8000/api/v1/Execution/ws/${executionId}`
    websocket = new WebSocket(wsUrl)

    websocket.onopen = () => {
      wsConnected.value = true
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'node_complete') {
        executionLogs.value.push({
          id: Date.now(),
          timestamp: new Date().toISOString(),
          message: data.message,
          level: data.level || 'info'
        })
      } else if (data.type === 'execution_complete') {
        currentExecution.value = data
      } else if (data.type === 'error') {
        // Handle execution error
      }
    }

    websocket.onerror = () => {
      // Handle WebSocket error
    }

    websocket.onclose = () => {
      wsConnected.value = false
    }
  }

  // 断开 WebSocket
  function disconnectWebSocket() {
    if (websocket) {
      websocket.close()
      websocket = null
      wsConnected.value = false
    }
  }

  // 发送心跳
  function sendHeartbeat() {
    if (websocket && wsConnected.value) {
      websocket.send('ping')
    }
  }

  // 清空日志
  function clearLogs() {
    executionLogs.value = []
  }

  return {
    currentExecution,
    executionLogs,
    wsConnected,
    connectWebSocket,
    disconnectWebSocket,
    sendHeartbeat,
    clearLogs
  }
})
