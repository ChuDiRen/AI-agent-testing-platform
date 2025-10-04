// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 数据管理 API
 * 对接 FastAPI 数据管理系统
 */
import { get, post, del } from './request'

export interface BackupFile {
  filename: string
  size: number
  created_time: string
  path: string
}

export interface DatabaseStats {
  total_tables: number
  total_records: number
  database_size: number
  backup_count: number
  table_stats: Array<{
    table: string
    records: number
  }>
}

export interface CleanupResult {
  notification_deleted: number
  days: number
}

/**
 * 获取备份列表
 */
export function getBackupList() {
  return get<{ success: boolean; message: string; data: BackupFile[] }>('/api/v1/data/backup/list')
}

/**
 * 创建备份
 */
export function createBackup() {
  return post<{ success: boolean; message: string; data: any }>('/api/v1/data/backup/create')
}

/**
 * 删除备份
 */
export function deleteBackup(filename: string) {
  return del<{ success: boolean; message: string }>(`/api/v1/data/backup/${filename}`)
}

/**
 * 获取数据库统计
 */
export function getDatabaseStats() {
  return get<{ success: boolean; data: DatabaseStats }>('/api/v1/data/stats')
}

/**
 * 清理旧数据
 */
export function cleanupData(days: number = 30) {
  return post<{ success: boolean; message: string; data: CleanupResult }>(`/api/v1/data/cleanup?days=${days}`)
}

/**
 * 优化数据库
 */
export function optimizeDatabase() {
  return post<{ success: boolean; message: string; data: any }>('/api/v1/data/optimize')
}

