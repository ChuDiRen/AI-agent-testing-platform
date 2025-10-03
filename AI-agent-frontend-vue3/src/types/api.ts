// Copyright (c) 2025 左岚. All rights reserved.
/**
 * API 通用类型定义
 * 对接 FastAPI RBAC 权限系统
 */

/**
 * 统一响应格式
 */
export interface APIResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error_code?: string
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page?: number
  page_size?: number
}

/**
 * 分页响应
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

/**
 * Token 响应
 */
export interface TokenResponse {
  access_token: string
  token_type: string
}

/**
 * 通用列表参数
 */
export interface ListParams {
  skip?: number
  limit?: number
}

/**
 * 导出格式
 */
export type ExportFormat = 'csv' | 'json'

/**
 * 文件上传响应
 */
export interface FileUploadResponse {
  filename: string
  url: string
  size: number
}

