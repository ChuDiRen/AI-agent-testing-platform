// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 角色管理 API
 */
import { get, post, del } from './request'

export interface Role {
  id: number
  name: string
  code: string
  description?: string
  permissions: string[]
  created_at: string
  updated_at: string
}

export interface RoleListParams {
  page?: number
  page_size?: number
  role_name?: string
}

export interface RoleCreateData {
  name: string
  code: string
  description?: string
  permission_ids?: number[]
}

/**
 * 获取角色列表
 */
export function getRoleList(params: RoleListParams = {}) {
  return get<{ code: number; data: { items: Role[]; total: number } }>('/api/v1/role/list', params)
}

/**
 * 获取角色详情
 */
export function getRoleDetail(id: number) {
  return get<{ code: number; data: Role }>(`/api/v1/role/${id}`)
}

/**
 * 创建角色
 */
export function createRole(data: RoleCreateData) {
  return post<{ code: number; msg: string }>('/api/v1/role/create', data)
}

/**
 * 更新角色
 */
export function updateRole(data: Partial<Role> & { id: number }) {
  return post<{ code: number; msg: string }>('/api/v1/role/update', data)
}

/**
 * 删除角色
 */
export function deleteRole(id: number) {
  return del<{ code: number; msg: string }>('/api/v1/role/delete', { id })
}

/**
 * 分配权限
 */
export function assignPermissions(roleId: number, permissionIds: number[]) {
  return post<{ code: number; msg: string }>('/api/v1/role/assign-permissions', {
    role_id: roleId,
    permission_ids: permissionIds
  })
}

