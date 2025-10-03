// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 角色菜单关联 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, del } from './request'
import type { Menu } from './menu'

export interface AssignMenusData {
  role_id: number
  menu_ids: number[]
}

/**
 * 为角色分配菜单权限
 */
export function assignRoleMenus(data: AssignMenusData) {
  return post<{ success: boolean; message: string }>('/api/v1/role-menus/assign', data)
}

/**
 * 获取角色的菜单列表
 */
export function getRoleMenus(roleId: number) {
  return get<{ success: boolean; data: Menu[] }>(`/api/v1/role-menus/${roleId}/menus`)
}

/**
 * 移除角色菜单权限
 */
export function removeRoleMenu(roleId: number, menuId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/role-menus/${roleId}/menus/${menuId}`)
}

