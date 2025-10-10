<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Promotion /></el-icon>
        <h1 v-show="!sidebarCollapsed" class="title">华测自动化测试平台</h1>
        <el-icon class="menu-icon" @click="toggleSidebar"><Expand /></el-icon>
      </div>

      <!-- 菜单列表 -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        @select="handleMenuSelect"
      >
        <!-- 仪表板 -->
        <el-menu-item index="dashboard" @click="router.push('/dashboard')">
          <el-icon><Monitor /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>

        <!-- 系统管理 -->
        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="system-user" @click="router.push('/system/user')">用户管理</el-menu-item>
          <el-menu-item index="system-role" @click="router.push('/system/role')">角色管理</el-menu-item>
          <el-menu-item index="system-menu" @click="router.push('/system/menu')">菜单管理</el-menu-item>
          <el-menu-item index="system-department" @click="router.push('/system/department')">部门管理</el-menu-item>
        </el-sub-menu>

        <!-- API引擎插件 -->
        <el-sub-menu index="api-engine">
          <template #title>
            <el-icon><Promotion /></el-icon>
            <span>API引擎</span>
          </template>
          <el-menu-item index="api-engine-suites" @click="router.push('/plugin/api-engine/suites')">测试套件</el-menu-item>
          <el-menu-item index="api-engine-cases" @click="router.push('/plugin/api-engine/cases')">用例管理</el-menu-item>
          <el-menu-item index="api-engine-batch-execution" @click="router.push('/plugin/api-engine/batch-execution')">批量执行</el-menu-item>
          <el-menu-item index="api-engine-executions" @click="router.push('/plugin/api-engine/executions')">执行历史</el-menu-item>
          <el-menu-item index="api-engine-keywords" @click="router.push('/plugin/api-engine/keywords')">关键字管理</el-menu-item>
        </el-sub-menu>

        <!-- 消息通知管理 -->
        <el-sub-menu index="message">
          <template #title>
            <el-icon><Message /></el-icon>
            <span>消息通知</span>
          </template>
          <el-menu-item index="message-list" @click="router.push('/message/list')">消息列表</el-menu-item>
          <el-menu-item index="message-setting" @click="router.push('/message/setting')">通知设置</el-menu-item>
        </el-sub-menu>

        <!-- 测试数据管理 -->
        <el-sub-menu index="data">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>数据管理</span>
          </template>
          <el-menu-item index="data-testdata" @click="router.push('/data/testdata')">测试数据</el-menu-item>
        </el-sub-menu>

        <!-- AI 功能 -->
        <el-sub-menu index="ai">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>AI 功能</span>
          </template>
          <el-menu-item index="ai-chat" @click="router.push('/ai/chat')">AI 助手</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <HeaderNav />
      
      <!-- 内容区域 -->
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Promotion,
  Expand,
  Monitor,
  Setting,
  Message,
  DataAnalysis
} from '@element-plus/icons-vue'
import HeaderNav from './HeaderNav.vue'

const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const activeMenu = ref('dashboard')

// 根据当前路由设置活跃菜单
const updateActiveMenu = () => {
  const path = route.path
  if (path.startsWith('/dashboard')) {
    activeMenu.value = 'dashboard'
  } else if (path.startsWith('/system/user')) {
    activeMenu.value = 'system-user'
  } else if (path.startsWith('/system/role')) {
    activeMenu.value = 'system-role'
  } else if (path.startsWith('/system/menu')) {
    activeMenu.value = 'system-menu'
  } else if (path.startsWith('/system/department')) {
    activeMenu.value = 'system-department'
  } else if (path.startsWith('/api/testcase')) {
    activeMenu.value = 'api-testcase'
  } else if (path.startsWith('/api/execute')) {
    activeMenu.value = 'api-execute'
  } else if (path.startsWith('/api/report')) {
    activeMenu.value = 'api-report'
  } else if (path.startsWith('/web/testcase')) {
    activeMenu.value = 'web-testcase'
  } else if (path.startsWith('/web/execute')) {
    activeMenu.value = 'web-execute'
  } else if (path.startsWith('/web/report')) {
    activeMenu.value = 'web-report'
  } else if (path.startsWith('/app/testcase')) {
    activeMenu.value = 'app-testcase'
  } else if (path.startsWith('/app/execute')) {
    activeMenu.value = 'app-execute'
  } else if (path.startsWith('/app/report')) {
    activeMenu.value = 'app-report'
  } else if (path.startsWith('/message/list')) {
    activeMenu.value = 'message-list'
  } else if (path.startsWith('/message/setting')) {
    activeMenu.value = 'message-setting'
  } else if (path.startsWith('/data/testdata')) {
    activeMenu.value = 'data-testdata'
  } else if (path.startsWith('/plugin/api-engine/suites')) {
    activeMenu.value = 'api-engine-suites'
  } else if (path.startsWith('/plugin/api-engine/cases')) {
    activeMenu.value = 'api-engine-cases'
  } else if (path.startsWith('/plugin/api-engine/batch-execution')) {
    activeMenu.value = 'api-engine-batch-execution'
  } else if (path.startsWith('/plugin/api-engine/executions')) {
    activeMenu.value = 'api-engine-executions'
  } else if (path.startsWith('/plugin/api-engine/keywords')) {
    activeMenu.value = 'api-engine-keywords'
  } else if (path.startsWith('/plugin/api-engine')) {
    activeMenu.value = 'api-engine-suites'  // 默认选中套件页面
  } else if (path.startsWith('/ai/chat')) {
    activeMenu.value = 'ai-chat'
  }
}

// 监听路由变化
watch(() => route.path, updateActiveMenu, { immediate: true })

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #5b6bdc 0%, #4755c9 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 64px;
}

.logo-icon {
  font-size: 28px;
  color: #fbbf24;
  flex-shrink: 0;
}

.title {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: white;
  white-space: nowrap;
  overflow: hidden;
}

.menu-icon {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
  flex-shrink: 0;
}

.menu-icon:hover {
  transform: rotate(180deg);
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  overflow-y: auto;
}

:deep(.el-menu) {
  background-color: transparent;
  border: none;
}

:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.9);
  height: 48px;
  line-height: 48px;
  font-size: 14px;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  height: 44px;
  line-height: 44px;
  font-size: 13px;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
}

:deep(.el-sub-menu .el-menu) {
  background-color: rgba(0, 0, 0, 0.1);
}

:deep(.el-sub-menu__icon-arrow) {
  color: rgba(255, 255, 255, 0.7);
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
