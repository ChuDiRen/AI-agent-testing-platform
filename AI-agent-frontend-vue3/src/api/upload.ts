// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 文件上传 API
 * 对接 FastAPI RBAC 权限系统
 */
import { request } from './request'
import { del } from './request'

export interface UploadResponse {
  success: boolean
  data: {
    filename: string
    url: string
    size: number
  }
}

/**
 * 上传头像
 */
export function uploadAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request<UploadResponse>({
    url: '/api/v1/upload/avatar',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上传文件
 */
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request<UploadResponse>({
    url: '/api/v1/upload/file',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除文件
 */
export function deleteFile(filename: string) {
  return del<{ success: boolean; message: string }>('/api/v1/upload/file', { filename })
}

