// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 消息通知状态管理
 * 适配 FastAPI 消息通知系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getNotificationList,
  getNotificationStats,
  getNotificationDetail,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  deleteAllNotifications,
  type Notification,
  type NotificationStats,
  type NotificationListParams
} from '@/api/notification'
import { ElMessage } from 'element-plus'

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<Notification[]>([])
  const stats = ref<NotificationStats>({ total: 0, unread: 0, read: 0 })
  const loading = ref(false)
  const currentNotification = ref<Notification | null>(null)

  // Actions
  async function fetchNotificationList(params: NotificationListParams = {}) {
    try {
      loading.value = true
      const response = await getNotificationList(params)
      
      if (response.success && response.data) {
        notifications.value = response.data.items
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取通知列表失败:', error)
      ElMessage.error('获取通知列表失败')
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchNotificationStats() {
    try {
      const response = await getNotificationStats()
      
      if (response.success && response.data) {
        stats.value = response.data
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取通知统计失败:', error)
      return null
    }
  }

  async function fetchNotificationDetail(notificationId: number) {
    try {
      loading.value = true
      const response = await getNotificationDetail(notificationId)
      
      if (response.success && response.data) {
        currentNotification.value = response.data
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取通知详情失败:', error)
      ElMessage.error('获取通知详情失败')
      return null
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(notificationId: number) {
    try {
      const response = await markNotificationAsRead(notificationId)
      
      if (response.success) {
        // 更新本地状态
        const notification = notifications.value.find(n => n.notification_id === notificationId)
        if (notification) {
          notification.is_read = true
          notification.read_time = new Date().toISOString()
        }
        
        // 更新统计
        await fetchNotificationStats()
        
        return true
      } else {
        ElMessage.error(response.message || '标记已读失败')
        return false
      }
    } catch (error: any) {
      console.error('标记已读失败:', error)
      ElMessage.error(error.message || '标记已读失败')
      return false
    }
  }

  async function markAllAsRead() {
    try {
      const response = await markAllNotificationsAsRead()
      
      if (response.success) {
        ElMessage.success(response.message || '已标记所有通知为已读')
        
        // 更新本地状态
        notifications.value.forEach(n => {
          n.is_read = true
          n.read_time = new Date().toISOString()
        })
        
        // 更新统计
        await fetchNotificationStats()
        
        return true
      } else {
        ElMessage.error(response.message || '操作失败')
        return false
      }
    } catch (error: any) {
      console.error('标记所有已读失败:', error)
      ElMessage.error(error.message || '操作失败')
      return false
    }
  }

  async function deleteNotificationAction(notificationId: number) {
    try {
      const response = await deleteNotification(notificationId)
      
      if (response.success) {
        ElMessage.success(response.message || '删除成功')
        
        // 从本地列表中移除
        notifications.value = notifications.value.filter(n => n.notification_id !== notificationId)
        
        // 更新统计
        await fetchNotificationStats()
        
        return true
      } else {
        ElMessage.error(response.message || '删除失败')
        return false
      }
    } catch (error: any) {
      console.error('删除通知失败:', error)
      ElMessage.error(error.message || '删除失败')
      return false
    }
  }

  async function deleteAllNotificationsAction() {
    try {
      const response = await deleteAllNotifications()
      
      if (response.success) {
        ElMessage.success(response.message || '已清空所有通知')
        
        // 清空本地列表
        notifications.value = []
        
        // 更新统计
        await fetchNotificationStats()
        
        return true
      } else {
        ElMessage.error(response.message || '操作失败')
        return false
      }
    } catch (error: any) {
      console.error('清空通知失败:', error)
      ElMessage.error(error.message || '操作失败')
      return false
    }
  }

  return {
    // State
    notifications,
    stats,
    loading,
    currentNotification,
    // Actions
    fetchNotificationList,
    fetchNotificationStats,
    fetchNotificationDetail,
    markAsRead,
    markAllAsRead,
    deleteNotification: deleteNotificationAction,
    deleteAllNotifications: deleteAllNotificationsAction
  }
})

