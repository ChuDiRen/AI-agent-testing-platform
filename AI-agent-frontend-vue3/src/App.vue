<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
// App.vue 主组件
import { onMounted, onUnmounted } from 'vue'
import { useWebSocket, useNotification } from '@/composables/useWebSocket'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const { connect, disconnect } = useWebSocket()

// 启用通知功能
useNotification()

// 初始化 WebSocket 连接（仅在已登录时）
onMounted(async () => {
  if (authStore.token) {
    try {
      // 这里使用模拟的 WebSocket 地址
      // 实际项目中应该从环境变量读取
      // await connect()
      console.log('[App] WebSocket 连接已准备（模拟模式）')
    } catch (error) {
      console.error('[App] WebSocket 连接失败:', error)
    }
  }
})

// 组件卸载时断开连接
onUnmounted(() => {
  disconnect()
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
