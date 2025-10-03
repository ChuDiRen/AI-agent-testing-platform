// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户管理状态
 * 适配 FastAPI RBAC 权限系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getUserList,
  updateUser,
  deleteUser,
  exportUsersCSV,
  exportUsersJSON,
  type User,
  type UserListParams,
  type UserUpdateData
} from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentUser = ref<User | null>(null)

  // Actions
  async function fetchUserList(params: UserListParams = {}) {
    try {
      loading.value = true
      const response = await getUserList(params)
      
      if (response.success && response.data) {
        users.value = response.data.items
        total.value = response.data.total
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      ElMessage.error('获取用户列表失败')
    } finally {
      loading.value = false
    }
  }

  async function updateUserAction(userId: number, data: UserUpdateData) {
    try {
      loading.value = true
      const response = await updateUser(userId, data)
      
      if (response.success) {
        ElMessage.success(response.message || '更新用户成功')
        return true
      } else {
        ElMessage.error(response.message || '更新用户失败')
        return false
      }
    } catch (error: any) {
      console.error('更新用户失败:', error)
      ElMessage.error(error.message || '更新用户失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteUserAction(userId: number) {
    try {
      loading.value = true
      const response = await deleteUser(userId)
      
      if (response.success) {
        ElMessage.success(response.message || '删除用户成功')
        users.value = users.value.filter(u => u.user_id !== userId)
        total.value -= 1
        return true
      } else {
        ElMessage.error(response.message || '删除用户失败')
        return false
      }
    } catch (error: any) {
      console.error('删除用户失败:', error)
      ElMessage.error(error.message || '删除用户失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function exportCSV(keyword?: string) {
    try {
      loading.value = true
      const blob = await exportUsersCSV(keyword)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `users_${new Date().getTime()}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('导出成功')
    } catch (error: any) {
      console.error('导出失败:', error)
      ElMessage.error(error.message || '导出失败')
    } finally {
      loading.value = false
    }
  }

  async function exportJSON(keyword?: string) {
    try {
      loading.value = true
      const blob = await exportUsersJSON(keyword)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `users_${new Date().getTime()}.json`
      link.click()
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('导出成功')
    } catch (error: any) {
      console.error('导出失败:', error)
      ElMessage.error(error.message || '导出失败')
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    users,
    total,
    loading,
    currentUser,
    // Actions
    fetchUserList,
    updateUser: updateUserAction,
    deleteUser: deleteUserAction,
    exportCSV,
    exportJSON
  }
})

