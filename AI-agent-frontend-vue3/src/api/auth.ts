// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 认证相关 API
 */
import { post, get } from './request'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  code: number
  data: {
    access_token: string
    refresh_token: string
    token_type: string
    userinfo: {
      id: number
      username: string
      nickname: string
      email: string
      avatar: string
      roles: string[]
      permissions: string[]
    }
  }
  message: string
}

export interface UserInfo {
  id: number
  username: string
  nickname: string
  email: string
  phone: string
  avatar: string
  dept_id: number
  dept_name: string
  roles: Array<{
    id: number
    name: string
    code: string
  }>
  permissions: string[]
}

/**
 * 用户登录
 */
export function login(data: LoginRequest) {
  return post<LoginResponse>('/api/v1/base/login', data)
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return get<{ code: number; data: UserInfo }>('/api/v1/base/userinfo')
}

/**
 * 获取用户菜单
 */
export function getUserMenu() {
  return get<any>('/api/v1/base/user/menu')
}

/**
 * 获取用户API权限
 */
export function getUserApi() {
  return get<any>('/api/v1/base/user/api')
}

/**
 * 用户登出
 */
export function logout() {
  return post('/api/v1/base/logout')
}

