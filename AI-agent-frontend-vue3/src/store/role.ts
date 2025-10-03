// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 角色管理状态
 * 适配 FastAPI RBAC 权限系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getRoleList,
  createRole,
  updateRole,
  deleteRole,
  getRoleDetail,
  type Role,
  type RoleWithMenus,
  type RoleCreateData,
  type RoleUpdateData,
  type RoleListParams
} from '@/api/role'
import { ElMessage } from 'element-plus'

export const useRoleStore = defineStore('role', () => {
  // State
  const roles = ref<RoleWithMenus[]>([])
  const loading = ref(false)
  const currentRole = ref<RoleWithMenus | null>(null)

  // Actions
  async function fetchRoleList(params: RoleListParams = {}) {
    try {
      loading.value = true
      const response = await getRoleList(params)
      
      if (response.success && response.data) {
        roles.value = response.data
      }
    } catch (error) {
      console.error('获取角色列表失败:', error)
      ElMessage.error('获取角色列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchRoleDetail(roleId: number) {
    try {
      loading.value = true
      const response = await getRoleDetail(roleId)
      
      if (response.success && response.data) {
        currentRole.value = response.data
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取角色详情失败:', error)
      ElMessage.error('获取角色详情失败')
      return null
    } finally {
      loading.value = false
    }
  }

  async function createRoleAction(data: RoleCreateData) {
    try {
      loading.value = true
      const response = await createRole(data)
      
      if (response.success) {
        ElMessage.success(response.message || '创建角色成功')
        return true
      } else {
        ElMessage.error(response.message || '创建角色失败')
        return false
      }
    } catch (error: any) {
      console.error('创建角色失败:', error)
      ElMessage.error(error.message || '创建角色失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateRoleAction(roleId: number, data: RoleUpdateData) {
    try {
      loading.value = true
      const response = await updateRole(roleId, data)
      
      if (response.success) {
        ElMessage.success(response.message || '更新角色成功')
        return true
      } else {
        ElMessage.error(response.message || '更新角色失败')
        return false
      }
    } catch (error: any) {
      console.error('更新角色失败:', error)
      ElMessage.error(error.message || '更新角色失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteRoleAction(roleId: number) {
    try {
      loading.value = true
      const response = await deleteRole(roleId)
      
      if (response.success) {
        ElMessage.success(response.message || '删除角色成功')
        roles.value = roles.value.filter(r => r.role_id !== roleId)
        return true
      } else {
        ElMessage.error(response.message || '删除角色失败')
        return false
      }
    } catch (error: any) {
      console.error('删除角色失败:', error)
      ElMessage.error(error.message || '删除角色失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    roles,
    loading,
    currentRole,
    // Actions
    fetchRoleList,
    fetchRoleDetail,
    createRole: createRoleAction,
    updateRole: updateRoleAction,
    deleteRole: deleteRoleAction
  }
})

