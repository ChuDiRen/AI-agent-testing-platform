// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户管理 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, put, del } from './request'

export interface User {
  user_id: number
  username: string
  email: string
  mobile?: string
  dept_id?: number
  status: string
  ssex?: string
  avatar?: string
  description?: string
  create_time?: string
  last_login_time?: string
  modify_time?: string
}

export interface UserListParams {
  page?: number
  page_size?: number
  keyword?: string
  is_active?: boolean
}

export interface UserCreateData {
  username: string
  password: string
  email?: string
  mobile?: string
  description?: string
  status?: string
  ssex?: string
  dept_id?: number
}

export interface UserUpdateData {
  email?: string
  mobile?: string
  description?: string
  status?: string
  ssex?: string
  avatar?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

/**
 * 获取用户列表（分页）
 */
export function getUserList(params: UserListParams) {
  return get<{ success: boolean; data: PaginatedResponse<User> }>('/api/v1/users/', params)
}

/**
 * 获取用户详情
 */
export function getUserDetail(userId: number) {
  return get<{ success: boolean; data: User }>(`/api/v1/users/${userId}`)
}

/**
 * 创建用户
 */
export function createUser(data: UserCreateData) {
  return post<{ success: boolean; message: string; data: User }>('/api/v1/users/', data)
}

/**
 * 更新用户信息
 */
export function updateUser(userId: number, data: UserUpdateData) {
  return put<{ success: boolean; message: string; data: User }>(`/api/v1/users/${userId}`, data)
}

/**
 * 删除用户
 */
export function deleteUser(userId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/users/${userId}`)
}

/**
 * 导出用户数据（CSV）
 */
export function exportUsersCSV(keyword?: string) {
  const params = keyword ? { keyword } : {}
  return get<Blob>('/api/v1/users/export/csv', params)
}

/**
 * 导出用户数据（JSON）
 */
export function exportUsersJSON(keyword?: string) {
  const params = keyword ? { keyword } : {}
  return get<Blob>('/api/v1/users/export/json', params)
}

