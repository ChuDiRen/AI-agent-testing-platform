// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 用户管理状态
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  resetPassword,
  changeUserStatus,
  type User,
  type UserListParams,
  type UserCreateData
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
      
      if (response.code === 200 && response.data) {
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
      
      if (response.code === 200) {
        ElMessage.success('创建用户成功')
        return true
      } else {
        ElMessage.error(response.msg || '创建用户失败')
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

  async function updateUserAction(data: Partial<User> & { id: number }) {
    try {
      loading.value = true
      const response = await updateUser(data)
      
      if (response.code === 200) {
        ElMessage.success('更新用户成功')
        return true
      } else {
        ElMessage.error(response.msg || '更新用户失败')
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

  async function deleteUserAction(id: number) {
    try {
      loading.value = true
      const response = await deleteUser(id)
      
      if (response.code === 200) {
        ElMessage.success('删除用户成功')
        users.value = users.value.filter(u => u.id !== id)
        total.value -= 1
        return true
      } else {
        ElMessage.error(response.msg || '删除用户失败')
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

  async function resetPasswordAction(id: number, password: string) {
    try {
      loading.value = true
      const response = await resetPassword(id, password)
      
      if (response.code === 200) {
        ElMessage.success('重置密码成功')
        return true
      } else {
        ElMessage.error(response.msg || '重置密码失败')
        return false
      }
    } catch (error: any) {
      console.error('重置密码失败:', error)
      ElMessage.error(error.message || '重置密码失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function changeStatusAction(id: number, status: number) {
    try {
      const response = await changeUserStatus(id, status)
      
      if (response.code === 200) {
        ElMessage.success('修改状态成功')
        // 更新本地状态
        const user = users.value.find(u => u.id === id)
        if (user) {
          user.status = status
        }
        return true
      } else {
        ElMessage.error(response.msg || '修改状态失败')
        return false
      }
    } catch (error: any) {
      console.error('修改状态失败:', error)
      ElMessage.error(error.message || '修改状态失败')
      return false
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
    resetPassword: resetPasswordAction,
    changeStatus: changeStatusAction
  }
})

