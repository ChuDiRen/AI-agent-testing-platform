<template>
  <div class="agent-chat-integrated">
    <!-- 使用 veaury 将 React 组件渲染在 Vue 中 -->
    <AgentChatReactComponent />
  </div>
</template>

<script setup>
import { applyReactInVue } from 'veaury'
import AgentChatApp from '@/agent-react/AgentChatApp.jsx'

// 将 React 组件转换为 Vue 组件
const AgentChatReactComponent = applyReactInVue(AgentChatApp)
</script>

<style scoped>
.agent-chat-integrated {
  width: 100%;
  height: calc(100vh - 60px);
  overflow: hidden;
}

/* 确保 React 组件的样式正常显示 */
.agent-chat-integrated :deep(*) {
  box-sizing: border-box;
}
</style>

