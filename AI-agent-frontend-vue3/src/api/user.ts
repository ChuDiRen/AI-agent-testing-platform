// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户管理 API
 */
import { get, post, put, del } from './request'

export interface User {
  id: number
  username: string
  nickname: string
  email: string
  phone?: string
  avatar?: string
  dept_id?: number
  dept_name?: string
  status: number
  roles: Array<{
    id: number
    name: string
    code: string
  }>
  created_at: string
  updated_at: string
}

export interface UserListParams {
  page?: number
  page_size?: number
  username?: string
  dept_id?: number
  status?: string
}

export interface UserCreateData {
  username: string
  password: string
  nickname: string
  email?: string
  phone?: string
  dept_id?: number
  role_ids?: number[]
}

/**
 * 获取用户列表
 */
export function getUserList(params: UserListParams) {
  return get<{ code: number; data: { items: User[]; total: number } }>('/api/v1/user/list', params)
}

/**
 * 获取用户详情
 */
export function getUserDetail(id: number) {
  return get<{ code: number; data: User }>(`/api/v1/user/${id}`)
}

/**
 * 创建用户
 */
export function createUser(data: UserCreateData) {
  return post<{ code: number; msg: string }>('/api/v1/user/create', data)
}

/**
 * 更新用户
 */
export function updateUser(data: Partial<User> & { id: number }) {
  return post<{ code: number; msg: string }>('/api/v1/user/update', data)
}

/**
 * 删除用户
 */
export function deleteUser(id: number) {
  return del<{ code: number; msg: string }>('/api/v1/user/delete', { id })
}

/**
 * 重置密码
 */
export function resetPassword(id: number, password: string) {
  return post<{ code: number; msg: string }>('/api/v1/user/reset-password', { id, password })
}

/**
 * 修改用户状态
 */
export function changeUserStatus(id: number, status: number) {
  return post<{ code: number; msg: string }>('/api/v1/user/change-status', { id, status })
}

