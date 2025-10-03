// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 角色管理 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, put, del } from './request'

export interface RoleMenu {
  menu_id: number
  menu_name: string
  perms?: string | null
  type?: string
}

export interface Role {
  role_id: number
  role_name: string
  remark?: string
  create_time?: string
  modify_time?: string
}

export interface RoleWithMenus extends Role {
  menus: RoleMenu[]
}

export interface RoleListParams {
  skip?: number
  limit?: number
}

export interface RoleCreateData {
  role_name: string
  remark?: string
}

export interface RoleUpdateData {
  role_name?: string
  remark?: string
}

/**
 * 创建角色
 */
export function createRole(data: RoleCreateData) {
  return post<{ success: boolean; message: string; data: Role }>('/api/v1/roles/', data)
}

/**
 * 获取角色列表
 */
export function getRoleList(params: RoleListParams = {}) {
  return get<{ success: boolean; data: RoleWithMenus[] }>('/api/v1/roles/', params)
}

/**
 * 获取角色详情
 */
export function getRoleDetail(roleId: number) {
  return get<{ success: boolean; data: RoleWithMenus }>(`/api/v1/roles/${roleId}`)
}

/**
 * 更新角色
 */
export function updateRole(roleId: number, data: RoleUpdateData) {
  return put<{ success: boolean; message: string; data: Role }>(`/api/v1/roles/${roleId}`, data)
}

/**
 * 删除角色
 */
export function deleteRole(roleId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/roles/${roleId}`)
}

