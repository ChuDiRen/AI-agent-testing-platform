<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="message-list-container">
    <el-card>
      <template #header>
        <div class="header">
          <h3>消息通知</h3>
          <div>
            <el-button @click="handleMarkAllRead">全部标记已读</el-button>
            <el-button type="danger" @click="handleClearAll">清空消息</el-button>
          </div>
        </div>
      </template>

      <!-- 过滤器 -->
      <div class="filter-bar">
        <el-radio-group v-model="filterType" @change="handleFilterChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="unread">未读</el-radio-button>
          <el-radio-button label="read">已读</el-radio-button>
          <el-radio-button label="system">系统通知</el-radio-button>
          <el-radio-button label="test">测试通知</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 消息列表 -->
      <el-timeline style="margin-top: 20px">
        <el-timeline-item
          v-for="msg in filteredMessages"
          :key="msg.notification_id"
          :timestamp="msg.create_time"
          placement="top"
          :type="msg.is_read ? 'default' : 'primary'"
        >
          <el-card :class="{ 'unread-message': !msg.is_read }">
            <div class="message-content">
              <div class="message-header">
                <span class="message-title">{{ msg.title }}</span>
                <el-tag :type="getMessageTypeColor(msg.type)" size="small">{{ getMessageTypeName(msg.type) }}</el-tag>
              </div>
              <div class="message-body">{{ msg.content }}</div>
              <div class="message-actions">
                <el-button v-if="!msg.is_read" link type="primary" @click="handleMarkRead(msg.notification_id)">标记已读</el-button>
                <el-button link type="danger" @click="handleDelete(msg.notification_id)">删除</el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 空状态 -->
      <el-empty v-if="filteredMessages.length === 0" description="暂无消息" />

      <!-- 分页 -->
      <div class="pagination" v-if="filteredMessages.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useNotificationStore } from '@/store/notification'
import type { Notification } from '@/api/notification'

const notificationStore = useNotificationStore()

// 状态
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const filteredMessages = computed(() => notificationStore.notifications)
const total = computed(() => notificationStore.stats.total)

// 初始化
onMounted(() => {
  loadNotifications()
  loadStats()
})

// 加载通知列表
const loadNotifications = async () => {
  await notificationStore.fetchNotificationList({
    filter_type: filterType.value,
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

// 加载统计信息
const loadStats = async () => {
  await notificationStore.fetchNotificationStats()
}

// 获取消息类型颜色
const getMessageTypeColor = (type: string): string | undefined => {
  const colorMap: Record<string, string | undefined> = {
    system: undefined,
    test: 'success',
    error: 'danger',
    info: 'info'
  }
  return colorMap[type]
}

// 获取消息类型名称
const getMessageTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    system: '系统',
    test: '测试',
    error: '错误',
    info: '信息'
  }
  return nameMap[type] || type
}

// 标记已读
const handleMarkRead = async (id: number) => {
  const success = await notificationStore.markAsRead(id)
  if (success) {
    await loadStats()
  }
}

// 全部标记已读
const handleMarkAllRead = async () => {
  const success = await notificationStore.markAllAsRead()
  if (success) {
    await loadNotifications()
  }
}

// 删除消息
const handleDelete = async (id: number) => {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await notificationStore.deleteNotification(id)
  }).catch(() => {})
}

// 清空所有消息
const handleClearAll = async () => {
  ElMessageBox.confirm('确定要清空所有消息吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await notificationStore.deleteAllNotifications()
  }).catch(() => {})
}

// 过滤器变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadNotifications()
}
</script>

<style scoped>
.message-list-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
}

.filter-bar {
  margin-top: 20px;
}

.message-content {
  padding: 10px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.message-title {
  font-weight: bold;
  font-size: 16px;
}

.message-body {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.6;
}

.message-actions {
  display: flex;
  gap: 10px;
}

.unread-message {
  border-left: 3px solid #409eff;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>


