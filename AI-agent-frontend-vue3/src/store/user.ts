// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户管理状态
 * 适配 FastAPI RBAC 权限系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  exportUsersCSV,
  exportUsersJSON,
  type User,
  type UserListParams,
  type UserCreateData,
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

  async function createUserAction(data: UserCreateData) {
    try {
      loading.value = true
      const response = await createUser(data)

      if (response.success) {
        ElMessage.success(response.message || '创建用户成功')
        return true
      } else {
        ElMessage.error(response.message || '创建用户失败')
        return false
      }
    } catch (error: any) {
      console.error('创建用户失败:', error)
      ElMessage.error(error.message || '创建用户失败')
      return false
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
      const response = await exportUsersCSV(keyword)

      // 处理不同类型的响应
      let blob: Blob
      if (response instanceof Blob) {
        blob = response
      } else if (response && typeof response === 'object' && response.data instanceof Blob) {
        blob = response.data
      } else {
        // 如果响应是字符串，创建Blob
        const content = typeof response === 'string' ? response : JSON.stringify(response)
        blob = new Blob([content], { type: 'text/csv;charset=utf-8' })
      }

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `users_${new Date().getTime()}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
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
      const response = await exportUsersJSON(keyword)

      // 处理不同类型的响应
      let blob: Blob
      if (response instanceof Blob) {
        blob = response
      } else if (response && typeof response === 'object' && response.data instanceof Blob) {
        blob = response.data
      } else {
        // 如果响应是字符串，创建Blob
        const content = typeof response === 'string' ? response : JSON.stringify(response)
        blob = new Blob([content], { type: 'application/json;charset=utf-8' })
      }

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `users_${new Date().getTime()}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
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
    createUser: createUserAction,
    updateUser: updateUserAction,
    deleteUser: deleteUserAction,
    exportCSV,
    exportJSON
  }
})

