import { defineStore } from 'pinia'
import { AuthApi } from '@/api/modules/auth'
import { UserApi } from '@/api/modules/user'
import { MenuApi } from '@/api/modules/menu'
import { getToken, setToken as setTokenStorage, removeToken } from '@/utils/auth'
import type { UserInfo, MenuInfo } from '@/api/types'

export interface UserState {
  token: string | null
  userInfo: UserInfo | null
  permissions: string[]
  roles: string[]
  menus: MenuInfo[]
  loading: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken() || null,
    userInfo: null,
    permissions: [],
    roles: [],
    menus: [],
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    getToken: (state) => state.token,
    username: (state) => state.userInfo?.username || '',
    avatar: (state) => state.userInfo?.avatar || '',
    hasRole: (state) => (role: string) => state.roles.includes(role),
    hasPermission: (state) => (permission: string) => state.permissions.includes(permission),
    hasAnyRole: (state) => (roles: string[]) => roles.some(role => state.roles.includes(role)),
    hasAnyPermission: (state) => (permissions: string[]) => permissions.some(perm => state.permissions.includes(perm)),
    hasAllRoles: (state) => (roles: string[]) => roles.every(role => state.roles.includes(role)),
    hasAllPermissions: (state) => (permissions: string[]) => permissions.every(perm => state.permissions.includes(perm))
  },

  actions: {
    // 设置token
    setToken(token: string | null) {
      this.token = token
      if (token) {
        setTokenStorage(token)
      } else {
        removeToken()
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

    // 清除用户数据
    clearUserData() {
      this.token = null
      this.userInfo = null
      this.permissions = []
      this.roles = []
      this.menus = []
      removeToken()
    },

    // 登录
    async login(username: string, password: string): Promise<boolean> {
      try {
        this.loading = true
        const response = await AuthApi.login({ username, password })
        
        if (response.success && response.data) {
          const { access_token, user_info, permissions } = response.data
          
          this.setToken(access_token)
          this.setUserInfo(user_info)
          this.setPermissions(permissions)
          
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

    // 获取用户菜单
    async getUserMenus(): Promise<void> {
      if (!this.userInfo?.user_id) return
      
      try {
        const response = await MenuApi.getMenuTree()
        
        if (response.success && response.data) {
          this.setMenus(response.data)
        }
      } catch (error) {
        console.error('获取用户菜单失败:', error)
      }
    },

    // 登出
    async logout(): Promise<void> {
      try {
        // 调用登出接口
        await AuthApi.logout()
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.clearUserData()
      }
    },

    // 刷新token
    async refreshToken(): Promise<boolean> {
      if (!this.token) return false
      
      try {
        const response = await AuthApi.refreshToken()
        
        if (response.success && response.data) {
          this.setToken(response.data.access_token)
          return true
        }
        return false
      } catch (error) {
        console.error('刷新token失败:', error)
        this.clearUserData()
        return false
      }
    }
  },

  persist: {
    key: 'user-store',
    storage: localStorage
  }
})