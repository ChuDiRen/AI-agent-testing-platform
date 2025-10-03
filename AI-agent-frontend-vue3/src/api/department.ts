// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 部门管理 API
 * 对接 FastAPI RBAC 权限系统
 */
import { get, post, put, del } from './request'

export interface Department {
  dept_id: number
  parent_id: number
  dept_name: string
  order_num?: number | null
  create_time?: string
  modify_time?: string
}

export interface DepartmentCreateData {
  parent_id: number
  dept_name: string
  order_num?: number | null
}

export interface DepartmentUpdateData {
  parent_id?: number
  dept_name?: string
  order_num?: number | null
}

/**
 * 创建部门
 */
export function createDepartment(data: DepartmentCreateData) {
  return post<{ success: boolean; message: string; data: Department }>('/api/v1/departments/', data)
}

/**
 * 获取部门列表
 */
export function getDepartmentList(params?: { skip?: number; limit?: number }) {
  return get<{ success: boolean; data: Department[] }>('/api/v1/departments/', params)
}

/**
 * 获取部门详情
 */
export function getDepartmentDetail(deptId: number) {
  return get<{ success: boolean; data: Department }>(`/api/v1/departments/${deptId}`)
}

/**
 * 更新部门
 */
export function updateDepartment(deptId: number, data: DepartmentUpdateData) {
  return put<{ success: boolean; message: string; data: Department }>(`/api/v1/departments/${deptId}`, data)
}

/**
 * 删除部门
 */
export function deleteDepartment(deptId: number) {
  return del<{ success: boolean; message: string }>(`/api/v1/departments/${deptId}`)
}

