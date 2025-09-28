// Copyright (c) 2025 左岚. All rights reserved.

import { defineStore } from 'pinia'
import { AuthApi } from '@/api/modules/auth'
import { UserApi } from '@/api/modules/user'
import { MenuApi } from '@/api/modules/menu'
import {
  getToken,
  setToken as setTokenStorage,
  removeToken,
  setRefreshToken,
  getRefreshToken,
} from '@/utils/auth'
import { setTokenVersion } from '@/utils/tokenValidator'
import type { UserInfo, MenuInfo } from '@/api/types'
import { usePermissionStore } from '@/store/modules/permission'
import { resetRoutes } from '@/router'

// 去重用的初始化进行中 Promise（不入持久化）
let initInFlight: Promise<void> | null = null

export interface UserState {
  token: string | null
  userInfo: UserInfo | null
  permissions: string[]
  roles: string[]
  menus: MenuInfo[]
  loading: boolean
  initialized?: boolean
  avatarTimestamp: number
}

export const useUserStore = defineStore('user', {
  state: (): UserState => {
    const token = getToken()
    console.log('UserStore initialized with token:', token ? 'exists' : 'null')
    return {
      token: token || null,
      userInfo: null,
      permissions: [],
      roles: [],
      menus: [],
      loading: false,
      initialized: false,
      avatarTimestamp: Date.now(),
    }
  },

  getters: {
    isLoggedIn: (state) => !!state.token,
    getToken: (state) => state.token,
    username: (state) => state.userInfo?.username || '',
    avatar: (state) => state.userInfo?.avatar || '',
    hasRole: (state) => (role: string) => state.roles.includes(role),
    hasPermission: (state) => (permission: string) => state.permissions.includes(permission),
    hasAnyRole: (state) => (roles: string[]) => roles.some((role) => state.roles.includes(role)),
    hasAnyPermission: (state) => (permissions: string[]) =>
      permissions.some((perm) => state.permissions.includes(perm)),
    hasAllRoles: (state) => (roles: string[]) => roles.every((role) => state.roles.includes(role)),
    hasAllPermissions: (state) => (permissions: string[]) =>
      permissions.every((perm) => state.permissions.includes(perm)),
  },

  actions: {
    // 设置token
    setToken(token: string | null) {
      this.token = token
      if (token) {
        setTokenStorage(token)
        // 设置token版本，确保新token有效
        setTokenVersion()
        console.log('Token set successfully in store and storage')
      } else {
        removeToken()
        console.log('Token removed from store and storage')
      }
    },

    // 设置用户信息
    setUserInfo(userInfo: UserInfo | null) {
      this.userInfo = userInfo
    },

    // 设置权限
    setPermissions(permissions: string[]) {
      this.permissions = permissions
    },

    // 设置角色
    setRoles(roles: string[]) {
      this.roles = roles
    },

    // 设置菜单
    setMenus(menus: MenuInfo[]) {
      this.menus = menus
    },

    // 更新头像时间戳
    updateAvatarTimestamp() {
      this.avatarTimestamp = Date.now()
    },

    // 清除用户数据
    async clearUserData() {
      this.token = null
      this.userInfo = null
      this.permissions = []
      this.roles = []
      this.menus = []
      this.initialized = false
      this.avatarTimestamp = Date.now()
      
      // 使用统一的token清理方法
      const { clearAllTokenData } = await import('@/utils/tokenValidator')
      clearAllTokenData()

      // 清除权限store数据
      const permissionStore = usePermissionStore()
      permissionStore.resetPermission()

      // 重置路由
      resetRoutes()
      console.log('User data cleared successfully')
    },

    // 规范化角色名，增加英文别名支持
    normalizeRoleNames(sourceRoles: Array<{ role_name?: string } | string>): string[] {
      const names: string[] = []
      for (const r of sourceRoles) {
        const name = typeof r === 'string' ? r : r?.role_name || ''
        if (!name) continue
        names.push(name)
        // 常见别名映射（根据后端角色中文名补充英文别名）
        if (name.includes('超级管理员')) names.push('super_admin')
        if (name.includes('管理员')) names.push('admin')
      }
      // 去重
      return Array.from(new Set(names))
    },

    // 登录
    async login(username: string, password: string): Promise<boolean> {
      try {
        this.loading = true
        const response = await AuthApi.login({ username, password })

        if (response.success && response.data) {
          const { access_token, refresh_token, user_info, permissions } = response.data as any

          this.setToken(access_token)
          if (refresh_token) setRefreshToken(refresh_token)
          this.setUserInfo(user_info)
          if (Array.isArray(permissions)) this.setPermissions(permissions)

          // 登录后统一初始化（去重）
          await this.initializeAfterLogin().catch(() => {})

          // 登录成功后，动态路由将在路由守卫中加载
          // 这里不需要立即加载，避免重复加载

          return true
        }
        return false
      } catch (error) {
        console.error('登录失败:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    // 获取用户信息
    async getUserInfo(): Promise<void> {
      if (!this.token || !this.userInfo?.user_id) return

      try {
        this.loading = true
        const response = await UserApi.getUserById(this.userInfo.user_id)

        if (response.success && response.data) {
          this.setUserInfo(response.data)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 获取用户权限
    async getUserPermissions(): Promise<void> {
      if (!this.userInfo?.user_id) return

      try {
        const response = await UserApi.getUserPermissions(this.userInfo.user_id)

        if (response.success && response.data) {
          this.setPermissions(response.data)
        }
      } catch (error) {
        console.error('获取用户权限失败:', error)
      }
    },

    // 获取用户角色
    async getUserRoles(): Promise<void> {
      if (!this.userInfo?.user_id) return

      try {
        const res = await UserApi.getUserRoles(this.userInfo.user_id)
        if (res.success && (res.data as any)?.roles) {
          const roleNames = this.normalizeRoleNames((res.data as any).roles)
          this.setRoles(roleNames)
        }
      } catch (error) {
        console.error('获取用户角色失败:', error)
      }
    },

    // 获取用户菜单
    async getUserMenus(): Promise<void> {
      if (!this.userInfo?.user_id) return

      try {
        const response = await MenuApi.getUserMenuTree(this.userInfo.user_id)

        if (response.success && response.data) {
          this.setMenus(response.data)
        }
      } catch (error) {
        console.error('获取用户菜单失败:', error)
      }
    },

    // 懒加载进入受保护路由所需数据（统一到初始化）
    async ensureAccessDataLoaded(): Promise<void> {
      if (!this.isLoggedIn) return
      await this.initializeAfterLogin().catch(() => {})
    },

    // 统一初始化（幂等 + 去重）：登录成功或首个受保护路由进入时调用
    async initializeAfterLogin(): Promise<void> {
      if (!this.isLoggedIn) return
      if (this.initialized) return
      if (initInFlight) return initInFlight
      initInFlight = (async () => {
        try {
          const tasks: Array<Promise<any>> = []
          if (this.userInfo?.user_id) {
            if (!this.roles?.length) tasks.push(this.getUserRoles())
            if (!this.permissions?.length) tasks.push(this.getUserPermissions())
            if (!this.menus?.length) tasks.push(this.getUserMenus())
          }
          if (tasks.length) await Promise.allSettled(tasks)
          this.initialized = true
        } finally {
          initInFlight = null
        }
      })()
      return initInFlight
    },

    // 登出
    async logout(): Promise<void> {
      try {
        // 调用登出接口（携带refresh_token黑名单）
        const rt = getRefreshToken()
        await AuthApi.logout(rt ? { refresh_token: rt } : undefined)
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        // 清除本地数据
        await this.clearUserData()

        // 重置路由
        const { resetRoutes } = await import('@/router')
        resetRoutes()
      }
    },

    // 刷新token（保留：若主动调用时使用，拦截器已兜底自动刷新）
    async refreshToken(): Promise<boolean> {
      if (!this.token) return false

      try {
        const response = await AuthApi.refreshToken()

        if (response.success && response.data) {
          this.setToken(response.data.access_token)
          if ((response.data as any).refresh_token) {
            setRefreshToken((response.data as any).refresh_token as string)
          }
          return true
        }
        return false
      } catch (error) {
        console.error('刷新token失败:', error)
        await this.clearUserData()
        return false
      }
    },
  },

  persist: {
    key: 'user-store',
    storage: localStorage,
  },
})
