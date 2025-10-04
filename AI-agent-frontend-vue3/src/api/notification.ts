// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 消息通知 API
 * 对接 FastAPI 消息通知系统
 */
import { get, post, put, del } from './request'

export interface Notification {
  notification_id: number
  user_id: number
  title: string
  content: string
  type: string // system/test/error/info
  is_read: boolean
  create_time: string
  read_time?: string
}

export interface NotificationStats {
  total: number
  unread: number
  read: number
}

export interface NotificationListParams {
  filter_type?: string // all/unread/read/system/test/error/info
  skip?: number
  limit?: number
}

/**
 * 获取通知列表
 */
export function getNotificationList(params: NotificationListParams = {}) {
  return get<{ success: boolean; data: { items: Notification[]; total: number; page: number; page_size: number; pages: number } }>('/api/v1/notifications/', params)
}

/**
 * 获取通知统计
 */
export function getNotificationStats() {
  return get<{ success: boolean; data: NotificationStats }>('/api/v1/notifications/stats')
}

/**
 * 获取通知详情
 */
export function getNotificationDetail(notificationId: number) {
  return get<{ success: boolean; data: Notification }>(`/api/v1/notifications/${notificationId}`)
}

/**
 * 标记通知为已读
 */
export function markNotificationAsRead(notificationId: number) {
  return put<{ success: boolean; message: string; data: Notification }>(`/api/v1/notifications/${notificationId}/read`, {})
}

/**
 * 标记所有通知为已读
 */
export function markAllNotificationsAsRead() {
  return put<{ success: boolean; message: string; data: { count: number } }>('/api/v1/notifications/read-all', {})
}

/**
 * 删除通知
 */
export function deleteNotification(notificationId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/notifications/${notificationId}`)
}

/**
 * 删除所有通知
 */
export function deleteAllNotifications() {
  return del<{ success: boolean; message: string; data: { count: number } }>('/api/v1/notifications/')
}

