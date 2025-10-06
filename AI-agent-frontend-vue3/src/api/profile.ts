// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 个人中心 API
 * 对接 FastAPI 用户个人资料系统
 */
import { get, put, post } from './request'
import type { User } from './user'

export interface ProfileUpdateData {
  email?: string
  mobile?: string
  description?: string
}

export interface PasswordChangeData {
  old_password: string
  new_password: string
}

/**
 * 获取当前用户信息
 */
export function getCurrentUserInfo() {
  return get<{ success: boolean; data: User }>('/api/v1/users/me')
}

/**
 * 更新个人资料
 */
export function updateProfile(data: ProfileUpdateData) {
  return put<{ success: boolean; message: string; data: User }>('/api/v1/users/me', data)
}

/**
 * 修改密码
 */
export function changePassword(data: PasswordChangeData) {
  return put<{ success: boolean; message: string }>('/api/v1/users/me/password', data)
}

/**
 * 上传头像
 */
export function uploadAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return post<{ success: boolean; message: string; data: { avatar_url: string; filename: string } }>(
    '/api/v1/upload/avatar',
    formData
  )
}

