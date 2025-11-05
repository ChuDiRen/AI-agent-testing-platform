<template>
  <div class="langgraph-chat-page">
    <AgentChatAppVue />
  </div>
</template>

<script setup>
import { applyReactInVue } from 'veaury'
import AgentChatApp from '~/agent-react/AgentChatApp'
// 导入兼容版本的样式（支持 Tailwind CSS v3）
import '../agentchat/agent-chat-styles.css'

// 使用 veaury 将 React 组件转换为 Vue 组件
// LangGraph 和 Agent Chat 使用同一个组件
const AgentChatAppVue = applyReactInVue(AgentChatApp)
</script>

<style scoped>
.langgraph-chat-page {
  width: 100%;
  height: calc(100vh - 64px);
  overflow: hidden;
  background: var(--background, #f5f7fa);
}
</style>
