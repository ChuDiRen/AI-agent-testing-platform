<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <header class="header-nav">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-section">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbItems" :key="item.path" :to="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 右侧操作区 -->
    <div class="header-actions">
      <!-- 刷新控制 -->
      <div class="refresh-controls">
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          style="margin-right: 15px"
          @change="handleAutoRefreshChange"
        />
        <el-button 
          :icon="Refresh" 
          circle 
          @click="handleManualRefresh" 
          :loading="refreshing" 
          title="刷新数据" 
        />
      </div>

      <!-- 消息通知 -->
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
        <el-button :icon="Bell" circle @click="showNotifications" title="消息通知" />
      </el-badge>

      <!-- 用户菜单 -->
      <el-dropdown @command="handleUserCommand" class="user-dropdown">
        <div class="user-info">
          <el-avatar :size="36" :src="authStore.userInfo?.avatar || defaultAvatar" />
          <span class="username">{{ authStore.userInfo?.username || '用户' }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <div class="user-detail">
                <div class="user-name">{{ authStore.userInfo?.username || '用户' }}</div>
                <div class="user-role">{{ authStore.userInfo?.roleName || '普通用户' }}</div>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><Switch /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useNotificationStore } from '@/store/notification'
import { ElMessageBox, ElMessage, ElNotification } from 'element-plus'
import {
  Refresh,
  Bell,
  User,
  Setting,
  Switch
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const autoRefresh = ref(false)
const refreshing = ref(false)
const unreadCount = computed(() => notificationStore.stats.unread) // 未读消息数量
let refreshTimer: number | null = null

// 面包屑导航数据
const breadcrumbItems = computed(() => {
  const path = route.path
  const items: Array<{ path: string; title: string }> = []
  
  if (path.startsWith('/system')) {
    items.push({ path: '/system', title: '系统管理' })
    if (path.includes('/user')) items.push({ path: '/system/user', title: '用户管理' })
    if (path.includes('/role')) items.push({ path: '/system/role', title: '角色管理' })
    if (path.includes('/permission')) items.push({ path: '/system/permission', title: '权限管理' })
    if (path.includes('/menu')) items.push({ path: '/system/menu', title: '菜单管理' })
    if (path.includes('/department')) items.push({ path: '/system/department', title: '部门管理' })
  } else if (path.startsWith('/plugin/api-engine')) {
    items.push({ path: '/plugin/api-engine', title: 'API引擎' })
    if (path.includes('/suites')) items.push({ path: '/plugin/api-engine/suites', title: '测试套件' })
    if (path.includes('/cases')) items.push({ path: '/plugin/api-engine/cases', title: '用例管理' })
    if (path.includes('/executions')) items.push({ path: '/plugin/api-engine/executions', title: '执行历史' })
    if (path.includes('/keywords')) items.push({ path: '/plugin/api-engine/keywords', title: '关键字管理' })
  } else if (path.startsWith('/message')) {
    items.push({ path: '/message', title: '消息通知' })
    if (path.includes('/list')) items.push({ path: '/message/list', title: '消息列表' })
    if (path.includes('/setting')) items.push({ path: '/message/setting', title: '通知设置' })
  } else if (path.startsWith('/data')) {
    items.push({ path: '/data', title: '数据管理' })
    if (path.includes('/testdata')) items.push({ path: '/data/testdata', title: '测试数据' })
  } else if (path.startsWith('/ai')) {
    items.push({ path: '/ai', title: 'AI功能' })
    if (path.includes('/chat')) items.push({ path: '/ai/chat', title: 'AI助手' })
  } else if (path.startsWith('/user')) {
    items.push({ path: '/user', title: '个人中心' })
    if (path.includes('/profile')) items.push({ path: '/user/profile', title: '个人资料' })
  } else if (path === '/dashboard') {
    items.push({ path: '/dashboard', title: '仪表板' })
  }
  
  return items
})

// 手动刷新
const handleManualRefresh = async () => {
  refreshing.value = true
  try {
    // 触发当前页面的刷新事件
    window.dispatchEvent(new CustomEvent('manual-refresh'))
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 自动刷新切换
const handleAutoRefreshChange = (value: boolean) => {
  if (value) {
    refreshTimer = window.setInterval(() => {
      window.dispatchEvent(new CustomEvent('auto-refresh'))
    }, 30000) // 30秒刷新一次
    ElMessage.success('已开启自动刷新（每30秒）')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

// 显示通知
const showNotifications = () => {
  router.push('/message/list')
}

// 用户菜单操作
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'settings':
      router.push('/message/setting')
      break
    case 'logout':
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await authStore.logout()
      router.push('/login')
      break
  }
}

// 获取未读消息数量
const fetchUnreadCount = async () => {
  await notificationStore.fetchNotificationStats()
}

onMounted(() => {
  fetchUnreadCount()
  // 每分钟检查一次未读消息
  const unreadTimer = setInterval(fetchUnreadCount, 60000)

  onUnmounted(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    clearInterval(unreadTimer)
  })
})
</script>

<style scoped>
.header-nav {
  background: white;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid #e5e7eb;
}

.breadcrumb-section {
  flex: 1;
}

:deep(.el-breadcrumb) {
  font-size: 14px;
}

:deep(.el-breadcrumb__item) {
  color: #6b7280;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #1f2937;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.refresh-controls {
  display: flex;
  align-items: center;
  padding-right: 20px;
  border-right: 1px solid #e5e7eb;
}

.notification-badge {
  margin-right: 8px;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f3f4f6;
}

.username {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.user-detail {
  padding: 8px 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}
</style>
