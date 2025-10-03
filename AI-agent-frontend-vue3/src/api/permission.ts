// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 权限管理 API
 */
import { get, post, del } from './request'

export interface Permission {
  id: number
  path: string
  method: string
  summary: string
  tags: string
  is_active: boolean
  created_at: string
}

export interface Menu {
  id: number
  name: string
  path: string
  parent_id?: number
  icon?: string
  order_num: number
  children?: Menu[]
}

export interface PermissionListParams {
  page?: number
  page_size?: number
  path?: string
  method?: string
}

/**
 * 获取API权限列表
 */
export function getApiList(params: PermissionListParams = {}) {
  return get<{ code: number; data: { items: Permission[]; total: number } }>('/api/v1/api/list', params)
}

/**
 * 获取菜单列表
 */
export function getMenuList(params: { menu_name?: string } = {}) {
  return get<{ code: number; data: { items: Menu[]; total: number } }>('/api/v1/menu/list', params)
}

/**
 * 获取角色权限
 */
export function getRolePermissions(roleId: number) {
  return get<{ code: number; data: { menus: Menu[]; apis: Permission[] } }>('/api/v1/role/authorized', { id: roleId })
}

/**
 * 更新角色权限
 */
export function updateRolePermissions(data: { role_id: number; menu_ids: number[]; api_ids: number[] }) {
  return post<{ code: number; msg: string }>('/api/v1/role/authorized', data)
}

