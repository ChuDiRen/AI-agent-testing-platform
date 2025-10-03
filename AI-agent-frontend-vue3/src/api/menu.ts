// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 菜单管理 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, put, del } from './request'

export interface Menu {
  menu_id: number
  parent_id: number
  menu_name: string
  path?: string
  component?: string
  perms?: string | null
  icon?: string
  type: string
  order_num?: number | null
  create_time?: string
  modify_time?: string
}

export interface MenuTree extends Menu {
  children: MenuTree[]
}

export interface MenuCreateData {
  parent_id: number
  menu_name: string
  path?: string
  component?: string
  perms?: string | null
  icon?: string
  type: string
  order_num?: number | null
}

export interface MenuUpdateData {
  parent_id?: number
  menu_name?: string
  path?: string
  component?: string
  perms?: string | null
  icon?: string
  type?: string
  order_num?: number | null
}

/**
 * 创建菜单/按钮
 */
export function createMenu(data: MenuCreateData) {
  return post<{ success: boolean; message: string; data: Menu }>('/api/v1/menus/', data)
}

/**
 * 获取菜单列表
 */
export function getMenuList(params?: { skip?: number; limit?: number }) {
  return get<{ success: boolean; data: Menu[] }>('/api/v1/menus/', params)
}

/**
 * 获取菜单树结构
 */
export function getMenuTree() {
  return get<{ success: boolean; data: MenuTree[] }>('/api/v1/menus/tree')
}

/**
 * 获取用户菜单
 */
export function getUserMenus(userId: number) {
  return get<{ success: boolean; data: Menu[] }>(`/api/v1/menus/user/${userId}`)
}

/**
 * 获取菜单详情
 */
export function getMenuDetail(menuId: number) {
  return get<{ success: boolean; data: Menu }>(`/api/v1/menus/${menuId}`)
}

/**
 * 更新菜单
 */
export function updateMenu(menuId: number, data: MenuUpdateData) {
  return put<{ success: boolean; message: string; data: Menu }>(`/api/v1/menus/${menuId}`, data)
}

/**
 * 删除菜单
 */
export function deleteMenu(menuId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/menus/${menuId}`)
}

