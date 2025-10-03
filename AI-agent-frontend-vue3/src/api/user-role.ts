// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户角色关联 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, del } from './request'
import type { Role } from './role'

export interface AssignRolesData {
  user_id: number
  role_ids: number[]
}

/**
 * 为用户分配角色
 */
export function assignUserRoles(data: AssignRolesData) {
  return post<{ success: boolean; message: string }>('/api/v1/user-roles/assign', data)
}

/**
 * 获取用户的角色列表
 */
export function getUserRoles(userId: number) {
  return get<{ success: boolean; data: Role[] }>(`/api/v1/user-roles/${userId}/roles`)
}

/**
 * 移除用户角色
 */
export function removeUserRole(userId: number, roleId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/user-roles/${userId}/roles/${roleId}`)
}

