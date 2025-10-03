// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getUserInfo, logout as logoutApi, type LoginRequest, type UserInfo } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const userInfo = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const hasRole = (role: string) => roles.value.includes(role)
  const hasPermission = (permission: string) => permissions.value.includes(permission)
  const isAdmin = computed(() => roles.value.some(role => role === 'admin' || role === 'super_admin'))

  // Actions
  async function loginAction(loginData: LoginRequest) {
    try {
      const response = await login(loginData)
      
      if (response.code === 200 && response.data) {
        // 保存 token
        token.value = response.data.access_token
        refreshToken.value = response.data.refresh_token
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('refreshToken', response.data.refresh_token)
        
        // 保存用户信息
        if (response.data.userinfo) {
          userInfo.value = response.data.userinfo as any
          roles.value = response.data.userinfo.roles || []
          permissions.value = response.data.userinfo.permissions || []
        }
        
        ElMessage.success('登录成功')
        return true
      } else {
        ElMessage.error(response.message || '登录失败')
        return false
      }
    } catch (error: any) {
      console.error('Login error:', error)
      ElMessage.error(error.message || '登录失败')
      return false
    }
  }

  async function fetchUserInfo() {
    try {
      const response = await getUserInfo()
      
      if (response.code === 200 && response.data) {
        userInfo.value = response.data
        roles.value = response.data.roles?.map(r => r.code) || []
        permissions.value = response.data.permissions || []
        return true
      }
      return false
    } catch (error) {
      console.error('Fetch user info error:', error)
      return false
    }
  }

  async function logoutAction() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // 清除本地数据
      token.value = ''
      refreshToken.value = ''
      userInfo.value = null
      permissions.value = []
      roles.value = []
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      ElMessage.success('已退出登录')
    }
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function clearAuth() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    permissions.value = []
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  return {
    // State
    token,
    refreshToken,
    userInfo,
    permissions,
    roles,
    // Getters
    isAuthenticated,
    isAdmin,
    // Actions
    login: loginAction,
    logout: logoutAction,
    fetchUserInfo,
    setToken,
    clearAuth,
    hasRole,
    hasPermission
  }
})

