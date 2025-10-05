// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 认证相关 API
 * 对接 FastAPI RBAC 权限系统
 */
import { post, get } from './request'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  email: string
  mobile?: string
  dept_id?: number
  ssex?: string
}

export interface LoginResponse {
  success: boolean
  message: string
  data: {
    access_token: string  // 访问令牌
    refresh_token: string  // 刷新令牌（必填）
    token_type: string  // 令牌类型
  }
}

export interface RegisterResponse {
  success: boolean
  message: string
  data: {
    user_id: number
    username: string
    email: string
    status: string
  }
}

export interface UserInfo {
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
}

/**
 * 用户注册
 */
export function register(data: RegisterRequest) {
  return post<RegisterResponse>('/api/v1/auth/register', data)
}

/**
 * 用户登录
 */
export function login(data: LoginRequest) {
  return post<LoginResponse>('/api/v1/auth/login', data)
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return get<{ success: boolean; data: UserInfo }>('/api/v1/users/me')
}

/**
 * 用户登出（本地处理）
 */
export function logout() {
  // FastAPI后端没有专门的logout接口，直接清除本地token
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  return Promise.resolve({ success: true, message: '登出成功' })
}

/**
 * 刷新访问令牌
 */
export function refreshToken(refreshToken: string) {
  return post<LoginResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken })
}

